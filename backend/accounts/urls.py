from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ChangeRoleView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-role/<int:pk>/", ChangeRoleView.as_view(), name="change-role-view"),
]