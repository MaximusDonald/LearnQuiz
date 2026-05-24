import { AxiosError } from 'axios'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { QuizQuestionView } from '../components/QuizQuestionView'
import {
  completeQuizSessionRequest,
  createQuizSessionRequest,
  submitQuizAnswerRequest,
} from '../services/quizSessionApi'
import type { SessionQuestion } from '../types/quizSession'
import styles from './QuizPage.module.css'


export function QuizPage() {
  const { quizId } = useParams()
  const navigate = useNavigate()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [questions, setQuestions] = useState<SessionQuestion[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function startQuizSession() {
      if (!quizId) {
        setError('Quiz introuvable.')
        setIsLoading(false)
        return
      }

      try {
        const response = await createQuizSessionRequest(quizId)
        setSessionId(response.session_id)
        setQuestions(response.questions)
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        setError(
          axiosError.response?.data?.detail ??
            'Impossible de démarrer cette session de quiz.',
        )
      } finally {
        setIsLoading(false)
      }
    }

    void startQuizSession()
  }, [quizId])

  const currentQuestion = questions[currentIndex] ?? null
  const progressPercentage = useMemo(() => {
    if (questions.length === 0) {
      return 0
    }
    return ((currentIndex + 1) / questions.length) * 100
  }, [currentIndex, questions.length])

  async function handleSubmit(answer: string) {
    if (!sessionId || !currentQuestion) {
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      await submitQuizAnswerRequest(sessionId, currentQuestion.id, answer)

      if (currentIndex === questions.length - 1) {
        await completeQuizSessionRequest(sessionId)
        navigate(`/quiz/${sessionId}/results`, { replace: true })
      } else {
        setCurrentIndex((index) => index + 1)
      }
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(
        axiosError.response?.data?.detail ??
          'Impossible d’enregistrer cette réponse.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <Link className={styles.backLink} to="/courses">
          Retour aux cours
        </Link>
        <span className={styles.kicker}>Quiz</span>
      </section>

      {isLoading ? <p className={styles.message}>Préparation du quiz...</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {!isLoading && currentQuestion ? (
        <div className={styles.layout}>
          <section className={styles.progressCard}>
            <p>
              Question {currentIndex + 1} sur {questions.length}
            </p>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </section>

          <QuizQuestionView
            question={currentQuestion}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
          />
        </div>
      ) : null}
    </main>
  )
}
