from django import forms
from django.forms import fields
from django.forms.formsets import formset_factory
from django.forms.models import ModelChoiceField
from .models import Job
from tasks.models import Task

class JobCreateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'start_time']
        

class TaskModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj) -> str:        
        return super().label_from_instance(obj.task_type)

class TaskForm(forms.Form):
    name = TaskModelChoiceField(queryset=Task.objects.all())
    args = forms.CharField(max_length=100, required=False)
    kwargs = forms.CharField(max_length=100, required=False)
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

class StepForm(forms.Form):
    name = forms.CharField(max_length=20)
    task = TaskForm
TaskFormSet = formset_factory(TaskForm)
