import { useState, useRef, useCallback, useEffect } from 'react'
import { ArrowLeft, Terminal, Brain, GitCompare, BookOpen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import VisualizationControls from '../components/visualization/VisualizationControls'
import VisualizationPanel from '../components/visualization/VisualizationPanel'
import ExecutionDetails from '../components/visualization/ExecutionDetails'
import ProgramOutputPanel from '../components/visualization/ProgramOutputPanel'
import Approachespanel from '../components/visualization/ApproachesPanel'
import ReferencesPanel from '../components/visualization/ReferencesPanel'
import { api } from '../api'
import type { TraceStep, TraceResponse, ApproachInfo, ReferencesInfo, ProgramOutput, AlgorithmDetection } from '../types'

const SAMPLE_CODE: Record<string, string> = {
  python: `numbers = list(map(int, input().split()))

largest = numbers[0]

for number in numbers:
    if number > largest:
        largest = number

print(largest)`,
  javascript: `function bubbleSort(arr) {
    let n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
            }
        }
    }
    return arr;
}

let data = [5, 2, 8, 1, 9, 3];
console.log(bubbleSort(data));`,
}

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
]

const ALGORITHM_PRESETS = [
  { label: 'Find Largest', code: `numbers = list(map(int, input().split()))\n\nlargest = numbers[0]\n\nfor number in numbers:\n    if number > largest:\n        largest = number\n\nprint(largest)` },
  { label: 'Bubble Sort', code: `data = [5, 2, 8, 1, 9, 3]\n\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\nprint(bubble_sort(data))` },
  { label: 'Selection Sort', code: `data = [5, 2, 8, 1, 9, 3]\n\ndef selection_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        min_idx = i\n        for j in range(i+1, n):\n            if arr[j] < arr[min_idx]:\n                min_idx = j\n        arr[i], arr[min_idx] = arr[min_idx], arr[i]\n    return arr\n\nprint(selection_sort(data))` },
  { label: 'Binary Search', code: `arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]\ntarget = 5\n\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\nprint(binary_search(arr, target))` },
  { label: 'Linear Search', code: `arr = [5, 2, 8, 1, 9, 3]\ntarget = 8\n\ndef linear_search(arr, target):\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1\n\nprint(linear_search(arr, target))` },
  { label: 'Two Sum (Hash)', code: `nums = [2, 7, 11, 15]\ntarget = 9\n\ndef two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []\n\nprint(two_sum(nums, target))` },
  { label: 'Factorial', code: `n = 5\n\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(n))` },
  { label: 'Two Pointers', code: `arr = [1, 2, 3, 4, 5, 6, 7]\ntarget = 9\n\ndef two_sum_sorted(arr, target):\n    left, right = 0, len(arr) - 1\n    while left < right:\n        s = arr[left] + arr[right]\n        if s == target:\n            return [left, right]\n        elif s < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n\nprint(two_sum_sorted(arr, target))` },
]

type RightTab = 'details' | 'output' | 'explanation' | 'approaches' | 'references'

