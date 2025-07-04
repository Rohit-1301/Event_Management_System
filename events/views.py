from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.urls import reverse
from .models import (Event, EventRegistration, Team, TeamMember, StudentProfile, 
                    RegistrationRemoval, EventDiscussion, EventReview)
from .forms import (EventRegistrationForm, EventForm, LoginForm, StudentSignupForm,
                   TeamForm, TeamCodeForm, TeamMemberForm, EventSearchForm,
                   StudentProfileForm, RemoveRegistrationForm, EventDiscussionForm,
                   EventReviewForm)
from datetime import date
import os

def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_staff

def home(request):
    from datetime import date, datetime, timedelta
    
    today = date.today()
    now = datetime.now()
    next_24_hours = now + timedelta(hours=24)
    
    # Auto-update event status for past events
    Event.objects.filter(date__lt=today, is_active=True).update(is_active=False)
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(date__gte=today, is_active=True).order_by('date')
    
    # Get events happening within the next 24 hours
    imminent_events = []
    for event in upcoming_events:
        event_datetime = datetime.combine(event.date, event.time)
        if now <= event_datetime <= next_24_hours:
            imminent_events.append(event)
    
    # Past events
    past_events = Event.objects.filter(date__lt=today).order_by('-date')
    
    # Get stats for the homepage
    event_count = Event.objects.count()
    registration_count = EventRegistration.objects.count()
    
    return render(request, 'events/home.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'imminent_events': imminent_events,
        'today': today,
        'event_count': event_count,
        'registration_count': registration_count
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    today = date.today()
    is_registered = False
    user_team = None
    user_has_reviewed = False
    discussion_form = None
    review_form = None
    
    # Check if user is already registered
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(event=event, user=request.user).first()
        is_registered = registration is not None
        if is_registered and registration.is_team_registration:
            user_team = registration.team
        
        # Check if user has already reviewed this event
        user_has_reviewed = EventReview.objects.filter(event=event, user=request.user).exists()
    
    # Get top-level discussions (no parent comment)
    discussions = EventDiscussion.objects.filter(event=event, parent=None).order_by('created_at')
    
    # Get reviews if it's a past event
    reviews = []
    avg_rating = 0
    if event.date < today:
        reviews = EventReview.objects.filter(event=event).order_by('-created_at')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Handle discussion form submission
    if request.method == 'POST' and request.user.is_authenticated:
        if 'discussion_form' in request.POST and event.date >= today:
            discussion_form = EventDiscussionForm(request.POST)
            if discussion_form.is_valid():
                comment = discussion_form.save(commit=False)
                comment.event = event
                comment.user = request.user
                comment.is_admin_response = request.user.is_staff
                
                # Check if this is a reply to another comment
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    comment.parent = EventDiscussion.objects.get(id=parent_id)
                    
                comment.save()
                messages.success(request, "Your comment has been added!")
                return redirect('event_detail', event_id=event.id)
            
        elif 'review_form' in request.POST and event.date < today and is_registered and not user_has_reviewed:
            review_form = EventReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.event = event
                review.user = request.user
                review.save()
                messages.success(request, "Thank you for your review!")
                return redirect('event_detail', event_id=event.id)
    
    # Create empty forms
    if request.user.is_authenticated:
        if event.date >= today:
            discussion_form = EventDiscussionForm()
        elif event.date < today and is_registered and not user_has_reviewed:
            review_form = EventReviewForm()
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'today': today,
        'is_registered': is_registered,
        'user_team': user_team,
        'domain_display': dict(Event.DOMAIN_CHOICES)[event.domain],
        'participation_type_display': dict(Event.PARTICIPATION_TYPE_CHOICES)[event.participation_type],
        'discussions': discussions,
        'discussion_form': discussion_form,
        'reviews': reviews,
        'review_form': review_form,
        'avg_rating': avg_rating,
        'user_has_reviewed': user_has_reviewed
    })

