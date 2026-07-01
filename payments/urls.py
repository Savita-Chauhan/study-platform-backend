# backend/payments/urls.py

from django.urls import path
from .views import CreateOrderView, VerifyPaymentView, PaymentHistoryView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
]