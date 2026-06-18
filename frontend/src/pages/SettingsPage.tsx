// frontend/src/pages/SettingsPage.tsx
import { useEffect, useState } from 'react'
import { Settings, CheckCircle, XCircle, RefreshCw, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, SectionHeader, Button, Badge, MetricTile } from '../components/ui'
import {
  getStatus, getPreferences, updatePreferences,
  resetPreferences, clearVectorStore,
} from '../services/api'
import type { StatusResponse, Preferences } from '../types'

export default function SettingsPage() {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [prefs, setPrefs] = useState<Preferences | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getStatus().then(setStatus).catch(() => toast.error('Could not reach backend.'))
    getPreferences().then(r => setPrefs(r.preferences)).catch(() => {})
  }, [])

  const savePrefs = async (updates: Partial<Preferences>) => {
    if (!prefs) return
    setSaving(true)
    try {
      const r = await updatePreferences(updates)
      setPrefs(r.preferences)
      toast.success('Preferences saved.')
    } catch { toast.error('Failed to save.') }
    finally { setSaving(false) }
  }

  const handleReset = async () => {
    const r = await resetPreferences()
    setPrefs(r.preferences)
    toast.success('Preferences reset.')
  }

  const handleClearVS = async () => {
    if (!confirm('Clear all indexed documents?')) return
    await clearVectorStore()
    if (status) setStatus({ ...status, vector_store_chunks: 0 })
    toast.success('Vector store cleared.')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
          <Settings size={22} className="text-brand-400" />
          Settings
        </h1>
        <p className="text-gray-500 text-sm mt-1">System status and user preferences</p>
      </div>

      {/* Status */}
      {status && (
        <Card>
          <SectionHeader icon="🔌" title="System Status" />
          <div className="grid grid-cols-2 gap-3 mb-4">
            <MetricTile
              label="Backend"
              value={status.status === 'ok' ? 'Online' : 'Error'}
              icon={status.status === 'ok' ? '✅' : '❌'}
            />
            <MetricTile
              label="Vector Store"
              value={`${status.vector_store_chunks} chunks`}
              icon="🗄️"
            />
          </div>

          {/* Exa */}
          <div className="mb-4">
            <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">Exa Search</p>
            <div className="flex items-center gap-2">
              {status.exa_configured ? (
                <><CheckCircle size={16} className="text-brand-400" /><span className="text-gray-300 text-sm">API key configured</span></>
              ) : (
                <><XCircle size={16} className="text-red-400" /><span className="text-gray-400 text-sm">EXA_API_KEY not set — <a href="https://exa.ai" target="_blank" rel="noopener noreferrer" className="text-brand-400 underline">get one free</a></span></>
              )}
            </div>
          </div>

          {/* LLM Providers */}
          <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">LLM Providers</p>
          <div className="space-y-2">
            {status.providers.map(p => (
              <div key={p.id} className="flex items-center justify-between bg-surface-700 rounded-lg px-4 py-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-200 font-medium text-sm">{p.name}</span>
                    <Badge variant="default">{p.model}</Badge>
                    {p.configured
                      ? <Badge variant="success">Configured</Badge>
                      : <Badge variant="error">Key missing</Badge>
                    }
                  </div>
                  <p className="text-gray-500 text-xs mt-0.5">{p.description}</p>
                </div>
                {p.configured
                  ? <CheckCircle size={18} className="text-brand-400" />
                  : <XCircle size={18} className="text-red-400" />
                }
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Preferences */}
      {prefs && (
        <Card>
          <SectionHeader icon="🎨" title="Preferences" />
          <div className="space-y-4">
            <div>
              <label className="text-gray-400 text-sm mb-1.5 block">Default LLM Provider</label>
              <select
                value={prefs.default_provider}
                onChange={e => savePrefs({ default_provider: e.target.value })}
                className="bg-surface-900 border border-white/10 rounded-lg px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-brand-500/50"
              >
                <option value="groq">⚡ Groq</option>
                <option value="gemini">✨ Gemini</option>
              </select>
            </div>

            <div>
              <label className="text-gray-400 text-sm mb-1.5 block">Research Depth</label>
              <select
                value={prefs.research_depth}
                onChange={e => savePrefs({ research_depth: e.target.value })}
                className="bg-surface-900 border border-white/10 rounded-lg px-3 py-2 text-gray-200 text-sm focus:outline-none focus:border-brand-500/50"
              >
                <option value="quick">Quick</option>
                <option value="standard">Standard</option>
                <option value="deep">Deep</option>
              </select>
            </div>

            <div className="flex items-center justify-between py-2 border-t border-white/5">
              <div>
                <p className="text-gray-300 text-sm font-medium">Auto-search YouTube</p>
                <p className="text-gray-500 text-xs">Find educational videos for each topic</p>
              </div>
              <button
                onClick={() => savePrefs({ auto_youtube: !prefs.auto_youtube })}
                className={`w-11 h-6 rounded-full transition-colors ${prefs.auto_youtube ? 'bg-brand-500' : 'bg-surface-600'}`}
              >
                <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform mx-1 ${prefs.auto_youtube ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>

            <div className="flex items-center justify-between py-2 border-t border-white/5">
              <div>
                <p className="text-gray-300 text-sm font-medium">Show Sources</p>
                <p className="text-gray-500 text-xs">Display Exa source links in results</p>
              </div>
              <button
                onClick={() => savePrefs({ show_sources: !prefs.show_sources })}
                className={`w-11 h-6 rounded-full transition-colors ${prefs.show_sources ? 'bg-brand-500' : 'bg-surface-600'}`}
              >
                <div className={`w-4 h-4 bg-white rounded-full shadow transition-transform mx-1 ${prefs.show_sources ? 'translate-x-5' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>

          <div className="flex gap-2 mt-4 pt-4 border-t border-white/5">
            <Button variant="secondary" onClick={handleReset} disabled={saving}>
              <RefreshCw size={14} /> Reset Defaults
            </Button>
          </div>
        </Card>
      )}

      {/* Danger zone */}
      <Card className="border-red-500/20">
        <SectionHeader icon="⚠️" title="Danger Zone" />
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-300 text-sm font-medium">Clear Vector Store</p>
            <p className="text-gray-500 text-xs">Remove all indexed PDF and research content from ChromaDB</p>
          </div>
          <Button variant="danger" onClick={handleClearVS}>
            <Trash2 size={14} /> Clear
          </Button>
        </div>
      </Card>
    </div>
  )
}
