import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'

import { CourseChat } from '../components/CourseChat'
import { MarkdownContent } from '../components/MarkdownContent'
import {
  fetchCourseDetailRequest,
  fetchCourseMessagesRequest,
  fetchCourseProgressRequest,
  fetchCourseQuizzesRequest,
  fetchCourseRelationsRequest,
  fetchCourseSummaryRequest,
  generateCourseAssetsRequest,
} from '../services/courseApi'
import type {
  CourseDetail,
  CourseMessage,
  CourseProgressDetail,
  CourseQuiz,
  RelatedCourseSummary,
} from '../types/course'
import styles from './CourseDetailPage.module.css'

// --- UX/UI: Wrapper réutilisable pour le contenu extensible ---
interface ExpandableWrapperProps {
  children: ReactNode;
  contentLength: number;
  maxLength: number;
  maxHeight?: string;
}

function ExpandableWrapper({ children, contentLength, maxLength, maxHeight = '180px' }: ExpandableWrapperProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isLongContent = contentLength > maxLength;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div
        style={{
          maxHeight: isExpanded || !isLongContent ? 'none' : maxHeight,
          overflow: 'hidden',
          transition: 'max-height 0.3s ease',
          // Crée un effet de fondu transparent vers le bas quand c'est réduit
          WebkitMaskImage: !isExpanded && isLongContent 
            ? 'linear-gradient(to bottom, black 60%, transparent 100%)' 
            : 'none',
          maskImage: !isExpanded && isLongContent 
            ? 'linear-gradient(to bottom, black 60%, transparent 100%)' 
            : 'none',
        }}
      >
        {children}
      </div>
      
      {isLongContent && (
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            alignSelf: 'flex-start',
            background: 'none',
            border: 'none',
            color: 'var(--primary-color, #007bff)',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem',
            padding: '0.25rem 0',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem'
          }}
        >
          {isExpanded ? 'Voir moins ▲' : 'Voir plus ▼'}
        </button>
      )}
    </div>
  );
}

