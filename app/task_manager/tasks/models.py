from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=100)