// frontend/src/types/index.ts

export interface SourceItem {
  title: string
  url: string
  snippet: string
  published_date?: string
  score: number
}

export interface VideoItem {
  title: string
  channel: string
  url: string
  thumbnail: string
  duration: string
  views: string
}

export interface ResearchResponse {
  topic: string
  provider: string
  overview: string
  key_concepts: string
  important_facts: string
  roadmap: string
  summary: string
  sources: SourceItem[]
  youtube_videos: VideoItem[]
  errors: string[]
  elapsed_seconds: number
  session_id: string
}

export interface PDFUploadResponse {
  filename: string
  pages: number
  chunks: number
  summary: string
  error?: string
}

export interface QuestionResponse {
  question: string
  answer: string
}

export interface SessionMeta {
  session_id: string
  topic: string
  provider: string
  timestamp: string
}

export interface SessionDetail extends SessionMeta {
  result: Record<string, unknown>
}

export interface ProviderInfo {
  id: string
  name: string
  model: string
  configured: boolean
  description: string
}

export interface StatusResponse {
  status: string
  providers: ProviderInfo[]
  vector_store_chunks: number
  exa_configured: boolean
}

export interface Preferences {
  default_provider: string
  research_depth: string
  auto_youtube: boolean
  show_sources: boolean
  theme: string
}

export type LLMProvider = 'groq' | 'gemini'
