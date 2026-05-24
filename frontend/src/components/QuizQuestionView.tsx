import { useEffect, useState } from 'react'

import type { SessionQuestion } from '../types/quizSession'
import styles from './QuizQuestionView.module.css'


interface QuizQuestionViewProps {
  question: SessionQuestion
  onSubmit: (answer: string) => Promise<void>
  isSubmitting: boolean
}


export function QuizQuestionView({
  question,
  onSubmit,
  isSubmitting,
}: QuizQuestionViewProps) {
  const [answer, setAnswer] = useState('')

  useEffect(() => {
    setAnswer('')
  }, [question.id])

  async function handleSubmit() {
    if (!answer.trim()) {
      return
    }

    await onSubmit(answer)
  }

  const isChoiceQuestion =
    question.question_type === 'mcq' || question.question_type === 'true_false'

  return (
    <section className={styles.card}>
      <h2>{question.content}</h2>

      {isChoiceQuestion && question.options ? (
        <div className={styles.options}>
          {question.options.map((option) => (
            <label key={option} className={styles.option}>
              <input
                type="radio"
                name={question.id}
                checked={answer === option}
                onChange={() => setAnswer(option)}
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      ) : (
        <textarea
          className={styles.textarea}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder="Écris ta réponse ici..."
          rows={5}
        />
      )}

      <div className={styles.actions}>
        <button
          className={styles.submitButton}
          type="button"
          onClick={() => void handleSubmit()}
          disabled={isSubmitting || !answer.trim()}
        >
          {isSubmitting ? 'Validation...' : 'Valider la réponse'}
        </button>
      </div>
    </section>
  )
}
