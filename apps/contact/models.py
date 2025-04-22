from django.db import models
from django.conf import settings

# Create your models here.
class Contact(models.Model):
    CONTACT_TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'), 
        ('billing', 'Billing Question'),
        ('feedback', 'General Feedback'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='contacts')
    email = models.EmailField()
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES, default='other')
    subject = models.CharField(max_length=500)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_contact_type_display()} - {self.subject}"
    

    