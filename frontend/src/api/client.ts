const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_PREFIX = '/api/v1';

export const API_BASE = `${BASE_URL}${API_PREFIX}`;

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const errorText = await response.text();
    let errMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const parsed = JSON.parse(errorText);
      errMessage = parsed.detail || errMessage;
    } catch {
      // Not JSON
    }
    throw new Error(errMessage);
  }
  
  return response.json() as Promise<T>;
}
