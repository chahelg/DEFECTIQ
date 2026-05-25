import { useMutation } from '@tanstack/react-query'
import { login, register } from '@api/auth'
import { useAppStore } from '@store/useAppStore'
import type { LoginPayload, RegisterPayload } from '@types'
import { toast } from 'react-hot-toast'

export function useLoginMutation() {
  const setAuth = useAppStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (payload: LoginPayload) => login(payload),
    onSuccess: (session) => {
      setAuth(session)
      toast.success('Welcome back. Access granted.')
    },
    onError: () => toast.error('Unable to sign in. Please verify your credentials.'),
  })
}

export function useRegisterMutation() {
  const setAuth = useAppStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (payload: RegisterPayload) => register(payload),
    onSuccess: (session) => {
      setAuth(session)
      toast.success('Your DefectIQ workspace is ready.')
    },
    onError: () => toast.error('Unable to create account right now.'),
  })
}