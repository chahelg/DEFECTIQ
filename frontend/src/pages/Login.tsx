import React, {useState} from 'react'

export default function Login(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  async function submit(){
    const fd = new FormData()
    fd.append('username', username)
    fd.append('password', password)
    const res = await fetch('/api/v1/auth/login', {method:'POST', body: fd})
    const json = await res.json()
    alert(JSON.stringify(json))
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <div className="bg-white rounded shadow p-4">
        <input placeholder="username" value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-2 border mb-2" />
        <input type="password" placeholder="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-2 border mb-2" />
        <button onClick={submit} className="px-4 py-2 bg-blue-600 text-white rounded">Login</button>
      </div>
    </div>
  )
}
