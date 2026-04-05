from django.urls import path
from .views import TransactionViewSet, RecentTransactionViewSet, FilterTransactionViewSet


transaction_list = TransactionViewSet.as_view({
    'get': 'list',
})

transaction_create = TransactionViewSet.as_view({
    'post': 'create',
})

transaction_details = TransactionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

recent_transactions_list = RecentTransactionViewSet.as_view({
    'get': 'retrieve',
})

filter_transaction = FilterTransactionViewSet.as_view({
    'get': 'retrieve',
})


urlpatterns = [
    path('list/all/', transaction_list, name='transaction-list'),
    path('create/', transaction_create, name="transaction-create"),

    path('retrieve/<int:pk>/', transaction_details, name="transaction-retrieve"),
    path('update/<int:pk>/', transaction_details, name="transaction-update"),
    path('partial-update/<int:pk>/', transaction_details, name="transaction-partial-update"),
    path('destroy/<int:pk>/', transaction_details, name="transaction-destroy"),

    path('recent/', recent_transactions_list, name="recent-transactions"),
    path('filter-transaction/', filter_transaction, name="filter_transactions"),
]   