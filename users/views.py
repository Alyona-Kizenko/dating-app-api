from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserPhoto
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserUpdateSerializer, UserPhotoSerializer
)
from interactions.models import ViewHistory


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.exclude(id=self.request.user.id)
        
        # Фильтрация по параметрам
        gender = self.request.query_params.get('gender')
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        city = self.request.query_params.get('city')
        status = self.request.query_params.get('status')
        
        if gender:
            queryset = queryset.filter(gender=gender)
        if min_age:
            queryset = queryset.filter(age__gte=min_age)
        if max_age:
            queryset = queryset.filter(age__lte=max_age)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('profile').prefetch_related('photos')


class RandomUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Получаем пользователей, которых еще не просматривали
        viewed_users = ViewHistory.objects.filter(
            viewer=self.request.user
        ).values_list('viewed_user_id', flat=True)
        
        # Фильтруем по параметрам
        queryset = User.objects.exclude(
            Q(id=self.request.user.id) | Q(id__in=viewed_users)
        )
        
        # Применяем фильтры из запроса
        gender = self.request.query_params.get('gender')
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        city = self.request.query_params.get('city')
        status = self.request.query_params.get('status')
        
        if gender:
            queryset = queryset.filter(gender=gender)
        if min_age:
            queryset = queryset.filter(age__gte=min_age)
        if max_age:
            queryset = queryset.filter(age__lte=max_age)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if status:
            queryset = queryset.filter(status=status)
        
        random_user = queryset.order_by('?').first()
        
        if random_user:
            # Добавляем в историю просмотров
            ViewHistory.objects.create(
                viewer=self.request.user,
                viewed_user=random_user
            )
        
        return random_user


class UserPhotoView(generics.ListCreateAPIView):
    serializer_class = UserPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return UserPhoto.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SetMainPhotoView(generics.UpdateAPIView):
    serializer_class = UserPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPhoto.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        photo = self.get_object()
        photo.is_main = True
        photo.save()
        return Response({'status': 'main photo set'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(username=email, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )