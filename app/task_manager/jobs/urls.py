from django.urls import path
from .views import JobIndexView, create_job, JobDetailView, JobDeleteView, edit_job, run_job


urlpatterns = [
    path('', JobIndexView.as_view(), name='job_index'),
    path('create/', create_job, name='job_create'),
    path('detail/<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('edit/<int:pk>/', edit_job, name='job_edit'),
    path('delete/<int:pk>/', JobDeleteView.as_view(), name='job_delete'),
    path('run/<int:pk>/', run_job, name='run_job')
]