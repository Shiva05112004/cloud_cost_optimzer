# Cloud Cost Optimizer Project Report

## 1. Project Summary

Cloud Cost Optimizer is a full-stack cloud cost analysis and recommendation platform built around AWS accounts. The product lets a user register and log in, connect an AWS account through an IAM role, inspect EC2 resources and monthly service costs, and review cost-saving recommendations generated from usage data. The UI presents a dashboard, a resources table, and a recommendations view, while the backend handles authentication, AWS API access, persistence, background refresh jobs, and lightweight ML-driven optimization logic.

The project is currently organized as a two-part application:

- `Backend/` contains the FastAPI service, SQLAlchemy models, Celery jobs, AWS client wrappers, and ML logic.
- `frontend/` contains the React + Vite dashboard UI with protected routes, local auth state, API wrappers, and reusable cards/tables/charts.

## 2. From Scratch View

If you explain the project from the beginning, the story is:

1. A user creates an account and signs in with email and password.
2. The backend issues a JWT token and the frontend stores it locally.
3. The user connects an AWS account by providing an IAM Role ARN.
4. The backend uses AWS STS to assume that role and then calls EC2, CloudWatch, and Cost Explorer.
5. The application calculates current cost, average CPU usage, and recommendation candidates.
6. The backend stores accounts and recommendation logs in the database.
7. Celery refresh jobs periodically rebuild recommendations so the dashboard stays fast.
8. The frontend reads the cached results and renders a dashboard, resources table, and recommendation cards.

## 3. Backend Architecture

The backend is a FastAPI application defined in [Backend/app/main.py](Backend/app/main.py). It exposes four main route groups:

- Auth at `/api/auth`
- Accounts at `/api/accounts`
- Resources at `/api/resources`
- Recommendations at `/api/recommendations`

### Core backend layers

- `app/config.py` loads environment settings such as the database URL, Redis URL, AWS region, JWT settings, and SES configuration.
- `app/models/database.py` creates the SQLAlchemy engine, session factory, and base model.
- `app/models/*.py` defines the database schema for users, cloud accounts, recommendations, anomalies, events, and metric features.
- `app/services/*.py` contains business logic for authentication, account persistence, alerting, anomaly analysis, and recommendation ranking.
- `app/cloud_api/*.py` wraps AWS SDK calls for EC2, CloudWatch, Cost Explorer, and STS role assumption.
- `app/ml/*.py` contains the cost-rightsizing logic, anomaly detectors, and Phase A ML playground code.
- `app/tasks.py` defines Celery tasks for refreshing recommendations and anomaly analysis.

## 4. Backend Features

### Authentication

Authentication is JWT-based. Users register with email, password, and optional full name. Passwords are hashed with `passlib`, and login returns a bearer token. The shared `get_current_user` dependency validates the token and protects authenticated endpoints.

### Cloud account connection

Users connect an AWS account by submitting an account name and IAM Role ARN. The role ARN is stored, then reused for AWS API calls after the backend assumes the role.

### Resource and cost collection

The resource endpoints fetch:

- EC2 instances and their state
- Average CPU utilization from CloudWatch
- Monthly service-level AWS costs from Cost Explorer

### Recommendation generation

The recommendation pipeline is a mix of rule-based ML and ranking logic:

- `app/ml/rightsizer.py` suggests stopping idle instances or downgrading low-utilization instances.
- `app/services/optimizer_service.py` converts savings, confidence, and risk into a priority score.
- `app/tasks.py` refreshes recommendations for one account, one user, or all accounts.
- `app/routes/recommendations.py` returns the cached recommendation logs for the authenticated user.

### Anomaly detection

The anomaly side of the backend includes:

- `app/services/anomaly_service.py`, which pulls daily cost history, builds features, runs a seasonal anomaly detector, and stores detected anomalies.
- `app/routes/anomalies.py`, which lists anomalies, marks false positives, and triggers analysis for an account.

### Alerts

`app/services/alert_service.py` can send alert emails through AWS SES when a cost issue is found.

## 5. Frontend Architecture

The frontend is a React app built with Vite. It uses:

- React Router for navigation
- Zustand for auth and dashboard state
- Axios for API calls
- React Hot Toast for user feedback
- Recharts for cost visualization