def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Redirect if event is inactive or past
    today = date.today()
    if event.date < today or not event.is_active:
        messages.error(request, "Registration is closed for this event.")
        return redirect('event_detail', event_id=event_id)
    
    # Require login for registration
    if not request.user.is_authenticated:
        messages.info(request, "Please login to register for this event.")
        return redirect('login')
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.info(request, "You are already registered for this event.")
        return redirect('event_detail', event_id=event_id)
    
    # For team events, redirect to team choice
    if event.participation_type == Event.TEAM:
        return redirect('team_choice', event_id=event_id)
    
    # For events that allow both solo and team, show options
    if event.participation_type == Event.BOTH:
        if 'participation_choice' not in request.POST:
            return render(request, 'events/participation_choice.html', {'event': event})
        
        # If user selected team participation
        if request.POST.get('participation_choice') == 'team':
            return redirect('team_choice', event_id=event_id)
    
    # Handle solo registration (automatically register the user without asking for info)
    if request.method == 'POST' or event.participation_type == Event.SOLO:
        # Create registration directly from user info
        registration = EventRegistration(
            event=event,
            name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            email=request.user.email,
            user=request.user,
            is_team_registration=False
        )
        registration.save()
        
        messages.success(request, f"You have successfully registered for {event.title}!")
        return redirect('event_detail', event_id=event_id)
    
    # This should only be reached for BOTH type events when no selection has been made yet
    return redirect('event_detail', event_id=event_id)

@login_required
def team_choice(request, event_id):
    """View to ask if user wants to create a new team or join an existing one"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if event allows team participation
    if event.participation_type not in [Event.TEAM, Event.BOTH]:
        messages.error(request, "This event does not allow team participation.")
        return redirect('event_detail', event_id=event_id)
    
    # Check if user is already registered for this event
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, "You are already registered for this event.")
        return redirect('event_detail', event_id=event_id)
    
    # Process form submission
    if request.method == 'POST':
        choice = request.POST.get('team_choice')
        if choice == 'create':
            return redirect('create_team', event_id=event_id)
        elif choice == 'join':
            return redirect('join_team', event_id=event_id)
    
    return render(request, 'events/team_choice.html', {'event': event})

@login_required
def join_team(request, event_id):
    """View to join an existing team using a team code"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is already registered for this event
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, "You are already registered for this event.")
        return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        form = TeamCodeForm(request.POST)
        if form.is_valid():
            team_code = form.cleaned_data['team_code']
            try:
                team = Team.objects.get(team_code=team_code, event=event)
                
                # Check if team is already full
                if team.is_full:
                    messages.error(request, f"This team is already full (max: {team.event.max_team_size} members).")
                    return redirect('team_choice', event_id=event_id)
                
                # Check if user's email is already in the team
                if TeamMember.objects.filter(team=team, email=request.user.email).exists():
                    messages.error(request, "You are already a member of this team.")
                    return redirect('event_detail', event_id=event_id)
                
                # Add user to the team
                TeamMember.objects.create(
                    team=team,
                    name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    email=request.user.email,
                    user=request.user
                )
                
                # Create EventRegistration for the new team member
                EventRegistration.objects.create(
                    event=event,
                    name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    email=request.user.email,
                    user=request.user,
                    team=team,
                    is_team_registration=True
                )
                
                messages.success(request, f"You have successfully joined team '{team.name}'!")
                return redirect('event_detail', event_id=event_id)
                
            except Team.DoesNotExist:
                messages.error(request, "Invalid team code for this event. Please check and try again.")
                form.add_error('team_code', "Invalid team code")
    else:
        form = TeamCodeForm()
    
    return render(request, 'events/join_team.html', {
        'form': form, 
        'event': event
    })

