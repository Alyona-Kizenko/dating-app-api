from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('random-user/', views.RandomUserView.as_view(), name='random-user'),
    path('photos/', views.UserPhotoView.as_view(), name='user-photos'),
    path('photos/<int:pk>/set-main/', views.SetMainPhotoView.as_view(), name='set-main-photo'),
]