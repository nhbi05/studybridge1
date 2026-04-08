-- Migration: Add missing columns to curriculum_topics table
-- This adds support for topic metadata (description, subtopics, difficulty level)

-- Add the missing columns to curriculum_topics
ALTER TABLE curriculum_topics
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS subtopics JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS difficulty_level TEXT DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'));

-- Create an index on difficulty_level for efficient filtering
CREATE INDEX IF NOT EXISTS idx_curriculum_topics_difficulty_level ON curriculum_topics(difficulty_level);

-- Verify the migration worked by checking the table structure
-- You can run this query to verify:
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name='curriculum_topics' ORDER BY ordinal_position;
