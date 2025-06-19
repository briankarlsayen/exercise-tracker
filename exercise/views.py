from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models.functions import ExtractWeek, ExtractYear
from django.db.models import Sum, Count
from collections import defaultdict
import calendar

from rest_framework import status
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

def get_weekly_streak(min_unique_days=4):
    # Step 1: Get all created_at dates with ISO year/week info
    exercises = (
        Exercise.objects
        .annotate(
            week=ExtractWeek('created_at'),
            year=ExtractYear('created_at'),
            date_only=ExtractWeek('created_at')  # to use distinct dates
        )
        .filter(is_active = True)
        .values('year', 'week', 'created_at')
        .distinct()
    )

    # Step 2: Build (year, week) -> set of unique dates
    week_day_map = defaultdict(set)
    for item in exercises:
        key = (item['year'], item['week'])
        week_day_map[key].add(item['created_at'])

    # Step 3: Convert to (year, week) -> count of unique days
    week_unique_day_counts = {k: len(v) for k, v in week_day_map.items()}

    today = timezone.now().date()
    current_year, current_week, _ = today.isocalendar()
    streak = 0
    checking_year, checking_week = current_year, current_week

    # If current week has < 4 unique days, start from previous week
    if week_unique_day_counts.get((checking_year, checking_week), 0) < min_unique_days:
        prev_date = datetime.strptime(f"{checking_year}-W{checking_week}-1", "%G-W%V-%u").date() - timedelta(days=7)
        checking_year, checking_week, _ = prev_date.isocalendar()

    while week_unique_day_counts.get((checking_year, checking_week), 0) >= min_unique_days:
        streak += 1
        prev_date = datetime.strptime(f"{checking_year}-W{checking_week}-1", "%G-W%V-%u").date() - timedelta(days=7)
        checking_year, checking_week, _ = prev_date.isocalendar()

    return streak

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    target_exercise_per_week = 4
    now = timezone.now()
    iso_year, iso_week, _ = now.isocalendar()
    weekly_exercise = Exercise.objects.annotate(week=ExtractWeek('created_at'), year=ExtractYear('created_at')).filter(week=iso_week, year=iso_year).filter(is_active = True)
    
    exercises_duration = weekly_exercise.aggregate(total_duration=Sum('duration'))['total_duration']

    exercise_days_done = weekly_exercise.values_list('created_at', flat=True).distinct().count()
    response = {
        "exercises_duration": exercises_duration,
        "exercise_days_done": f"{exercise_days_done}/{target_exercise_per_week}",
        "streak": get_weekly_streak(target_exercise_per_week)
    }
    return Response(response)


# get all dates 
# get distinct dates with exercises
# format

def get_date_range(start_date: str, end_date: str) -> list[str]:
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    date_list = []
    current = start
    while current <= end:
        date_list.append(current.isoformat())
        current += timedelta(days=1)

    return date_list

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_exercises(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    today = timezone.now()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    if not month and not year:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try :
        num_month = int(month)
        num_year = int(year)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if current_year == num_year and current_month == num_month:
        start_date = f"{current_year}-{current_month}-01"
        end_date = f"{current_year}-{current_month}-{current_day}"
        date_range = get_date_range(start_date=start_date, end_date=end_date)
    else:
        max_days = calendar.monthrange(num_year, num_month)[1]
        start_date = f"{num_year}-{num_month}-01"
        end_date = f"{num_year}-{num_month}-{max_days}"
        date_range = get_date_range(start_date=start_date, end_date=end_date)
        
    prefix = f"{num_year}-{str(num_month).zfill(2)}" 
    exercise_date_range = list(Exercise.objects.values_list('created_at', flat=True).filter(created_at__startswith=prefix).filter(is_active = True).distinct().order_by('created_at'))
    exercise_date_range_str = [dt.isoformat() for dt in exercise_date_range]

    calendar_dates = [{"date": d, "isDone": d in exercise_date_range_str} for d in date_range]

    response = {
        # 'exercise_date_range': exercise_date_range,
        "calendar_dates": calendar_dates
    }
    
    return Response(response)
