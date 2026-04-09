/**
 * StudyBridge API Client
 * Centralized API calls to backend with Supabase auth
 */

import { createClient } from '@supabase/supabase-js';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY || ''
);

// Get authorization header with Supabase token
async function getAuthHeader(): Promise<Record<string, string>> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      return {
        Authorization: `Bearer ${session.access_token}`,
      };
    }
  } catch (err) {
    console.error('Failed to get auth token:', err);
  }
  return {};
}

interface CurriculumRequest {
  // user_id is now extracted from authentication token
}

interface RecommendationRequest {
  // user_id is now extracted from authentication token
  curriculum_id?: string;
  topic?: string;
  difficulty?: string;
  resource_types?: string[];
  limit?: number;
}

interface ChatRequest {
  // user_id is now extracted from authentication token
  curriculum_id?: string;
  current_recommendations?: string[];
  conversation_history?: Array<{ role: 'user' | 'assistant'; content: string }>;
  user_message: string;
}

// ============ Response Types ============

interface CurriculumResponse {
  curriculum_id: string;
  user_id: string;
  file_name: string;
  file_url: string;
  topics_extracted: Array<{
    name: string;
    description: string;
    subtopics?: string[];
    difficulty_level?: string;
  }>;
  total_topics: number;
  summary: string;
}

interface RecommendationResponse {
  recommendations: Array<{
    id: string;
    title: string;
    type: string;
    topic: string;
    relevance_score: number;
    summary: string;
    metadata?: Record<string, unknown>;
  }>;
  query_topic?: string;
  total_results: number;
  timestamp?: string;
}

interface ChatResponse {
  assistant_message: string;
  confidence_score?: number;
  updated_filters?: Record<string, unknown>;
  suggested_resources?: string[];
}

interface ChatSession {
  session_id: string;
  user_id: string;
  curriculum_id?: string;
  title: string;
  created_at: string;
}

interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface HealthResponse {
  status: string;
  timestamp: string;
}

/**
 * Handle fetch errors with consistent error format
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: `API Error: ${response.statusText}`,
    }));
    throw new Error(error.detail || error.error || 'API request failed');
  }
  return response.json();
}

export const api = {
  // ============ Curriculum Endpoints ============

  curriculum: {
    /**
     * Upload and parse a curriculum file
     * User ID is extracted from authentication token
     */
    upload: async (file: File): Promise<CurriculumResponse> => {
      const formData = new FormData();
      formData.append('file', file);
      const authHeaders = await getAuthHeader();

      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/upload`,
        {
          method: 'POST',
          headers: authHeaders,
          body: formData,
        }
      );

      return handleResponse<CurriculumResponse>(response);
    },

    /**
     * Get all curriculums for authenticated user
     */
    list: async (): Promise<{ curriculums: CurriculumResponse[] }> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/list`,
        { headers: authHeaders }
      );

      return handleResponse<{ curriculums: CurriculumResponse[] }>(response);
    },

    /**
     * Get a specific curriculum
     */
    get: async (curriculumId: string): Promise<CurriculumResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/${encodeURIComponent(curriculumId)}`,
        { headers: authHeaders }
      );

      return handleResponse<CurriculumResponse>(response);
    },
  },

  // ============ Recommendations Endpoints ============

  recommendations: {
    /**
     * Get personalized recommendations for authenticated user
     */
    get: async (request: RecommendationRequest): Promise<RecommendationResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/get`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify(request),
        }
      );

      return handleResponse<RecommendationResponse>(response);
    },

    /**
     * Get all recommendations for authenticated user
     */
    getUserRecommendations: async (limit: number = 20): Promise<RecommendationResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/user?limit=${limit}`,
        { headers: authHeaders }
      );

      return handleResponse<RecommendationResponse>(response);
    },

    /**
     * Find resources similar to a given resource
     */
    getSimilar: async (resourceId: string, limit: number = 5): Promise<RecommendationResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/similar/${encodeURIComponent(resourceId)}?limit=${limit}`,
        { headers: authHeaders }
      );

      return handleResponse<RecommendationResponse>(response);
    },

    /**
     * Rerank resources using LLM
     */
    rerank: async (resources: string[], userContext: string, limit: number = 10): Promise<RecommendationResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/rerank`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify({
            resources,
            user_context: userContext,
            limit,
          }),
        }
      );

      return handleResponse<RecommendationResponse>(response);
    },
  },

  // ============ Chat Endpoints ============

  chat: {
    /**
     * Send a message to the AI advisor (requires authentication)
     */
    sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/chat/message`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify(request),
        }
      );

      return handleResponse<ChatResponse>(response);
    },

    /**
     * Create a new chat session for authenticated user
     */
    createSession: async (): Promise<ChatSession> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/chat/session`,
        {
          method: 'POST',
          headers: authHeaders,
        }
      );

      return handleResponse<ChatSession>(response);
    },

    /**
     * Get chat history for a session
     */
    getHistory: async (sessionId: string): Promise<{ messages: ChatMessage[] }> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/chat/history/${encodeURIComponent(sessionId)}`,
        { headers: authHeaders }
      );

      return handleResponse<{ messages: ChatMessage[] }>(response);
    },
  },

  // ============ Health Check ============

  /**
   * Check API health status
   */
  health: async (): Promise<HealthResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return handleResponse<HealthResponse>(response);
    } catch (error) {
      return { status: 'error', timestamp: new Date().toISOString() };
    }
  },

  // ============ Profile Endpoints ============

  profile: {
    /**
     * Get current user profile
     */
    get: async (): Promise<any> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/auth/profile`,
        { headers: authHeaders }
      );
      return handleResponse(response);
    },

    /**
     * Update user profile
     */
    update: async (profileData: any): Promise<any> => {
      const authHeaders = await getAuthHeader();
      // Only send fields that backend expects (UserProfileUpdate)
      const updateData = {
        name: profileData.name,
        year_of_study: profileData.year_of_study,
        semester: profileData.semester,
        course: profileData.course,
      };
      const response = await fetch(
        `${API_BASE_URL}/api/auth/profile`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify(updateData),
        }
      );
      return handleResponse(response);
    },

    /**
     * Delete user profile
     */
    delete: async (): Promise<any> => {
      const authHeaders = await getAuthHeader();
      const response = await fetch(
        `${API_BASE_URL}/api/auth/profile`,
        {
          method: 'DELETE',
          headers: authHeaders,
        }
      );
      return handleResponse(response);
    },
  },
};

// Export types for use in components
export type {
  CurriculumRequest,
  RecommendationRequest,
  ChatRequest,
  CurriculumResponse,
  RecommendationResponse,
  ChatResponse,
  ChatSession,
  ChatMessage,
  HealthResponse,
};
