from django.contrib import admin
from django.urls import path, include
from recruiter import views

urlpatterns = [
    path('profile/',views.RecruiterProfileAPIView.as_view(),name='recruiter-profile'),
    path('dashboard-cards/',views.RecruiterDashboardAPIView.as_view(),name='recruiter-dashboards'),
    path('job-post/',views.RecruiterJobPostAPIView.as_view(),name='recruiter-job-post'),
    path('job-post-detail/<str:id>/',views.RecruiterJobPostDetailAPIView.as_view(),name='recruiter-job-post-detail'),
    path('job-applications-list/',views.RecruiterJobApplicationsListAPIView.as_view(),name='job-applications-list'),
    path('job-applications/<str:job_id>/',views.RecruiterJobApplicationsAPIView.as_view(),name='candidate-job-applications'),
    path('scheduled_interviews/',views.RecruitersJobSchdeduledInterviews.as_view(),name='scheduled-interviews'),

    
]