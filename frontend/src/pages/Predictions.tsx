import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { predictionsApi, holdingsApi, type PortfolioPrediction, type HourlyForecast } from '../api/client'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

function DirectionIcon({ dir }: { dir: string }) {
  if (dir === 'up') return <span style={{ color: 'var(--accent-green)', fontSize: '1.5rem' }}>▲</span>
  if (dir === 'down') return <span style={{ color: 'var(--accent-red)', fontSize: '1.5rem' }}>▼</span>
  return <span style={{ color: 'var(--text-secondary)', fontSize: '1.5rem' }}>→</span>
}

function ConfBar({ value }: { value?: number }) {
  if (value == null) return null
  const pct = (value * 100).toFixed(0)
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{ flex: 1, height: 6, background: 'var(--bg-secondary)', borderRadius: 3 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{pct}%</span>
    </div>
  )
}

function HourlyChart({ data, currentPrice }: { data: HourlyForecast[]; currentPrice?: number }) {
  if (!data || data.length === 0) return <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>時間別データなし</div>
  const chartData = data.map(d => ({ hour: d.hour, price: d.estimated_price }))
  const prices = data.map(d => d.estimated_price)
  const minP = Math.min(...prices) * 0.998
  const maxP = Math.max(...prices) * 1.002

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
        <defs>
          <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#58a6ff" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#58a6ff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="hour" tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
        <YAxis domain={[minP, maxP]} tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} tickFormatter={v => `¥${v.toLocaleString()}`} />
        <Tooltip formatter={(v: any) => [`¥${v.toLocaleString()}`, '予測株価']} labelFormatter={l => `${l}`} contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6 }} />
        {currentPrice && <ReferenceLine y={currentPrice} stroke="var(--accent-yellow)" strokeDasharray="4 4" label={{ value: '現在値', fill: 'var(--accent-yellow)', fontSize: 11 }} />}
        <Area type="monotone" dataKey="price" stroke="#58a6ff" fill="url(#priceGrad)" strokeWidth={2} dot={{ fill: '#58a6ff', r: 3 }} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

function PredCard({ pp, onGenerate }: { pp: PortfolioPrediction; onGenerate: (code: string) => void }) {
  const p = pp.prediction
  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div>
          <span style={{ fontWeight: 700 }}>{pp.name}</span>
          <span style={{ marginLeft: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{pp.code}</span>
          {pp.current_price && <span style={{ marginLeft: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>¥{pp.current_price.toLocaleString()}</span>}
        </div>
        <button className="btn-ghost" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => onGenerate(pp.code)}>
          🤖 予測生成
        </button>
      </div>

      {!p ? (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', padding: '1rem 0' }}>
          「予測生成」をクリックしてAI予測を生成してください
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <DirectionIcon dir={p.direction} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>明日の方向</div>
                <div style={{ fontWeight: 600 }}>
                  {p.direction === 'up' ? '上昇' : p.direction === 'down' ? '下落' : '横ばい'}
                </div>
              </div>
            </div>
            <div style={{ minWidth: 140 }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: 3 }}>信頼度</div>
              <ConfBar value={p.confidence} />
            </div>
            {p.predicted_range_low && p.predicted_range_high && (
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>予測レンジ</div>
                <div style={{ fontSize: '0.875rem' }}>¥{p.predicted_range_low.toLocaleString()} 〜 ¥{p.predicted_range_high.toLocaleString()}</div>
              </div>
            )}
          </div>

          {p.hourly_forecast && p.hourly_forecast.length > 0 && (
            <div style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>⏰ 時間別予測</div>
              <HourlyChart data={p.hourly_forecast} currentPrice={pp.current_price} />
            </div>
          )}

          {p.reasoning && (
            <div style={{ background: 'var(--bg-secondary)', borderRadius: 6, padding: '0.75rem', fontSize: '0.825rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--text-primary)' }}>AI分析：</strong>{p.reasoning}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Predictions() {
  const qc = useQueryClient()

  const { data: holdings = [] } = useQuery({ queryKey: ['holdings'], queryFn: holdingsApi.list })
  const { data: portfolio = [], isLoading } = useQuery({
    queryKey: ['predictions-portfolio'],
    queryFn: predictionsApi.portfolio,
  })

  const generateMut = useMutation({
    mutationFn: (code: string) => predictionsApi.generate(code),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['predictions-portfolio'] }),
  })

  const [generating, setGenerating] = useState<string | null>(null)
  const handleGenerate = (code: string) => {
    setGenerating(code)
    generateMut.mutate(code, { onSettled: () => setGenerating(null) })
  }

  const generateAll = async () => {
    for (const h of holdings as any[]) {
      setGenerating(h.code)
      await generateMut.mutateAsync(h.code).catch(() => {})
    }
    setGenerating(null)
    qc.invalidateQueries({ queryKey: ['predictions-portfolio'] })
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>🤖 AI株価予測</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>
            テクニカル指標とニュースに基づくAI予測（明日の動向）
          </p>
        </div>
        <button className="btn-primary" onClick={generateAll} disabled={!!generating || holdings.length === 0}>
          {generating ? `⏳ 生成中 (${generating})...` : '🤖 全銘柄の予測を生成'}
        </button>
      </div>

      <div style={{ background: 'rgba(210,153,34,0.1)', border: '1px solid rgba(210,153,34,0.3)', borderRadius: 8, padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.8rem', color: 'var(--accent-yellow)' }}>
        ⚠️ AI予測は参考情報です。テクニカル分析とニュースを基にした推定であり、実際の株価との乖離があります。投資は自己責任でお願いします。
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}><div className="spinner" /></div>
      ) : portfolio.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💼</div>
          <div>保有株を登録してください</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {portfolio.map((pp: PortfolioPrediction) => (
            <PredCard key={pp.code} pp={pp} onGenerate={handleGenerate} />
          ))}
        </div>
      )}
    </div>
  )
}
