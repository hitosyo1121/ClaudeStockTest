import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { screeningApi, type ScreeningResult } from '../api/client'

function ScoreBar({ score }: { score?: number }) {
  if (score == null) return null
  const pct = Math.min(score, 100)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <div style={{ flex: 1, height: 6, background: 'var(--bg-secondary)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: pct >= 70 ? 'var(--accent-green)' : pct >= 50 ? 'var(--accent-yellow)' : 'var(--accent-blue)', borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', minWidth: 28 }}>{pct}</span>
    </div>
  )
}

export default function Screening() {
  const qc = useQueryClient()
  const [running, setRunning] = useState(false)
  const [tab, setTab] = useState<'buy' | 'sell' | 'watch'>('buy')

  const { data: results, isLoading } = useQuery({
    queryKey: ['screening'],
    queryFn: screeningApi.results,
  })

  const runMut = useMutation({
    mutationFn: screeningApi.run,
    onMutate: () => setRunning(true),
    onSettled: () => setRunning(false),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['screening'] }),
  })

  const tabs = [
    { id: 'buy', label: '🟢 購入推奨', count: results?.buy_recommendations.length || 0 },
    { id: 'sell', label: '🔴 売却シグナル', count: results?.sell_signals.length || 0 },
    { id: 'watch', label: '🟡 ウォッチリスト', count: results?.watch_list.length || 0 },
  ]

  const currentList: ScreeningResult[] =
    tab === 'buy' ? (results?.buy_recommendations || []) :
    tab === 'sell' ? (results?.sell_signals || []) :
    (results?.watch_list || [])

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>🔍 銘柄スクリーニング</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>
            東証スクリーニング基準によるAI銘柄推奨
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={() => runMut.mutate()}
          disabled={running}
        >
          {running ? '⏳ スクリーニング実行中...' : '▶ スクリーニング実行'}
        </button>
      </div>

      {/* Disclaimer */}
      <div style={{ background: 'rgba(210,153,34,0.1)', border: '1px solid rgba(210,153,34,0.3)', borderRadius: 8, padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.8rem', color: 'var(--accent-yellow)' }}>
        ⚠️ 本スクリーニング結果はAIによる参考情報です。投資の最終判断はご自身でお行いください。
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id as any)} style={{
            padding: '0.5rem 1rem', background: 'none', border: 'none', cursor: 'pointer',
            fontSize: '0.875rem', fontWeight: tab === t.id ? 600 : 400,
            color: tab === t.id ? 'var(--accent-blue)' : 'var(--text-secondary)',
            borderBottom: tab === t.id ? '2px solid var(--accent-blue)' : '2px solid transparent',
            marginBottom: -1,
          }}>
            {t.label} ({t.count})
          </button>
        ))}
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}><div className="spinner" /></div>
      ) : currentList.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
          <div>「スクリーニング実行」をクリックして銘柄を分析してください</div>
          <div style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>※ 初回は時間がかかる場合があります</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {currentList.map((r: ScreeningResult, idx: number) => (
            <div key={r.code} className="card">
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem' }}>{r.name}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{r.code}</span>
                    <span className={`badge-${r.action}`}>{r.action === 'buy' ? 'BUY' : r.action === 'sell' ? 'SELL' : 'WATCH'}</span>
                    {tab === 'buy' && <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>#{idx+1}</span>}
                  </div>

                  {r.score != null && (
                    <div style={{ marginBottom: '0.5rem', maxWidth: 200 }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: 3 }}>スクリーニングスコア</div>
                      <ScoreBar score={r.score} />
                    </div>
                  )}

                  {r.reasons && r.reasons.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginTop: '0.375rem' }}>
                      {r.reasons.map((reason: string, i: number) => (
                        <span key={i} style={{
                          fontSize: '0.75rem',
                          padding: '0.2rem 0.5rem',
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border)',
                          borderRadius: 4,
                          color: 'var(--text-secondary)',
                        }}>
                          {reason}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {r.price_at_run && (
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>スクリーニング時株価</div>
                    <div style={{ fontWeight: 600 }}>¥{r.price_at_run.toLocaleString()}</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
