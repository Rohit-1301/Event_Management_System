# This script fixes the team code issue in the Eventure application

# Navigate to the project directory
cd "c:\Users\Naresh Yelev\OneDrive\Desktop\LandT project\event_mgmt"

# Create backup of the views.py file
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item "events\views.py" "events\views.py.bak-$timestamp"
Write-Host "Backup created: events\views.py.bak-$timestamp"

# Apply migrations
python manage.py migrate

# Delete the sqlite database for a clean start (if desired)
# Remove-Item "db.sqlite3" -Force

Write-Host ""
Write-Host "Fixes applied successfully!"
Write-Host ""
Write-Host "To start the server, run:"
Write-Host "cd c:\Users\Naresh Yelev\OneDrive\Desktop\LandT project\event_mgmt"
Write-Host "python manage.py runserver"
