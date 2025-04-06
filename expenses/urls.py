from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, BudgetViewSet, SummaryView, BudgetCreateAPIView
from .views_frontend import (
    home, budget_page, expense_page, analytics_page,
    edit_expense, delete_expense, edit_budget, delete_budget, 
    signup_view, login_view, logout_view, welcome, health_check
)
from django.views.generic import RedirectView
router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='welcome', permanent=False)),  # Redirects "/" to welcome
    path('welcome/', welcome, name='welcome'),  # Use the correct function name
    path('home/', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include(router.urls)),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('budget/', budget_page, name='budget_page'),
    path('expense/', expense_page, name='expense_page'),
    path('analytics/', analytics_page, name='analytics_page'),
    path('expense/edit/<str:transaction_id>/', edit_expense, name='edit_expense'),
    path('expense/delete/<str:transaction_id>/', delete_expense, name='delete_expense'),
    path('budget/edit/<uuid:pk>/', edit_budget, name='edit_budget'),
    path('budget/delete/<uuid:pk>/', delete_budget, name='delete_budget'),
    path('api/budgets/', BudgetCreateAPIView.as_view(), name='api_budgets'),
    path('dashboard/', budget_page, name='dashboard'),
]
