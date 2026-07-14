from pydantic import BaseModel, Field
from typing import Any


class TraceStep(BaseModel):
    step: int
    line: int
    operation: str = ""
    variables: dict[str, Any] = Field(default_factory=dict)
    dataStructure: dict[str, Any] | None = None
    highlightedIndexes: list[int] = Field(default_factory=list)
    callStack: list[str] = Field(default_factory=list)
    output: str = ""
    explanation: str = ""
    complexity: dict[str, str] | None = None
    changedVariables: list[str] = Field(default_factory=list)
    loopIteration: int | None = None
    conditionResult: bool | None = None


class TraceRequest(BaseModel):
    code: str
    language: str = "python"
    algorithm: str | None = None
    input_data: str = ""


class AlgorithmDetection(BaseModel):
    detected: str = "General Iterative Approach"
    confidence: int = 0
    reason: str = ""
    all_detections: list[dict] = Field(default_factory=list)


class AlternativeApproach(BaseModel):
    algorithm: str
    time_complexity: str
    space_complexity: str
    explanation: str
    why_faster: str = ""
    additional_memory: str = ""
    when_current_better: str = ""
    when_alternative_better: str = ""


class ApproachInfo(BaseModel):
    algorithm: str
    time_complexity: str
    space_complexity: str
    alternatives: list[AlternativeApproach] = Field(default_factory=list)


class ProgramOutput(BaseModel):
    stdout: str = ""
    stderr: str = ""
    compile_error: str = ""
    runtime_error: str = ""
    exit_status: int = 0
    execution_time_ms: int = 0
    memory_usage_kb: int = 0


class ReferencesInfo(BaseModel):
    main_concept: str = ""
    pattern: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    similar_problems: list[str] = Field(default_factory=list)
    related_topics: list[str] = Field(default_factory=list)
    practice_problems: list[str] = Field(default_factory=list)
    pseudocode: str = ""


class TraceResponse(BaseModel):
    steps: list[TraceStep]
    total_steps: int
    algorithm_type: str
    time_complexity: str = ""
    space_complexity: str = ""
    detection: AlgorithmDetection = Field(default_factory=AlgorithmDetection)
    approaches: ApproachInfo | None = None
    references: ReferencesInfo | None = None
    program_output: ProgramOutput = Field(default_factory=ProgramOutput)


class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    input_data: str = ""
    algorithm: str | None = None


class AnalyzeResponse(BaseModel):
    detection: AlgorithmDetection
    approaches: ApproachInfo | None = None
    references: ReferencesInfo | None = None


class ExplainStepRequest(BaseModel):
    code: str
    step: TraceStep
    algorithm_type: str = ""
    mode: str = "beginner"


class ExplainStepResponse(BaseModel):
    explanation: str
    mode: str
