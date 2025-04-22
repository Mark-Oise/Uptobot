from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'contact_type', 'email', 'user', 'created_at')
    list_filter = ('contact_type', 'created_at')
    search_fields = ('subject', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
