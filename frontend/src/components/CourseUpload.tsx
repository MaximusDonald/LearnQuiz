import { useRef, useState } from 'react'
import type { DragEvent } from 'react'

import styles from './CourseUpload.module.css'


interface CourseUploadProps {
  isUploading: boolean
  onUpload: (file: File) => Promise<void>
}


const acceptedMimeTypes = new Set([
  'application/pdf',
  'text/plain',
  'text/markdown',
  'text/x-markdown',
])


function isSupportedFile(file: File): boolean {
  return acceptedMimeTypes.has(file.type) || /\.(pdf|txt|md)$/i.test(file.name)
}


export function CourseUpload({ isUploading, onUpload }: CourseUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  async function handleFile(file: File | null) {
    if (!file) {
      return
    }

    if (!isSupportedFile(file)) {
      setError('Seuls les fichiers PDF, TXT et MD sont acceptés.')
      return
    }

    setError(null)
    await onUpload(file)
  }

  async function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault()
    setDragActive(false)
    const file = event.dataTransfer.files.item(0)
    await handleFile(file)
  }

  return (
    <section className={styles.wrapper}>
      <button
        className={`${styles.dropzone} ${dragActive ? styles.active : ''}`}
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(event) => void handleDrop(event)}
        disabled={isUploading}
      >
        <span className={styles.badge}>Import de cours</span>
        <strong>{isUploading ? 'Extraction en cours...' : 'Glisse ton fichier ici'}</strong>
        <p>Ou clique pour choisir un fichier PDF, TXT ou Markdown de 10MB maximum.</p>
      </button>

      <input
        ref={inputRef}
        className={styles.input}
        type="file"
        accept=".pdf,.txt,.md,text/plain,text/markdown,application/pdf"
        onChange={(event) => void handleFile(event.target.files?.item(0) ?? null)}
      />

      {error ? <p className={styles.error}>{error}</p> : null}
    </section>
  )
}
