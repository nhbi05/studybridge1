# StudyBridge Backend API Specification

## Overview
RESTful API for AI-powered curriculum-based learning resource recommendations.

**Base URL**: `http://localhost:8000`
**API Documentation**: `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Curriculum Management

### Upload Curriculum
**POST** `/api/curriculum/upload`

Upload and analyze a curriculum file (PDF, DOCX, or TXT).

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Unique user identifier |

**Request Body:**
```multipart/form-data
file: <binary> (PDF, DOCX, or TXT file)
```

**Response (200):**
```json
{
  "curriculum_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "file_name": "Calculus_101_Syllabus.pdf",
  "topics_extracted": [
    {
      "name": "Limits and Continuity",
      "description": "Understanding behavior of functions...",
      "subtopics": ["One-sided limits", "Continuous functions"],
      "difficulty_level": "beginner"
    }
  ],
  "total_topics": 12,
  "summary": "Comprehensive calculus course covering limits, derivatives, and integrals..."
}
```

**Error Responses:**
- `400`: Invalid file format
- `500`: Processing failed

---

### List User's Curriculums
**GET** `/api/curriculum/list/{user_id}`

Retrieve all uploaded curriculums for a user.

**Response (200):**
```json
{
  "curriculums": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user123",
      "file_name": "Calculus_101.pdf",
      "topics": [...],
      "summary": "...",
      "created_at": "2024-04-06T12:34:56Z"
    }
  ],
  "total": 2
}
```

---

### Get Curriculum Details
**GET** `/api/curriculum/{curriculum_id}`

Retrieve detailed information about a specific curriculum.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "file_name": "Calculus_101.pdf",
  "topics": [
    {
      "name": "Derivatives",
      "description": "Rate of change...",
      "subtopics": ["Power rule", "Chain rule"],
      "difficulty_level": "intermediate"
    }
  ],
  "summary": "...",
  "created_at": "2024-04-06T12:34:56Z"
}
```

---

## Recommendations

### Get Personalized Recommendations
**POST** `/api/recommendations/get`

Get AI-powered resource recommendations based on curriculum and user preferences.

