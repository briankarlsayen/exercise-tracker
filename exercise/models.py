from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Exercise(models.Model):
    category = models.ForeignKey(Category, related_name='exercise', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exercise')
    duration  = models.IntegerField(null=True, blank=True)
    intensity = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
    
    def __str__(self):
        return self.name

