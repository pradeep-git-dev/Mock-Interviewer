from django.urls import path

from . import views

urlpatterns = [
    # ── Pages ──
    path("", views.index, name="interview-home"),
    path("past-scores/", views.past_scores_page, name="past-scores"),
    path("advanced/", views.advanced_interview_page, name="advanced-interview"),
    path("performance/", views.performance_dashboard_page, name="performance-dashboard"),

    # ── Basic Interview API ──
    path("api/start/", views.start_interview),
    path("api/answer/", views.submit_answer),

    # ── Advanced Interview API ──
    path("api/adv/start/", views.adv_start),
    path("api/adv/answer/", views.adv_answer),
    path("api/adv/skip/", views.adv_skip),
    path("api/adv/end/", views.adv_end),

    # ── Legacy redirects ──
    path("signin/", views.legacy_auth_redirect),
    path("signup/", views.legacy_auth_redirect),
    path("logout/", views.legacy_auth_submit_redirect),
]
