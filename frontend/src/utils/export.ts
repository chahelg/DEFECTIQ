import type { Defect } from '@types'

function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.click()
  URL.revokeObjectURL(url)
}

export function exportDefectsToCsv(rows: Defect[], fileName = 'defectiq-defects.csv') {
  const headers = [
    'ticketNumber',
    'title',
    'status',
    'priority',
    'assignmentGroup',
    'assignedTo',
    'slaBreached',
    'updatedAt',
  ]

  const csv = [headers.join(',')]
    .concat(
      rows.map((row) =>
        [
          row.ticketNumber,
          row.title,
          row.status,
          row.priority,
          row.assignmentGroup,
          row.assignedTo,
          row.slaBreached ? 'Yes' : 'No',
          row.updatedAt,
        ]
          .map((value) => `"${String(value).replaceAll('"', '""')}"`)
          .join(','),
      ),
    )
    .join('\n')

  downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8;' }), fileName)
}

export function exportJson<T>(data: T, fileName = 'defectiq-export.json') {
  downloadBlob(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8;' }), fileName)
}