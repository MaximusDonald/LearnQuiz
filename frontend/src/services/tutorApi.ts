import { apiClient } from './authApi'

export interface TutorFeedbackResponse {
  answer_id: string
  ai_feedback: string
}

export async function fetchTutorFeedbackRequest(
  answerId: string,
): Promise<TutorFeedbackResponse> {
  const response = await apiClient.post<TutorFeedbackResponse>(
    `/api/tutor/${answerId}/analyze`,
  )
  return response.data
}
