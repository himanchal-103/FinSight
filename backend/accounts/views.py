from django.contrib.auth import login, logout, get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsAdminRole
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


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
    

class ChangeRoleView(APIView):
    """
    GET  /api/accounts/change-role/<pk>/   — Retrieve details of a specific user by ID.
    PATCH /api/accounts/change-role/<pk>/  — Update a specific user's role by ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

    def get(self, request, pk=None):
        try:
            user = self.queryset.get(pk=pk)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found!"},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, pk=None):
        try:
            user = self.queryset.get(id=pk)
            if request.method == "GET":
                serializer = self.serializer_class(user)
                return Response(
                {
                    "message": "Current user fetched successfully!",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Profile updated!", 
                        "user": {"id": request.user.id, **serializer.data}
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found!"},
                status=status.HTTP_404_NOT_FOUND
            )