const isDevelopment = import.meta.env.MODE === 'development';

export const API_BASE_URL = isDevelopment 
  ? ''  // Vite proxy handles this locally (forwarding to localhost:8000)
  : import.meta.env.VITE_API_URL || ''; // In prod, use env var or relative path if served from same origin
