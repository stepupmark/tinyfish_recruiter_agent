from django.contrib import admin
from django.urls import path, include
from candidate import views

urlpatterns = [
    path('candidate-job-suggestions/',views.CandidateJobSuggestions.as_view(),name='candidate-job-suggestions'),
    path('job-application/',views.CandidateJobApplicationAPIView.as_view(),name='candidate-job-application'),
]