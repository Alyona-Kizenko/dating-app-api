from django.urls import path
from . import views

urlpatterns = [
    path('interact/', views.InteractionView.as_view(), name='interact'),
    path('view-history/', views.ViewHistoryListView.as_view(), name='view-history'),
    path('liked-users/', views.LikedUsersListView.as_view(), name='liked-users'),
    path('disliked-users/', views.DislikedUsersListView.as_view(), name='disliked-users'),
    path('received-likes/', views.ReceivedLikesListView.as_view(), name='received-likes'),
    path('matches/', views.MatchListView.as_view(), name='matches'),
    path('date-invitations/', views.DateInvitationView.as_view(), name='date-invitations'),
    path('contact-exchange/', views.ContactExchangeView.as_view(), name='contact-exchange'),
]