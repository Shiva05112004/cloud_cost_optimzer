# Cloud Cost Optimizer - Vercel Deployment Guide

This guide will help you deploy the Cloud Cost Optimizer project to Vercel.

## Project Structure

This is a monorepo with:
- `frontend/` - React + Vite frontend
- `Backend/` - FastAPI Python backend

## Prerequisites

1. Vercel account
2. PostgreSQL database (recommended: Supabase, Neon, or Railway)
3. Redis instance (recommended: Upstash or Railway)
4. AWS account with appropriate credentials

## Deployment Strategy

We recommend deploying the frontend and backend as separate Vercel projects for better isolation and scaling.

### Option 1: Separate Deployments (Recommended)

#### Backend Deployment

1. **Deploy Backend:**
   ```bash
   cd Backend
   vercel
   ```
   
2. **Configure Environment Variables in Vercel Dashboard:**
   - `DATABASE_URL` - Your PostgreSQL connection string
   - `SECRET_KEY` - Random secret key for JWT
   - `REDIS_URL` - Your Redis connection string
   - `AWS_ACCESS_KEY_ID` - AWS access key
   - `AWS_SECRET_ACCESS_KEY` - AWS secret key
   - `AWS_DEFAULT_REGION` - AWS region (e.g., us-east-1)
   - `JWT_ALGORITHM` - HS256
   - `JWT_EXPIRE_MINUTES` - 60

3. **Note the deployed backend URL** (e.g., `https://cloud-cost-backend.vercel.app`)

#### Frontend Deployment

1. **Configure Environment Variable:**
   ```bash
   cd frontend
   vercel env add VITE_API_URL
   # Enter your backend URL: https://cloud-cost-backend.vercel.app
   ```

2. **Deploy Frontend:**
   ```bash
   vercel
   ```

### Option 2: Monorepo Deployment

If you prefer to deploy as a single project, use the root-level configuration.

1. **Set Environment Variables in Vercel Dashboard:**
   - All backend variables listed above
   - `VITE_API_URL` - Your backend URL (can be same domain)

2. **Deploy:**
   ```bash
   vercel
   ```

## Database Setup

### PostgreSQL (Required)

1. Create a PostgreSQL database on Supabase, Neon, or Railway
2. Get the connection string in format: `postgresql+psycopg2://user:password@host:5432/database`
3. Add to Vercel environment variables

### Redis (Optional but Recommended)

1. Create a Redis instance on Upstash or Railway
2. Get the connection string: `redis://host:6379/0`
3. Add to Vercel environment variables

## AWS Configuration

1. Create an IAM user with the following permissions:
   - `AmazonEC2ReadOnlyAccess`
   - `CloudWatchReadOnlyAccess`
   - `AWSCostExplorerReadOnlyAccess`

2. Generate access keys and add to Vercel environment variables

## Post-Deployment Steps

1. **Run Database Migrations:**
   - Access your Vercel deployment
   - Run the Alembic migrations to set up database tables
   - Or use the automatic table creation in `main.py`

2. **Test the Application:**
   - Register a new user
   - Connect an AWS account using IAM Role ARN
   - Verify the connection status indicator shows as connected
   - Check dashboard for cost data

## Environment Variables Reference

### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `REDIS_URL` - Redis connection string
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_DEFAULT_REGION` - AWS region
- `JWT_ALGORITHM` - JWT algorithm (HS256)
- `JWT_EXPIRE_MINUTES` - JWT expiration time
- `SES_SENDER_EMAIL` - Email for alerts (optional)
- `SES_REGION` - AWS SES region (optional)

### Frontend
- `VITE_API_URL` - Backend API URL

## Troubleshooting

### CORS Issues
- The backend is configured to allow all origins for deployment
- If you still face CORS issues, check the backend logs

### Database Connection
- Ensure your PostgreSQL database allows connections from Vercel's IP ranges
- Check the connection string format

### AWS Connection
- Verify IAM permissions are correct
- Check that the IAM Role ARN format is correct
- Ensure the role trusts your AWS account

## Scaling Considerations

- Backend: Vercel's serverless functions automatically scale
- Database: Choose a managed PostgreSQL service that scales
- Redis: Use a managed Redis service for production
- Frontend: Vercel's edge network handles global distribution

## Monitoring

- Set up Vercel Analytics for frontend monitoring
- Use Vercel Logs for backend debugging
- Monitor database performance through your provider's dashboard
- Set up AWS CloudWatch for AWS API usage monitoring
