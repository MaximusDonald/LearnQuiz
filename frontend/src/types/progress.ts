export interface RecentCourseProgress {
  course_id: string
  title: string
  latest_score: number | null
  best_score: number | null
  total_sessions: number
  last_session_at: string | null
}

export interface GlobalProgress {
  total_courses: number
  total_quiz_sessions: number
  average_score: number
  weak_topics: string[]
  recent_courses: RecentCourseProgress[]
}
