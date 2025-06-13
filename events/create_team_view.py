def create_team(request, event_id):
    """View for creating a new team"""
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
            try:
                import uuid
                
                team = form.save(commit=False)
                team.event = event
                team.leader = request.user
                
                # Generate a unique team code
                team.team_code = uuid.uuid4().hex[:8]
                while Team.objects.filter(team_code=team.team_code).exists():
                    team.team_code = uuid.uuid4().hex[:8]
                
                # Save the team with the unique code
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
                
            except Exception as e:
                messages.error(request, f"Error creating team: {str(e)}")
    else:
        form = TeamForm()
    
    return render(request, 'events/create_team.html', {
        'form': form,
        'event': event
    })
