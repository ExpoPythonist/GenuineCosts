from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.ExpenseIndexView.as_view(), name="expenses"),
    path('add-expense/', views.AddExpenseView.as_view(), name="add-expenses"),
    path('edit-expense/<int:id>', views.EditExpenseView.as_view(), name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),

    path('search-expenses', csrf_exempt(views.search_expenses), name="search_expenses"),
    path('expense_category_summary', views.expense_category_summary, name="expense_category_summary"),
    path('stats', views.stats_view, name="stats")
]
