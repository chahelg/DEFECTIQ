import React from 'react'
import { useEffect, useState } from 'react'
import TrendChart from '../components/charts/TrendChart'

export default function Dashboard(){
  const [backlog, setBacklog] = useState<any[]>([])
  const [trends, setTrends] = useState<any[]>([])

  useEffect(()=>{
    fetch('/api/v1/analytics/backlog').then(r=>r.json()).then(setBacklog)
    fetch('/api/v1/analytics/trends').then(r=>r.json()).then(setTrends)
  },[])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded shadow">Total Backlog: {backlog.reduce((s,a)=>s+a.backlog,0)}</div>
        <div className="p-4 bg-white rounded shadow">Placeholder KPI</div>
        <div className="p-4 bg-white rounded shadow">Placeholder KPI</div>
      </div>
      <section className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Backlog by Assignment Group</h2>
        <ul className="bg-white rounded shadow p-4">
          {backlog.map((b,idx)=>(<li key={idx} className="py-1">{b.assignment_group}: {b.backlog}</li>))}
        </ul>
      </section>
      <section className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Trends</h2>
        <div className="bg-white p-4 rounded shadow">
          <TrendChart data={trends} />
        </div>
      </section>
    </div>
  )
}
