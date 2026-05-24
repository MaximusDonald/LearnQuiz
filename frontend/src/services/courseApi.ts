import { apiClient } from './authApi'
import type {
  CourseDetail,
  CourseGenerationResponse,
  CourseListItem,
  CourseMessage,
  CourseMessageExchange,
  CourseProgressDetail,
  CourseQuiz,
  CourseSummaryResponse,
  RelatedCourseSummary,
} from '../types/course'


export async function fetchCoursesRequest(): Promise<CourseListItem[]> {
  const response = await apiClient.get<CourseListItem[]>('/api/courses')
  return response.data
}


export async function fetchCourseDetailRequest(courseId: string): Promise<CourseDetail> {
  const response = await apiClient.get<CourseDetail>(`/api/courses/${courseId}`)
  return response.data
}


export async function uploadCourseRequest(file: File): Promise<CourseDetail> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<CourseDetail>('/api/courses', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}


export async function deleteCourseRequest(courseId: string): Promise<void> {
  await apiClient.delete(`/api/courses/${courseId}`)
}


export async function generateCourseAssetsRequest(
  courseId: string,
  difficulty: 'easy' | 'medium' | 'hard' = 'medium',
): Promise<CourseGenerationResponse> {
  const response = await apiClient.post<CourseGenerationResponse>(
    `/api/courses/${courseId}/generate`,
    undefined,
    {
      params: { difficulty },
    },
  )
  return response.data
}


export async function fetchCourseSummaryRequest(
  courseId: string,
): Promise<CourseSummaryResponse> {
  const response = await apiClient.get<CourseSummaryResponse>(
    `/api/courses/${courseId}/summary`,
  )
  return response.data
}


export async function fetchCourseQuizzesRequest(courseId: string): Promise<CourseQuiz[]> {
  const response = await apiClient.get<CourseQuiz[]>(`/api/courses/${courseId}/quizzes`)
  return response.data
}


export async function fetchCourseProgressRequest(
  courseId: string,
): Promise<CourseProgressDetail> {
  const response = await apiClient.get<CourseProgressDetail>(
    `/api/courses/${courseId}/progress`,
  )
  return response.data
}


export async function fetchCourseRelationsRequest(
  courseId: string,
): Promise<RelatedCourseSummary[]> {
  const response = await apiClient.get<RelatedCourseSummary[]>(
    `/api/courses/${courseId}/relations`,
  )
  return response.data
}


export async function fetchCourseMessagesRequest(
  courseId: string,
): Promise<CourseMessage[]> {
  const response = await apiClient.get<CourseMessage[]>(`/api/courses/${courseId}/messages`)
  return response.data
}


export async function sendCourseMessageRequest(
  courseId: string,
  question: string,
): Promise<CourseMessageExchange> {
  const response = await apiClient.post<CourseMessageExchange>(
    `/api/courses/${courseId}/messages`,
    { question },
  )
  return response.data
}
