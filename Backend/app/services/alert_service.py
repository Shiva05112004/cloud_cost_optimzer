import boto3
from app.config import get_settings

settings = get_settings()


def send_alert_email(to_email: str, subject: str, body: str) -> dict:
    """
    Sends an alert email via AWS SES.
    Requires:
      - SES_SENDER_EMAIL in .env (must be verified in AWS SES)
      - SES_REGION in .env
      - AWS credentials with ses:SendEmail permission
    """
    ses = boto3.client("ses", region_name=settings.ses_region)

    response = ses.send_email(
        Source=settings.ses_sender_email,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Text": {
                    "Data": body,
                    "Charset": "UTF-8",
                }
            },
        },
    )

    return {
        "message_id": response["MessageId"],
        "status": "sent",
        "to": to_email,
    }


def send_cost_spike_alert(to_email: str, resource_id: str, savings: float) -> dict:
    """
    Convenience wrapper — sends a pre-formatted cost alert.
    """
    subject = f"Cost Alert: {resource_id} is wasting ${savings:.2f}/month"
    body = (
        f"Cloud Cost Optimizer detected an issue:\n\n"
        f"Resource : {resource_id}\n"
        f"Estimated waste : ${savings:.2f} / month\n\n"
        f"Log in to your dashboard to review and apply the recommendation.\n"
    )
    return send_alert_email(to_email, subject, body)