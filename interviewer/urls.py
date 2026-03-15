from django.urls import path

from . import views

urlpatterns = [
    # ── Pages ──
    path("", views.index, name="interview-home"),
    path("select/", views.select_interview_page, name="select-interview"),
    path("theory/", views.theory_interview_page, name="theory-interview"),
    path("advanced/", views.advanced_interview_page, name="advanced-interview"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("past-scores/", views.legacy_auth_redirect),
    path("performance/", views.legacy_auth_redirect),

    # ── Basic Interview API ──
    path("api/start/", views.start_interview),
    path("api/answer/", views.submit_answer),

    # ── Advanced Interview API ──
    path("api/adv/start/", views.adv_start),
    path("api/adv/answer/", views.adv_answer),
    path("api/adv/skip/", views.adv_skip),
    path("api/adv/end/", views.adv_end),

    # ── Aptitude Interview API ──
    path("api/aptitude/start/", views.aptitude_start),
    path("api/aptitude/answer/", views.aptitude_answer),
    path("api/aptitude/skip/", views.aptitude_skip),
    path("api/aptitude/end/", views.aptitude_end),
    path("aptitude/", views.aptitude_interview_page, name="aptitude-interview"),

    # ── Legacy redirects ──
    path("signin/", views.legacy_auth_redirect),
    path("signup/", views.legacy_auth_redirect),
    path("logout/", views.legacy_auth_submit_redirect),
]
