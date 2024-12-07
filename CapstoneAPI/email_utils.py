# from django.core.mail import send_mail
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def send_email_with_ses(subject, body, recipient):
    """Sends an email using Amazon SES"""
    ses_client = boto3.client(
        "ses",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME,
    )

    try:
        response = ses_client.send_email(
            Source=settings.DEFAULT_FROM_EMAIL,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": body},
                },
            },
        )
        return response
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
        return None
