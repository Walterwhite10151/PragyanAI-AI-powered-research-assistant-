// frontend/src/services/api.ts
import axios from 'axios'
import type {
  ResearchResponse, PDFUploadResponse, QuestionResponse,
  SessionMeta, SessionDetail, StatusResponse, Preferences,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 2400_000, // 40 min — five sequential LLM calls add up once they're actually succeeding
})

// ── Research ───────────────────────────────────────────────────────────────────

export const runResearch = (topic: string, provider: string): Promise<ResearchResponse> =>
  api.post('/research', { topic, provider }).then(r => r.data)

export const getStatus = (): Promise<StatusResponse> =>
  api.get('/status').then(r => r.data)

// ── PDF ────────────────────────────────────────────────────────────────────────

export const uploadPDF = (file: File, provider: string): Promise<PDFUploadResponse> => {
  const form = new FormData()
  form.append('file', file)
  form.append('provider', provider)
  return api.post('/pdf/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export const askQuestion = (question: string, provider: string): Promise<QuestionResponse> =>
  api.post('/pdf/question', { question, provider }).then(r => r.data)

export const getVectorStoreStats = () =>
  api.get('/pdf/stats').then(r => r.data)

export const clearVectorStore = () =>
  api.delete('/pdf/clear').then(r => r.data)

// ── History ────────────────────────────────────────────────────────────────────

export const getHistory = (): Promise<SessionMeta[]> =>
  api.get('/history').then(r => r.data)

export const getSessionDetail = (id: string): Promise<SessionDetail> =>
  api.get(`/history/${id}`).then(r => r.data)

export const clearHistory = () =>
  api.delete('/history').then(r => r.data)

// ── Preferences ────────────────────────────────────────────────────────────────

export const getPreferences = (): Promise<{ preferences: Preferences }> =>
  api.get('/preferences').then(r => r.data)

export const updatePreferences = (prefs: Partial<Preferences>): Promise<{ preferences: Preferences }> =>
  api.put('/preferences', prefs).then(r => r.data)

export const resetPreferences = (): Promise<{ preferences: Preferences }> =>
  api.delete('/preferences/reset').then(r => r.data)