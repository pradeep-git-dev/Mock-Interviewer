import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .logic import InterviewSession
from .questions import get_question_bank, get_question_topics

SESSION_KEY = "interview_state"
HISTORY_KEY = "interview_history"
AUTH_USER_KEY = "auth_user"
USER_STORE_KEY = "auth_users"


def _serialize_question(question):
    return {
        "qid": question.qid,
        "topic": question.topic,
        "prompt": question.prompt,
    }


def _load_session(request: HttpRequest) -> InterviewSession:
    return InterviewSession.from_dict(request.session.get(SESSION_KEY, {}))


def _save_session(request: HttpRequest, session: InterviewSession) -> None:
    request.session[SESSION_KEY] = session.to_dict()
    request.session.modified = True


def _get_auth_user(request: HttpRequest) -> dict:
    user = request.session.get(AUTH_USER_KEY, {})
    if isinstance(user, dict):
        return user
    return {}


def _is_authenticated(request: HttpRequest) -> bool:
    return bool(_get_auth_user(request).get("username"))


def _login_session_user(request: HttpRequest, username: str, name: str) -> None:
    request.session[AUTH_USER_KEY] = {
        "username": username,
        "name": name or username,
    }
    request.session.modified = True


def _logout_session_user(request: HttpRequest) -> None:
    request.session.pop(AUTH_USER_KEY, None)
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True


def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not _is_authenticated(request):
            return redirect("signin-page")
        return view_func(request, *args, **kwargs)

    return _wrapped


@never_cache
@ensure_csrf_cookie
@require_GET
def signin_page(request: HttpRequest):
    if _is_authenticated(request):
        return redirect("interview-home")
    return render(request, "interviewer/signin.html")


@require_POST
def signin_submit(request: HttpRequest):
    name = str(request.POST.get("name", "")).strip()
    username = str(request.POST.get("username", "")).strip()
    password = str(request.POST.get("password", "")).strip()

    if not username or not password:
        messages.error(request, "Username and password are required.")
        return redirect("signin-page")

    users = request.session.get(USER_STORE_KEY, {})
    existing = users.get(username) if isinstance(users, dict) else None
    if existing and not check_password(password, existing.get("password_hash", "")):
        messages.error(request, "Invalid username or password.")
        return redirect("signin-page")

    resolved_name = name or (existing or {}).get("name") or username
    _login_session_user(request, username, resolved_name)
    return redirect("interview-home")


@never_cache
@ensure_csrf_cookie
@require_GET
def signup_page(request: HttpRequest):
    if _is_authenticated(request):
        return redirect("interview-home")
    return render(request, "interviewer/signup.html")


@require_POST
def signup_submit(request: HttpRequest):
    name = str(request.POST.get("name", "")).strip()
    username = str(request.POST.get("username", "")).strip()
    password = str(request.POST.get("password", "")).strip()

    if not name or not username or not password:
        messages.error(request, "Name, username, and password are required.")
        return redirect("signup-page")

    users = request.session.get(USER_STORE_KEY, {})
    if not isinstance(users, dict):
        users = {}

    if username in users:
        messages.error(request, "Username already exists.")
        return redirect("signup-page")

    users[username] = {"name": name, "password_hash": make_password(password)}
    request.session[USER_STORE_KEY] = users
    _login_session_user(request, username, name)
    return redirect("interview-home")


@require_POST
def logout_submit(request: HttpRequest):
    _logout_session_user(request)
    return redirect("signin-page")


@session_login_required
@require_GET
def index(request: HttpRequest):
    auth_user = _get_auth_user(request)
    context = {
        "total_questions": 25,
        "topics": ", ".join(get_question_topics()),
        "question_bank_size": len(get_question_bank()),
        "display_name": auth_user.get("name") or auth_user.get("username") or "Candidate",
    }
    return render(request, "interviewer/index.html", context)


@session_login_required
@require_GET
def past_scores_page(request: HttpRequest):
    return render(request, "interviewer/past_scores.html")


@session_login_required
@require_GET
def start_interview(request: HttpRequest):
    session = InterviewSession()
    _save_session(request, session)
    question = session.get_current_question()
    return JsonResponse(
        {
            "started": True,
            "total_questions": len(session.questions),
            "question_index": 1,
            "question": _serialize_question(question),
        }
    )


@session_login_required
@require_POST
def submit_answer(request: HttpRequest):
    session = _load_session(request)
    if session.is_finished():
        report = session.final_report()
        return JsonResponse({"finished": True, "report": report})

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")

    answer = str(payload.get("answer", "")).strip()
    session.save_response(answer)

    if session.is_finished():
        _save_session(request, session)
        report = session.final_report()

        history = list(request.session.get(HISTORY_KEY, []))
        history.insert(
            0,
            {
                "completed_at": timezone.now().isoformat(),
                "report": report,
            },
        )
        request.session[HISTORY_KEY] = history[:20]
        request.session.modified = True
        return JsonResponse(
            {
                "finished": True,
                "report": report,
            }
        )

    next_question = session.get_current_question()
    _save_session(request, session)
    return JsonResponse(
        {
            "finished": False,
            "question_index": session.index + 1,
            "total_questions": len(session.questions),
            "question": _serialize_question(next_question),
        }
    )


@session_login_required
@require_GET
def interview_history(request: HttpRequest):
    history = list(request.session.get(HISTORY_KEY, []))
    return JsonResponse({"history": history})
