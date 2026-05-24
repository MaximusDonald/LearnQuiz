export interface CourseListItem {
  id: string
  title: string
  file_name: string | null
  file_type: string | null
  status: 'processing' | 'ready' | 'error'
  created_at: string
  updated_at: string
}

export interface CourseDetail extends CourseListItem {
  description: string | null
  raw_text: string
  summary: string | null
}

export interface CourseSummaryResponse {
  course_id: string
  summary: string | null
}

export interface QuizQuestion {
  id: string
  content: string
  question_type: string
  options: string[] | null
  correct_answer: string
  explanation: string | null
  order_index: number
  created_at: string
  updated_at: string
}

export interface CourseQuiz {
  id: string
  title: string | null
  difficulty: string
  created_at: string
  updated_at: string
  questions: QuizQuestion[]
}

export interface CourseGenerationResponse {
  summary: string
  quiz: CourseQuiz
}

export interface CourseProgressScorePoint {
  session_id: string
  score: number
  completed_at: string | null
}

export interface CourseProgressDetail {
  course_id: string
  total_sessions: number
  best_score: number | null
  average_score: number
  score_history: CourseProgressScorePoint[]
  weak_topics: string[]
}

export interface RelatedCourseSummary {
  relation_id: string
  relation_type: 'prerequisite' | 'sequel' | 'related'
  course_id: string
  title: string
  status: 'processing' | 'ready' | 'error'
  created_at: string
}

export interface CourseMessage {
  id: string
  user_id: string
  course_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  updated_at: string
}

export interface CourseMessageExchange {
  user_message: CourseMessage
  assistant_message: CourseMessage
}