@login_required
def create_team(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if event allows team participation
    if event.participation_type not in [Event.TEAM, Event.BOTH]:
        messages.error(request, "This event does not allow team participation.")
        return redirect('event_detail', event_id=event_id)
    
    # Check if user is already registered for this event
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, "You are already registered for this event.")
        return redirect('event_detail', event_id=event_id)
        
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.event = event
            team.leader = request.user
            team.save()
            
            # Add the leader as the first team member
            TeamMember.objects.create(
                team=team,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                email=request.user.email,
                user=request.user
            )
            
            # Create the event registration for the team leader
            EventRegistration.objects.create(
                event=event,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                email=request.user.email,
                user=request.user,
                team=team,
                is_team_registration=True
            )
            
            messages.success(request, f"Team '{team.name}' has been created! Now you can add team members. Your team code is {team.team_code}")
            return redirect('manage_team', team_id=team.id)
    else:
        form = TeamForm()
    
    return render(request, 'events/create_team.html', {
        'form': form,
        'event': event
    })

def withdraw_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to withdraw from an event.")
        return redirect('login')
    
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
        registration.delete()
        messages.success(request, f"Your registration for '{event.title}' has been successfully withdrawn.")
    except EventRegistration.DoesNotExist:
        messages.error(request, "You are not registered for this event.")
    
    return redirect('event_detail', event_id=event_id)

def search_events(request):
    form = EventSearchForm(request.GET)
    today = date.today()
    results = Event.objects.all()
    
    if form.is_valid():
        # Text search
        query = form.cleaned_data.get('query')
        if query:
            results = results.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(venue__icontains=query)
            )
        
        # Domain filter
        domain = form.cleaned_data.get('domain')
        if domain:
            results = results.filter(domain=domain)
        
        # Participation type filter
        participation_type = form.cleaned_data.get('participation_type')
        if participation_type:
            results = results.filter(participation_type=participation_type)
        
        # Date range filter
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            results = results.filter(date__gte=date_from)
            
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            results = results.filter(date__lte=date_to)
        
        # Upcoming only filter
        if form.cleaned_data.get('upcoming_only'):
            results = results.filter(date__gte=today)
    else:
        # Default to upcoming events if no search params
        results = results.filter(date__gte=today, is_active=True)
    
    # Sort the results
    results = results.order_by('date')
    
    return render(request, 'events/search.html', {
        'form': form,
        'results': results, 
        'query': request.GET.get('query', ''),
        'today': today,
        'domain_choices': Event.DOMAIN_CHOICES,
        'participation_choices': Event.PARTICIPATION_TYPE_CHOICES
    })

