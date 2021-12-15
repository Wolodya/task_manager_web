from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import re
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your models here.
class Job(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    config = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('job_detail', args=[str(self.id)])

    @staticmethod
    def parse_config(form):
        config = []
        step_pattern = re.compile(r'step-\d+')
        found_steps = sorted(list({step_pattern.match(key).group(
        ) for key in form.data.keys() if re.search(step_pattern, key)}))
        for step_key in found_steps:
            task_pattern = re.compile(step_key+'-task-\d+')
            found_tasks = sorted(list({task_pattern.match(key).group(
            ) for key in form.data.keys() if re.search(task_pattern, key)}))
            step = []
            for task_key in found_tasks:
                task = {
                    'task_name': form.data[task_key+'-name'],
                    'task_type': form.data[task_key+'-type'],
                    'args': form.data[task_key+'-args'],
                    'kwargs': form.data[task_key+'-kwargs'] if form.data[task_key+'-kwargs'] else {},
                }
                step.append(task)
            config.append(step)
        return config

    @staticmethod
    def save_files(files, id):
        job_dir = os.path.join(settings.TASK_DATA_DIR, str(id))
        os.makedirs(job_dir, exist_ok=True)
        for key, file_obj in files.items():
            file_storage = FileSystemStorage(location=job_dir)
            filename = file_storage.save(file_obj.name, file_obj)
            print(filename)
