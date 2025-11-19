from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from interactions.models import Interaction, Match

class InteractionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            gender='M',
            age=25,
            city='Moscow'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='password123',
            first_name='Jane',
            last_name='Doe',
            gender='F',
            age=23,
            city='Moscow'
        )
        
        self.client.force_authenticate(user=self.user1)
    
    def test_like_interaction(self):
        url = reverse('interact')
        data = {
            'to_user': self.user2.id,
            'action': 'like'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что взаимодействие создано
        interaction = Interaction.objects.get(
            from_user=self.user1,
            to_user=self.user2
        )
        self.assertEqual(interaction.action, 'like')
        
        # Проверяем, что счетчик лайков увеличился
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.likes_count, 1)
    
    def test_mutual_like_creates_match(self):
        # User1 лайкает User2
        Interaction.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            action='like'
        )
        
        # User2 лайкает User1
        Interaction.objects.create(
            from_user=self.user2,
            to_user=self.user1,
            action='like'
        )
        
        # Должен создаться мэтч
        match_exists = Match.objects.filter(
            user1=self.user1,
            user2=self.user2
        ).exists()
        
        self.assertTrue(match_exists)
    
    def test_cannot_interact_with_self(self):
        url = reverse('interact')
        data = {
            'to_user': self.user1.id,
            'action': 'like'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)