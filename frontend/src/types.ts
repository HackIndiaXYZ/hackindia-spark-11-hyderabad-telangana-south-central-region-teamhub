export interface User {
  id: string
  email: string
  username: string
  avatar_url?: string
  provider: string
}

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  language: string
  framework?: string
  created_at: string
  updated_at: string
}

export interface FileItem {
  id: string
  project_id: string
  path: string
  content?: string
  language?: string
  created_at: string
  updated_at: string
}

export interface Message {
  role: string
  content: string
  agent_name?: string
}

export interface ChatHistory {
  id: string
  title: string
  pinned: boolean
  created_at: string
  updated_at: string
  messages: Message[]
}

export interface AgentInfo {
  key: string
  name: string
  description: string
  icon?: string
  color?: string
  system_prompt?: string
}

export interface ProjectStats {
  id: string
  name: string
  language: string
  file_count: number
}

export interface TraceStep {
  step: number
  line: number
  operation: string
  variables: Record<string, unknown>
  dataStructure: {
    type: string
    values: unknown[]
    nodes?: string[]
    edges?: [string, string][]
    visited?: string[]
    current?: string | null
    root?: unknown
  } | null
  highlightedIndexes: number[]
  callStack: string[]
  output: string
  explanation: string
  complexity?: { time: string; space: string } | null
  changedVariables?: string[]
  loopIteration?: number | null
  conditionResult?: boolean | null
}

export interface AlgorithmDetection {
  detected: string
  confidence: number
  reason: string
  all_detections: { name: string; score: number }[]
}

export interface AlternativeApproach {
  algorithm: string
  time_complexity: string
  space_complexity: string
  explanation: string
  why_faster: string
  additional_memory: string
  when_current_better: string
  when_alternative_better: string
}

export interface ApproachInfo {
  algorithm: string
  time_complexity: string
  space_complexity: string
  alternatives: AlternativeApproach[]
}

export interface ProgramOutput {
  stdout: string
  stderr: string
  compile_error: string
  runtime_error: string
  exit_status: number
  execution_time_ms: number
  memory_usage_kb: number
}

export interface ReferencesInfo {
  main_concept: string
  pattern: string
  prerequisites: string[]
  similar_problems: string[]
  related_topics: string[]
  practice_problems: string[]
  pseudocode: string
}

export interface TraceResponse {
  steps: TraceStep[]
  total_steps: number
  algorithm_type: string
  time_complexity: string
  space_complexity: string
  detection: AlgorithmDetection
  approaches: ApproachInfo | null
  references: ReferencesInfo | null
  program_output: ProgramOutput
}

export type VisualizationMode = 'beginner' | 'professional'
