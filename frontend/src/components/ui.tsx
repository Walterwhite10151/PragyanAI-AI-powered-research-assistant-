// frontend/src/components/ui.tsx
import { type ReactNode } from 'react'
import { clsx } from 'clsx'

// ── Card ──────────────────────────────────────────────────────────────────────
export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={clsx(
      'bg-surface-800 border border-brand-500/20 rounded-xl p-5',
      className
    )}>
      {children}
    </div>
  )
}

// ── SectionHeader ─────────────────────────────────────────────────────────────
export function SectionHeader({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="text-brand-400">{icon}</span>
      <h3 className="text-brand-400 font-bold uppercase tracking-widest text-sm">{title}</h3>
    </div>
  )
}

// ── Badge ─────────────────────────────────────────────────────────────────────
export function Badge({
  children,
  variant = 'default',
}: {
  children: ReactNode
  variant?: 'default' | 'success' | 'error' | 'warning' | 'purple'
}) {
  const styles = {
    default: 'bg-brand-500/10 text-brand-400 border-brand-500/20',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    error:   'bg-red-500/10 text-red-400 border-red-500/20',
    warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    purple:  'bg-purple-500/10 text-purple-400 border-purple-500/20',
  }
  return (
    <span className={clsx(
      'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border',
      styles[variant]
    )}>
      {children}
    </span>
  )
}

// ── Button ────────────────────────────────────────────────────────────────────
export function Button({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  className,
  type = 'button',
}: {
  children: ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  disabled?: boolean
  className?: string
  type?: 'button' | 'submit'
}) {
  const styles = {
    primary:   'bg-brand-500 hover:bg-brand-600 text-white',
    secondary: 'bg-surface-700 hover:bg-surface-600 text-gray-200 border border-white/10',
    danger:    'bg-red-600/80 hover:bg-red-600 text-white',
    ghost:     'hover:bg-white/5 text-gray-400 hover:text-gray-200',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        styles[variant],
        className
      )}
    >
      {children}
    </button>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const s = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }
  return (
    <div className={clsx(
      'animate-spin rounded-full border-2 border-surface-600 border-t-brand-400',
      s[size]
    )} />
  )
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: string; label: string; icon?: string }[]
  active: string
  onChange: (id: string) => void
}) {
  return (
    <div className="flex gap-1 bg-surface-900 p-1 rounded-xl border border-white/5 flex-wrap">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={clsx(
            'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all',
            active === tab.id
              ? 'bg-brand-500/20 text-brand-400 shadow-sm'
              : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
          )}
        >
          {tab.icon && <span>{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  )
}

// ── MetricTile ────────────────────────────────────────────────────────────────
export function MetricTile({ label, value, icon }: { label: string; value: string | number; icon?: string }) {
  return (
    <div className="bg-surface-700 rounded-lg px-4 py-3 border-l-2 border-brand-500">
      <div className="text-brand-400 font-bold text-xl">{icon} {value}</div>
      <div className="text-gray-500 text-xs uppercase tracking-wider mt-0.5">{label}</div>
    </div>
  )
}

// ── Input ─────────────────────────────────────────────────────────────────────
export function Input({
  value,
  onChange,
  placeholder,
  className,
  onKeyDown,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  className?: string
  onKeyDown?: (e: React.KeyboardEvent) => void
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      onKeyDown={onKeyDown}
      className={clsx(
        'w-full bg-surface-900 border border-white/10 rounded-lg px-4 py-3',
        'text-gray-100 placeholder-gray-600',
        'focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/30',
        'transition-all text-sm',
        className
      )}
    />
  )
}

// ── ProviderSelector ──────────────────────────────────────────────────────────
export function ProviderSelector({
  value,
  onChange,
}: {
  value: string
  onChange: (v: string) => void
}) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className="bg-surface-900 border border-white/10 rounded-lg px-3 py-3 text-gray-200 text-sm focus:outline-none focus:border-brand-500/50 cursor-pointer"
    >
      <option value="groq">⚡ Groq (Fast)</option>
      <option value="gemini">✨ Gemini</option>
    </select>
  )
}
