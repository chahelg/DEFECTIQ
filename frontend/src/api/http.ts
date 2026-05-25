import axios from 'axios'
import { API_BASE_URL } from '@lib/constants'
import { useAppStore } from '@store/useAppStore'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = useAppStore.getState().auth?.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      useAppStore.getState().clearAuth()
    }
    return Promise.reject(error)
  },
)