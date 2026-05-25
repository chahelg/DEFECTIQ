import { DragEvent, useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileSpreadsheet, Loader2, Upload, UploadCloud } from 'lucide-react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { UploadResponse } from '@/types/phase1'

async function uploadDefects(file: File, onProgress: (progress: number) => void) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (!progressEvent.total) {
        return
      }

      onProgress(Math.round((progressEvent.loaded / progressEvent.total) * 100))
    },
  })

  return response.data
}

export function UploadPage() {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [progress, setProgress] = useState(0)
  const [dragActive, setDragActive] = useState(false)

  const mutation = useMutation({
    mutationFn: (file: File) => uploadDefects(file, setProgress),
  })

  const handleFile = (file: File | undefined) => {
    if (!file) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.xlsx')) {
      mutation.reset()
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
    mutation.reset()
    setProgress(0)
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragActive(false)
    handleFile(event.dataTransfer.files[0])
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Upload Defects</CardTitle>
          <CardDescription>Drop a .csv or .xlsx file to bulk insert defect records.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div
            className={`rounded-3xl border-2 border-dashed px-6 py-12 text-center transition ${
              dragActive ? 'border-cyan-300 bg-cyan-400/10' : 'border-white/15 bg-white/5'
            }`}
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={handleDrop}
          >
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-400/15 text-cyan-300 ring-1 ring-cyan-300/20">
              <UploadCloud className="h-8 w-8" />
            </div>
            <h2 className="mt-4 text-2xl font-semibold text-white">Drag and drop your file</h2>
            <p className="mt-2 text-sm text-slate-400">Accepted formats: .csv and .xlsx</p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Button onClick={() => inputRef.current?.click()} type="button" variant="outline">
                <FileSpreadsheet className="mr-2 h-4 w-4" />
                Choose File
              </Button>
              <Button
                disabled={!selectedFile || mutation.isPending}
                onClick={() => selectedFile && mutation.mutate(selectedFile)}
                type="button"
              >
                {mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
                Upload
              </Button>
            </div>
            <input
              accept=".csv,.xlsx"
              className="hidden"
              onChange={(event) => handleFile(event.target.files?.[0])}
              ref={inputRef}
              type="file"
            />
          </div>

          {selectedFile ? (
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
              Selected file: <span className="font-medium text-white">{selectedFile.name}</span>
            </div>
          ) : null}

          {mutation.isPending ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm text-slate-400">
                <span>Uploading...</span>
                <span>{progress}%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-sky-400 transition-all" style={{ width: `${progress}%` }} />
              </div>
            </div>
          ) : null}

          {mutation.data ? (
            <div className="grid gap-4 md:grid-cols-2">
              <SummaryTile label="Rows inserted" value={String(mutation.data.rows_inserted)} />
              <SummaryTile label="Rows failed" value={String(mutation.data.rows_failed)} />
              <div className="md:col-span-2 rounded-3xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Column mapping used</p>
                <pre className="mt-3 overflow-x-auto text-xs text-slate-200">{JSON.stringify(mutation.data.column_mapping_used, null, 2)}</pre>
              </div>
            </div>
          ) : null}

          {mutation.isError ? (
            <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
              {(mutation.error as Error).message}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
    </div>
  )
}