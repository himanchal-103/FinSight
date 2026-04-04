from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # DRF browsable UI login / logout buttons
    path("api-auth/", include("rest_framework.urls")),
    
    path('', include('dashboard.urls')),
    path("api/accounts/", include("accounts.urls")),
    path('transactions/', include('transactions.urls')),
]
