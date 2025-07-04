# Generated by Django 5.2.3 on 2025-06-13 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_merge_0006_alter_team_team_code_0007_cleanup_teams'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, help_text='Upload an image for the event (optional)', null=True, upload_to='event_images/'),
        ),
    ]
