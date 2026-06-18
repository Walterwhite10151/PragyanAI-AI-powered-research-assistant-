// frontend/src/pages/ResearchPage.tsx
import { useState } from 'react'
import { Search, Zap, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Input, ProviderSelector, Card } from '../components/ui'
import { ResearchResults } from '../components/ResearchResults'
import { runResearch } from '../services/api'
import type { ResearchResponse, LLMProvider } from '../types'

const STEPS = [
  '🔍 Searching the web with Exa…',
  '🗄️ Retrieving from knowledge base…',
  '✍️ Generating overview…',
  '🔑 Extracting key concepts…',
  '📊 Gathering important facts…',
  '🗺️ Building learning roadmap…',
  '📝 Writing final summary…',
  '🎬 Finding YouTube videos…',
]

export default function ResearchPage() {
  const [topic, setTopic] = useState('')
  const [provider, setProvider] = useState<LLMProvider>('groq')
  const [loading, setLoading] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [result, setResult] = useState<ResearchResponse | null>(null)

  const handleResearch = async () => {
    if (!topic.trim()) { toast.error('Enter a topic first'); return }

    setLoading(true)
    setResult(null)
    setStepIndex(0)

    // Cycle through step labels every ~3s for UX feedback
    const interval = setInterval(() => {
      setStepIndex(i => (i + 1) % STEPS.length)
    }, 3000)

    try {
      const data = await runResearch(topic.trim(), provider)
      setResult(data)
      toast.success(`Research complete in ${data.elapsed_seconds}s!`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } }; message?: string })
        ?.response?.data?.detail || (err as { message?: string })?.message || 'Research failed'
      toast.error(msg)
    } finally {
      clearInterval(interval)
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <Search size={22} className="text-brand-400" />
          Research a Topic
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Powered by <span className="text-brand-400">Exa neural search</span> +{' '}
          <span className="text-purple-400">Groq / Gemini LLMs</span> via LangGraph
        </p>
      </div>

      {/* Input card */}
      <Card>
        <div className="flex gap-3">
          <Input
            value={topic}
            onChange={setTopic}
            placeholder="e.g. Transformer architecture, CRISPR, Rust async runtime…"
            onKeyDown={e => e.key === 'Enter' && !loading && handleResearch()}
            className="flex-1"
          />
          <ProviderSelector value={provider} onChange={v => setProvider(v as LLMProvider)} />
          <Button onClick={handleResearch} disabled={loading} className="shrink-0">
            {loading
              ? <><Loader2 size={15} className="animate-spin" /> Researching…</>
              : <><Zap size={15} /> Research</>
            }
          </Button>
        </div>

        {/* Progress indicator */}
        {loading && (
          <div className="mt-4 bg-surface-900 rounded-lg p-4 border border-brand-500/10">
            <div className="flex items-center gap-3">
              <Loader2 size={16} className="animate-spin text-brand-400 shrink-0" />
              <span className="text-brand-400 text-sm font-medium">{STEPS[stepIndex]}</span>
            </div>
            <div className="mt-3 h-1 bg-surface-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-purple-500 rounded-full transition-all duration-700"
                style={{ width: `${((stepIndex + 1) / STEPS.length) * 100}%` }}
              />
            </div>
            <p className="text-gray-600 text-xs mt-2">
              Step {stepIndex + 1} of {STEPS.length} — this takes 30–90 seconds depending on the LLM
            </p>
          </div>
        )}
      </Card>

      {/* Architecture diagram (shown before first search) */}
      {!result && !loading && (
        <Card className="border-dashed border-white/10">
          <p className="text-gray-600 text-xs uppercase tracking-widest mb-4 font-semibold">How it works</p>
          <div className="flex items-center justify-center flex-wrap gap-2 text-sm">
            {[
              ['👤', 'You'],
              ['→', ''],
              ['🔍', 'Exa Search'],
              ['→', ''],
              ['🗄️', 'ChromaDB RAG'],
              ['→', ''],
              ['⚡', 'Groq / Gemini'],
              ['→', ''],
              ['📊', 'LangGraph Pipeline'],
              ['→', ''],
              ['📝', 'Research Report'],
            ].map(([icon, label], i) =>
              label === '' ? (
                <span key={i} className="text-gray-700 font-mono">{icon}</span>
              ) : (
                <div key={i} className="flex items-center gap-1.5 bg-surface-700 rounded-lg px-3 py-2">
                  <span>{icon}</span>
                  <span className="text-gray-400 text-xs font-medium">{label}</span>
                </div>
              )
            )}
          </div>
        </Card>
      )}

      {/* Results */}
      {result && <ResearchResults data={result} />}
    </div>
  )
}
