from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="interview-home"),
    path("past-scores/", views.past_scores_page, name="past-scores-page"),
    path("api/start/", views.start_interview, name="interview-start"),
    path("api/answer/", views.submit_answer, name="interview-answer"),
]
