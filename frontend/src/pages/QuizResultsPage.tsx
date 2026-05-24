import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchQuizSessionResultsRequest } from '../services/quizSessionApi'
import type { QuizSessionResult } from '../types/quizSession'
import styles from './QuizResultsPage.module.css'


export function QuizResultsPage() {
  const { sessionId } = useParams()
  const [results, setResults] = useState<QuizSessionResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

      {isLoading ? <p className={styles.message}>Chargement des résultats...</p> : null}
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
              </article>
            ))}
          </section>
        </div>
      ) : null}
    </main>
  )
}