def signup_view(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False  # Ensure user is not staff
            user.save()
            # Authenticate and login the new user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Your account has been created successfully.")
            return redirect('home')
    else:
        form = StudentSignupForm()
    return render(request, 'events/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        if 'username' in request.POST:  # Admin login
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:  # Student login
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Verify that the email contains "vit.edu.in" domain
            if not "vit.edu.in" in email:
                messages.error(request, 'Please use your VIT email address (containing vit.edu.in).')
                return render(request, 'events/login.html', {'login_form': LoginForm()})
            
            # Try to get user by email first
            try:
                user = User.objects.get(email=email)
                # Authenticate with username and password
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email. Please sign up first.')
    
    return render(request, 'events/login.html', {'login_form': LoginForm()})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = date.today()
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
    past_events = Event.objects.filter(date__lt=today).order_by('-date')
    recent_registrations = EventRegistration.objects.select_related('event').order_by('-registered_at')[:5]
    registration_count = EventRegistration.objects.count()
    
    return render(request, 'events/admin_dashboard.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'recent_registrations': recent_registrations,
        'registration_count': registration_count,
    })

@login_required
@user_passes_test(is_admin)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('admin_dashboard')
    else:
        form = EventForm()
    
    return render(request, 'events/create_event.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            # Delete the old image if a new one is uploaded
            if 'image' in request.FILES and event.image:
                if os.path.isfile(event.image.path):
                    os.remove(event.image.path)
            
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

@login_required
@user_passes_test(is_admin)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    title = event.title
    event.delete()
    messages.success(request, f'Event "{title}" deleted successfully!')
    return redirect('admin_dashboard')

@login_required
def my_registrations(request):
    """View for students to see events they have registered for"""
    today = date.today()
    
    # Get all registrations for the current user
    registrations = EventRegistration.objects.filter(user=request.user).select_related('event').order_by('-registered_at')
    
    # Separate into upcoming and past events
    upcoming_registrations = [reg for reg in registrations if reg.event.date >= today]
    past_registrations = [reg for reg in registrations if reg.event.date < today]
    
    return render(request, 'events/my_registrations.html', {
        'upcoming_registrations': upcoming_registrations,
        'past_registrations': past_registrations,
        'total_registrations': len(registrations),
    })

@login_required
def manage_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Only team leader can manage the team
    if team.leader != request.user:
        messages.error(request, "You don't have permission to manage this team.")
        return redirect('event_detail', event_id=team.event.id)
    
    # Handle team finalization
    if 'finalize_team' in request.POST:
        if not team.is_valid:
            messages.error(request, f"Your team needs at least {team.event.min_team_size} members to participate.")
        else:
            # Update team status or create a final registration if needed
            messages.success(request, f"Team '{team.name}' has been finalized for the event!")
            return redirect('event_detail', event_id=team.event.id)
    
    # Handle adding new team member
    elif request.method == 'POST' and 'add_member' in request.POST:
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            # Check if team is already full
            if team.member_count >= team.event.max_team_size:
                messages.error(request, f"Team is already full (max: {team.event.max_team_size} members).")
            else:
                # Check if email already exists in the team
                email = form.cleaned_data.get('email')
                if TeamMember.objects.filter(team=team, email=email).exists():
                    messages.error(request, "A member with this email already exists in the team.")
                else:
                    # Try to find a user with this email - required for team members
                    try:
                        user = User.objects.get(email=email)
                        
                        # Check if user is already registered for this event
                        if EventRegistration.objects.filter(event=team.event, user=user).exists():
                            messages.error(request, f"User {user.username} is already registered for this event.")
                        else:
                            # Create the team member
                            member = form.save(commit=False)
                            member.team = team
                            member.user = user
                            member.name = f"{user.first_name} {user.last_name}".strip() or user.username
                            member.save()
                            
                            # Create registration for the team member
                            EventRegistration.objects.create(
                                event=team.event,
                                name=member.name,
                                email=member.email,
                                user=user,
                                team=team,
                                is_team_registration=True
                            )
                            
                            messages.success(request, f"{member.name} has been added to the team.")
                            
                    except User.DoesNotExist:
                        form.add_error('email', "This email is not registered in the system. Only registered users can be added to teams.")
        
    else:
        form = TeamMemberForm()
    
    # Get all team members
    members = TeamMember.objects.filter(team=team).order_by('added_at')
    
    # Check if team meets minimum size requirement
    meets_min_size = team.member_count >= team.event.min_team_size
    
    return render(request, 'events/manage_team.html', {
        'team': team,
        'members': members,
        'form': form,
        'event': team.event,
        'meets_min_size': meets_min_size,
        'team_code': team.team_code
    })

@login_required
def remove_team_member(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    team = member.team
    
    # Only team leader can remove members
    if team.leader != request.user:
        messages.error(request, "You don't have permission to manage this team.")
        return redirect('event_detail', event_id=team.event.id)
    
    # Don't allow removing the team leader
    if member.user == request.user:
        messages.error(request, "You cannot remove yourself as the team leader.")
        return redirect('manage_team', team_id=team.id)
    
    member_name = member.name
    
    # Remove event registration for this member if it exists
    if member.user:
        EventRegistration.objects.filter(event=team.event, user=member.user, team=team).delete()
    
    # Delete the team member
    member.delete()
    messages.success(request, f"{member_name} has been removed from the team.")
    
    return redirect('manage_team', team_id=team.id)

@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    event_id = team.event.id
    
    # Only team leader can delete the team
    if team.leader != request.user:
        messages.error(request, "You don't have permission to delete this team.")
        return redirect('event_detail', event_id=event_id)
    
    team_name = team.name
    
    # Delete the team registration
    EventRegistration.objects.filter(team=team).delete()
    
    # Team deletion will cascade to team members
    team.delete()
    
    messages.success(request, f"Team '{team_name}' has been deleted.")
    return redirect('event_detail', event_id=event_id)

@login_required
def student_profile(request):
    """View for students to see and edit their profile"""
    from datetime import date
    
    # Get or create the profile for the user
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if created:
        # If profile was just created, show a welcome message
        messages.success(request, "Welcome! Please complete your profile information below.")
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=profile)
    
    # Get all registrations for the student
    registrations = EventRegistration.objects.filter(user=request.user).select_related('event')
    
    # Get notifications of removed registrations
    removals = RegistrationRemoval.objects.filter(user=request.user, is_read=False)
    
    return render(request, 'events/student_profile.html', {
        'form': form,
        'profile': profile,
        'registrations': registrations,
        'removals': removals,
        'today': date.today()
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a removal notification as read"""
    notification = get_object_or_404(RegistrationRemoval, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.info(request, f"Notification marked as read.")
    return redirect('student_profile')

@login_required
@user_passes_test(is_admin)
def remove_registration(request, registration_id):
    """Admin view to remove a student from an event with remarks"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    if request.method == 'POST':
        form = RemoveRegistrationForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            remarks = form.cleaned_data['remarks']
            
            # Create a removal record
            RegistrationRemoval.objects.create(
                user=registration.user,
                event=registration.event,
                removed_by=request.user,
                reason=reason,
                remarks=remarks
            )
            
            # Delete the registration
            event_title = registration.event.title
            student_name = registration.user.get_full_name() or registration.user.username
            
            # If team registration, handle differently
            if registration.is_team_registration and registration.team:
                team = registration.team
                # If user is team leader, delete the whole team
                if team.leader == registration.user:
                    # Remove all team members
                    TeamMember.objects.filter(team=team).delete()
                    # Remove all registrations for team members
                    EventRegistration.objects.filter(team=team).delete()
                    # Delete the team
                    team.delete()
                    messages.success(request, f"Team '{team.name}' for event '{event_title}' has been removed.")
                else:
                    # Just remove this member from the team
                    TeamMember.objects.filter(team=team, user=registration.user).delete()
                    registration.delete()
                    messages.success(request, f"{student_name} has been removed from team '{team.name}' for event '{event_title}'.")
            else:
                # For solo registrations
                registration.delete()
                messages.success(request, f"{student_name} has been removed from event '{event_title}'.")
                
            return redirect('admin_dashboard')
    else:
        form = RemoveRegistrationForm()
    
    return render(request, 'events/remove_registration.html', {
        'form': form,
        'registration': registration
    })

@login_required
@user_passes_test(is_admin)
def view_event_registrations(request, event_id):
    """Admin view to see all registrations for an event"""
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event).select_related('user', 'team')
    
    return render(request, 'events/event_registrations.html', {
        'event': event,
        'registrations': registrations
    })

@login_required
def reply_to_comment(request, discussion_id):
    """View to handle replying to comments"""
    parent_comment = get_object_or_404(EventDiscussion, id=discussion_id)
    event = parent_comment.event
    
    if request.method == 'POST':
        form = EventDiscussionForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.event = event
            reply.user = request.user
            reply.parent = parent_comment
            reply.is_admin_response = request.user.is_staff
            reply.save()
            messages.success(request, "Your reply has been added!")
    
    return redirect('event_detail', event_id=event.id)

@login_required
def delete_comment(request, discussion_id):
    """View to delete a comment or reply"""
    comment = get_object_or_404(EventDiscussion, id=discussion_id)
    event_id = comment.event.id
    
    # Ensure the user is the owner of the comment or an admin
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")
    
    return redirect('event_detail', event_id=event_id)

@login_required
def delete_review(request, review_id):
    """View to delete a review"""
    review = get_object_or_404(EventReview, id=review_id)
    event_id = review.event.id
    
    # Ensure the user is the owner of the review or an admin
    if review.user == request.user or request.user.is_staff:
        review.delete()
        messages.success(request, "Review deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this review.")
    
    return redirect('event_detail', event_id=event_id)
