import { type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AuthLayout } from '@components/auth/AuthLayout'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { Select } from '@components/ui/select'
import { useRegisterMutation } from '@hooks/useAuth'
import { toast } from 'react-hot-toast'

export function RegisterPage() {
  const navigate = useNavigate()
  const registerMutation = useRegisterMutation()

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)

    const payload = {
      fullName: String(formData.get('fullName') ?? ''),
      username: String(formData.get('username') ?? ''),
      email: String(formData.get('email') ?? ''),
      password: String(formData.get('password') ?? ''),
      department: String(formData.get('department') ?? ''),
      role: String(formData.get('role') ?? 'analyst') as 'admin' | 'manager' | 'analyst' | 'viewer',
    }

    try {
      await registerMutation.mutateAsync(payload)
      toast.success('Account created')
      navigate('/dashboard')
    } catch {
      toast.error('Unable to create account')
    }
  }

  return (
    <AuthLayout title="Create account" subtitle="Secure access for analytics, AI insights, and defect triage.">
      <form className="space-y-4" onSubmit={submit}>
        <div>
          <label className="mb-2 block text-sm font-medium text-foreground">Full name</label>
          <Input name="fullName" placeholder="Avery Morgan" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">Username</label>
            <Input name="username" placeholder="ops-analyst" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">Department</label>
            <Input name="department" placeholder="Operations Intelligence" />
          </div>
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-foreground">Email</label>
          <Input name="email" type="email" placeholder="name@company.com" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">Password</label>
            <Input name="password" type="password" placeholder="••••••••" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">Role</label>
            <Select name="role" defaultValue="analyst">
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
            </Select>
          </div>
        </div>
        <Button className="w-full" type="submit" disabled={registerMutation.isPending}>
          Create account
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link className="text-cyan-300 hover:text-cyan-200" to="/auth/login">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  )
}