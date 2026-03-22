import { useQuery } from '@tanstack/react-query'
import { holdingsApi, screeningApi, type Holding } from '../api/client'

interface Props {
  onNavigate: (page: any) => void
}

function fmt(n?: number | null, decimals = 0) {
  if (n == null) return '—'
  return n.toLocaleString('ja-JP', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function fmtPct(n?: number | null) {
  if (n == null) return '—'
  const sign = n >= 0 ? '+' : ''
  return `${sign}${n.toFixed(2)}%`
}

export default function Dashboard({ onNavigate }: Props) {
  const { data: holdings = [] } = useQuery({
    queryKey: ['holdings'],
    queryFn: holdingsApi.list,
    refetchInterval: 120000,
  })

  const { data: screening } = useQuery({
    queryKey: ['screening'],
    queryFn: screeningApi.results,
  })

  const totalValue = holdings.reduce((s: number, h: Holding) => s + (h.market_value || 0), 0)
  const totalCost  = holdings.reduce((s: number, h: Holding) => s + (h.avg_cost * h.quantity), 0)
  const totalPnl   = totalValue - totalCost
  const totalPnlPct = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0

  const gainers  = [...holdings].filter((h: Holding) => (h.unrealized_pnl || 0) > 0).sort((a: Holding, b: Holding) => (b.pnl_pct||0)-(a.pnl_pct||0)).slice(0,3)
  const losers   = [...holdings].filter((h: Holding) => (h.unrealized_pnl || 0) < 0).sort((a: Holding, b: Holding) => (a.pnl_pct||0)-(b.pnl_pct||0)).slice(0,3)

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>ダッシュボード</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>
          ポートフォリオ概要
        </p>
      </div>

      {/* KPI Grid */}
      <div className="kpi-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="kpi-card">
          <div className="kpi-label">保有銘柄数</div>
          <div className="kpi-value">{holdings.length}<span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>銘柄</span></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">評価額合計</div>
          <div className="kpi-value" style={{ fontSize: '1.25rem' }}>¥{fmt(totalValue)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">未実現損益</div>
          <div className={`kpi-value ${totalPnl >= 0 ? 'positive' : 'negative'}`} style={{ fontSize: '1.25rem' }}>
            {totalPnl >= 0 ? '+' : ''}¥{fmt(totalPnl)}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">損益率</div>
          <div className={`kpi-value ${totalPnlPct >= 0 ? 'positive' : 'negative'}`}>
            {fmtPct(totalPnlPct)}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {/* Top gainers */}
        <div className="card">
          <div className="section-header">
            <span className="section-title">📈 上昇銘柄</span>
            <button className="btn-ghost" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }} onClick={() => onNavigate('holdings')}>全銘柄</button>
          </div>
          {gainers.length === 0 ? <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>なし</p> : (
            <table>
              <thead><tr><th>銘柄</th><th>現在値</th><th>損益率</th></tr></thead>
              <tbody>
                {gainers.map((h: Holding) => (
                  <tr key={h.id}>
                    <td><div style={{ fontWeight: 500 }}>{h.name}</div><div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{h.code}</div></td>
                    <td>¥{fmt(h.current_price)}</td>
                    <td className="positive">{fmtPct(h.pnl_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Top losers */}
        <div className="card">
          <div className="section-header">
            <span className="section-title">📉 下落銘柄</span>
          </div>
          {losers.length === 0 ? <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>なし</p> : (
            <table>
              <thead><tr><th>銘柄</th><th>現在値</th><th>損益率</th></tr></thead>
              <tbody>
                {losers.map((h: Holding) => (
                  <tr key={h.id}>
                    <td><div style={{ fontWeight: 500 }}>{h.name}</div><div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{h.code}</div></td>
                    <td>¥{fmt(h.current_price)}</td>
                    <td className="negative">{fmtPct(h.pnl_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Buy recommendations preview */}
      {screening && screening.buy_recommendations.length > 0 && (
        <div className="card">
          <div className="section-header">
            <span className="section-title">🎯 購入推奨銘柄</span>
            <button className="btn-ghost" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }} onClick={() => onNavigate('screening')}>詳細</button>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            {screening.buy_recommendations.slice(0,5).map(r => (
              <div key={r.code} style={{ background: 'rgba(88,166,255,0.07)', border: '1px solid rgba(88,166,255,0.2)', borderRadius: 8, padding: '0.75rem 1rem', minWidth: 130 }}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{r.code}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 4 }}>{r.name}</div>
                <span className="badge-buy">BUY</span>
                {r.score && <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: 4 }}>スコア: {r.score}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
