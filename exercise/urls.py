from django.urls import path, include
from exercise import views

urlpatterns = [
    path('latest-exercises/', views.get_latest_exercises, name='get_latest_exercises'),
    path('exercises/', views.get_exercises, name='get_exercises'),
    path('exercises/stats/', views.get_stats, name='get_stats'),
    path('exercises/create', views.create_exercise, name='create_exercise'),
    path('exercises/<int:pk>/', views.get_exercise, name='get_exercise'),

    path('categories/', views.get_category_list, name='get_category_list'),
]