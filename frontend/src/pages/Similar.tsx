import React, {useState} from 'react'

export default function Similar(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])

  async function search(){
    const res = await fetch('/api/v1/search/semantic', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({query, top_k:5})})
    const json = await res.json()
    setResults(json.results || [])
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Similar Defects</h1>
      <div className="bg-white rounded shadow p-4">
        <div className="flex gap-2">
          <input value={query} onChange={e=>setQuery(e.target.value)} className="flex-1 p-2 border" />
          <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={search}>Search</button>
        </div>
        <ul className="mt-4">
          {results.map((r,idx)=>(<li key={idx}>{r.defect_id} (score: {r.score})</li>))}
        </ul>
      </div>
    </div>
  )
}
