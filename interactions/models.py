from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Interaction(models.Model):
    ACTION_CHOICES = [
        ('like', 'Лайк'),
        ('dislike', 'Дизлайк'),
        ('super_like', 'Суперлайк'),
    ]
    
    from_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_interactions'
    )
    to_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_interactions'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['from_user', 'created_at']),
            models.Index(fields=['to_user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.action})"


class ViewHistory(models.Model):
    viewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='viewed_profiles'
    )
    viewed_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='viewed_by'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['viewer', 'viewed_user']
        indexes = [
            models.Index(fields=['viewer', 'viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.viewer} viewed {self.viewed_user}"


class Match(models.Model):
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='matches_as_user1'
    )
    user2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='matches_as_user2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user1', 'user2']
    
    def __str__(self):
        return f"Match: {self.user1} & {self.user2}"


class DateInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('cancelled', 'Отменено'),
    ]
    
    from_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_invitations'
    )
    to_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_invitations'
    )
    message = models.TextField()
    proposed_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Date invitation from {self.from_user} to {self.to_user}"


class ContactExchange(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='contact_exchanges')
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_info = models.TextField()
    exchanged_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact exchange for match {self.match}"