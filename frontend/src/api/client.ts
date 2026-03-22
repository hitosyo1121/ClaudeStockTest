import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// Types
export interface Holding {
  id: number;
  code: string;
  name: string;
  quantity: number;
  avg_cost: number;
  market: string;
  sector?: string;
  current_price?: number;
  market_value?: number;
  unrealized_pnl?: number;
  pnl_pct?: number;
  day_change?: number;
  day_change_pct?: number;
  created_at: string;
  updated_at: string;
}

export interface HoldingCreate {
  code: string;
  name: string;
  quantity: number;
  avg_cost: number;
  market?: string;
  sector?: string;
}

export interface NewsItem {
  id: number;
  news_date: string;
  source?: string;
  title: string;
  summary?: string;
  url?: string;
  relevance: string;
}

export interface NewsResponse {
  date: string;
  items: NewsItem[];
  market_summary?: string;
}

export interface ScreeningResult {
  id: number;
  run_date: string;
  code: string;
  name: string;
  action: string;
  score?: number;
  reasons?: string[];
  price_at_run?: number;
}

export interface ScreeningResponse {
  run_date: string;
  buy_recommendations: ScreeningResult[];
  sell_signals: ScreeningResult[];
  watch_list: ScreeningResult[];
}

export interface HourlyForecast {
  hour: string;
  estimated_price: number;
}

export interface Prediction {
  id: number;
  code: string;
  prediction_date: string;
  direction: 'up' | 'down' | 'flat';
  confidence?: number;
  predicted_range_low?: number;
  predicted_range_high?: number;
  hourly_forecast?: HourlyForecast[];
  reasoning?: string;
  generated_at: string;
}

export interface PortfolioPrediction {
  code: string;
  name: string;
  current_price?: number;
  prediction?: Prediction;
}

export interface Technicals {
  code: string;
  ma25?: number;
  ma75?: number;
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  trend?: string;
  ichimoku_above_cloud?: boolean;
}

export interface TomorrowOutlook {
  overall_direction: string;
  confidence: number;
  key_factors: Array<{ factor: string; impact: string; magnitude: string }>;
  sector_outlook: Array<{ sector: string; direction: string; reason: string }>;
  scheduled_events: string[];
  risk_factors: string[];
  summary: string;
  hourly_trend: Array<{ time_range: string; trend: string; note: string }>;
}

// API functions
export const holdingsApi = {
  list: () => api.get<Holding[]>('/holdings').then(r => r.data),
  create: (data: HoldingCreate) => api.post<Holding>('/holdings', data).then(r => r.data),
  update: (id: number, data: Partial<HoldingCreate>) => api.put<Holding>(`/holdings/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/holdings/${id}`),
};

export const stocksApi = {
  price: (code: string) => api.get(`/stocks/${code}/price`).then(r => r.data),
  technicals: (code: string) => api.get<Technicals>(`/stocks/${code}/technicals`).then(r => r.data),
  history: (code: string, period = '3mo') => api.get(`/stocks/${code}/history?period=${period}`).then(r => r.data),
  search: (q: string) => api.get(`/stocks/search?q=${encodeURIComponent(q)}`).then(r => r.data),
};

export const newsApi = {
  today: () => api.get<NewsResponse>('/news/today').then(r => r.data),
  tomorrow: () => api.get<TomorrowOutlook>('/news/tomorrow').then(r => r.data),
  refresh: () => api.post('/news/refresh').then(r => r.data),
};

export const screeningApi = {
  results: () => api.get<ScreeningResponse>('/screening/results').then(r => r.data),
  run: () => api.post('/screening/run').then(r => r.data),
};

export const predictionsApi = {
  portfolio: () => api.get<PortfolioPrediction[]>('/predictions/portfolio').then(r => r.data),
  get: (code: string) => api.get<Prediction>(`/predictions/${code}`).then(r => r.data),
  generate: (code: string) => api.post<Prediction>(`/predictions/generate/${code}`).then(r => r.data),
};

export default api;
