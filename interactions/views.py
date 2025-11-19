from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.db.models import Q
from .models import Interaction, ViewHistory, Match, DateInvitation, ContactExchange
from .serializers import (
    InteractionSerializer, ViewHistorySerializer, 
    MatchSerializer, DateInvitationSerializer, ContactExchangeSerializer
)
from users.models import User


class InteractionView(generics.CreateAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        with transaction.atomic():
            interaction = serializer.save(from_user=self.request.user)
            
            # Обновляем счетчик лайков
            if interaction.action == 'like':
                interaction.to_user.likes_count += 1
                interaction.to_user.save()
            
            # Проверяем взаимный лайк
            mutual_like = Interaction.objects.filter(
                from_user=interaction.to_user,
                to_user=interaction.from_user,
                action='like'
            ).exists()
            
            if mutual_like and interaction.action == 'like':
                # Создаем мэтч
                Match.objects.get_or_create(
                    user1=min(interaction.from_user, interaction.to_user, key=lambda u: u.id),
                    user2=max(interaction.from_user, interaction.to_user, key=lambda u: u.id)
                )


class ViewHistoryListView(generics.ListAPIView):
    serializer_class = ViewHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ViewHistory.objects.filter(
            viewer=self.request.user
        ).select_related('viewed_user', 'viewed_user__profile').prefetch_related('viewed_user__photos')


class LikedUsersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        liked_user_ids = Interaction.objects.filter(
            from_user=self.request.user,
            action='like'
        ).values_list('to_user_id', flat=True)
        
        return User.objects.filter(id__in=liked_user_ids).select_related('profile').prefetch_related('photos')


class DislikedUsersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        disliked_user_ids = Interaction.objects.filter(
            from_user=self.request.user,
            action='dislike'
        ).values_list('to_user_id', flat=True)
        
        return User.objects.filter(id__in=disliked_user_ids).select_related('profile').prefetch_related('photos')


class ReceivedLikesListView(generics.ListAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Interaction.objects.filter(
            to_user=self.request.user,
            action='like'
        ).select_related('from_user', 'from_user__profile').prefetch_related('from_user__photos')


class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Match.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user),
            is_active=True
        ).select_related('user1', 'user2', 'user1__profile', 'user2__profile')


class DateInvitationView(generics.ListCreateAPIView):
    serializer_class = DateInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DateInvitation.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        ).select_related('from_user', 'to_user')
    
    def perform_create(self, serializer):
        # Проверяем, есть ли мэтч между пользователями
        to_user = serializer.validated_data['to_user']
        match_exists = Match.objects.filter(
            Q(user1=self.request.user, user2=to_user) |
            Q(user1=to_user, user2=self.request.user),
            is_active=True
        ).exists()
        
        if not match_exists:
            raise serializers.ValidationError("Приглашение можно отправить только взаимолайкнувшим пользователям")
        
        serializer.save(from_user=self.request.user)


class ContactExchangeView(generics.CreateAPIView):
    serializer_class = ContactExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        match = serializer.validated_data['match']
        
        # Проверяем, что пользователь является участником мэтча
        if self.request.user not in [match.user1, match.user2]:
            raise serializers.ValidationError("Вы не являетесь участником этого мэтча")
        
        serializer.save(initiated_by=self.request.user)