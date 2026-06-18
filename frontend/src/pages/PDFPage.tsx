// frontend/src/pages/PDFPage.tsx
import { useState, useRef } from 'react'
import { FileText, Upload, MessageSquare, Loader2, Trash2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import { Card, SectionHeader, Button, MetricTile, Input, ProviderSelector } from '../components/ui'
import { uploadPDF, askQuestion, clearVectorStore } from '../services/api'
import type { PDFUploadResponse, LLMProvider } from '../types'

interface QAPair { q: string; a: string }

export default function PDFPage() {
  const [provider, setProvider] = useState<LLMProvider>('groq')
  const [uploading, setUploading] = useState(false)
  const [pdfResult, setPdfResult] = useState<PDFUploadResponse | null>(null)
  const [question, setQuestion] = useState('')
  const [asking, setAsking] = useState(false)
  const [qaHistory, setQaHistory] = useState<QAPair[]>([])
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are supported.')
      return
    }
    setUploading(true)
    try {
      const result = await uploadPDF(file, provider)
      setPdfResult(result)
      toast.success(`${file.name} processed — ${result.pages} pages indexed!`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Upload failed'
      toast.error(msg)
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleAsk = async () => {
    if (!question.trim()) return
    setAsking(true)
    try {
      const res = await askQuestion(question.trim(), provider)
      setQaHistory(h => [{ q: res.question, a: res.answer }, ...h])
      setQuestion('')
    } catch {
      toast.error('Failed to get answer.')
    } finally {
      setAsking(false)
    }
  }

  const handleClearStore = async () => {
    await clearVectorStore()
    setPdfResult(null)
    setQaHistory([])
    toast.success('Knowledge base cleared.')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
            <FileText size={22} className="text-brand-400" />
            PDF Assistant
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Upload PDFs to index them into ChromaDB, then ask questions using RAG
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ProviderSelector value={provider} onChange={v => setProvider(v as LLMProvider)} />
          <Button variant="danger" onClick={handleClearStore}>
            <Trash2 size={14} /> Clear KB
          </Button>
        </div>
      </div>

      {/* Drop zone */}
      <Card>
        <div
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
            dragging
              ? 'border-brand-500 bg-brand-500/5'
              : 'border-white/10 hover:border-brand-500/40 hover:bg-white/2'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 size={36} className="animate-spin text-brand-400" />
              <p className="text-gray-400 text-sm">Processing PDF — extracting text and indexing…</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload size={36} className="text-gray-600" />
              <p className="text-gray-400 text-sm">
                Drag & drop a PDF here, or <span className="text-brand-400">click to browse</span>
              </p>
              <p className="text-gray-600 text-xs">Max 50 MB</p>
            </div>
          )}
        </div>
      </Card>

      {/* PDF result */}
      {pdfResult && (
        <Card>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <MetricTile label="Pages" value={pdfResult.pages} icon="📄" />
            <MetricTile label="Chunks Indexed" value={pdfResult.chunks} icon="🧩" />
            <MetricTile label="Status" value="Ready" icon="✅" />
          </div>
          <SectionHeader icon="📋" title={`Summary — ${pdfResult.filename}`} />
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="text-gray-300 leading-relaxed mb-2">{children}</p>,
                strong: ({ children }) => <strong className="text-gray-100">{children}</strong>,
                li: ({ children }) => <li className="text-gray-300 mb-1">{children}</li>,
                h1: ({ children }) => <h1 className="text-gray-100 text-lg font-bold mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-gray-100 font-bold mb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-brand-400 font-semibold mb-1">{children}</h3>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
              }}
            >{pdfResult.summary}</ReactMarkdown>
          </div>
        </Card>
      )}

      {/* Q&A */}
      <Card>
        <SectionHeader icon="💬" title="Ask Questions (RAG)" />
        <div className="flex gap-2">
          <Input
            value={question}
            onChange={setQuestion}
            placeholder="What does the document say about…?"
            onKeyDown={e => e.key === 'Enter' && !asking && handleAsk()}
            className="flex-1"
          />
          <Button onClick={handleAsk} disabled={asking || !question.trim()}>
            {asking
              ? <><Loader2 size={14} className="animate-spin" /> Thinking…</>
              : <><MessageSquare size={14} /> Ask</>
            }
          </Button>
        </div>

        {qaHistory.length > 0 && (
          <div className="mt-4 space-y-4">
            {qaHistory.map((item, i) => (
              <div key={i} className="space-y-2">
                <div className="bg-surface-900 rounded-lg px-4 py-3">
                  <p className="text-xs text-gray-500 mb-1">Question</p>
                  <p className="text-gray-200 text-sm">{item.q}</p>
                </div>
                <div className="bg-brand-500/5 border border-brand-500/15 rounded-lg px-4 py-3">
                  <p className="text-xs text-brand-500 mb-1">Answer</p>
                  <p className="text-gray-300 text-sm leading-relaxed">{item.a}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
