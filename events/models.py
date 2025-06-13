from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import os

# Model for tracking registration removals with remarks
class RegistrationRemoval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registration_removals')
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    removed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='removals_done')
    reason = models.TextField()
    remarks = models.TextField()
    removed_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} removed from {self.event.title}"

class Event(models.Model):
    # Domain choices
    TECHNICAL = 'TECH'
    CULTURAL = 'CULT'
    SPORTS = 'SPORTS'
    ACADEMIC = 'ACAD'
    OTHER = 'OTHER'
    
    DOMAIN_CHOICES = [
        (TECHNICAL, 'Technical'),
        (CULTURAL, 'Cultural'),
        (SPORTS, 'Sports'),
        (ACADEMIC, 'Academic'),
        (OTHER, 'Other')
    ]
    
    # Team type choices
    SOLO = 'SOLO'
    TEAM = 'TEAM'
    BOTH = 'BOTH'
    
    PARTICIPATION_TYPE_CHOICES = [
        (SOLO, 'Solo Participant'),
        (TEAM, 'Team Participation'),
        (BOTH, 'Both Solo & Team')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    domain = models.CharField(max_length=10, choices=DOMAIN_CHOICES, default=OTHER)
    participation_type = models.CharField(max_length=5, choices=PARTICIPATION_TYPE_CHOICES, default=SOLO)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    min_team_size = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_team_size = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    image = models.ImageField(upload_to='event_images/', null=True, blank=True, 
                              help_text="Upload an image for the event (optional)")

    def __str__(self):
        return self.title
        
    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure min team size <= max team size
        if self.min_team_size > self.max_team_size:
            raise ValidationError({'min_team_size': 'Minimum team size cannot be greater than maximum team size.'})
        
        # Solo events should have team size of 1
        if self.participation_type == self.SOLO:
            self.min_team_size = 1
            self.max_team_size = 1
            
    def delete(self, *args, **kwargs):
        # Delete the image file when the event is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

class Team(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    created_at = models.DateTimeField(auto_now_add=True)
    team_code = models.CharField(max_length=8, unique=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"
    
    @property
    def member_count(self):
        return self.teammember_set.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.event.max_team_size
        
    @property
    def is_valid(self):
        return self.member_count >= self.event.min_team_size
    
    def save(self, *args, **kwargs):
        if not self.team_code:
            # Generate a unique team code
            self.team_code = uuid.uuid4().hex[:8]
            # Ensure uniqueness
            while Team.objects.filter(team_code=self.team_code).exists():
                self.team_code = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('team', 'email')
    
    def __str__(self):
        return f"{self.name} - member of {self.team.name}"

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    is_team_registration = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_team_registration and self.team:
            return f"Team {self.team.name} registered for {self.event.title}"
        return f"{self.name} registered for {self.event.title}"


# Student Profile Model to store additional information
class StudentProfile(models.Model):
    # Branch/Department Choices
    CSE = 'CSE'
    ECE = 'ECE'
    EEE = 'EEE'
    MECH = 'MECH'
    CIVIL = 'CIVIL'
    IT = 'IT'
    OTHER = 'OTHER'
    
    BRANCH_CHOICES = [
        (CSE, 'Computer Science Engineering'),
        (ECE, 'Electronics and Communication Engineering'),
        (EEE, 'Electrical and Electronics Engineering'),
        (MECH, 'Mechanical Engineering'),
        (CIVIL, 'Civil Engineering'),
        (IT, 'Information Technology'),
        (OTHER, 'Other')
    ]
    
    # Year Choices
    FIRST = '1'
    SECOND = '2'
    THIRD = '3'
    FOURTH = '4'
    
    YEAR_CHOICES = [
        (FIRST, 'First Year'),
        (SECOND, 'Second Year'),
        (THIRD, 'Third Year'),
        (FOURTH, 'Fourth Year')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    branch = models.CharField(max_length=5, choices=BRANCH_CHOICES, default=OTHER)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    hobbies = models.CharField(max_length=200, null=True, blank=True)
    interests = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def delete(self, *args, **kwargs):
        # Delete the profile picture when profile is deleted
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)


# Create a profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:  # Only create profiles for non-staff users
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not instance.is_staff and hasattr(instance, 'profile'):
        instance.profile.save()

# Models for event discussions and reviews

class EventDiscussion(models.Model):
    """Model for discussions on upcoming events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin_response = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title}"

class EventReview(models.Model):
    """Model for reviews on past events"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure one review per user per event
        unique_together = ('event', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.rating}-star review on {self.event.title}"
