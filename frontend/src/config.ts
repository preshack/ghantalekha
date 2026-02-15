// Use empty strings in dev (proxy) to avoid CORS issues
// In production, VITE_API_URL must be set if backend is on a different domain
export const API_BASE_URL = import.meta.env.DEV 
  ? '' 
  : (import.meta.env.VITE_API_URL || '');
