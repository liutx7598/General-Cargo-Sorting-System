import axios from 'axios';

import type { ApiResponse } from '@/types';

function normalizeBaseUrl(baseUrl?: string): string {
  const normalized = (baseUrl ?? '/api').trim();
  if (!normalized) {
    return '/api';
  }
  return normalized.replace(/\/+$/, '');
}

function normalizePath(path?: string): string | undefined {
  if (!path) {
    return path;
  }
  const normalized = path.trim();
  if (!normalized) {
    return '/';
  }
  return normalized.startsWith('/') ? normalized : `/${normalized}`;
}

const client = axios.create({
  baseURL: normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL),
  timeout: 20000,
});

client.interceptors.request.use((config) => {
  config.baseURL = normalizeBaseUrl(config.baseURL);
  config.url = normalizePath(config.url);
  return config;
});

client.interceptors.response.use((response) => response, (error) => {
  const message = error.response?.data?.message ?? error.message ?? '请求失败';
  return Promise.reject(new Error(message));
});

export async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await promise;
  return response.data.data;
}

export default client;
