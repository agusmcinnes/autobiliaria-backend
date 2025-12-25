from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import LoginView, LogoutView, MeView, RefreshTokenView

app_name = 'usuarios'

urlpatterns = [
    path('login/', csrf_exempt(LoginView.as_view()), name='login'),
    path('refresh/', csrf_exempt(RefreshTokenView.as_view()), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
]
