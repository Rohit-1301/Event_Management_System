from events.models import RegistrationRemoval

def notification_processor(request):
    """Context processor to add notification count to all templates"""
    context = {
        'unread_notifications_count': 0
    }
    
    if request.user.is_authenticated and not request.user.is_staff:
        context['unread_notifications_count'] = RegistrationRemoval.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
            
    return context