export function CourseDetailPage() {
  const { courseId } = useParams()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [messages, setMessages] = useState<CourseMessage[]>([])
  const [summary, setSummary] = useState<string | null>(null)
  const [quizzes, setQuizzes] = useState<CourseQuiz[]>([])
  const [progress, setProgress] = useState<CourseProgressDetail | null>(null)
  const [relations, setRelations] = useState<RelatedCourseSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    async function loadCourse() {
      if (!courseId) {
        setError('Cours introuvable.')
        setIsLoading(false)
        return
      }

      try {
        const [
          courseResponse,
          messagesResponse,
          summaryResponse,
          quizzesResponse,
          progressResponse,
          relationsResponse,
        ] = await Promise.all([
          fetchCourseDetailRequest(courseId),
          fetchCourseMessagesRequest(courseId),
          fetchCourseSummaryRequest(courseId),
          fetchCourseQuizzesRequest(courseId),
          fetchCourseProgressRequest(courseId),
          fetchCourseRelationsRequest(courseId),
        ])

        setCourse(courseResponse)
        setMessages(messagesResponse)
        setSummary(summaryResponse.summary)
        setQuizzes(quizzesResponse)
        setProgress(progressResponse)
        setRelations(relationsResponse)
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        setError(axiosError.response?.data?.detail ?? 'Impossible de charger le cours.')
      } finally {
        setIsLoading(false)
      }
    }

    void loadCourse()
  }, [courseId])

  async function handleGenerateQuiz() {
    if (!courseId) {
      return
    }

    setError(null)
    setIsGenerating(true)

    try {
      const response = await generateCourseAssetsRequest(courseId, 'medium')
      setSummary(response.summary)
      setQuizzes((currentQuizzes) => [response.quiz, ...currentQuizzes])
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      setError(
        axiosError.response?.data?.detail ??
          'Impossible de generer le resume et le quiz pour ce cours.',
      )
    } finally {
      setIsGenerating(false)
    }
  }

  // Constantes pour définir le seuil (en caractères) à partir duquel on ajoute le bouton
  const MAX_SUMMARY_LENGTH = 400
  const MAX_TEXT_LENGTH = 400

  return (
    <main className={styles.page}>
      <Link className={styles.backLink} to="/courses">
        Retour aux cours
      </Link>

      {isLoading ? <p className={styles.message}>Chargement du cours...</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {course ? (
        <div className={styles.layout}>
          <section className={styles.card}>
            <div className={styles.heading}>
              <span className={styles.kicker}>
                {course.file_type?.toUpperCase() ?? 'COURSE'}
              </span>
              <h1>{course.title}</h1>
              <p>Statut: {course.status}</p>
            </div>

            <div className={styles.meta}>
              <span>Fichier: {course.file_name ?? 'N/A'}</span>
              <span>Cree le {new Date(course.created_at).toLocaleString()}</span>
            </div>

            <div className={styles.actions}>
              <button
                className={styles.generateButton}
                type="button"
                onClick={() => void handleGenerateQuiz()}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generation en cours...' : 'Generer le quiz'}
              </button>
            </div>

            {progress ? (
              <section className={styles.progressPanel}>
                <h2>Progression sur ce cours</h2>
                <div className={styles.progressStats}>
                  <article>
                    <span>Sessions</span>
                    <strong>{progress.total_sessions}</strong>
                  </article>
                  <article>
                    <span>Meilleur score</span>
                    <strong>
                      {progress.best_score === null
                        ? 'Aucun'
                        : `${Math.round(progress.best_score * 100)}%`}
                    </strong>
                  </article>
                  <article>
                    <span>Score moyen</span>
                    <strong>{Math.round(progress.average_score * 100)}%</strong>
                  </article>
                </div>

                {progress.weak_topics.length > 0 ? (
                  <div className={styles.topicList}>
                    {progress.weak_topics.map((topic) => (
                      <span key={topic} className={styles.topicChip}>
                        {topic}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className={styles.placeholder}>
                    Les points faibles apparaitront apres les premiers quiz.
                  </p>
                )}
              </section>
            ) : null}

            <section className={styles.summaryPanel}>
              <h2>Resume</h2>
              {summary ? (
                <ExpandableWrapper 
                  contentLength={summary.length} 
                  maxLength={MAX_SUMMARY_LENGTH}
                  maxHeight="150px"
                >
                  <MarkdownContent markdown={summary} />
                </ExpandableWrapper>
              ) : (
                <p className={styles.placeholder}>Aucun resume genere pour le moment.</p>
              )}
            </section>

            <section className={styles.textPanel}>
              <h2>Texte extrait</h2>
              {course.raw_text ? (
                <ExpandableWrapper 
                  contentLength={course.raw_text.length} 
                  maxLength={MAX_TEXT_LENGTH}
                  maxHeight="200px"
                >
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', margin: 0 }}>
                    {course.raw_text}
                  </pre>
                </ExpandableWrapper>
              ) : (
                <p className={styles.placeholder}>Aucun texte extrait disponible.</p>
              )}
            </section>

            <section className={styles.quizPanel}>
              <h2>Quiz generes</h2>
              {quizzes.length === 0 ? (
                <p className={styles.placeholder}>Aucun quiz genere pour le moment.</p>
              ) : (
                <div className={styles.quizList}>
                  {quizzes.map((quiz) => (
                    <article key={quiz.id} className={styles.quizCard}>
                      <h3>{quiz.title ?? 'Quiz sans titre'}</h3>
                      <p>Difficulte: {quiz.difficulty}</p>
                      <p>Questions: {quiz.questions.length}</p>
                      <Link className={styles.startQuizLink} to={`/quiz/${quiz.id}`}>
                        Commencer ce quiz
                      </Link>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <CourseChat
              courseId={course.id}
              messages={messages}
              onMessagesChange={setMessages}
            />
          </section>

          <aside className={styles.sidebar}>
            <section className={styles.sidebarCard}>
              <span className={styles.kicker}>Cours lies</span>
              <h2>Parcours recommande</h2>
              {relations.length === 0 ? (
                <p className={styles.placeholder}>Aucun cours lie pour le moment.</p>
              ) : (
                <div className={styles.relationList}>
                  {relations.map((relation) => (
                    <Link
                      key={relation.relation_id}
                      className={styles.relationCard}
                      to={`/courses/${relation.course_id}`}
                    >
                      <strong>{relation.title}</strong>
                      <span>Type: {relation.relation_type}</span>
                      <span>Statut: {relation.status}</span>
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </aside>
        </div>
      ) : null}
    </main>
  )
}