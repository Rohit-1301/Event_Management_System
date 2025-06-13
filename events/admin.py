from django.contrib import admin
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'is_active')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'description', 'venue')
    date_hierarchy = 'date'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'registered_at')
    list_filter = ('event', 'registered_at')
    search_fields = ('name', 'email')
    date_hierarchy = 'registered_at'
