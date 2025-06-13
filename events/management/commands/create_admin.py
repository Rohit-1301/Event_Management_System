from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Creates a default admin user'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        try:
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {username}'))
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(self.style.WARNING('IMPORTANT: Change this password in production!'))
        except IntegrityError:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {username}'))
            self.stdout.write(self.style.SUCCESS('Use this account to login or create a new superuser with:'))
            self.stdout.write('python manage.py createsuperuser')
