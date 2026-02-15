from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="interview-home"),
    path("api/start/", views.start_interview, name="interview-start"),
    path("api/answer/", views.submit_answer, name="interview-answer"),
]
