from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('report/generate/', views.generate_report, name='generate_report'),
    path('report/export/', views.export_report, name='export_report'),
    path('widget/<int:pk>/settings/', views.widget_settings, name='widget_settings'),
    path('widget/position/update/', views.update_widget_position, name='update_widget_position'),
] 