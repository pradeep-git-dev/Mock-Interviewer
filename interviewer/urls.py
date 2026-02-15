from django.urls import path

from . import views

urlpatterns = [
    path("signin/", views.signin_page, name="signin-page"),
    path("signin/submit/", views.signin_submit, name="signin-submit"),
    path("signup/", views.signup_page, name="signup-page"),
    path("signup/submit/", views.signup_submit, name="signup-submit"),
    path("logout/", views.logout_submit, name="logout-submit"),
    path("", views.index, name="interview-home"),
    path("past-scores/", views.past_scores_page, name="past-scores-page"),
    path("api/start/", views.start_interview, name="interview-start"),
    path("api/answer/", views.submit_answer, name="interview-answer"),
    path("api/history/", views.interview_history, name="interview-history"),
]
