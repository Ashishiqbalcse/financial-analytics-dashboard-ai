export interface OHLCVData {
  symbol: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TechnicalIndicator {
  symbol: string;
  indicator_type: string;
  data: Array<{
    timestamp: string;
    value: number;
    signal?: string;
    metadata?: Record<string, any>;
  }>;
}

export interface Prediction {
  symbol: string;
  prediction_date: string;
  predicted_close: number;
  confidence_lower: number;
  confidence_upper: number;
  model_type: string;
}

export interface Portfolio {
  id: number;
  user_id: string;
  symbol: string;
  shares: number;
  average_cost: number;
  current_price?: number;
  current_value?: number;
  profit_loss?: number;
  profit_loss_percent?: number;
  created_at: string;
  updated_at?: string;
}

export interface Alert {
  id: number;
  user_id: string;
  symbol: string;
  condition: 'above' | 'below';
  target_price: number;
  is_active: boolean;
  triggered: boolean;
  triggered_at?: string;
  created_at: string;
}

export interface MarketData {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  high_52w?: number;
  low_52w?: number;
  market_cap?: number;
}

export interface WebSocketMessage {
  type: 'price' | 'indicator' | 'alert';
  symbol: string;
  data: Record<string, any>;
  timestamp: string;
}
