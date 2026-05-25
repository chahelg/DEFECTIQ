import React from 'react'
import { useEffect, useState } from 'react'

export default function Explorer(){
  const [defects, setDefects] = useState<any[]>([])

  useEffect(()=>{
    fetch('/api/v1/defects').then(r=>r.json()).then(setDefects).catch(()=>setDefects([]))
  },[])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Defect Explorer</h1>
      <div className="bg-white rounded shadow p-4">
        <table className="w-full">
          <thead><tr><th>ID</th><th>Short</th><th>Assignment</th></tr></thead>
          <tbody>
            {defects.map((d:any)=>(<tr key={d.id}><td>{d.defect_id}</td><td>{d.short_description}</td><td>{d.assignment_group}</td></tr>))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
