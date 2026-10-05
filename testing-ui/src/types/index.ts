export interface ResponseEnvelope<T> {
  success: boolean;
  message: string;
  data: T | null;
  errors: any;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone_number?: string | null;
  preferred_language?: string;
  profile_image_url?: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_used?: string | null;
  token_count?: number | null;
  created_at?: string;
}

export interface ChatUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface RidePlace {
  name: string;
  city: string;
  lat: number;
  lng: number;
}

export interface CabOption {
  tier: 'mini' | 'sedan' | 'suv';
  label: string;
  seats: number;
  fare_inr: number;
  distance_km: number;
  trip_minutes: number;
  currency: 'INR';
  is_demo: boolean;
}

/** A car option as stored in a persisted quote (GET /api/v1/recommendations/{id}). */
export interface StoredQuoteOption {
  tier: string;
  display_name?: string;
  fare?: string | number;
  currency?: string;
  eta_minutes?: number;
  capacity?: number;
  description?: string;
}

export interface RideBookingInfo {
  id: string;
  reference: string;
  status: string;
  tier: string | null;
  fare_inr: number | null;
  provider: string;
}

export type RideStage = 'idle' | 'collecting' | 'quoted' | 'confirming' | 'booked';

export interface RideState {
  stage: RideStage;
  pickup: RidePlace | null;
  drop: RidePlace | null;
  options: CabOption[];
  selected_tier: string | null;
  booking: RideBookingInfo | null;
  currency: 'INR';
  is_demo: boolean;
  supported_cities: string[];
}

export interface ChatResponse {
  conversation_id: string;
  session_id: string;
  message: ChatMessage;
  recommendation_id?: string | null;
  route?: 'ride' | 'knowledge' | 'general';
  ride?: RideState | null;
  sources?: string[];
  usage: ChatUsage;
}

export interface Recommendation {
  id: string;
  conversation_id: string;
  recommendation_type: string;
  recommendation_data: {
    options?: StoredQuoteOption[];
    is_demo?: boolean;
    selected_tier?: string;
    [key: string]: unknown;
  };
  status: string;
}

export interface Booking {
  id: string;
  recommendation_id?: string | null;
  booking_reference: string;
  booking_status: string;
  provider: string;
  external_booking_id?: string | null;
  booked_at?: string;
}

export interface RideOption {
  tier: string;
  label?: string;
  estimated_price: number;
  eta_minutes: number;
}

export interface HealthInfo {
  status: string;
  application: string;
  version: string;
  environment: string;
}

export interface UIError {
  type: 'offline' | 'timeout' | 'gemini_error' | 'server_error' | 'validation';
  message: string;
  details?: string;
}
