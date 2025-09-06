from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('create/', views.resume_create, name='resume_create'),
    path('<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('<int:resume_id>/edit/', views.resume_edit, name='resume_edit'),
    path('<int:resume_id>/pdf/', views.resume_pdf, name='resume_pdf'),
    path('<int:resume_id>/delete/', views.resume_delete, name='resume_delete'),
]