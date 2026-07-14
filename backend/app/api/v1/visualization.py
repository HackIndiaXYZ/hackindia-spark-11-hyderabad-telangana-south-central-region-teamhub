from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.project import Project
from app.models.file import File
from app.models.chat import Chat, Message
from app.schemas.visualization import (
    TraceRequest, TraceResponse, TraceStep,
    ExplainStepRequest, ExplainStepResponse,
    AlgorithmDetection, AlternativeApproach, ApproachInfo,
    ProgramOutput, ReferencesInfo,
    AnalyzeRequest, AnalyzeResponse,
)
from app.services.trace_generator import generate_trace
from app.services.code_runner import run_and_trace
from app.services.algorithm_detector import detect_algorithm
from app.services.alternative_approaches import (
    get_alternative_approaches,
    get_current_approach_complexity,
)
from app.services.references_db import get_references
from app.services.trace_normalizer import normalize_trace

router = APIRouter()


@router.get("/project/{project_id}")
async def project_viz(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    files_result = await db.execute(select(File).where(File.project_id == project_id))
    files = files_result.scalars().all()
    return {
        "project": {"id": project.id, "name": project.name, "language": project.language},
        "files": [{"id": f.id, "path": f.path, "language": f.language} for f in files],
        "file_count": len(files),
        "languages": list({f.language for f in files if f.language}),
    }


@router.get("/activity/{user_id}")
async def user_activity(user_id: str = "default", days: int = Query(7, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timezone, timedelta
    since = datetime.now(timezone.utc) - timedelta(days=days)
    project_count = await db.scalar(select(func.count(Project.id)).where(Project.user_id == user_id, Project.created_at >= since))
    chat_count = await db.scalar(select(func.count(Chat.id)).where(Chat.user_id == user_id, Chat.created_at >= since))
    msg_count = await db.scalar(select(func.count(Message.id)).where(Message.created_at >= since))
    return {"projects": project_count or 0, "chats": chat_count or 0, "messages": msg_count or 0, "period_days": days}


def _build_enhanced_response(trace_result: dict) -> dict:
    steps_raw = trace_result.get("steps", [])
    algo_type = trace_result.get("algorithm_type", "general")

    code = trace_result.get("_code", "")
    detection = detect_algorithm(code) if code else AlgorithmDetection().model_dump()

    algo_name = detection.get("detected", algo_type)
    time_c, space_c = get_current_approach_complexity(algo_name)
    alternatives_raw = get_alternative_approaches(algo_name)

    approaches = ApproachInfo(
        algorithm=algo_name,
        time_complexity=time_c,
        space_complexity=space_c,
        alternatives=[AlternativeApproach(**a) for a in alternatives_raw],
    ) if alternatives_raw else None

    refs_raw = get_references(algo_name)
    references = ReferencesInfo(**refs_raw) if refs_raw else None

    program_output = ProgramOutput(
        stdout=trace_result.get("output_lines", [""])[0] if trace_result.get("output_lines") else "",
        stderr="".join(trace_result.get("errors", [])),
        compile_error=trace_result.get("compile_error", ""),
        runtime_error=trace_result.get("runtime_error", ""),
        exit_status=trace_result.get("exit_status", 0),
        execution_time_ms=trace_result.get("execution_time_ms", 0),
        memory_usage_kb=trace_result.get("memory_usage_kb", 0),
    )

    return {
        "steps": steps_raw,
        "total_steps": len(steps_raw),
        "algorithm_type": algo_type,
        "time_complexity": time_c,
        "space_complexity": space_c,
        "detection": detection,
        "approaches": approaches.model_dump() if approaches else None,
        "references": references.model_dump() if references else None,
        "program_output": program_output.model_dump(),
    }


@router.post("/trace")
async def generate_code_trace(request: TraceRequest):
    lang = request.language.lower()
    code = request.code

    if lang == "python" or lang == "py":
        trace_result = run_and_trace(code, request.input_data)
    else:
        trace_result = generate_trace(code, lang, request.algorithm, request.input_data)

    trace_result["_code"] = code
    return _build_enhanced_response(trace_result)


@router.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    code = request.code
    lang = request.language.lower()

    detection = detect_algorithm(code)
    algo_name = detection.get("detected", "general")
    time_c, space_c = get_current_approach_complexity(algo_name)
    alternatives_raw = get_alternative_approaches(algo_name)

    approaches = ApproachInfo(
        algorithm=algo_name,
        time_complexity=time_c,
        space_complexity=space_c,
        alternatives=[AlternativeApproach(**a) for a in alternatives_raw],
    ) if alternatives_raw else None

    refs_raw = get_references(algo_name)
    references = ReferencesInfo(**refs_raw) if refs_raw else None

    return AnalyzeResponse(
        detection=AlgorithmDetection(**detection),
        approaches=approaches,
        references=references,
    )


@router.post("/explain-step")
async def explain_step(request: ExplainStepRequest):
    from app.services.llm_service import llm_service
    step_info = request.step.model_dump()
    prompt = (
        f"Explain this code execution step in {'simple beginner-friendly' if request.mode == 'beginner' else 'technical'} language.\n\n"
        f"Code:\n{request.code[:1000]}\n\n"
        f"Step {step_info.get('step', 0)}:\n"
        f"- Operation: {step_info.get('operation', '')}\n"
        f"- Line: {step_info.get('line', 0)}\n"
        f"- Variables: {step_info.get('variables', {})}\n"
        f"- Data Structure: {step_info.get('dataStructure', {})}\n"
        f"- Output: {step_info.get('output', '')}\n"
        f"- Current explanation: {step_info.get('explanation', '')}\n"
    )
    if request.mode == "beginner":
        prompt += "\nExplain what happened in this step like you're teaching a beginner programmer. Use simple analogies if possible."
    else:
        prompt += "\nExplain what happened in this step with technical detail. Include time/space complexity implications if relevant."

    messages = [{"role": "user", "content": prompt}]
    system_prompt = "You are a technical educator helping visualize code execution. Be concise and clear."
    result = await llm_service.chat_with_agents(messages, "explainer", system_prompt)
    explanation = result.get("content", step_info.get("explanation", ""))
    return ExplainStepResponse(explanation=explanation, mode=request.mode)
