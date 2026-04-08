-- StudyBridge Complete Database Schema for Supabase
-- Copy and paste this entire script into Supabase SQL Editor

-- ============================================
-- Enable Extensions
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";


-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  year_of_study INTEGER DEFAULT 1 CHECK (year_of_study >= 1 AND year_of_study <= 4),
  semester INTEGER DEFAULT 1 CHECK (semester >= 1 AND semester <= 2),
  course TEXT DEFAULT 'CS',
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


-- ============================================
-- 2. CURRICULUMS TABLE (Parent/Metadata)
-- ============================================
CREATE TABLE IF NOT EXISTS curriculums (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_url TEXT,
  summary TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ensure indexes exist (idempotent with CREATE INDEX IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_curriculums_user_id ON curriculums(user_id);
CREATE INDEX IF NOT EXISTS idx_curriculums_created_at ON curriculums(created_at DESC);

-- Drop old JSONB topics column if it exists (migrate from old schema)
ALTER TABLE curriculums DROP COLUMN IF EXISTS topics;


-- ============================================
-- 2B. CURRICULUM_TOPICS TABLE (The Engine - pgvector)
-- ============================================
CREATE TABLE IF NOT EXISTS curriculum_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  curriculum_id UUID NOT NULL REFERENCES curriculums(id) ON DELETE CASCADE,
  topic_name TEXT NOT NULL,
  description TEXT DEFAULT '',
  subtopics JSONB DEFAULT '[]',
  difficulty_level TEXT DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  embedding VECTOR(384) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_curriculum_topics_curriculum_id ON curriculum_topics(curriculum_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_topics_embedding ON curriculum_topics USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_curriculum_topics_difficulty_level ON curriculum_topics(difficulty_level);


-- ============================================
-- 3. RESOURCES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS resources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('video', 'article', 'exercise', 'book', 'course')),
  topic TEXT NOT NULL,
  summary TEXT,
  url TEXT,
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', NULL)),
  duration_minutes INTEGER,
  embedding VECTOR(384),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_resources_topic ON resources(topic);
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
CREATE INDEX IF NOT EXISTS idx_resources_difficulty ON resources(difficulty);
-- Vector search index
CREATE INDEX IF NOT EXISTS idx_resources_embedding ON resources USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- ============================================
-- 4. RECOMMENDATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS recommendations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  relevance_score FLOAT NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 1),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_resource ON recommendations(user_id, resource_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON recommendations(relevance_score DESC);


-- ============================================
-- 5. EMBEDDINGS TABLE (Cache)
-- ============================================
CREATE TABLE IF NOT EXISTS embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  text_id TEXT UNIQUE NOT NULL,
  text_type TEXT NOT NULL CHECK (text_type IN ('topic', 'resource', 'query')),
  embedding VECTOR(384) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_text_id ON embeddings(text_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_type ON embeddings(text_type);


-- ============================================
-- 6. CHAT SESSIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  curriculum_id UUID REFERENCES curriculums(id) ON DELETE SET NULL,
  title TEXT DEFAULT 'Chat Session',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);


-- ============================================
-- 7. CHAT MESSAGES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  filters_applied JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);


-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Sample user
INSERT INTO users (email, name) 
VALUES ('student@example.com', 'John Doe')
ON CONFLICT DO NOTHING;

-- Sample resources
INSERT INTO resources (title, type, topic, summary, difficulty, duration_minutes)
VALUES 
  ('Linear Algebra Fundamentals', 'video', 'Mathematics', 'Comprehensive introduction to vectors and matrices', 'beginner', 120),
  ('Advanced Calculus Concepts', 'article', 'Mathematics', 'Deep dive into multivariable calculus', 'advanced', NULL),
  ('Data Structures Practice', 'exercise', 'Computer Science', 'Interactive coding problems', 'intermediate', 90),
  ('Web Development Basics', 'course', 'Web Development', 'HTML, CSS, JavaScript fundamentals', 'beginner', 480),
  ('Machine Learning Theory', 'book', 'Artificial Intelligence', 'Mathematical foundations of ML', 'advanced', NULL)
ON CONFLICT DO NOTHING;


-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users (drop and recreate to ensure correct state)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for curriculums
DROP TRIGGER IF EXISTS update_curriculums_updated_at ON curriculums;
CREATE TRIGGER update_curriculums_updated_at
BEFORE UPDATE ON curriculums
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for resources
DROP TRIGGER IF EXISTS update_resources_updated_at ON resources;
CREATE TRIGGER update_resources_updated_at
BEFORE UPDATE ON resources
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for chat_sessions
DROP TRIGGER IF EXISTS update_chat_sessions_updated_at ON chat_sessions;
CREATE TRIGGER update_chat_sessions_updated_at
BEFORE UPDATE ON chat_sessions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- RPC FUNCTIONS FOR SEMANTIC SEARCH
-- ============================================

-- Match resources by vector similarity (pgvector cosine distance)
CREATE OR REPLACE FUNCTION match_resources (
  query_embedding vector(384),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  title text,
  type text,
  topic text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    resources.id,
    resources.title,
    resources.type,
    resources.topic,
    1 - (resources.embedding <=> query_embedding) AS similarity
  FROM resources
  WHERE resources.embedding IS NOT NULL
    AND 1 - (resources.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- Match curriculum topics by vector similarity
CREATE OR REPLACE FUNCTION match_curriculum_topics (
  query_embedding vector(384),
  curriculum_id_filter uuid DEFAULT NULL,
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  curriculum_id uuid,
  topic_name text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    curriculum_topics.id,
    curriculum_topics.curriculum_id,
    curriculum_topics.topic_name,
    1 - (curriculum_topics.embedding <=> query_embedding) AS similarity
  FROM curriculum_topics
  WHERE (curriculum_id_filter IS NULL OR curriculum_topics.curriculum_id = curriculum_id_filter)
    AND 1 - (curriculum_topics.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;


-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE curriculums ENABLE ROW LEVEL SECURITY;
ALTER TABLE curriculum_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

-- ============ USERS TABLE POLICIES ============
CREATE POLICY "Users can view their own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- ============ CURRICULUMS TABLE POLICIES ============
CREATE POLICY "Users can view their own curriculums"
  ON curriculums FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert curriculums for themselves"
  ON curriculums FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own curriculums"
  ON curriculums FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own curriculums"
  ON curriculums FOR DELETE
  USING (auth.uid() = user_id);

-- ============ CURRICULUM_TOPICS TABLE POLICIES ============
CREATE POLICY "Users can view topics from their curriculums"
  ON curriculum_topics FOR SELECT
  USING (
    curriculum_id IN (
      SELECT id FROM curriculums WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert topics for their curriculums"
  ON curriculum_topics FOR INSERT
  WITH CHECK (
    curriculum_id IN (
      SELECT id FROM curriculums WHERE user_id = auth.uid()
    )
  );

-- ============ CHAT_SESSIONS TABLE POLICIES ============
CREATE POLICY "Users can view their own chat sessions"
  ON chat_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create chat sessions"
  ON chat_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own chat sessions"
  ON chat_sessions FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ============ CHAT_MESSAGES TABLE POLICIES ============
CREATE POLICY "Users can view messages from their sessions"
  ON chat_messages FOR SELECT
  USING (
    session_id IN (
      SELECT id FROM chat_sessions WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert messages in their sessions"
  ON chat_messages FOR INSERT
  WITH CHECK (
    auth.uid() = user_id AND
    session_id IN (
      SELECT id FROM chat_sessions WHERE user_id = auth.uid()
    )
  );

-- ============ RECOMMENDATIONS TABLE POLICIES ============
CREATE POLICY "Users can view their own recommendations"
  ON recommendations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "System can insert recommendations for users"
  ON recommendations FOR INSERT
  WITH CHECK (auth.uid() = user_id);


-- ============================================
-- STORAGE RLS POLICIES (Execute in Supabase UI)
-- ============================================
-- NOTE: Storage policies must be created via Supabase Dashboard UI
-- Go to: Storage → curriculums → Policies → New Policy
-- 
-- Use the code blocks below:
-- 
-- POLICY 1: Read own files
-- ========================
-- Policy name: Read own curriculum files
-- Allowed operation: SELECT
-- Target roles: authenticated
-- Using expression:
--   (bucket_id = 'curriculums') AND 
--   ((storage.foldername(name))[1] = (auth.uid())::text)
--
-- POLICY 2: Upload to own folder
-- ==============================
-- Policy name: Upload curriculum files
-- Allowed operation: INSERT
-- Target roles: authenticated
-- With check expression:
--   (bucket_id = 'curriculums') AND 
--   ((storage.foldername(name))[1] = (auth.uid())::text)
--
-- POLICY 3: Delete own files
-- ==========================
-- Policy name: Delete own curriculum files
-- Allowed operation: DELETE
-- Target roles: authenticated
-- Using expression:
--   (bucket_id = 'curriculums') AND 
--   ((storage.foldername(name))[1] = (auth.uid())::text)
