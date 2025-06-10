from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Category, Exercise
from .serializers import CategorySerializer, ExerciseSerializer

class LatestExerciseList(APIView):
    def get(self, request, format=None):
        exercise = Exercise.objects.all()[0:4]
        serializer = ExerciseSerializer(exercise, many=True)
        return Response(serializer.data)
    
class ExerciseDetail(APIView):
    def get_object(self, id):
        try:
            return Exercise.objects.get(id=id)
        except Exercise.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        exercise = self.get_object(id)
        serializer = ExerciseSerializer(exercise)
        return Response(serializer.data)
    
# filter by date and user
class ExercisesByDate(APIView):
    def get(self, request, format=None):

        # future reference 
        # user = self.request.user
        # queryset = Todo.objects.filter(user=user)
        date = self.request.GET.get('created_at')
        print('date', date)
        exercises = Exercise.objects.all()
        

        if date is not None:
            exercises = exercises.filter(created_at = date)
            
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)

class CategoryList(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many= True)
        return Response(serializer.data)