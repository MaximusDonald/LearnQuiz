import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { fetchGlobalProgressRequest } from '../services/progressApi'
import { useAuthStore } from '../store/useAuthStore'
import type { GlobalProgress } from '../types/progress'
import styles from './DashboardPage.module.css'


function formatScore(score: number | null): string {
  if (score === null) {
    return 'Pas encore de score'
  }

  return `${Math.round(score * 100)}%`
}


export function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const [progress, setProgress] = useState<GlobalProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadProgress() {
      try {
        const response = await fetchGlobalProgressRequest()
        setProgress(response)
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        setError(
          axiosError.response?.data?.detail ??
            'Impossible de charger le tableau de bord de progression.',
        )
      } finally {
        setIsLoading(false)
      }
    }

    void loadProgress()
  }, [])

  return (
    <main className={styles.page}>
      <section className={styles.heroCard}>
        <span className={styles.kicker}>Progression</span>
        <h1>Bonjour {user?.full_name ?? user?.email ?? 'sur LearnQUIZ'}</h1>
        <p>
          Voici un apercu de ton rythme d&apos;etude, des quiz deja passes et des
          notions a retravailler en priorite.
        </p>
        <div className={styles.actions}>
          <Link className={styles.primaryAction} to="/courses">
            Voir mes cours
          </Link>
          <Link className={styles.secondaryAction} to="/quiz">
            Revenir aux quiz
          </Link>
        </div>
      </section>

      {isLoading ? <p className={styles.message}>Chargement des statistiques...</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {progress ? (
        <>
          <section className={styles.statsGrid}>
            <article className={styles.statCard}>
              <span className={styles.statLabel}>Cours importes</span>
              <strong>{progress.total_courses}</strong>
            </article>
            <article className={styles.statCard}>
              <span className={styles.statLabel}>Quiz passes</span>
              <strong>{progress.total_quiz_sessions}</strong>
            </article>
            <article className={styles.statCard}>
              <span className={styles.statLabel}>Score moyen</span>
              <strong>{formatScore(progress.average_score)}</strong>
            </article>
          </section>

          <section className={styles.contentGrid}>
            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <span className={styles.kicker}>Cours recents</span>
                  <h2>Scores par cours</h2>
                </div>
                <Link className={styles.inlineLink} to="/courses">
                  Tous les cours
                </Link>
              </div>

              {progress.recent_courses.length === 0 ? (
                <p className={styles.placeholder}>
                  Aucun cours n&apos;a encore ete travaille. Commence par importer un cours
                  puis lance un quiz.
                </p>
              ) : (
                <div className={styles.courseList}>
                  {progress.recent_courses.map((course) => (
                    <article key={course.course_id} className={styles.courseCard}>
                      <div>
                        <h3>{course.title}</h3>
                        <p>
                          {course.total_sessions} session
                          {course.total_sessions > 1 ? 's' : ''}
                        </p>
                      </div>

                      <div className={styles.scoreMeta}>
                        <span>Dernier score: {formatScore(course.latest_score)}</span>
                        <span>Meilleur score: {formatScore(course.best_score)}</span>
                        <Link className={styles.inlineLink} to={`/courses/${course.course_id}`}>
                          Ouvrir le cours
                        </Link>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <aside className={styles.panel}>
              <span className={styles.kicker}>Points a retravailler</span>
              <h2>Themes faibles</h2>
              {progress.weak_topics.length === 0 ? (
                <p className={styles.placeholder}>
                  Les points faibles apparaitront apres quelques reponses incorrectes en quiz.
                </p>
              ) : (
                <div className={styles.topicList}>
                  {progress.weak_topics.map((topic) => (
                    <span key={topic} className={styles.topicChip}>
                      {topic}
                    </span>
                  ))}
                </div>
              )}
            </aside>
          </section>
        </>
      ) : null}
    </main>
  )
}
