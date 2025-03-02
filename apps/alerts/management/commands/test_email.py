from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test sending emails through Resend'

    def handle(self, *args, **options):
        try:
            send_mail(
                subject='Test Email from UpToBot',
                message='This is a test email to verify Resend configuration.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['markoise669@gmail.com'],  # Replace with your email
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))