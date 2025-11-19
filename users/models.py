from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    
    STATUS_CHOICES = [
        ('looking', 'В поиске'),
        ('relationship', 'В отношениях'),
        ('married', 'Женат/Замужем'),
        ('complicated', 'Все сложно'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Публичный'),
        ('private', 'Приватный'),
        ('friends_only', 'Только друзья'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    city = models.CharField(max_length=100)
    hobbies = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='looking')
    privacy_settings = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    likes_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='user_photos/')
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.is_main:
            # Снимаем флаг is_main с других фото этого пользователя
            UserPhoto.objects.filter(user=self.user, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Photo of {self.user}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    education = models.CharField(max_length=200, blank=True)
    profession = models.CharField(max_length=200, blank=True)
    smoking = models.BooleanField(default=False)
    drinking = models.BooleanField(default=False)
    relationship_goals = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profile of {self.user}"