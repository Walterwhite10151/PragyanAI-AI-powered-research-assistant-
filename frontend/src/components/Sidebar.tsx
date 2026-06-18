// frontend/src/components/Sidebar.tsx
import { NavLink } from 'react-router-dom'
import { Search, FileText, Clock, Settings, Zap } from 'lucide-react'
import { clsx } from 'clsx'

const links = [
  { to: '/',         icon: Search,   label: 'Research'     },
  { to: '/pdf',      icon: FileText, label: 'PDF Assistant' },
  { to: '/history',  icon: Clock,    label: 'History'      },
  { to: '/settings', icon: Settings, label: 'Settings'     },
]

export function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-surface-800 border-r border-white/5 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="px-5 py-6 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand-500/20 flex items-center justify-center text-brand-400">
            🔬
          </div>
          <div>
            <div className="font-bold text-gray-100 text-sm leading-tight">PragyanAI</div>
            <div className="text-gray-500 text-xs">Agent v2</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-brand-500/15 text-brand-400'
                  : 'text-gray-500 hover:text-gray-200 hover:bg-white/5'
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/5">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <Zap size={12} className="text-brand-500" />
          <span>Exa + Groq/Gemini</span>
        </div>
        <div className="text-xs text-gray-700 mt-0.5">LangGraph · ChromaDB</div>
      </div>
    </aside>
  )
}
