from rest_framework import serializers
from .models import Interaction, ViewHistory, Match, DateInvitation, ContactExchange
from users.serializers import UserSerializer


class InteractionSerializer(serializers.ModelSerializer):
    from_user_info = UserSerializer(source='from_user', read_only=True)
    to_user_info = UserSerializer(source='to_user', read_only=True)
    
    class Meta:
        model = Interaction
        fields = ['id', 'from_user', 'to_user', 'from_user_info', 
                 'to_user_info', 'action', 'created_at']
        read_only_fields = ['from_user', 'created_at']


class ViewHistorySerializer(serializers.ModelSerializer):
    viewed_user_info = UserSerializer(source='viewed_user', read_only=True)
    
    class Meta:
        model = ViewHistory
        fields = ['id', 'viewed_user', 'viewed_user_info', 'viewed_at']
        read_only_fields = ['viewer', 'viewed_at']


class MatchSerializer(serializers.ModelSerializer):
    user1_info = UserSerializer(source='user1', read_only=True)
    user2_info = UserSerializer(source='user2', read_only=True)
    
    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'user1_info', 'user2_info', 
                 'created_at', 'is_active']


class DateInvitationSerializer(serializers.ModelSerializer):
    from_user_info = UserSerializer(source='from_user', read_only=True)
    to_user_info = UserSerializer(source='to_user', read_only=True)
    
    class Meta:
        model = DateInvitation
        fields = ['id', 'from_user', 'to_user', 'from_user_info', 
                 'to_user_info', 'message', 'proposed_date', 'status', 
                 'created_at', 'updated_at']
        read_only_fields = ['from_user', 'created_at', 'updated_at']


class ContactExchangeSerializer(serializers.ModelSerializer):
    initiated_by_info = UserSerializer(source='initiated_by', read_only=True)
    
    class Meta:
        model = ContactExchange
        fields = ['id', 'match', 'initiated_by', 'initiated_by_info', 
                 'contact_info', 'exchanged_at']
        read_only_fields = ['initiated_by', 'exchanged_at']