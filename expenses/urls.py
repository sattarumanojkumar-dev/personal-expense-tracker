from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list_view, name='expense_list'),
    path('add/', views.expense_create_view, name='expense_create'),
    path('edit/<int:pk>/', views.expense_update_view, name='expense_update'),
    path('delete/<int:pk>/', views.expense_delete_view, name='expense_delete'),
    path('reports/', views.monthly_reports_view, name='monthly_reports'),
    path('api/charts/', views.chart_data_api, name='chart_data_api'),
]
