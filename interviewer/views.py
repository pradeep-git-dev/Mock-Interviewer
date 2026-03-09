import json
import time

from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .logic import InterviewSession
from .questions import get_question_bank, get_question_topics
from .advanced_logic import AdvancedSession

SESSION_KEY = "interview_state"
ADV_SESSION_KEY = "advanced_interview_state"


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


@require_GET
def legacy_auth_redirect(request: HttpRequest):
    return redirect("interview-home")


@require_POST
def legacy_auth_submit_redirect(request: HttpRequest):
    return redirect("interview-home")


@never_cache
@ensure_csrf_cookie
@require_GET
def index(request: HttpRequest):
    context = {
        "total_questions": 25,
        "topics": ", ".join(get_question_topics()),
        "question_bank_size": len(get_question_bank()),
    }
    return render(request, "interviewer/index.html", context)


@require_GET
def select_interview_page(request: HttpRequest):
    return render(request, "interviewer/select_interview.html")


@never_cache
@ensure_csrf_cookie
@require_GET
def theory_interview_page(request: HttpRequest):
    return render(request, "interviewer/theory_interview.html")


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
    end_interview = bool(payload.get("end_interview", False))
    
    evaluation = session.save_response(answer)
    
    if end_interview:
        # Force finish
        session.index = len(session.questions)

    if session.is_finished():
        _save_session(request, session)
        report = session.final_report()
        return JsonResponse(
            {
                "finished": True,
                "report": report,
                "last_evaluation": {
                    "score": evaluation["score"],
                    "feedback": evaluation["feedback"],
                    "strengths": evaluation.get("strengths", ""),
                    "improvement": evaluation.get("improvement", ""),
                },
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
            "evaluation": {
                "score": evaluation["score"],
                "feedback": evaluation["feedback"],
                "strengths": evaluation.get("strengths", ""),
                "improvement": evaluation.get("improvement", ""),
            },
        }
    )


# ═══════════════════════════════════
#  ADVANCED INTERVIEW VIEWS
# ═══════════════════════════════════

def _adv_load(request):
    data = request.session.get(ADV_SESSION_KEY)
    return AdvancedSession.from_dict(data) if data else None


def _adv_save(request, s):
    request.session[ADV_SESSION_KEY] = s.to_dict()
    request.session.modified = True


@never_cache
@ensure_csrf_cookie
@require_GET
def advanced_interview_page(request):
    return render(request, "interviewer/advanced_interview.html")


@require_GET
def adv_start(request):
    lang = request.GET.get("lang", "python")
    mode = request.GET.get("mode", "debug")  # "debug" or "logical"

    if mode not in ("debug", "logical"):
        mode = "debug"

    s = AdvancedSession(mode=mode, lang=lang)
    q = s.get_current_question_for_client()

    if not q:
        return JsonResponse({"error": "Failed to generate question"}, status=500)

    _adv_save(request, s)
    return JsonResponse({
        "started": True,
        "mode": mode,
        "language": lang,
        "total_questions": s.total_questions,
        "question_index": 1,
        "remaining_seconds": s.remaining_seconds(),
        "question": q,
    })


@require_POST
def adv_answer(request):
    s = _adv_load(request)
    if not s:
        return JsonResponse({"error": "No active session"}, status=400)
    if s.is_finished():
        report = s.compile_report()
        return JsonResponse({"finished": True, "report": report})

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    submitted_code = str(body.get("code", "")).strip()
    eval_result = s.evaluate_answer(submitted_code)

    if s.is_finished():
        s.end_interview()
        _adv_save(request, s)
        report = s.compile_report()
        return JsonResponse({
            "finished": True,
            "report": report,
            "last_evaluation": {
                "score": eval_result["score"],
                "feedback": eval_result.get("feedback", ""),
                "strengths": eval_result.get("strengths", ""),
                "improvement": eval_result.get("improvement", ""),
                "bugs_found": eval_result.get("bugs_found", []),
                "passed_tests": eval_result.get("passed_tests", 0),
                "total_tests": eval_result.get("total_tests", 0),
            },
        })

    # Generate next question
    nq = s.get_current_question_for_client()
    _adv_save(request, s)

    response_data = {
        "finished": False,
        "question_index": s.index + 1,
        "total_questions": s.total_questions,
        "remaining_seconds": s.remaining_seconds(),
        "question": nq,
        "evaluation": {
            "score": eval_result["score"],
            "feedback": eval_result.get("feedback", ""),
            "strengths": eval_result.get("strengths", ""),
            "improvement": eval_result.get("improvement", ""),
            "bugs_found": eval_result.get("bugs_found", []),
            "passed_tests": eval_result.get("passed_tests", 0),
            "total_tests": eval_result.get("total_tests", 0),
        },
    }

    # Include solution/fix for review
    if s.mode == "debug":
        response_data["evaluation"]["fixed_code"] = eval_result.get("fixed_code", "")
        response_data["evaluation"]["bug_explanation"] = eval_result.get("bug_explanation", "")
    else:
        response_data["evaluation"]["correct_answer"] = eval_result.get("correct_answer", "")

    return JsonResponse(response_data)


@require_POST
def adv_skip(request):
    s = _adv_load(request)
    if not s:
        return JsonResponse({"error": "No active session"}, status=400)
    if s.is_finished():
        report = s.compile_report()
        return JsonResponse({"finished": True, "report": report})

    skip_result = s.skip_question()

    if s.is_finished():
        s.end_interview()
        _adv_save(request, s)
        return JsonResponse({"finished": True, "report": s.compile_report()})

    nq = s.get_current_question_for_client()
    _adv_save(request, s)
    return JsonResponse({
        "finished": False,
        "question_index": s.index + 1,
        "total_questions": s.total_questions,
        "remaining_seconds": s.remaining_seconds(),
        "question": nq,
        "skipped": True,
    })


@require_POST
def adv_end(request):
    s = _adv_load(request)
    if not s:
        return JsonResponse({"error": "No active session"}, status=400)
    s.end_interview()
    _adv_save(request, s)
    report = s.compile_report()
    return JsonResponse({"finished": True, "report": report})


@require_GET
def dashboard_page(request):
    return render(request, "interviewer/dashboard.html")

