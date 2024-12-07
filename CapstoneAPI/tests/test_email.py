from django.test import TestCase
from CapstoneAPI.email_utils import send_custom_email


class TestAmazonSESSending(TestCase):
    def test_send_email_sandbox(self):
        """Test sending in SES sandbox environment."""
        subject = "Test Email 1"
        message = "This is a test email sent via Amazon SES Sandbox part 2."
        recipient_email = "arciagajethro_bsit@plmun.edu.ph"

        # Call the utility function
        result = send_custom_email(subject, message, [recipient_email])

        # Assert that the email was sent successfully
        self.assertTrue(result)
