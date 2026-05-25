import { create } from 'zustand'
import { api, AUTH_STORAGE_KEY, setApiAuthToken } from '@/services/api'
import type { AuthSession, AuthUser, AuthResponse } from '@/types/phase1'

interface AuthState {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  loadFromStorage: () => void
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

function persistSession(session: AuthSession | null) {
  if (typeof window === 'undefined') {
    return
  }

  if (!session) {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return
  }

  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
}

function syncAuthState(session: AuthSession | null, setState: (partial: Partial<AuthState>) => void) {
  if (session) {
    setState({ user: session.user, token: session.token, isAuthenticated: true })
    setApiAuthToken(session.token)
    persistSession(session)
    return
  }

  setState({ user: null, token: null, isAuthenticated: false })
  setApiAuthToken(null)
  persistSession(null)
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  loadFromStorage: () => {
    if (typeof window === 'undefined') {
      return
    }

    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) {
      syncAuthState(null, set)
      return
    }

    try {
      const session = JSON.parse(raw) as AuthSession
      if (!session.token || !session.user) {
        syncAuthState(null, set)
        return
      }

      syncAuthState(session, set)
    } catch {
      syncAuthState(null, set)
    }
  },
  login: async (email: string, password: string) => {
    const payload = new URLSearchParams()
    payload.set('username', email)
    payload.set('password', password)

    const response = await api.post<AuthResponse>('/auth/login', payload, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    syncAuthState(
      {
        token: response.data.access_token,
        user: response.data.user,
      },
      set,
    )
  },
  logout: () => {
    syncAuthState(null, set)
  },
}))