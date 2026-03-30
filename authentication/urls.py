from django.contrib import admin
from django.urls import path, include
from authentication import views

urlpatterns = [
    path('recruiter-register/',views.RecruiterRegisterAPIView.as_view()),
    path('login/',views.LoginAPIView.as_view()),
    path('candidate-register/',views.CandidateRegisterAPIView.as_view()),
]