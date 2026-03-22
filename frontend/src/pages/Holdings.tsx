import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { holdingsApi, type Holding, type HoldingCreate } from '../api/client'

function fmt(n?: number | null) { return n != null ? n.toLocaleString('ja-JP') : '—' }
function fmtPct(n?: number | null) {
  if (n == null) return '—'
  const s = n >= 0 ? '+' : ''
  return `${s}${n.toFixed(2)}%`
}

const emptyForm: HoldingCreate = { code: '', name: '', quantity: 0, avg_cost: 0, market: 'prime', sector: '' }

export default function Holdings() {
  const qc = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [form, setForm] = useState<HoldingCreate>(emptyForm)
  const [search, setSearch] = useState('')

  const { data: holdings = [], isLoading } = useQuery({
    queryKey: ['holdings'],
    queryFn: holdingsApi.list,
    refetchInterval: 120000,
  })

  const createMut = useMutation({
    mutationFn: holdingsApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['holdings'] }); closeModal() },
  })
  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<HoldingCreate> }) => holdingsApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['holdings'] }); closeModal() },
  })
  const deleteMut = useMutation({
    mutationFn: holdingsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['holdings'] }),
  })

  const openCreate = () => { setForm(emptyForm); setEditId(null); setShowModal(true) }
  const openEdit = (h: Holding) => {
    setForm({ code: h.code, name: h.name, quantity: h.quantity, avg_cost: h.avg_cost, market: h.market, sector: h.sector || '' })
    setEditId(h.id)
    setShowModal(true)
  }
  const closeModal = () => { setShowModal(false); setEditId(null); setForm(emptyForm) }
  const handleSubmit = () => {
    if (!form.code || !form.name || form.quantity <= 0 || form.avg_cost <= 0) return
    if (editId) {
      updateMut.mutate({ id: editId, data: form })
    } else {
      createMut.mutate(form)
    }
  }

  const filtered = holdings.filter((h: Holding) =>
    h.name.includes(search) || h.code.includes(search)
  )

  const totalValue = filtered.reduce((s: number, h: Holding) => s + (h.market_value || 0), 0)
  const totalPnl   = filtered.reduce((s: number, h: Holding) => s + (h.unrealized_pnl || 0), 0)

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>💼 保有株管理</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: 4 }}>保有している株式を登録・管理します</p>
        </div>
        <button className="btn-primary" onClick={openCreate}>＋ 銘柄を追加</button>
      </div>

      {/* Summary */}
      <div className="kpi-grid" style={{ marginBottom: '1rem' }}>
        <div className="kpi-card">
          <div className="kpi-label">保有銘柄数</div>
          <div className="kpi-value">{filtered.length}<span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>銘柄</span></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">評価額合計</div>
          <div className="kpi-value" style={{ fontSize: '1.2rem' }}>¥{fmt(totalValue)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">未実現損益</div>
          <div className={`kpi-value ${totalPnl >= 0 ? 'positive' : 'negative'}`} style={{ fontSize: '1.2rem' }}>
            {totalPnl >= 0 ? '+' : ''}¥{fmt(totalPnl)}
          </div>
        </div>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '1rem' }}>
        <input className="input" placeholder="銘柄名・コードで検索..." value={search} onChange={e => setSearch(e.target.value)} style={{ maxWidth: 300 }} />
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}><div className="spinner" /></div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💼</div>
            <div>保有株がありません。「銘柄を追加」から登録してください。</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>銘柄</th>
                <th>株数</th>
                <th>取得単価</th>
                <th>現在値</th>
                <th>評価額</th>
                <th>未実現損益</th>
                <th>損益率</th>
                <th>当日変化</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((h: Holding) => (
                <tr key={h.id}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{h.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{h.code} · {h.market}</div>
                  </td>
                  <td>{fmt(h.quantity)}株</td>
                  <td>¥{fmt(h.avg_cost)}</td>
                  <td>{h.current_price ? `¥${fmt(h.current_price)}` : <span className="spinner" style={{ width: 12, height: 12 }} />}</td>
                  <td>{h.market_value ? `¥${fmt(h.market_value)}` : '—'}</td>
                  <td className={h.unrealized_pnl != null ? (h.unrealized_pnl >= 0 ? 'positive' : 'negative') : ''}>
                    {h.unrealized_pnl != null ? `${h.unrealized_pnl >= 0 ? '+' : ''}¥${fmt(h.unrealized_pnl)}` : '—'}
                  </td>
                  <td className={h.pnl_pct != null ? (h.pnl_pct >= 0 ? 'positive' : 'negative') : 'neutral'}>
                    {fmtPct(h.pnl_pct)}
                  </td>
                  <td className={h.day_change_pct != null ? (h.day_change_pct >= 0 ? 'positive' : 'negative') : 'neutral'}>
                    {fmtPct(h.day_change_pct)}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button className="btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => openEdit(h)}>編集</button>
                      <button className="btn-danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => deleteMut.mutate(h.id)}>削除</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-title">{editId ? '保有株を編集' : '保有株を追加'}</div>
            <div className="form-group">
              <label className="form-label">銘柄コード *</label>
              <input className="input" placeholder="例: 6501" value={form.code} onChange={e => setForm({...form, code: e.target.value})} disabled={!!editId} />
            </div>
            <div className="form-group">
              <label className="form-label">銘柄名 *</label>
              <input className="input" placeholder="例: 日立製作所" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">保有株数 *</label>
                <input className="input" type="number" placeholder="100" value={form.quantity || ''} onChange={e => setForm({...form, quantity: Number(e.target.value)})} />
              </div>
              <div className="form-group">
                <label className="form-label">平均取得単価（円）*</label>
                <input className="input" type="number" placeholder="2500" value={form.avg_cost || ''} onChange={e => setForm({...form, avg_cost: Number(e.target.value)})} />
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">市場</label>
                <select className="input" value={form.market} onChange={e => setForm({...form, market: e.target.value})}>
                  <option value="prime">プライム</option>
                  <option value="standard">スタンダード</option>
                  <option value="growth">グロース</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">セクター</label>
                <input className="input" placeholder="電気機器" value={form.sector || ''} onChange={e => setForm({...form, sector: e.target.value})} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1.25rem' }}>
              <button className="btn-ghost" onClick={closeModal}>キャンセル</button>
              <button className="btn-primary" onClick={handleSubmit} disabled={createMut.isPending || updateMut.isPending}>
                {createMut.isPending || updateMut.isPending ? '処理中...' : editId ? '更新' : '追加'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
