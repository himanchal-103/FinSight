from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from decimal import Decimal

from transactions.models import Transaction
from .serializers import DashboardSerializer

from accounts.permissions import IsViewer, IsAnalyst, IsAdminRole



# Create your views here.
class DashboardView(APIView):
    """
    GET /dashboard/
    Returns KPI metrics: total revenue, deposits, withdrawals, net balance,
    and a per-category breakdown for both deposits and withdrawals.
    """
    # permission_classes = [IsViewer, IsAnalyst, IsAdminRole]

    def get(self, request):
        queryset = Transaction.objects.all()

        # Top-level KPIs
        deposit_agg = queryset.filter(
            transaction_type=Transaction.TransactionType.DEPOSIT
        ).aggregate(total=Sum("amount"), count=Count("id"))

        withdrawn_agg = queryset.filter(
            transaction_type=Transaction.TransactionType.WITHDRAWN
        ).aggregate(total=Sum("amount"), count=Count("id"))

        total_deposits = deposit_agg["total"] or Decimal("0.00")
        total_withdrawn = withdrawn_agg["total"] or Decimal("0.00")
        total_revenue = total_deposits
        net_balance = total_deposits - total_withdrawn

        # Category breakdowns
        deposits_by_category = (
            queryset.filter(transaction_type=Transaction.TransactionType.DEPOSIT)
            .values("category")
            .annotate(total=Sum("amount"), transaction_count=Count("id"))
            .order_by("-total")
        )

        withdrawals_by_category = (
            queryset.filter(transaction_type=Transaction.TransactionType.WITHDRAWN)
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
        return Response(serializer.data, status=status.HTTP_200_OK)