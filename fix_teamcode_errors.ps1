# Fix the UNIQUE constraint error with team_code

# Correct the Team model to use blank instead of default
$modelPath = "c:\Users\Naresh Yelev\OneDrive\Desktop\LandT project\event_mgmt\events\models.py"
$modelContent = Get-Content $modelPath -Raw

# Update the Team model definition
$updatedModelContent = $modelContent -replace "team_code = models.CharField\(max_length=8, unique=True, default=uuid.uuid4\(\).hex\[:8\], editable=False\)", "team_code = models.CharField(max_length=8, unique=True, blank=True)"

# Write the updated model content
Set-Content -Path $modelPath -Value $updatedModelContent
Write-Host "Updated models.py to fix team_code definition"

# Make migrations
cd "c:\Users\Naresh Yelev\OneDrive\Desktop\LandT project\event_mgmt"

try {
    # Run the migrations
    & python manage.py makemigrations
    & python manage.py migrate

    Write-Host ""
    Write-Host "All fixes applied successfully!"
    Write-Host ""
    Write-Host "Please restart the server now."
    Write-Host "cd c:\Users\Naresh Yelev\OneDrive\Desktop\LandT project\event_mgmt"
    Write-Host "python manage.py runserver"
} catch {
    Write-Error "Error applying migrations: $_"
}
