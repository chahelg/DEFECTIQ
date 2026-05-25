import { api } from './http'
import { ENABLE_MOCKS } from '@lib/constants'
import { demoSession, demoUser } from '@data/mockData'
import type { AuthSession, LoginPayload, RegisterPayload, User } from '@types'

export async function login(payload: LoginPayload): Promise<AuthSession> {
  try {
    const response = await api.post<AuthSession>('/auth/login', payload)
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return {
      ...demoSession,
      user: {
        ...demoUser,
        email: payload.email,
      },
    }
  }
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  try {
    const response = await api.post<AuthSession>('/auth/register', payload)
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return {
      ...demoSession,
      user: {
        ...demoUser,
        email: payload.email,
        username: payload.username,
        fullName: payload.fullName,
        department: payload.department,
      },
    }
  }
}

export async function me(): Promise<User | null> {
  try {
    const response = await api.get<User>('/auth/me')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return demoUser
  }
}

export async function refresh(): Promise<AuthSession> {
  try {
    const response = await api.post<AuthSession>('/auth/refresh')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return demoSession
  }
}