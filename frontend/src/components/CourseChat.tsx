import { AxiosError } from 'axios'
import { useState } from 'react'
import type { KeyboardEvent } from 'react'

import { sendCourseMessageRequest } from '../services/courseApi'
import type { CourseMessage } from '../types/course'
import styles from './CourseChat.module.css'


interface CourseChatProps {
  courseId: string
  messages: CourseMessage[]
  onMessagesChange: (messages: CourseMessage[]) => void
}


export function CourseChat({
  courseId,
  messages,
  onMessagesChange,
}: CourseChatProps) {
  const [question, setQuestion] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSending, setIsSending] = useState(false)

  async function handleSend() {
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion) {
      return
    }

    setError(null)
    setIsSending(true)

    try {
      const exchange = await sendCourseMessageRequest(courseId, trimmedQuestion)
      onMessagesChange([...messages, exchange.user_message, exchange.assistant_message])
      setQuestion('')
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(
        axiosError.response?.data?.detail ??
          'Impossible d’envoyer cette question pour le moment.',
      )
    } finally {
      setIsSending(false)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
    }
  }

  return (
    <section className={styles.chatPanel}>
      <div className={styles.header}>
        <h2>Chat Q&A</h2>
        <p>Pose une question sur ce cours. Le tuteur répond à partir du contenu importé.</p>
      </div>

      <div className={styles.messages}>
        {messages.length === 0 ? (
          <p className={styles.placeholder}>
            Aucune question pour le moment. Commence la discussion ci-dessous.
          </p>
        ) : (
          messages.map((message) => (
            <article
              key={message.id}
              className={`${styles.messageBubble} ${
                message.role === 'user' ? styles.userBubble : styles.assistantBubble
              }`}
            >
              <span className={styles.messageRole}>
                {message.role === 'user' ? 'Toi' : 'Professeur IA'}
              </span>
              <p>{message.content}</p>
            </article>
          ))
        )}
      </div>

      {error ? <p className={styles.error}>{error}</p> : null}

      <div className={styles.composer}>
        <textarea
          className={styles.input}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pose ta question sur le cours..."
          rows={3}
          disabled={isSending}
        />
        <button
          className={styles.sendButton}
          type="button"
          onClick={() => void handleSend()}
          disabled={isSending || !question.trim()}
        >
          {isSending ? 'Envoi...' : 'Envoyer'}
        </button>
      </div>
    </section>
  )
}