**Request Body:**
```json
{
  "user_id": "user123",
  "curriculum_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Linear Algebra",
  "difficulty": "intermediate",
  "resource_types": ["video", "exercise"],
  "limit": 10
}
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "id": "resource-123",
      "title": "Linear Algebra Fundamentals",
      "type": "video",
      "topic": "Linear Algebra",
      "relevance_score": 0.95,
      "summary": "Comprehensive video series covering vectors and matrices...",
      "metadata": {
        "url": "https://example.com/video",
        "duration_minutes": 180,
        "difficulty": "intermediate"
      }
    }
  ],
  "query_topic": "Linear Algebra",
  "total_results": 8,
  "timestamp": "2024-04-06T12:34:56Z"
}
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Max 50 results |

---

### Get User's Saved Recommendations
**GET** `/api/recommendations/user/{user_id}`

Retrieve all previously recommended resources for a user.

**Query Parameters:**
| Parameter | Type | Default |
|-----------|------|---------|
| `limit` | integer | 20 |

**Response (200):**
```json
{
  "recommendations": [...],
  "total": 25
}
```

---

### Find Similar Resources
**GET** `/api/recommendations/similar/{resource_id}`

Find resources similar to a given resource using semantic similarity.

**Query Parameters:**
| Parameter | Type | Default |
|-----------|------|---------|
| `limit` | integer | 5 |

**Response (200):**
```json
{
  "resources": [
    {
      "id": "resource-456",
      "title": "Advanced Linear Algebra",
      "type": "article",
      "topic": "Linear Algebra",
      "relevance_score": 0.87,
      "summary": "..."
    }
  ],
  "total": 4
}
```

---

### Rerank Resources
**POST** `/api/recommendations/rerank`

Use LLM to rerank resources based on user context.

**Request Body:**
```json
{
  "resources": ["resource-id-1", "resource-id-2"],
  "user_context": "I want to understand eigenvalues visually",
  "limit": 10
}
```

**Response (200):**
```json
{
  "reranked": [...],
  "total": 10
}
```

---

## AI Chat

### Send Message to AI Advisor
**POST** `/api/chat/message`

Send a message to the AI advisor and get personalized guidance.

**Request Body:**
```json
{
  "user_id": "user123",
  "curriculum_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_message": "I already know basic linear algebra, can you find advanced resources?",
  "conversation_history": [
    {
      "role": "user",
      "content": "What resources do you recommend?"
    },
    {
      "role": "assistant",
      "content": "Based on your curriculum..."
    }
  ]
}
```

**Response (200):**
```json
{
  "assistant_message": "Great! Since you have a solid foundation in linear algebra, I'd recommend...",
  "confidence_score": 0.92,
  "updated_filters": {
    "difficulty": "advanced",
    "resource_types": ["research_paper", "advanced_course"]
  },
  "suggested_resources": ["resource-789", "resource-790"]
}
```

---

### Create Chat Session
**POST** `/api/chat/session`

Create a new conversation session.

**Query Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| `user_id` | string | Yes |

**Response (200):**
```json
{
  "session_id": "session_user123_1712430896",
  "user_id": "user123",
  "created_at": "2024-04-06T12:34:56Z"
}
```

---

### Get Chat History
**GET** `/api/chat/history/{session_id}`

Retrieve conversation history for a session.

**Response (200):**
```json
{
  "session_id": "session_user123_1712430896",
  "messages": [
    {
      "role": "user",
      "content": "What should I learn?"
    },
    {
      "role": "assistant",
      "content": "Based on your curriculum..."
    }
  ]
}
```

---

## Health & Status

### Health Check
**GET** `/`

Basic health check.

**Response (200):**
```json
{
  "status": "ok",
  "service": "StudyBridge API",
  "version": "1.0.0"
}
```

---

### Detailed Health Status
**GET** `/health`

Detailed service status.

**Response (200):**
```json
{
  "status": "healthy",
  "ai_services": "ready",
  "database": "connected"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid parameters |
| `404` | Not Found - Resource doesn't exist |
| `500` | Internal Server Error - Service error |

**Examples:**

**400 - Invalid File Format**
```json
{
  "detail": "Upload failed: Failed to parse PDF"
}
```

**404 - Curriculum Not Found**
```json
{
  "detail": "Curriculum not found"
}
```

**500 - Recommendation Error**
```json
{
  "detail": "Failed to get recommendations: Service unavailable"
}
```

---

## Data Models

### CurriculumUploadRequest
```json
{
  "user_id": "string",
  "file_name": "string",
  "content": "string",
  "file_type": "pdf|docx|text"
}
```

### Resource
```json
{
  "id": "string",
  "title": "string",
  "type": "video|article|exercise|book|course",
  "topic": "string",
  "relevance_score": 0.0 - 1.0,
  "summary": "string",
  "metadata": {
    "url": "string",
    "duration_minutes": "integer",
    "difficulty": "beginner|intermediate|advanced",
    "language": "string"
  }
}
```

### ChatMessage
```json
{
  "role": "user|assistant",
  "content": "string"
}
```

---

## Rate Limiting & Quotas

- **Curriculum Upload**: 10 files per hour per user
- **Recommendations**: 100 requests per hour per user
- **Chat Messages**: 50 messages per hour per user
- **File Size Limit**: 50MB per curriculum

---

## Authentication

Currently: No authentication (development mode)

**Future Implementation**: JWT tokens will be required
```
Authorization: Bearer <token>
```

---

## CORS

**Allowed Origins (Development):**
- `http://localhost:3000`
- `http://localhost:3001`
- `*` (to be restricted in production)

---

## Changelog

### v1.0.0 (Current)
- Curriculum upload and parsing
- AI-powered recommendations
- Semantic similarity search
- Chat interface
- User preference tracking