The main app shell is in [frontend/src/App.jsx](frontend/src/App.jsx). Protected routes wrap the dashboard pages, while the login and register screens stay public.

### Main pages

- `LoginPage.jsx` handles sign-in and stores the JWT.
- `RegisterPage.jsx` creates a new user.
- `DashboardPage.jsx` loads EC2, cost, and recommendation data and shows KPI cards, a cost chart, and top recommendations.
- `ResourcesPage.jsx` shows all EC2 instances in a table with CPU-based status indicators.
- `RecommendationPage.jsx` shows ranked optimization recommendations.
- `ConnectAccountPage.jsx` collects the IAM Role ARN and explains the AWS setup steps.

### UI system

The visual style is dark, modern, and dashboard-oriented. Global colors, typography, cards, badges, and tables are defined in [frontend/src/index.css](frontend/src/index.css). The sidebar and KPI cards provide the main navigation and overview experience.

## 6. Data Flow

The project’s runtime flow looks like this:

1. The frontend authenticates the user and keeps the token in local storage.
2. Authenticated API requests automatically include the JWT.
3. The user connects an AWS role, which gets saved in the database.
4. Backend AWS clients assume that role and collect EC2, CloudWatch, and Cost Explorer data.
5. Recommendation tasks calculate savings opportunities and persist them in `recommendation_logs`.
6. The dashboard reads the cached recommendation rows and renders them quickly.
7. Anomaly analysis and alerting remain available as adjacent capability paths.

## 7. Local Setup And Infra

The repository includes local infrastructure support for Postgres and Redis in [docker-compose.yml](docker-compose.yml). The backend docs in `Backend/POSTGRES_SETUP.md` describe a Postgres + Alembic workflow, while `Backend/run.sh` still shows a simple local startup path that initializes a SQLite database and launches Uvicorn.

That means the project is currently in a mixed setup state:

- Postgres and Redis are explicitly supported for the newer workflow.
- The backend code still contains SQLite-oriented startup logic.
- The runtime configuration defaults to a Postgres connection string.

## 8. ML Scope

There are three ML-related tracks in the repo:

- Rightsizing recommendations based on EC2 CPU utilization.
- Anomaly detection on cost history using feature engineering and seasonal logic.
- Phase A playground code that builds a dataset from event rows and compares Random Forest versus XGBoost on a labeled classification task.

The Phase A pipeline lives in `Backend/app/ml/phase_a/` and is run through `Backend/scripts/run_phase_a_ml.py`. It reads either Postgres or CSV event data, creates time features, labels high-value events by quantile, and reports validation/test metrics for both models.

## 9. Current Status

At the current state of the repo, the project is best described as a working prototype with a fairly complete product skeleton:

- The API, database models, and frontend screens are all in place.
- Recommendation generation and auth flows are implemented.
- AWS integration points are wired for EC2, CloudWatch, Cost Explorer, and SES.
- Background job plumbing is present through Celery and Redis.
- The Phase A ML playground and anomaly pipeline are included, but they look like adjacent analytic tracks rather than a single polished production model.

## 10. Good Resume Framing

If you want to present this as a resume project, the strongest framing is:

- Built a full-stack AWS cost optimization platform.
- Implemented JWT auth, multi-account onboarding, and protected dashboards.
- Integrated AWS EC2, CloudWatch, Cost Explorer, and SES through role-based access.
- Added background recommendation refresh jobs with Celery and Redis.
- Designed ML-assisted rightsizing and anomaly detection workflows.
- Built a polished React dashboard with live resource visibility and cost-saving recommendations.

## 11. Notes For Claude Or Another LLM

If you hand this project to Claude, the best prompt is to ask it to:

1. Summarize the product purpose in plain language.
2. Explain the backend, frontend, AWS, database, and ML layers separately.
3. Identify what is complete versus what still looks experimental or in progress.
4. Turn the codebase into a resume-ready project description.
5. Suggest follow-up improvements, tests, and deployment hardening.

## 12. Short Handoff Summary

This repo is a cloud cost optimization assistant for AWS. The backend is FastAPI with JWT auth, SQLAlchemy, Celery, Redis, and AWS SDK integrations. The frontend is a Vite React dashboard with protected routes, auth state, charts, and recommendation views. The project also includes anomaly detection and a Phase A ML playground for model comparison.