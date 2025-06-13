import os
import sys
import subprocess
import time

def run_command(command, description):
    print(f"\n{description}...\n")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False

def main():
    # Make migrations
    if not run_command("python manage.py makemigrations", "Making migrations"):
        return

    # Apply migrations
    if not run_command("python manage.py migrate", "Applying migrations"):
        return

    # Create admin user (faster than createsuperuser command)
    print("\nDo you want to create a default admin user? (y/n): ", end="")
    create_admin = input().strip().lower()
    if create_admin == 'y':
        if not run_command("python manage.py create_admin", "Creating admin user"):
            return
    else:
        print("\nDo you want to create a custom superuser for admin access? (y/n): ", end="")
        create_superuser = input().strip().lower()
        if create_superuser == 'y':
            if not run_command("python manage.py createsuperuser", "Creating superuser"):
                return

    # Seed the database with sample data
    print("\nDo you want to seed the database with sample events? (y/n): ", end="")
    seed_data = input().strip().lower()
    if seed_data == 'y':
        if not run_command("python manage.py seed_data", "Seeding database"):
            return

    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        return

    # Run the server
    print("\nSetup complete! Starting the development server...\n")
    print("\nAccess the site at: http://127.0.0.1:8000/")
    print("\nAdmin credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run("python manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
