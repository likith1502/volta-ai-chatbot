import {
  Booking,
  ChatResponse,
  HealthInfo,
  Recommendation,
  ResponseEnvelope,
  User,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiError extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = 60000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const url = `${API_BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const json = await res.json().catch(() => null);

    if (!res.ok) {
      const errMsg =
        json?.message ||
        json?.detail ||
        `HTTP Error ${res.status}: ${res.statusText}`;
      throw new ApiError(errMsg, res.status, json);
    }

    if (json && typeof json === 'object' && 'data' in json) {
      const envelope = json as ResponseEnvelope<T>;
      if (!envelope.success) {
        throw new ApiError(envelope.message || 'API request reported failure', res.status, envelope);
      }
      return envelope.data as T;
    }

    return json as T;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new ApiError(`Request timed out after ${timeoutMs / 1000}s. The backend or AI provider took too long to respond.`, 408);
    }
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      'Unable to connect to VOLTA right now. Please check your internet connection and try again.',
      0
    );
  }
}

export const api = {
  // Health probe
  async checkHealth(): Promise<HealthInfo> {
    return request<HealthInfo>('/health', { method: 'GET' }, 5000);
  },

  // Chat conversation
  async sendChat(userId: string, sessionId: string, message: string): Promise<ChatResponse> {
    return request<ChatResponse>(
      '/api/v1/chat',
      {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message,
        }),
      },
      65000 // Allow up to 65s for full AI reasoning turn
    );
  },

  // User management
  async createUser(fullName: string, email: string, phoneNumber?: string): Promise<User> {
    return request<User>('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify({
        full_name: fullName,
        email,
        phone_number: phoneNumber ?? null,
        preferred_language: 'en',
      }),
    });
  },

  async getUser(userId: string): Promise<User> {
    return request<User>(`/api/v1/users/${userId}`, { method: 'GET' });
  },

  // Booking management
  // Admin/dev only. Customers book through the chat (explicit confirmation).
  async createBooking(recommendationId: string, selectedTier?: string): Promise<Booking> {
    return request<Booking>('/api/v1/bookings', {
      method: 'POST',
      body: JSON.stringify({
        recommendation_id: recommendationId,
        selected_tier: selectedTier ?? null,
      }),
    });
  },

  async getRecommendation(recommendationId: string): Promise<Recommendation> {
    return request<Recommendation>(
      `/api/v1/recommendations/${encodeURIComponent(recommendationId)}`,
      { method: 'GET' }
    );
  },

  async getBooking(bookingReference: string): Promise<Booking> {
    return request<Booking>(`/api/v1/bookings/${encodeURIComponent(bookingReference)}`, {
      method: 'GET',
    });
  },
};
