from django.contrib import admin
from django.urls import path, include
from recruiter import views

urlpatterns = [
    path('job-post/',views.RecruiterJobPostAPIView.as_view(),name='recruiter-job-post'),
    path('job-post-detail/<str:id>/',views.RecruiterJobPostDetailAPIView.as_view(),name='recruiter-job-post-detail'),
    
]