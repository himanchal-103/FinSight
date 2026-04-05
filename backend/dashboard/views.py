import json
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.cache import cache
from django.db.models import Sum, Count

from transactions.models import Transaction
from .serializers import DashboardSerializer

from accounts.permissions import IsViewer, IsAnalyst, IsAdminRole
from utils.rate_limit import rate_limit



# Create your views here.
class DashboardView(APIView):
    """
    GET /dashboard/
    Returns KPI metrics: total revenue, deposits, withdrawals, net balance, and a per-category breakdown for both deposits and withdrawals.
    """
    queryset = Transaction.objects.all()
    # permission_classes = [IsViewer, IsAnalyst, IsAdminRole]
    CACHE_KEY = "dashboard"
    CACHE_TTL = 10  # 10 seconds

    @rate_limit(limit=5, window=30, key_func="dashboard")
    def get(self, request):
        # Check for cached data
        cached = cache.get(self.CACHE_KEY)
        if cached:
            return Response(
                {
                    "message": "Dashboard KPIs...",
                    "source": "cache",
                    "data": json.loads(cached)
                },
                status=status.HTTP_200_OK
            )
        
        # Top-level KPIs
        deposit_agg = self.queryset.filter(
            transaction_type=Transaction.TransactionType.DEPOSIT
        ).aggregate(total=Sum("amount"), count=Count("id"))

        withdrawn_agg = self.queryset.filter(
            transaction_type=Transaction.TransactionType.WITHDRAWN
        ).aggregate(total=Sum("amount"), count=Count("id"))

        total_deposits = deposit_agg["total"] or Decimal("0.00")
        total_withdrawn = withdrawn_agg["total"] or Decimal("0.00")
        total_revenue = total_deposits
        net_balance = total_deposits - total_withdrawn

        # Category breakdowns
        deposits_by_category = (
            self.queryset.filter(transaction_type=Transaction.TransactionType.DEPOSIT)
            .values("category")
            .annotate(total=Sum("amount"), transaction_count=Count("id"))
            .order_by("-total")
        )

        withdrawals_by_category = (
            self.queryset.filter(transaction_type=Transaction.TransactionType.WITHDRAWN)
            .values("category")
            .annotate(total=Sum("amount"), transaction_count=Count("id"))
            .order_by("-total")
        )

        data = {
            "total_revenue": total_revenue,
            "total_deposits": total_deposits,
            "total_withdrawn": total_withdrawn,
            "net_balance": net_balance,
            "total_transactions": (deposit_agg["count"] or 0) + (withdrawn_agg["count"] or 0),
            "deposits_by_category": list(deposits_by_category),
            "withdrawals_by_category": list(withdrawals_by_category),
        }

        serializer = DashboardSerializer(data)
        cache.set(self.CACHE_KEY, json.dumps(serializer.data), timeout=self.CACHE_TTL)  # set data from db to cache
        return Response(
                {
                    "message": "Dashboard KPIs...",
                    "source": "db",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )