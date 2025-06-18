
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import Category, Exercise
from .serializers import CategorySerializer, ExerciseSerializer, CreateExerciseSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_exercises(request):
    exercise = Exercise.objects.filter(user=request.user.id)[0:4]
    serializer = ExerciseSerializer(exercise, many=True)
    return Response(serializer.data)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_exercise(request, pk):
    try:
        exercise=Exercise.objects.get(pk=pk)
    except Exercise.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExerciseSerializer(exercise)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ExerciseSerializer(exercise, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        exercise.is_active = False
        exercise.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exercise(request):
    form_data = request.data
    form_data['user'] = request.user.id

    serializer = CreateExerciseSerializer(data=form_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exercises(request):
    date = request.GET.get('created_at')
    exercises = Exercise.objects.filter(user=request.user.id).filter(is_active = True)

    if date is not None:
        exercises = exercises.filter(created_at = date)
        
    serializer = ExerciseSerializer(exercises, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many= True)
    return Response(serializer.data)