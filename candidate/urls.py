from django.contrib import admin
from django.urls import path, include
from candidate import views

urlpatterns = [
    path('profile/',views.CandidateProfileAPIView.as_view(),name='candidate-profile'),
    path('candidate-job-suggestions/',views.CandidateJobSuggestions.as_view(),name='candidate-job-suggestions'),
    path('job-application/',views.CandidateJobApplicationAPIView.as_view(),name='candidate-job-application'),
    path('schedule-interview/',views.CandidateScheduleInterviewAPIView.as_view(),name='schedule-interview'),
    path('start-interview-process/<str:application_id>/',views.CandidateInterviewAPIView.as_view(),name='start-interview-proces'),
    path('interview-process/',views.CandidateInterviewProcessBeginAPIView.as_view(),name='interview-process'),
    path('interview-answer-evaluation/',views.AnswerEvaluationAPIView.as_view(),name='answer-evaluation'),
    path('dashboard-cards/',views.CandidateDashboardAPIView.as_view(),name='candidate-dashboard-cards')
]