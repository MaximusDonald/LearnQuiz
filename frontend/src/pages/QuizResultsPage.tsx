import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchQuizSessionResultsRequest } from '../services/quizSessionApi'
import { fetchTutorFeedbackRequest } from '../services/tutorApi'
import type { QuizSessionResult } from '../types/quizSession'
import styles from './QuizResultsPage.module.css'


export function QuizResultsPage() {
  const { sessionId } = useParams()
  const [results, setResults] = useState<QuizSessionResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetchingFeedback, setFetchingFeedback] = useState<string | null>(null)

  async function handleRequestFeedback(answerId: string) {
    if (!answerId) return
    setFetchingFeedback(answerId)
    try {
      const response = await fetchTutorFeedbackRequest(answerId)
      setResults((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          answers: prev.answers.map((ans) =>
            ans.answer_id === answerId
              ? { ...ans, ai_feedback: response.ai_feedback }
              : ans
          ),
        }
      })
    } catch (err) {
      console.error(err)
      alert("Impossible de charger l'explication du Tuteur IA.")
    } finally {
      setFetchingFeedback(null)
    }
  }

  useEffect(() => {
    async function loadResults() {
      if (!sessionId) {
        setError('Session introuvable.')
        setIsLoading(false)
        return
      }

      try {
        const response = await fetchQuizSessionResultsRequest(sessionId)
        setResults(response)
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        setError(
          axiosError.response?.data?.detail ??
            'Impossible de charger les résultats du quiz.',
        )
      } finally {
        setIsLoading(false)
      }
    }

    void loadResults()
  }, [sessionId])

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <Link className={styles.backLink} to="/courses">
          Retour aux cours
        </Link>
        <span className={styles.kicker}>Résultats</span>
      </section>

      {isLoading ? (
        <div className={styles.layout}>
          <section className={`${styles.summaryCard} ${styles.skeleton}`}>
            <div className={`${styles.skeleton} ${styles.skeletonTitle}`} />
            <div className={`${styles.skeleton} ${styles.skeletonText}`} />
            <div className={`${styles.skeleton} ${styles.skeletonText}`} style={{ width: '40%' }} />
          </section>
          <section className={styles.answersList}>
            <div className={`${styles.skeleton} ${styles.skeletonCard}`} />
            <div className={`${styles.skeleton} ${styles.skeletonCard}`} />
            <div className={`${styles.skeleton} ${styles.skeletonCard}`} />
          </section>
        </div>
      ) : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {results ? (
        <div className={styles.layout}>
          <section className={styles.summaryCard}>
            <h1>{results.quiz_title ?? 'Résultats du quiz'}</h1>
            <p>
              Score global: <strong>{Math.round(results.score * 100)}%</strong>
            </p>
            <p>
              Bonnes réponses: {results.correct_answers} / {results.total_questions}
            </p>
          </section>

          <section className={styles.answersList}>
            {results.answers.map((answer, index) => (
              <article key={answer.question_id} className={styles.answerCard}>
                <div className={styles.answerHeader}>
                  <span className={styles.questionNumber}>Question {index + 1}</span>
                  <span
                    className={`${styles.statusBadge} ${
                      answer.is_correct ? styles.correct : styles.incorrect
                    }`}
                  >
                    {answer.is_correct ? 'Correcte' : 'Incorrecte'}
                  </span>
                </div>

                <h2>{answer.content}</h2>
                <p>
                  <strong>Ta réponse:</strong> {answer.user_answer}
                </p>
                <p>
                  <strong>Bonne réponse:</strong> {answer.correct_answer}
                </p>
                {answer.explanation ? (
                  <p>
                    <strong>Explication:</strong> {answer.explanation}
                  </p>
                ) : null}
                {!answer.is_correct && answer.ai_feedback ? (
                  <div className={styles.feedbackBox}>
                    <strong>Tuteur IA</strong>
                    <p>{answer.ai_feedback}</p>
                  </div>
                ) : null}
                {!answer.is_correct && !answer.ai_feedback && answer.answer_id ? (
                  <button
                    className={styles.tutorButton}
                    onClick={() => void handleRequestFeedback(answer.answer_id!)}
                    disabled={fetchingFeedback === answer.answer_id}
                  >
                    {fetchingFeedback === answer.answer_id
                      ? 'Réflexion en cours...'
                      : 'Demander une explication au Tuteur IA'}
                  </button>
                ) : null}
              </article>
            ))}
          </section>
        </div>
      ) : null}
    </main>
  )
}
