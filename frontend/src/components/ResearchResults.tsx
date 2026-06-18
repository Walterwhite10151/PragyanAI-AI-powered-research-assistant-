// frontend/src/components/ResearchResults.tsx
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ExternalLink } from 'lucide-react'
import { Card, SectionHeader, MetricTile, Tabs, Badge } from './ui'
import type { ResearchResponse } from '../types'

const TABS = [
  { id: 'overview',    label: 'Overview',      icon: '📖' },
  { id: 'concepts',   label: 'Key Concepts',  icon: '🔑' },
  { id: 'facts',      label: 'Facts',         icon: '📊' },
  { id: 'roadmap',    label: 'Roadmap',       icon: '🗺️' },
  { id: 'summary',    label: 'Summary',       icon: '📝' },
  { id: 'videos',     label: 'Videos',        icon: '🎬' },
  { id: 'sources',    label: 'Sources',       icon: '🔗' },
]

interface Props { data: ResearchResponse }

export function ResearchResults({ data }: Props) {
  const [tab, setTab] = useState('overview')

  const md = (text: string) => (
    <ReactMarkdown remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="text-gray-300 leading-relaxed mb-3">{children}</p>,
        strong: ({ children }) => <strong className="text-gray-100 font-semibold">{children}</strong>,
        li: ({ children }) => <li className="text-gray-300 mb-1">{children}</li>,
        h1: ({ children }) => <h1 className="text-gray-100 text-xl font-bold mb-3 mt-4">{children}</h1>,
        h2: ({ children }) => <h2 className="text-gray-100 text-lg font-bold mb-2 mt-3">{children}</h2>,
        h3: ({ children }) => <h3 className="text-brand-400 font-semibold mb-2 mt-3">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-3">{children}</ol>,
      }}
    >{text}</ReactMarkdown>
  )

  return (
    <div className="space-y-4">
      {/* Metrics row */}
      <div className="grid grid-cols-3 gap-3">
        <MetricTile label="Time" value={`${data.elapsed_seconds}s`} icon="⏱️" />
        <MetricTile label="Sources" value={data.sources.length} icon="🌐" />
        <MetricTile label="Provider" value={data.provider.toUpperCase()} icon="⚡" />
      </div>

      {/* Errors */}
      {data.errors.length > 0 && (
        <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-3 space-y-1">
          {data.errors.map((e, i) => (
            <p key={i} className="text-yellow-400 text-sm">⚠️ {e}</p>
          ))}
        </div>
      )}

      {/* Tab navigation */}
      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {/* Tab content */}
      <Card>
        {tab === 'overview' && (
          <>
            <SectionHeader icon="📖" title="Overview" />
            {md(data.overview || '_No overview generated._')}
          </>
        )}

        {tab === 'concepts' && (
          <>
            <SectionHeader icon="🔑" title="Key Concepts" />
            {md(data.key_concepts || '_No concepts generated._')}
          </>
        )}

        {tab === 'facts' && (
          <>
            <SectionHeader icon="📊" title="Important Facts" />
            {md(data.important_facts || '_No facts generated._')}
          </>
        )}

        {tab === 'roadmap' && (
          <>
            <SectionHeader icon="🗺️" title="Learning Roadmap" />
            {md(data.roadmap || '_No roadmap generated._')}
          </>
        )}

        {tab === 'summary' && (
          <>
            <SectionHeader icon="📝" title="Final Summary" />
            <div className="bg-brand-500/5 border border-brand-500/20 rounded-lg p-4">
              {md(data.summary || '_No summary generated._')}
            </div>
          </>
        )}

        {tab === 'videos' && (
          <>
            <SectionHeader icon="🎬" title="Recommended Videos" />
            {data.youtube_videos.length === 0 ? (
              <p className="text-gray-500 text-sm">No videos found.</p>
            ) : (
              <div className="space-y-3">
                {data.youtube_videos.map((v, i) => (
                  <div key={i} className="flex gap-3 bg-surface-700 rounded-lg p-3 hover:bg-surface-600 transition-colors">
                    {v.thumbnail && (
                      <img src={v.thumbnail} alt={v.title} className="w-28 h-16 object-cover rounded" />
                    )}
                    <div className="flex-1 min-w-0">
                      <a href={v.url} target="_blank" rel="noopener noreferrer"
                        className="text-gray-100 font-medium text-sm hover:text-brand-400 transition-colors line-clamp-2">
                        {v.title}
                      </a>
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
                        <span>📺 {v.channel}</span>
                        <span>⏱️ {v.duration}</span>
                        <span>👁️ {v.views}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {tab === 'sources' && (
          <>
            <SectionHeader icon="🔗" title="Exa Sources" />
            <div className="space-y-3">
              {data.sources.map((s, i) => (
                <div key={i} className="bg-surface-700 rounded-lg p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-gray-500 text-xs font-mono">[{i + 1}]</span>
                        {s.published_date && (
                          <Badge variant="default">{s.published_date.slice(0, 10)}</Badge>
                        )}
                        {s.score > 0 && (
                          <Badge variant="purple">score: {s.score.toFixed(3)}</Badge>
                        )}
                      </div>
                      <a href={s.url} target="_blank" rel="noopener noreferrer"
                        className="text-gray-200 font-medium text-sm hover:text-brand-400 transition-colors">
                        {s.title}
                      </a>
                      <p className="text-gray-500 text-xs mt-1 line-clamp-2">{s.snippet}</p>
                    </div>
                    <a href={s.url} target="_blank" rel="noopener noreferrer"
                      className="text-gray-600 hover:text-brand-400 transition-colors shrink-0">
                      <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
