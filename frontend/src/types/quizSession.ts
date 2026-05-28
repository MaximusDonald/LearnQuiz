export interface SessionQuestion {
  id: string
  content: string
  question_type: string
  options: string[] | null
  order_index: number
}

export interface QuizSessionCreateResponse {
  session_id: string
  quiz_id: string
  questions: SessionQuestion[]
}

export interface SubmitAnswerResponse {
  answer_id: string
  question_id: string
  is_correct: boolean
  correct_answer: string
  explanation: string | null
  ai_feedback: string | null
}

export interface CompleteQuizSessionResponse {
  session_id: string
  score: number
  total_questions: number
  correct_answers: number
}

export interface ResultAnswer {
  answer_id?: string
  question_id: string
  content: string
  question_type: string
  options: string[] | null
  correct_answer: string
  explanation: string | null
  user_answer: string
  is_correct: boolean
  ai_feedback: string | null
}

export interface QuizSessionResult {
  session_id: string
  quiz_id: string
  quiz_title: string | null
  score: number
  total_questions: number
  correct_answers: number
  started_at: string | null
  completed_at: string | null
  answers: ResultAnswer[]
}
