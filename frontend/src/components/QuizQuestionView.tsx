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
        <fieldset className={styles.fieldset}>
          <legend className="visually-hidden">Options de réponse</legend>
          <ul className={styles.optionsList}>
            {question.options.map((option) => (
              <li key={option} className={styles.optionItem}>
                <label className={styles.optionLabel}>
                  <input
                    type="radio"
                    name={question.id}
                    value={option}
                    checked={answer === option}
                    onChange={() => setAnswer(option)}
                    aria-checked={answer === option}
                  />
                  <span>{option}</span>
                </label>
              </li>
            ))}
          </ul>
        </fieldset>
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
