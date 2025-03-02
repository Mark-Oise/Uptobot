from django.core.mail import send_mail
from django.conf import settings

def test_email_delivery():
    subject = "Test Email from UpToBot"
    message = "This is a test email to verify Resend delivery is working correctly."
    
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["markoise669@gmail.com"],  # Use your actual email
            fail_silently=False,
        )
        print(f"Email sent successfully: {result}")
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False