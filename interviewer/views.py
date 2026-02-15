import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .logic import InterviewSession
from .questions import get_question_bank, get_question_topics

SESSION_KEY = "interview_state"
HISTORY_KEY = "interview_history"


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


@never_cache
@ensure_csrf_cookie
@require_GET
def signin_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("interview-home")
    return render(request, "interviewer/signin.html")


@require_POST
def signin_submit(request: HttpRequest):
    username = str(request.POST.get("username", "")).strip()
    password = str(request.POST.get("password", "")).strip()

    user = authenticate(request, username=username, password=password)
    if not user:
        messages.error(request, "Invalid username or password.")
        return redirect("signin-page")

    login(request, user)
    return redirect("interview-home")


@never_cache
@ensure_csrf_cookie
@require_GET
def signup_page(request: HttpRequest):
    if request.user.is_authenticated:
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

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists.")
        return redirect("signup-page")

    user = User.objects.create_user(username=username, password=password, first_name=name)
    login(request, user)
    return redirect("interview-home")


@require_POST
def logout_submit(request: HttpRequest):
    logout(request)
    return redirect("signin-page")


@login_required(login_url="/signin/")
@require_GET
def index(request: HttpRequest):
    context = {
        "total_questions": 25,
        "topics": ", ".join(get_question_topics()),
        "question_bank_size": len(get_question_bank()),
        "display_name": request.user.first_name or request.user.username,
    }
    return render(request, "interviewer/index.html", context)


@login_required(login_url="/signin/")
@require_GET
def past_scores_page(request: HttpRequest):
    return render(request, "interviewer/past_scores.html")


@login_required(login_url="/signin/")
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


@login_required(login_url="/signin/")
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


@login_required(login_url="/signin/")
@require_GET
def interview_history(request: HttpRequest):
    history = list(request.session.get(HISTORY_KEY, []))
    return JsonResponse({"history": history})
