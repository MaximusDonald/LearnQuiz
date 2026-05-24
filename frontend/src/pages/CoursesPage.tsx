import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { CourseUpload } from '../components/CourseUpload'
import {
  deleteCourseRequest,
  fetchCoursesRequest,
  uploadCourseRequest,
} from '../services/courseApi'
import type { CourseListItem } from '../types/course'
import styles from './CoursesPage.module.css'


function formatStatusLabel(status: CourseListItem['status']): string {
  if (status === 'ready') {
    return 'Prêt'
  }
  if (status === 'processing') {
    return 'Traitement'
  }
  return 'Erreur'
}


export function CoursesPage() {
  const [courses, setCourses] = useState<CourseListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadCourses() {
      try {
        const response = await fetchCoursesRequest()
        setCourses(response)
      } catch {
        setError('Impossible de charger les cours.')
      } finally {
        setIsLoading(false)
      }
    }

    void loadCourses()
  }, [])

  async function handleUpload(file: File) {
    setError(null)
    setIsUploading(true)

    try {
      const course = await uploadCourseRequest(file)
      setCourses((currentCourses) => [course, ...currentCourses])
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(axiosError.response?.data?.detail ?? 'Upload impossible pour le moment.')
    } finally {
      setIsUploading(false)
    }
  }

  async function handleDelete(courseId: string) {
    try {
      await deleteCourseRequest(courseId)
      setCourses((currentCourses) =>
        currentCourses.filter((course) => course.id !== courseId),
      )
    } catch {
      setError('Suppression impossible pour le moment.')
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <div>
          <span className={styles.kicker}>Cours</span>
          <h1>Bibliothèque personnelle</h1>
          <p>Importe tes supports et retrouve leur texte extrait instantanément.</p>
        </div>
        <Link className={styles.backLink} to="/dashboard">
          Retour au dashboard
        </Link>
      </section>

      <CourseUpload isUploading={isUploading} onUpload={handleUpload} />

      {error ? <p className={styles.error}>{error}</p> : null}

      {isLoading ? (
        <p className={styles.emptyState}>Chargement des cours...</p>
      ) : courses.length === 0 ? (
        <p className={styles.emptyState}>Aucun cours importé pour le moment.</p>
      ) : (
        <section className={styles.grid}>
          {courses.map((course) => (
            <article key={course.id} className={styles.card}>
              <div className={styles.cardHeader}>
                <span
                  className={`${styles.statusBadge} ${
                    course.status === 'ready'
                      ? styles.ready
                      : course.status === 'processing'
                        ? styles.processing
                        : styles.errorStatus
                  }`}
                >
                  {formatStatusLabel(course.status)}
                </span>
                <button
                  className={styles.deleteButton}
                  type="button"
                  onClick={() => void handleDelete(course.id)}
                >
                  Supprimer
                </button>
              </div>
              <h2>{course.title}</h2>
              <p>{course.file_name ?? 'Fichier sans nom'}</p>
              <div className={styles.cardMeta}>
                <span>{course.file_type?.toUpperCase() ?? 'N/A'}</span>
                <span>{new Date(course.created_at).toLocaleString()}</span>
              </div>
              <Link className={styles.detailLink} to={`/courses/${course.id}`}>
                Voir le détail
              </Link>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}
