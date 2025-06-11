from rest_framework import serializers
from .models import Category, Exercise

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "is_active"
        )

class ExerciseSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S") 

    class Meta: 
        model = Exercise
        fields = (
            "id",
            "name",
            "duration",
            "intensity",
            "is_completed",
            "is_active",
            "created_at",
            "category",
            "user",
            "updated_at",
        )