export default function CodeVisualization() {
  const navigate = useNavigate()
  const [code, setCode] = useState(SAMPLE_CODE.python)
  const [language, setLanguage] = useState('python')
  const [inputData, setInputData] = useState('')
  const [steps, setSteps] = useState<TraceStep[]>([])
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(700)
  const [isGenerating, setIsGenerating] = useState(false)
  const [algorithmType, setAlgorithmType] = useState('')
  const [timeComplexity, setTimeComplexity] = useState('')
  const [spaceComplexity, setSpaceComplexity] = useState('')
  const [aiExplanation, setAiExplanation] = useState('')
  const [explanationMode, setExplanationMode] = useState<'beginner' | 'professional'>('beginner')
  const [loadingExplanation, setLoadingExplanation] = useState(false)
  const [programOutput, setProgramOutput] = useState<ProgramOutput | null>(null)
  const [detection, setDetection] = useState<AlgorithmDetection | null>(null)
  const [approaches, setApproaches] = useState<ApproachInfo | null>(null)
  const [references, setReferences] = useState<ReferencesInfo | null>(null)
  const [rightTab, setRightTab] = useState<RightTab>('details')
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const codeLines = code.split('\n')
  const currentStepData = steps[currentStep] || null

  const stopPlayback = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    setIsPlaying(false)
  }, [])

  const startPlayback = useCallback(() => {
    stopPlayback()
    setIsPlaying(true)
    timerRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          stopPlayback()
          return prev
        }
        return prev + 1
      })
    }, speed)
  }, [steps.length, speed, stopPlayback])

  useEffect(() => {
    if (isPlaying && steps.length > 0) {
      startPlayback()
    }
    return stopPlayback
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [speed])

  const handlePlayPause = useCallback(() => {
    if (isPlaying) {
      stopPlayback()
    } else {
      if (currentStep >= steps.length - 1) setCurrentStep(0)
      startPlayback()
    }
  }, [isPlaying, currentStep, steps.length, startPlayback, stopPlayback])

  const executeCode = useCallback(async (mode: 'visualize' | 'run') => {
    if (!code.trim()) return
    stopPlayback()
    setIsGenerating(true)
    try {
      const result: TraceResponse = await api.viz.trace(code, language, undefined, inputData)
      setSteps(result.steps)
      setAlgorithmType(result.algorithm_type)
      setTimeComplexity(result.time_complexity)
      setSpaceComplexity(result.space_complexity)
      setCurrentStep(mode === 'visualize' ? 0 : result.steps.length - 1)
      setAiExplanation('')
      setProgramOutput(result.program_output || null)
      setDetection(result.detection || null)
      setApproaches(result.approaches || null)
      setReferences(result.references || null)
      if (mode === 'run') setRightTab('output')
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Execution failed'
      if (mode === 'visualize') {
        setSteps([{
          step: 1, line: 1, operation: 'error', variables: {},
          dataStructure: null, highlightedIndexes: [], callStack: [],
          output: errMsg, explanation: 'An error occurred while generating the execution trace.',
        }])
      }
      setProgramOutput({ stdout: '', stderr: errMsg, compile_error: '', runtime_error: errMsg, exit_status: 1, execution_time_ms: 0, memory_usage_kb: 0 })
      if (mode === 'run') setRightTab('output')
    } finally {
      setIsGenerating(false)
    }
  }, [code, language, inputData, stopPlayback])

  const handleVisualize = useCallback(() => executeCode('visualize'), [executeCode])
  const handleRun = useCallback(() => executeCode('run'), [executeCode])

  const handleGetAIExplanation = useCallback(async () => {
    if (!currentStepData || !code) return
    setLoadingExplanation(true)
    try {
      const result = await api.viz.explainStep(code, currentStepData, algorithmType, explanationMode)
      setAiExplanation(result.explanation)
      setRightTab('explanation')
    } catch {
      setAiExplanation(currentStepData.explanation || 'Could not generate explanation.')
      setRightTab('explanation')
    } finally {
      setLoadingExplanation(false)
    }
  }, [currentStepData, code, algorithmType, explanationMode])

  const handleSpeedChange = useCallback((newSpeed: number) => {
    setSpeed(newSpeed)
  }, [])

  const handlePreset = useCallback((presetCode: string) => {
    stopPlayback()
    setCode(presetCode)
    setSteps([])
    setCurrentStep(0)
    setAlgorithmType('')
    setTimeComplexity('')
    setSpaceComplexity('')
    setAiExplanation('')
    setProgramOutput(null)
    setDetection(null)
    setApproaches(null)
    setReferences(null)
    setRightTab('details')
  }, [stopPlayback])

  const tabs: { key: RightTab; label: string; icon: React.ReactNode }[] = [
    { key: 'details', label: 'Details', icon: null },
    { key: 'output', label: 'Output', icon: <Terminal size={14} /> },
    { key: 'explanation', label: 'AI Explain', icon: <Brain size={14} /> },
    { key: 'approaches', label: 'Approaches', icon: <GitCompare size={14} /> },
    { key: 'references', label: 'References', icon: <BookOpen size={14} /> },
  ]

  return (
    <div className="viz-page">
      <div className="viz-topbar">
        <button className="back-link" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} /> Back
        </button>
        <h2>Code Visualization</h2>
        <div className="viz-topbar-right">
          <select className="viz-lang-select" value={language} onChange={(e) => {
            setLanguage(e.target.value)
            if (SAMPLE_CODE[e.target.value]) setCode(SAMPLE_CODE[e.target.value])
          }}>
            {LANGUAGES.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>
        </div>
      </div>

      <div className="viz-presets">
        <span className="viz-presets-label">Presets:</span>
        {ALGORITHM_PRESETS.map((p, i) => (
          <button key={i} className="btn btn-sm btn-secondary" onClick={() => handlePreset(p.code)}>
            {p.label}
          </button>
        ))}
      </div>

      <div className="viz-panels">
        <div className="viz-left">
          <div className="viz-left-header">Code Editor</div>
          <CodeEditor
            value={code}
            onChange={setCode}
            language={language}
            height="calc(100vh - 300px)"
            minimap={false}
          />
          <div className="viz-input-section">
            <label className="viz-input-label">Input / Test Data</label>
            <input
              className="viz-input-field"
              type="text"
              placeholder='e.g. 10 25 8 42 17 or [5, 2, 8, 1]'
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
            />
          </div>
        </div>

        <div className="viz-center">
          <VisualizationPanel
            step={currentStepData}
            algorithmType={algorithmType}
            codeLines={codeLines}
            detection={detection}
          />
        </div>

        <div className="viz-right">
          <div className="viz-right-tabs">
            {tabs.map(t => (
              <button
                key={t.key}
                className={`viz-tab ${rightTab === t.key ? 'active' : ''}`}
                onClick={() => {
                  setRightTab(t.key)
                  if (t.key === 'explanation') handleGetAIExplanation()
                }}
              >
                {t.icon && <span className="viz-tab-icon">{t.icon}</span>}
                {t.label}
              </button>
            ))}
          </div>
          <div className="viz-right-content">
            {rightTab === 'details' && (
              <ExecutionDetails step={currentStepData} />
            )}
            {rightTab === 'output' && (
              <ProgramOutputPanel output={programOutput} />
            )}
            {rightTab === 'explanation' && (
              <div className="viz-ai-explanation">
                <div className="viz-explanation-mode-toggle">
                  <button
                    className={`btn btn-sm ${explanationMode === 'beginner' ? 'btn-ai-active' : 'btn-secondary'}`}
                    onClick={() => { setExplanationMode('beginner'); setAiExplanation('') }}
                  >
                    Beginner
                  </button>
                  <button
                    className={`btn btn-sm ${explanationMode === 'professional' ? 'btn-ai-active' : 'btn-secondary'}`}
                    onClick={() => { setExplanationMode('professional'); setAiExplanation('') }}
                  >
                    Professional
                  </button>
                </div>
                {aiExplanation ? (
                  <div className="viz-explanation-content">
                    <div className="viz-explanation-mode-label">{explanationMode === 'beginner' ? 'Beginner' : 'Professional'} Explanation</div>
                    <p>{aiExplanation}</p>
                    <button className="btn btn-sm btn-secondary" onClick={handleGetAIExplanation} disabled={loadingExplanation}>
                      Regenerate
                    </button>
                  </div>
                ) : (
                  <div className="viz-explanation-content">
                    {loadingExplanation ? (
                      <p>Loading explanation...</p>
                    ) : (
                      <>
                        <p>Click the <strong>AI Explain</strong> tab or press the button below to get an AI-powered explanation of the current execution step.</p>
                        <button className="btn btn-sm btn-primary" onClick={handleGetAIExplanation} disabled={loadingExplanation}>
                          {loadingExplanation ? 'Loading...' : 'Get AI Explanation'}
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
            {rightTab === 'approaches' && (
              <Approachespanel
                approaches={approaches}
                detection={detection}
                timeComplexity={timeComplexity}
                spaceComplexity={spaceComplexity}
              />
            )}
            {rightTab === 'references' && (
              <ReferencesPanel references={references} detection={detection} />
            )}
          </div>
        </div>
      </div>

      <VisualizationControls
        totalSteps={steps.length}
        currentStep={currentStep}
        isPlaying={isPlaying}
        speed={speed}
        onStepPrev={() => { stopPlayback(); setCurrentStep(Math.max(0, currentStep - 1)) }}
        onStepNext={() => { stopPlayback(); setCurrentStep(Math.min(steps.length - 1, currentStep + 1)) }}
        onPlayPause={handlePlayPause}
        onRestart={() => { stopPlayback(); setCurrentStep(0) }}
        onSpeedChange={handleSpeedChange}
        onVisualize={handleVisualize}
        onRun={handleRun}
        isGenerating={isGenerating}
        hasCode={code.trim().length > 0}
      />
    </div>
  )
}
