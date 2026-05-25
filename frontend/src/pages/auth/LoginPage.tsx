import { useEffect, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthLayout } from '@components/auth/AuthLayout'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { useLoginMutation } from '@hooks/useAuth'
import { useAppStore } from '@store/useAppStore'
import { toast } from 'react-hot-toast'

export function LoginPage() {
  const navigate = useNavigate()
  const loginMutation = useLoginMutation()
  const setTheme = useAppStore((state) => state.setTheme)

  useEffect(() => {
    setTheme('dark')
  }, [setTheme])

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const email = String(formData.get('email') ?? '')
    const password = String(formData.get('password') ?? '')

    try {
      await loginMutation.mutateAsync({ email, password })
      toast.success('Signed in successfully')
      navigate('/dashboard')
    } catch {
      toast.error('Unable to sign in')
    }
  }

  return (
    <AuthLayout title="Sign in" subtitle="Access your enterprise defect intelligence workspace.">
      <form className="space-y-4" onSubmit={submit}>
        <div>
          <label className="mb-2 block text-sm font-medium text-foreground">Email</label>
          <Input name="email" defaultValue="analyst@defectiq.ai" type="email" placeholder="name@company.com" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-foreground">Password</label>
          <Input name="password" defaultValue="Password123!" type="password" placeholder="••••••••" />
        </div>
        <Button className="w-full" type="submit" disabled={loginMutation.isPending}>
          Sign in
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Need an account?{' '}
        <Link className="text-cyan-300 hover:text-cyan-200" to="/auth/register">
          Register
        </Link>
      </p>
    </AuthLayout>
  )
}