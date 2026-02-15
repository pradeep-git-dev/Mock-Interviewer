import json

from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .logic import InterviewSession
from .questions import get_question_bank, get_question_topics

SESSION_KEY = "interview_state"


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
def index(request: HttpRequest):
    context = {
        "total_questions": len(get_question_bank()),
        "topics": ", ".join(get_question_topics()),
    }
    return render(request, "interviewer/index.html", context)


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


@csrf_exempt
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
    evaluation = session.save_response(answer)

    if session.is_finished():
        _save_session(request, session)
        report = session.final_report()
        return JsonResponse(
            {
                "finished": True,
                "evaluation": evaluation,
                "report": report,
            }
        )

    next_question = session.get_current_question()
    _save_session(request, session)
    return JsonResponse(
        {
            "finished": False,
            "evaluation": evaluation,
            "question_index": session.index + 1,
            "question": _serialize_question(next_question),
        }
    )
