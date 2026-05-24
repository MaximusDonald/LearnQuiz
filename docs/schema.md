-- Utilisateurs
users
  id UUID PK
  email VARCHAR UNIQUE NOT NULL
  password_hash VARCHAR (nullable si OAuth only)
  google_id VARCHAR UNIQUE (nullable)
  full_name VARCHAR
  avatar_url VARCHAR
  created_at TIMESTAMP
  updated_at TIMESTAMP

-- Cours uploadés
courses
  id UUID PK
  user_id UUID FK → users.id
  title VARCHAR NOT NULL
  description TEXT
  file_name VARCHAR
  file_type ENUM('pdf', 'txt', 'md')
  raw_text TEXT               -- texte extrait du fichier
  summary TEXT                -- résumé généré par Gemini
  status ENUM('processing', 'ready', 'error')
  created_at TIMESTAMP
  updated_at TIMESTAMP

-- Relations inter-cours (ex: CNN → Deep Learning → ML)
course_relations
  id UUID PK
  course_id UUID FK → courses.id
  related_course_id UUID FK → courses.id
  relation_type VARCHAR        -- 'prerequisite' | 'sequel' | 'related'

-- Quiz générés
quizzes
  id UUID PK
  course_id UUID FK → courses.id
  title VARCHAR
  difficulty ENUM('easy', 'medium', 'hard')
  generated_at TIMESTAMP

-- Questions
questions
  id UUID PK
  quiz_id UUID FK → quizzes.id
  content TEXT NOT NULL
  question_type ENUM('mcq', 'true_false', 'open')
  options JSONB               -- ['option A', 'option B', ...]
  correct_answer TEXT
  explanation TEXT            -- explication de la bonne réponse
  order_index INTEGER

-- Sessions de quiz (une tentative)
quiz_sessions
  id UUID PK
  user_id UUID FK → users.id
  quiz_id UUID FK → quizzes.id
  started_at TIMESTAMP
  completed_at TIMESTAMP
  score FLOAT                 -- ex: 0.75 pour 75%

-- Réponses de l'utilisateur
user_answers
  id UUID PK
  session_id UUID FK → quiz_sessions.id
  question_id UUID FK → questions.id
  user_answer TEXT
  is_correct BOOLEAN
  ai_feedback TEXT            -- explication personnalisée du tuteur IA
  answered_at TIMESTAMP

-- Historique de progression par cours
course_progress
  id UUID PK
  user_id UUID FK → users.id
  course_id UUID FK → courses.id
  total_sessions INTEGER DEFAULT 0
  best_score FLOAT
  last_session_at TIMESTAMP
  weak_topics JSONB           -- topics où l'user fait des erreurs

-- Messages Q&A sur un cours
course_messages
  id UUID PK
  user_id UUID FK → users.id
  course_id UUID FK → courses.id
  role ENUM('user', 'assistant')
  content TEXT
  created_at TIMESTAMP