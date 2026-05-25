import React, {useState} from 'react'

export default function Predictions(){
  const [features, setFeatures] = useState('')
  const [model, setModel] = useState('sla_breach')
  const [result, setResult] = useState<any>(null)
  const [explain, setExplain] = useState<any>(null)

  async function infer(){
    try{
      const payload = JSON.parse(features)
      payload._model = model
      const res = await fetch('/api/v1/predictions/infer', {method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({features: payload})})
      setResult(await res.json())
    }catch(e){
      setResult({error: String(e)})
    }
  }

  async function explainModel(){
    try{
      const payload = JSON.parse(features)
      const res = await fetch('/api/v1/predictions/explain', {method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({features: payload})})
      setExplain(await res.json())
    }catch(e){
      setExplain({error: String(e)})
    }
  }

  async function trainModel(){
    try{
      const res = await fetch('/api/v1/predictions/train/quick', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({model: model, version: 'v1'})})
      setResult(await res.json())
    }catch(e){
      setResult({error: String(e)})
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Predictions</h1>
      <div className="bg-white rounded shadow p-4">
        <div className="mb-2">
          <label className="mr-2">Model:</label>
          <select value={model} onChange={e=>setModel(e.target.value)} className="p-2 border">
            <option value="sla_breach">SLA Breach</option>
            <option value="assignment_recommend">Assignment Recommend</option>
            <option value="resolution_time">Resolution Time</option>
          </select>
        </div>
        <textarea rows={8} value={features} onChange={e=>setFeatures(e.target.value)} className="w-full p-2 border" placeholder='{"age_days":10,"is_open":1,"reopen_count":0,"priority_score":3,"text_len":150}'></textarea>
        <div className="flex gap-2 mt-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded" onClick={infer}>Run Inference</button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded" onClick={explainModel}>Explain</button>
          <button className="px-4 py-2 bg-green-600 text-white rounded" onClick={trainModel}>Train Model</button>
        </div>
        <pre className="mt-4">{JSON.stringify(result, null, 2)}</pre>
        <div className="mt-4">
          {explain && explain.contributions && (
            <div className="bg-white p-4 rounded shadow">
              <h3 className="font-semibold mb-2">SHAP Contributions</h3>
              <ul>
                {explain.contributions.map((c:any,idx:number)=>(<li key={idx}>{c.feature}: {c.shap.toFixed(4)} (value: {c.value})</li>))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
