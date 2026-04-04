from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """
    GET  /api/accounts/register/  — browsable UI form
    POST /api/accounts/register/  — create a new user (role defaults to viewer)
    Only admin can assign analyst or admin roles.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = RegisterSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            requested_role = request.data.get("role", "viewer")
            caller = request.user
            if requested_role in ("analyst", "admin"):
                if not (caller.is_authenticated and caller.role == "admin"):
                    serializer.validated_data["role"] = "viewer"
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    GET  /api/accounts/login/  — browsable UI form
    POST /api/accounts/login/  — authenticate with email + password, sets session cookie
    """
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = LoginSerializer()
        return Response(serializer.data)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(
                {
                    "message": "Login successful.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    GET  /api/accounts/logout/  — browsable UI hint
    POST /api/accounts/logout/  — clears the session
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Send a POST request to logout."})

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    GET  /api/accounts/me/  — current user profile
    PUT  /api/accounts/me/  — update name / email (role change restricted to admin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            if "role" in serializer.validated_data and request.user.role != "admin":
                serializer.validated_data.pop("role")
            serializer.save()
            return Response(
                {"message": "Profile updated.", "user": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)