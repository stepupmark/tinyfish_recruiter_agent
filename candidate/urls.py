from django.contrib import admin
from django.urls import path, include
from candidate import views

urlpatterns = [
    path('candidate-job-suggestions/',views.CandidateJobSuggestions.as_view(),name='candidate-job-suggestions'),
    path('job-application/',views.CandidateJobApplicationAPIView.as_view(),name='candidate-job-application'),
    path('start-interview-process/<str:application_id>/',views.CandidateInterviewAPIView.as_view(),name='start-interview-proces'),
    path('schedule-interview/',views.CandidateScheduleInterviewAPIView.as_view(),name='schedule-interview'),
]