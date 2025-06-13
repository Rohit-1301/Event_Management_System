# Event Management System

A Django-based web application for managing and registering for events with a modern Bootstrap interface.

## Features

- **Admin Interface** for managing events (Create, Read, Update, Delete)
- **User Interface** for viewing and registering for events
- **Event Categories** - Upcoming and Past Events
- **Event Registration** for users
- **Search Functionality** to find specific events
- **User Authentication** - Separate student and admin logins
- **Responsive Design** - Works on mobile and desktop devices

## Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd event_mgmt
```

### 2. Create a virtual environment (optional but recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Quick Setup (Windows)

For Windows users, we've provided convenient setup scripts:

1. Run the full setup (first-time use):
   - Double-click `run_event_system.bat` in the project root folder
   - OR run `.\run_event_system.ps1` in PowerShell

2. For subsequent starts (after setup):
   - Run `.\start_server.ps1` in PowerShell

### 5. Manual Setup

If you prefer to set up manually:

```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create default admin user
python manage.py create_admin
# OR create custom superuser
python manage.py createsuperuser

# Seed the database with sample data (optional)
python manage.py seed_data

# Run the development server
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

Admin interface: http://127.0.0.1:8000/admin/

## Project Structure

- `event_mgmt_project/` - Main project configuration
- `events/` - Main application
  - `models.py` - Database models for events and registrations
  - `views.py` - View functions for rendering templates
  - `admin.py` - Admin interface customization
  - `forms.py` - Form definitions
  - `urls.py` - URL routing for the application
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and image files
  - `management/commands/` - Custom management commands

## Authentication System

The application has a dual authentication system:

1. **Admin Authentication**:
   - Uses Django's built-in authentication system
   - Full access to event creation, editing, and deletion
   - Access to the admin dashboard
   - Can view the site both as an admin and as a regular user

2. **Student/User Authentication**:
   - Simplified authentication using name and email
   - Can view events and register for them
   - Cannot access admin features

When a student logs in with their email for the first time, a user account is automatically created with a non-usable password (they'll always authenticate using their email + name combination).

## Usage

### Login Information

After setup, you can use the following credentials:

- **Admin Login**:
  - Username: admin
  - Password: admin123
  - URL: http://127.0.0.1:8000/login/ (select Admin tab)

- **Student Login**:
  - Simply enter your name and email address
  - URL: http://127.0.0.1:8000/login/ (default Student tab)

### Admin Tasks
1. Log in with admin credentials
2. Access the admin dashboard at `/admin-dashboard/`
3. Create, edit, or delete events from the dashboard
4. View all registrations
5. Toggle between admin and user views

### User Tasks
1. View upcoming and past events on the home page
2. Search for events using the search bar
3. Click on an event to see details
4. Register for upcoming events by filling out the registration form
5. View event statistics
