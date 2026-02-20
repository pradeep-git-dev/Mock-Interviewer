from django.urls import path

from . import views

urlpatterns = [
    path("signin/", views.legacy_auth_redirect, name="legacy-signin"),
    path("signup/", views.legacy_auth_redirect, name="legacy-signup"),
    path("logout/", views.legacy_auth_submit_redirect, name="legacy-logout"),
    path("signin/submit/", views.legacy_auth_submit_redirect, name="legacy-signin-submit"),
    path("signup/submit/", views.legacy_auth_submit_redirect, name="legacy-signup-submit"),
    path("", views.index, name="interview-home"),
    path("past-scores/", views.past_scores_page, name="past-scores-page"),
    path("api/start/", views.start_interview, name="interview-start"),
    path("api/answer/", views.submit_answer, name="interview-answer"),
]
