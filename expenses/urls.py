from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.category_list, name="category-list"),
    path("expenses/", views.expense_list, name="expense-list"),
    
    path("expenses/summary/", views.expense_summary, name="expense-summary"),
    path("register/", views.register),
    path("expenses/monthly-summary/", views.monthly_summary, name="monthly-summary"),
    path("login/", views.login),
    path("expenses/<pk>/", views.expense_detail, name="expense-detail"),
]
