import json
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.cache import cache
from django.db.models import Sum, Count, Q

from transactions.models import Transaction
from accounts.permissions import IsViewer
from .serializers import DashboardSerializer

from utils.rate_limit import rate_limit


class DashboardView(APIView):
    """
    GET /dashboard/
    Returns KPI metrics: total revenue, deposits, withdrawals, net balance, and a per-category breakdown for both deposits and withdrawals.
    """
    permission_classes = [IsViewer]
    CACHE_KEY = "dashboard"
    CACHE_TTL = 10

    @rate_limit(limit=5, window=30, key_func="dashboard")
    def get(self, request):
        # Cache check
        cached = cache.get(self.CACHE_KEY)
        if cached:
            return Response(
                {"message": "Dashboard KPIs", "source": "cache", "data": cached},
                status=status.HTTP_200_OK,
            )
        
        kpis = Transaction.objects.aggregate(
            total_deposits=Sum(
                "amount", filter=Q(transaction_type=Transaction.TransactionType.DEPOSIT)
            ),
            deposit_count=Count(
                "id", filter=Q(transaction_type=Transaction.TransactionType.DEPOSIT)
            ),
            total_withdrawn=Sum(
                "amount", filter=Q(transaction_type=Transaction.TransactionType.WITHDRAWN)
            ),
            withdrawn_count=Count(
                "id", filter=Q(transaction_type=Transaction.TransactionType.WITHDRAWN)
            ),
        )

        total_deposits = kpis["total_deposits"] or Decimal("0.00")
        total_withdrawn = kpis["total_withdrawn"] or Decimal("0.00")

        category_rows = (
            Transaction.objects
            .values("transaction_type", "category")
            .annotate(total=Sum("amount"), transaction_count=Count("id"))
            .order_by("transaction_type", "-total")
        )

        deposits_by_category = []
        withdrawals_by_category = []

        for row in category_rows:
            entry = {
                "category": row["category"],
                "total": row["total"],
                "transaction_count": row["transaction_count"],
            }
            if row["transaction_type"] == Transaction.TransactionType.DEPOSIT:
                deposits_by_category.append(entry)
            else:
                withdrawals_by_category.append(entry)

        data = {
            "total_revenue": total_deposits,
            "total_deposits": total_deposits,
            "total_withdrawn": total_withdrawn,
            "net_balance": total_deposits - total_withdrawn,
            "total_transactions": (kpis["deposit_count"] or 0) + (kpis["withdrawn_count"] or 0),
            "deposits_by_category": deposits_by_category,
            "withdrawals_by_category": withdrawals_by_category,
        }
        serializer = DashboardSerializer(data)
        cache.set(self.CACHE_KEY, serializer.data, timeout=self.CACHE_TTL) # store data from db to cache
        return Response(
            {"message": "Dashboard KPIs", "source": "db", "data": serializer.data},
            status=status.HTTP_200_OK,
        )