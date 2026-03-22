import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Holdings from './pages/Holdings'
import News from './pages/News'
import Screening from './pages/Screening'
import Predictions from './pages/Predictions'

type Page = 'dashboard' | 'holdings' | 'news' | 'screening' | 'predictions'

const navItems: { id: Page; label: string; icon: string }[] = [
  { id: 'dashboard',   label: 'ダッシュボード', icon: '📊' },
  { id: 'holdings',    label: '保有株',         icon: '💼' },
  { id: 'news',        label: 'ニュース',       icon: '📰' },
  { id: 'screening',   label: '銘柄推奨',       icon: '🔍' },
  { id: 'predictions', label: 'AI予測',         icon: '🤖' },
]

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <nav style={{
        width: 220,
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border)',
        padding: '1.25rem 0.75rem',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}>
        <div style={{ marginBottom: '1.5rem', padding: '0 0.5rem' }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-blue)' }}>
            📈 株式分析
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: 2 }}>
            AI Stock Analysis
          </div>
        </div>
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-link${page === item.id ? ' active' : ''}`}
            onClick={() => setPage(item.id)}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
        <div style={{ marginTop: 'auto', padding: '0.5rem', fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
          ⚠️ AI参考情報。投資は自己責任でお願いします。
        </div>
      </nav>

      {/* Main content */}
      <main style={{ flex: 1, padding: '1.5rem', overflow: 'auto' }}>
        {page === 'dashboard'   && <Dashboard onNavigate={setPage} />}
        {page === 'holdings'    && <Holdings />}
        {page === 'news'        && <News />}
        {page === 'screening'   && <Screening />}
        {page === 'predictions' && <Predictions />}
      </main>
    </div>
  )
}
