// frontend/src/pages/HistoryPage.tsx
import { useEffect, useState } from 'react'
import { Clock, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import { Card, Button, Badge } from '../components/ui'
import { getHistory, getSessionDetail, clearHistory } from '../services/api'
import type { SessionMeta, SessionDetail } from '../types'

export default function HistoryPage() {
  const [sessions, setSessions] = useState<SessionMeta[]>([])
  const [expanded, setExpanded] = useState<string | null>(null)
  const [detail, setDetail] = useState<SessionDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  const loadHistory = async () => {
    try {
      setSessions(await getHistory())
    } catch {
      toast.error('Failed to load history.')
    }
  }

  useEffect(() => { loadHistory() }, [])

  const toggleSession = async (id: string) => {
    if (expanded === id) { setExpanded(null); setDetail(null); return }
    setExpanded(id)
    setLoadingDetail(true)
    try {
      setDetail(await getSessionDetail(id))
    } catch {
      toast.error('Could not load session.')
    } finally {
      setLoadingDetail(false)
    }
  }

  const handleClear = async () => {
    if (!confirm('Delete all research history?')) return
    await clearHistory()
    setSessions([])
    setExpanded(null)
    setDetail(null)
    toast.success('History cleared.')
  }

  const providerBadge = (p: string) =>
    p === 'gemini' ? <Badge variant="purple">Gemini</Badge> : <Badge variant="success">Groq</Badge>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
            <Clock size={22} className="text-brand-400" />
            Research History
          </h1>
          <p className="text-gray-500 text-sm mt-1">{sessions.length} sessions saved locally</p>
        </div>
        {sessions.length > 0 && (
          <Button variant="danger" onClick={handleClear}>
            <Trash2 size={14} /> Clear All
          </Button>
        )}
      </div>

      {sessions.length === 0 ? (
        <Card className="text-center py-12">
          <Clock size={36} className="text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500">No research sessions yet.</p>
          <p className="text-gray-600 text-sm mt-1">Run a research query to see it here.</p>
        </Card>
      ) : (
        <div className="space-y-2">
          {sessions.map(s => (
            <Card key={s.session_id} className="cursor-pointer hover:border-brand-500/30 transition-colors p-0 overflow-hidden">
              <button
                className="w-full px-5 py-4 flex items-center justify-between text-left"
                onClick={() => toggleSession(s.session_id)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-gray-600 font-mono text-xs">[{s.session_id}]</span>
                  <span className="text-gray-200 font-medium">{s.topic}</span>
                  {providerBadge(s.provider)}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-gray-600 text-xs">
                    {new Date(s.timestamp).toLocaleString()}
                  </span>
                  {expanded === s.session_id
                    ? <ChevronUp size={14} className="text-gray-500" />
                    : <ChevronDown size={14} className="text-gray-500" />
                  }
                </div>
              </button>

              {expanded === s.session_id && (
                <div className="border-t border-white/5 px-5 pb-5 pt-4">
                  {loadingDetail ? (
                    <p className="text-gray-500 text-sm animate-pulse">Loading session…</p>
                  ) : detail && (
                    <div className="space-y-4">
                      {(['overview', 'key_concepts', 'summary'] as const).map(key => {
                        const val = (detail.result as Record<string, string>)[key]
                        if (!val) return null
                        const labels: Record<string, string> = {
                          overview: '📖 Overview',
                          key_concepts: '🔑 Key Concepts',
                          summary: '📝 Summary',
                        }
                        return (
                          <div key={key}>
                            <p className="text-brand-400 text-xs font-bold uppercase tracking-widest mb-2">
                              {labels[key]}
                            </p>
                            <div className="text-gray-400 text-sm leading-relaxed line-clamp-6">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}
                                components={{
                                  p: ({ children }) => <p className="mb-1">{children}</p>,
                                  strong: ({ children }) => <strong className="text-gray-300">{children}</strong>,
                                  li: ({ children }) => <li>{children}</li>,
                                  ul: ({ children }) => <ul className="list-disc list-inside">{children}</ul>,
                                }}
                              >{val}</ReactMarkdown>
                            </div>
                          </div>
                        )
                      })}
                      {Array.isArray((detail.result as Record<string, unknown>).sources) && (
                        <div>
                          <p className="text-brand-400 text-xs font-bold uppercase tracking-widest mb-2">
                            🔗 Sources
                          </p>
                          <ul className="space-y-1">
                            {((detail.result as Record<string, Array<{title: string; url: string}>|unknown>).sources as Array<{title: string; url: string}>).map((src, i) => (
                              <li key={i} className="text-xs">
                                <a href={src.url} target="_blank" rel="noopener noreferrer"
                                  className="text-brand-400/70 hover:text-brand-400 transition-colors">
                                  {src.title || src.url}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
