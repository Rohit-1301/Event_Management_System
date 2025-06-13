from django import forms
from .models import EventRegistration, Event, Team, TeamMember, StudentProfile, EventDiscussion, EventReview
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'domain', 'participation_type', 
                  'venue', 'date', 'time', 'is_active', 
                  'min_team_size', 'max_team_size', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'participation_type': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'min_team_size': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'max_team_size': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class StudentSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must be at least 8 characters long and contain letters and numbers.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
          # Add Bootstrap classes to the password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        # Validate that email contains vit.edu.in
        if not "vit.edu.in" in email:
            raise forms.ValidationError("Please use your VIT email address (containing vit.edu.in).")
            
        return email

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter team name'})
        }

class TeamCodeForm(forms.Form):
    team_code = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter team code'
        })
    )

    def clean_team_code(self):
        code = self.cleaned_data.get('team_code')
        try:
            team = Team.objects.get(team_code=code)
            return code
        except Team.DoesNotExist:
            raise forms.ValidationError("Invalid team code. Please check and try again.")

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Member name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Member email'})
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if the email belongs to a registered user
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not registered in the system. Only registered users can be added to teams.")
        
        # Also verify that the email is a VIT email
        if not "vit.edu.in" in email:
            raise forms.ValidationError("Please use a VIT email address (containing vit.edu.in).")
            
        return email

class EventSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search events...'})
    )
    domain = forms.ChoiceField(
        required=False,
        choices=[('', 'All Domains')] + list(Event.DOMAIN_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    participation_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Event.PARTICIPATION_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    upcoming_only = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture', 'branch', 'year', 'bio', 'hobbies', 'interests', 'phone_number']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hobbies': forms.TextInput(attrs={'class': 'form-control'}),
            'interests': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +91 9876543210'})
        }

class RemoveRegistrationForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Provide a reason for removing this registration."
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Additional remarks or instructions for the student."
    )

class EventDiscussionForm(forms.ModelForm):
    """Form for adding comments to event discussions"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Share your thoughts or questions about this event...'
        })
    )
    
    class Meta:
        model = EventDiscussion
        fields = ['message']


class EventReviewForm(forms.ModelForm):
    """Form for reviewing past events"""
    rating = forms.ChoiceField(
        choices=EventReview.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Share your experience with this event...'
        }),
        required=False
    )
    
    class Meta:
        model = EventReview
        fields = ['rating', 'comment']
