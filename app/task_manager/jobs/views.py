import re
from django import conf
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Job
from tasks.models import Task
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from job.file_process_multiprocess import Step, FileProcessJob
from task import TASK_MAP
from django.conf import settings
from .forms import JobCreateForm, TaskForm, TaskFormSet
import os
import json
import tempfile
import shutil


class JobIndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'jobs/index.html'
    model = Job
    context_object_name = 'jobs'
    login_url = '/accounts/login/'


@login_required(login_url='/accounts/login')
def create_job(request):
    if request.method == 'POST':
        form = JobCreateForm(request.POST)
        files = request.FILES
        config = Job.parse_config(form)        
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.config = config
            job.save()
            Job.save_files(files, job.id)
            return HttpResponseRedirect('/jobs/')
    else:
        form = JobCreateForm()
        tasks = Task.objects.all().values('id', 'task_type')
    return render(request, 'jobs/create.html', {'form': form, 'tasks': tasks})


class JobDetailView(LoginRequiredMixin, generic.DetailView):
    model = Job
    template_name = 'jobs/detail.html'
    login_url = '/accounts/login/'


@login_required(login_url='/accounts/login')
def edit_job(request, pk):
    obj = get_object_or_404(Job, id=pk)
    form = JobCreateForm(request.POST or None, instance=obj)
    print(form.data)
    files = request.FILES
    config = Job.parse_config(form)
    if form.is_valid():        
        job = form.save(commit=False)
        job.user = request.user
        job.config = config
        job.save()
        Job.save_files(files, job.id)
        return HttpResponseRedirect('/jobs/detail/'+str(pk))
    steps = obj.config
    tasks = Task.objects.all().values('task_type')
    return render(request, 'jobs/edit.html', {'form': form, 'steps': steps, 'all_tasks': tasks})


class JobDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Job
    template_name = 'jobs/delete.html'
    success_url = reverse_lazy('job_index')
    login_url = '/accounts/login/'


@login_required(login_url='/accounts/login')
def run_job(request, pk):
    job_config = Job.objects.filter(user=request.user, id=pk).first()
    job_dir = os.path.join(settings.TASK_DATA_DIR, str(job_config.id))
    current_dir = os.getcwd()
    print(f'current dir: {current_dir}')
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f'temp dir: {tmpdir}')
        shutil.copytree(job_dir, tmpdir, dirs_exist_ok=True)
        os.chdir(tmpdir)
        job = FileProcessJob('multi step job')
        for index, step in enumerate(job_config.config, 1):
            step_obj = Step({'name': f'step{index}'})
            for task in step:
                task_obj = TASK_MAP[task['task_type']]
                step_obj.add_task(
                    task_obj, {'name': task['task_name']}, task['args'])
            job.add_step(step_obj)
        try:
            job.run()
        except Exception as e:
            print(e)
        finally:
            os.chdir(current_dir)
        result = {key: dict(val) for key, val in job.result_manager.items()}
        os.chdir(current_dir)
        return JsonResponse(result)
