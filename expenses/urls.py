from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    
    path(
        "api/expenses/",
        views.ExpenseListCreateAPIView.as_view(),
        name="api_expenses",
    ),

    path(
        "api/expenses/<int:pk>/",
        views.ExpenseDetailAPIView.as_view(),
        name="api_expense_detail",
    ),

    path(
        "api/payments/",
        views.PaymentAPIView.as_view(),
        name="api_payments",
    ),

    path(
        "api/payments/callback/",
        views.mpesa_callback,
        name="mpesa_callback",
    ),
]
