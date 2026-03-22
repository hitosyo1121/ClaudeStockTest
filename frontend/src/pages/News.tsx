import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { newsApi, type NewsItem } from '../api/client'

function RelBadge({ rel }: { rel: string }) {
  if (rel === 'macro') return <span style={{ fontSize: '0.7rem', color: 'var(--accent-purple)', background: 'rgba(188,140,255,0.1)', border: '1px solid rgba(188,140,255,0.3)', borderRadius: 4, padding: '0.1rem 0.4rem' }}>マクロ</span>
  if (rel === 'holding') return <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', background: 'rgba(88,166,255,0.1)', border: '1px solid rgba(88,166,255,0.3)', borderRadius: 4, padding: '0.1rem 0.4rem' }}>保有株</span>
  return <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', borderRadius: 4, padding: '0.1rem 0.4rem' }}>市場</span>
}

function DirectionBadge({ dir }: { dir: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    '上昇': { label: '▲ 上昇', cls: 'positive' },
    '下落': { label: '▼ 下落', cls: 'negative' },
    '横ばい': { label: '→ 横ばい', cls: 'neutral' },
    'bullish': { label: '▲ 強気', cls: 'positive' },
    'bearish': { label: '▼ 弱気', cls: 'negative' },
    'neutral': { label: '→ 中立', cls: 'neutral' },
  }
  const m = map[dir] || { label: dir, cls: 'neutral' }
  return <span className={m.cls} style={{ fontWeight: 600 }}>{m.label}</span>
}

export default function News() {
  const [tab, setTab] = useState<'today' | 'tomorrow'>('today')
  const qc = useQueryClient()

  const { data: todayData, isLoading: todayLoading } = useQuery({
    queryKey: ['news-today'],
    queryFn: newsApi.today,
    staleTime: 300000,
  })

  const { data: tomorrowData, isLoading: tomorrowLoading } = useQuery({
    queryKey: ['news-tomorrow'],
    queryFn: newsApi.tomorrow,
    staleTime: 300000,
    enabled: tab === 'tomorrow',
  })

  const refreshMut = useMutation({
    mutationFn: newsApi.refresh,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['news-today'] }),
  })

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>📰 ニュース</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>市場ニュース・明日の見通し</p>
        </div>
        <button className="btn-ghost" onClick={() => refreshMut.mutate()} disabled={refreshMut.isPending}>
          {refreshMut.isPending ? '更新中...' : '🔄 更新'}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: 0 }}>
        {(['today', 'tomorrow'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '0.5rem 1rem', background: 'none', border: 'none', cursor: 'pointer',
            fontSize: '0.875rem', fontWeight: tab === t ? 600 : 400,
            color: tab === t ? 'var(--accent-blue)' : 'var(--text-secondary)',
            borderBottom: tab === t ? '2px solid var(--accent-blue)' : '2px solid transparent',
            marginBottom: -1,
          }}>
            {t === 'today' ? '📅 今日のニュース' : '🔮 明日の見通し（AI）'}
          </button>
        ))}
      </div>

      {tab === 'today' && (
        <div>
          {todayLoading && <div style={{ textAlign: 'center', padding: '3rem' }}><div className="spinner" /></div>}
          {todayData && (
            <>
              {todayData.market_summary && (
                <div className="card" style={{ marginBottom: '1rem', borderLeft: '3px solid var(--accent-blue)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--accent-blue)', fontWeight: 600, marginBottom: '0.5rem' }}>AI市場サマリー</div>
                  <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.6 }}>{todayData.market_summary}</p>
                </div>
              )}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                {todayData.items.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>ニュースを取得できませんでした</div>
                ) : todayData.items.map((item: NewsItem) => (
                  <div key={item.id} className="card" style={{ padding: '0.875rem' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.375rem' }}>
                          <RelBadge rel={item.relevance} />
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{item.source}</span>
                        </div>
                        {item.url ? (
                          <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 500, fontSize: '0.9rem' }}>
                            {item.title}
                          </a>
                        ) : (
                          <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{item.title}</div>
                        )}
                        {item.summary && <p style={{ margin: '0.375rem 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{item.summary}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {tab === 'tomorrow' && (
        <div>
          {tomorrowLoading && <div style={{ textAlign: 'center', padding: '3rem' }}><div className="spinner" /></div>}
          {tomorrowData && (
            <div>
              {/* Overall direction */}
              <div className="card" style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 4 }}>明日の市場方向</div>
                    <div style={{ fontSize: '1.5rem' }}><DirectionBadge dir={tomorrowData.overall_direction} /></div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 4 }}>信頼度</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{((tomorrowData.confidence || 0) * 100).toFixed(0)}%</div>
                  </div>
                </div>
                {tomorrowData.summary && <p style={{ marginTop: '0.75rem', marginBottom: 0, fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>{tomorrowData.summary}</p>}
              </div>

              {/* Hourly trend */}
              {tomorrowData.hourly_trend?.length > 0 && (
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="section-title" style={{ marginBottom: '0.75rem' }}>⏰ 時間別トレンド予測</div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {tomorrowData.hourly_trend.map((h: any) => (
                      <div key={h.time_range} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8, padding: '0.5rem 0.75rem', minWidth: 100 }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{h.time_range}</div>
                        <div><DirectionBadge dir={h.trend} /></div>
                        {h.note && <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: 2 }}>{h.note}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Key factors */}
              {tomorrowData.key_factors?.length > 0 && (
                <div className="card" style={{ marginBottom: '1rem' }}>
                  <div className="section-title" style={{ marginBottom: '0.75rem' }}>📋 主要要因</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {tomorrowData.key_factors.map((f: any, i: number) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                        <span style={{ color: f.impact === 'positive' ? 'var(--accent-green)' : f.impact === 'negative' ? 'var(--accent-red)' : 'var(--text-secondary)', marginTop: 2 }}>
                          {f.impact === 'positive' ? '▲' : f.impact === 'negative' ? '▼' : '→'}
                        </span>
                        <span style={{ fontSize: '0.875rem' }}>{f.factor}</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginLeft: 'auto', flexShrink: 0 }}>{f.magnitude === 'high' ? '高' : f.magnitude === 'medium' ? '中' : '低'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                {tomorrowData.sector_outlook?.length > 0 && (
                  <div className="card">
                    <div className="section-title" style={{ marginBottom: '0.75rem' }}>🏭 セクター別見通し</div>
                    {tomorrowData.sector_outlook.map((s: any, i: number) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid rgba(48,54,61,0.5)' }}>
                        <span style={{ fontSize: '0.875rem' }}>{s.sector}</span>
                        <DirectionBadge dir={s.direction} />
                      </div>
                    ))}
                  </div>
                )}
                {tomorrowData.risk_factors?.length > 0 && (
                  <div className="card">
                    <div className="section-title" style={{ marginBottom: '0.75rem' }}>⚠️ リスク要因</div>
                    {tomorrowData.risk_factors.map((r: string, i: number) => (
                      <div key={i} style={{ fontSize: '0.875rem', padding: '0.3rem 0', borderBottom: '1px solid rgba(48,54,61,0.5)', color: 'var(--accent-yellow)' }}>
                        • {r}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                ⚠️ AI生成による参考情報です。投資判断は必ずご自身でお行いください。
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
