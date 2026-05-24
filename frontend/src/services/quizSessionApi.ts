import { apiClient } from './authApi'
import type {
  CompleteQuizSessionResponse,
  QuizSessionCreateResponse,
  QuizSessionResult,
  SubmitAnswerResponse,
} from '../types/quizSession'


export async function createQuizSessionRequest(
  quizId: string,
): Promise<QuizSessionCreateResponse> {
  const response = await apiClient.post<QuizSessionCreateResponse>('/api/quiz-sessions', {
    quiz_id: quizId,
  })
  return response.data
}


export async function submitQuizAnswerRequest(
  sessionId: string,
  questionId: string,
  userAnswer: string,
): Promise<SubmitAnswerResponse> {
  const response = await apiClient.post<SubmitAnswerResponse>(
    `/api/quiz-sessions/${sessionId}/answers`,
    {
      question_id: questionId,
      user_answer: userAnswer,
    },
  )
  return response.data
}


export async function completeQuizSessionRequest(
  sessionId: string,
): Promise<CompleteQuizSessionResponse> {
  const response = await apiClient.post<CompleteQuizSessionResponse>(
    `/api/quiz-sessions/${sessionId}/complete`,
  )
  return response.data
}


export async function fetchQuizSessionResultsRequest(
  sessionId: string,
): Promise<QuizSessionResult> {
  const response = await apiClient.get<QuizSessionResult>(
    `/api/quiz-sessions/${sessionId}/results`,
  )
  return response.data
}
