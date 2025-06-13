from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

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
