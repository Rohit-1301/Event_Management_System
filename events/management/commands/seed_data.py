from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Seeds the database with sample events'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with sample events...')
        
        # Clear existing events
        Event.objects.all().delete()
        
        # Current date
        today = date.today()
        
        # Create upcoming events
        upcoming_events = [
            {
                'title': 'Tech Conference 2025',
                'description': 'Join us for the largest technology conference in the region. Topics include AI, Machine Learning, Web Development, and more.',
                'venue': 'Tech Center, Downtown',
                'date': today + timedelta(days=15),
                'time': '09:00:00',
                'is_active': True
            },
            {
                'title': 'Music Festival',
                'description': 'A three-day music festival featuring local and international artists from various genres.',
                'venue': 'City Park Amphitheater',
                'date': today + timedelta(days=30),
                'time': '16:00:00',
                'is_active': True
            },
            {
                'title': 'Startup Networking Event',
                'description': 'Network with founders, investors, and entrepreneurs. Great opportunity to pitch your ideas and find collaborators.',
                'venue': 'Innovation Hub',
                'date': today + timedelta(days=7),
                'time': '18:30:00',
                'is_active': True
            },
            {
                'title': 'Charity Gala Dinner',
                'description': 'Annual charity gala raising funds for children\'s education. Formal attire required.',
                'venue': 'Grand Hotel Ballroom',
                'date': today + timedelta(days=45),
                'time': '19:00:00',
                'is_active': True
            },
        ]
        
        # Create past events
        past_events = [
            {
                'title': 'Annual Science Fair',
                'description': 'Students from local schools showcased their science projects and innovations.',
                'venue': 'Community College',
                'date': today - timedelta(days=20),
                'time': '10:00:00',
                'is_active': True
            },
            {
                'title': 'Art Exhibition',
                'description': 'Featured works from contemporary artists focusing on environmental themes.',
                'venue': 'Downtown Gallery',
                'date': today - timedelta(days=45),
                'time': '11:00:00',
                'is_active': True
            },
            {
                'title': 'Business Workshop',
                'description': 'Marketing strategies for small businesses in the digital age.',
                'venue': 'Business Center',
                'date': today - timedelta(days=10),
                'time': '14:00:00',
                'is_active': True
            },
        ]
        
        # Add to database
        for event_data in upcoming_events + past_events:
            Event.objects.create(**event_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(upcoming_events)} upcoming and {len(past_events)} past events'))
