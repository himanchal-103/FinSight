import json
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.cache import cache

from accounts.permissions import IsAdminRole, IsAnalyst
from .models import Transaction
from .serializers import TransactionSerializer

from utils.rate_limit import rate_limit

# Create your views here.
class TransactionViewSet(viewsets.ViewSet):
    """
    ViewSet for full CRUD operations on Transaction records
    Permissions: Requires IsAdminRole
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminRole]

    def list(self, request):
        transactions = self.queryset
        serializer = self.serializer_class(transactions, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            transaction = self.queryset.get(pk=pk)
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Transaction created successfully!",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        try:
            transaction = self.queryset.get(id=pk)
            serializer = self.serializer_class(transaction, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                {
                    "message": "Transaction updated successfully!",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def partial_update(self, request, pk=None):
        try:
            transaction = self.queryset.get(id=pk)
            serializer = self.serializer_class(transaction, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                {
                    "message": "Transaction updated successfully!",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
        
    def destroy(self, request, pk=None):
        try:
            transaction = self.queryset.get(id=pk)
            transaction.delete()
            return Response({"message": "Transaction deleted successfully!"}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found!"},
                status=status.HTTP_404_NOT_FOUND
            )
        

class RecentTransactionViewSet(viewsets.ViewSet):
    """
    ViewSet for retrieving the most recent transactions
    Endpoints:
        GET /recent-transactions/   - Retrieve the 5 most recent transactions
 
    Permissions: Requires IsAnalyst
    Rate Limit: 5 requests per 60 seconds
    Caching: Results are cached for 60 seconds under the key 'recent-transactions'
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAnalyst]
    CACHE_KEY = "recent-transactions"
    CACHE_TTL = 60 # 1 minutes

    @rate_limit(limit=5, window=60, key_func="recent-transactions")
    def retrieve(self, request):
        # Check for cached data
        cached = cache.get(self.CACHE_KEY)
        if cached:
            return Response(
                {
                    "message": "Recent transactions...",
                    "source": "cache",
                    "data": json.loads(cached)
                },
                status=status.HTTP_200_OK
            )
        transactions = self.queryset[:5]
        serializer = self.serializer_class(transactions, many=True)
        cache.set(self.CACHE_KEY, json.dumps(serializer.data), timeout=self.CACHE_TTL)  # set data from db to cache
        return Response(
            {
                "message": "Recent transactions...",
                "source": "db",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    

class FilterTransactionViewSet(viewsets.ViewSet):
    """
    ViewSet for filtering transactions within a date range
    Endpoints:
        GET /filter-transactions/?start=YYYY-MM-DD&end=YYYY-MM-DD
 
    Permissions: Requires IsAnalyst
    Rate Limit: 10 requests per 60 seconds per client
    Query optimization: Only fetches id, amount, transaction_type, category, and transaction_at fields
    """
    queryset = Transaction.objects.only("id", "amount", "transaction_type", "category", "transaction_at")
    serializer_class = TransactionSerializer
    permission_classes = [IsAnalyst]

    @rate_limit(limit=10, window=60, key_func="filter-transactions")
    def retrieve(self, request):
        start_param = request.query_params.get('start')
        end_param = request.query_params.get('end')

        if start_param is None:
            return Response(
                {"error": "Invalid 'start' date. Use YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if end_param is None:
            return Response(
                {"error": "Invalid 'end' date. Use YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # parse strings into date objects
        try:
            start_date = datetime.strptime(start_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": f"Invalid 'start' format '{start_param}'. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_date = datetime.strptime(end_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": f"Invalid 'end' format '{end_param}'. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date > end_date:
            return Response(
                {"error": "'start' date must be before 'end' date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter the queryset
        queryset = self.queryset.filter(
            transaction_at__date__gte=start_date,
            transaction_at__date__lte=end_date,
        )

        serializer = self.serializer_class(queryset, many=True)
        return Response(
            {
                "start": str(start_date),
                "end": str(end_date),
                "count": queryset.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )