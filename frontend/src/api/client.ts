import axios from 'axios';

import type { ApiResponse } from '@/types';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 20000,
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
