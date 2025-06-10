from django.urls import path, include
from exercise import views

urlpatterns = [
    path('latest-exercises/', views.LatestExerciseList.as_view()),
    path('exercisers/', views.ExercisesByDate.as_view()),
    path('exercises/<id>/', views.ExerciseDetail.as_view()),

    path('categories/', views.CategoryList.as_view())
]