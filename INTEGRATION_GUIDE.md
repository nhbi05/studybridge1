# StudyBridge Full Integration Guide

## Architecture Overview

```
Frontend (localhost:3000)
    ↓ HTTP Requests
Backend API (localhost:8000)
    ↓ Connected via Supabase Client
Supabase (PostgreSQL + Vector Search)
```

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Project
1. Go to https://supabase.com
2. Click "Create a new project"
3. Name it "studybridge"
4. Save your password
5. Wait for provisioning (~2 mins)

### 1.2 Run Database Schema
1. In Supabase Dashboard → SQL Editor
2. Click "New Query"
3. Copy entire contents of `SUPABASE_SCHEMA.sql`
4. Paste into SQL Editor
5. Click "Run"
6. Confirm all tables created (7 tables)

### 1.3 Get API Credentials
1. Go to Settings → API
2. Copy `Project URL` → Save as `SUPABASE_URL`
3. Copy `anon/public` key → Save as `SUPABASE_KEY`

---

## Step 2: Backend Configuration

### 2.1 Create Environment File

Create `backend/.env`:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# AI Services
ANTHROPIC_API_KEY=your-claude-api-key

# Server
PORT=8000
```

### 2.2 Install & Run Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will start at: `http://localhost:8000`

**Test it:**
```bash
curl http://localhost:8000/health
```

---

## Step 3: Frontend Configuration

### 3.1 Create API Client

Create `frontend/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  // Curriculum endpoints
  curriculum: {
    upload: async (userId: string, file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/upload?user_id=${userId}`,
        { method: 'POST', body: formData }
      );
      return response.json();
    },
    list: async (userId: string) => {
      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/list/${userId}`
      );
      return response.json();
    },
    get: async (curriculumId: string) => {
      const response = await fetch(
        `${API_BASE_URL}/api/curriculum/${curriculumId}`
      );
      return response.json();
    },
  },

  // Recommendations endpoints
  recommendations: {
    get: async (request: any) => {
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/get`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        }
      );
      return response.json();
    },
    getUserRecommendations: async (userId: string, limit: number = 20) => {
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/user/${userId}?limit=${limit}`
      );
      return response.json();
    },
    getSimilar: async (resourceId: string, limit: number = 5) => {
      const response = await fetch(
        `${API_BASE_URL}/api/recommendations/similar/${resourceId}?limit=${limit}`
      );
      return response.json();
    },
  },

  // Chat endpoints
  chat: {
    sendMessage: async (request: any) => {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/message`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        }
      );
      return response.json();
    },
    createSession: async (userId: string) => {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/session?user_id=${userId}`,
        { method: 'POST' }
      );
      return response.json();
    },
    getHistory: async (sessionId: string) => {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/history/${sessionId}`
      );
      return response.json();
    },
  },
};
```

### 3.2 Update Next.js Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.3 Update Next.js Config

Edit `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ],
    };
  },
};

export default nextConfig;
```

### 3.4 Run Frontend

```bash
cd frontend
npm run dev
```

Frontend will start at: `http://localhost:3000`

---

## Step 4: Connect Components

### 4.1 Update Dashboard Page

Edit `frontend/app/page.tsx`:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function Dashboard() {
  const [userId] = useState('test-user-123');
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const data = await api.recommendations.get({
          user_id: userId,
          limit: 3,
        });
        setRecommendations(data.recommendations || []);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
      }
      setLoading(false);
    };

    fetchRecommendations();
  }, [userId]);

  // ... rest of component
}
```

### 4.2 Update Curriculum Upload

Edit `frontend/app/components/CurriculumUpload.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Upload, FileText } from 'lucide-react';

export default function CurriculumUpload() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      setUploadedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    try {
      const result = await api.curriculum.upload('test-user-123', uploadedFile);
      setResult(result);
      alert(`Curriculum uploaded! ${result.total_topics} topics extracted.`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Check console.');
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`rounded-lg border-2 border-dashed transition-colors p-12 text-center ${
          isDragOver ? 'border-emerald-400 bg-emerald-50' : 'border-gray-300'
        }`}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900">Drop your syllabus</h3>
        <input
          type="file"
          className="absolute inset-0 opacity-0 cursor-pointer"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              setUploadedFile(e.target.files[0]);
            }
          }}
        />
      </div>

      {uploadedFile && (
        <div className="bg-emerald-50 rounded-lg p-4 flex items-center gap-3">
          <FileText className="w-5 h-5 text-emerald-600" />
          <div className="flex-1">
            <p className="font-medium text-emerald-900">{uploadedFile.name}</p>
          </div>
          <button
            onClick={handleUpload}
            disabled={loading}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-900 font-semibold">Success!</p>
          <p className="text-green-700 text-sm mt-1">
            Extracted {result.total_topics} topics from {result.file_name}
          </p>
        </div>
      )}
    </div>
  );
}
```

### 4.3 Update Chat Interface

Edit `frontend/app/components/ChatInterface.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Send, MessageCircle } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.chat.sendMessage({
        user_id: 'test-user-123',
        user_message: input,
        conversation_history: messages,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.assistant_message,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    }

    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200">
      {/* ... rest of component */}
    </div>
  );
}
```

---

## Step 5: Testing Checklist

### Test Backend
```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Create user data in Supabase SQL Editor
INSERT INTO users (email, name) VALUES ('test@example.com', 'Test User');

# 3. Test with sample curriculum upload
curl -X POST "http://localhost:8000/api/curriculum/upload?user_id=test-user-123" \
  -F "file=@sample.pdf"

# 4. Get recommendations
curl -X POST "http://localhost:8000/api/recommendations/get" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user-123","limit":5}'
```

### Test Frontend
1. Navigate to `http://localhost:3000`
2. Upload a curriculum file
3. View recommendations
4. Chat with AI advisor
5. Check console for API calls

### Monitor Supabase
1. Open Supabase Dashboard
2. Check "curriculums" table for new entries
3. Check "recommendations" table for scores
4. Verify "embeddings" table population

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Forbidden from Supabase | Check anon key permissions in Supabase → Auth → Policies |
| CORS errors | Backend CORS is enabled for localhost:3000 |
| API 404 errors | Ensure backend is running on 8000, frontend on 3000 |
| Empty recommendations | Add sample resources to the resources table |
| Chat not working | Check ANTHROPIC_API_KEY is set and valid |
| Embedding errors | Verify pgvector extension is enabled (`CREATE EXTENSION IF NOT EXISTS "vector"`) |

---

## Environment Variables Summary

### Backend (`backend/.env`)
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
PORT=8000
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## File Structure After Setup

```
studybridge1/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env (created)
│   ├── routers/
│   ├── services/
│   ├── models/
│   └── db/
├── frontend/
│   ├── app/
│   ├── lib/
│   │   └── api.ts (create)
│   ├── next.config.ts (updated)
│   └── .env.local (created)
└── SUPABASE_SCHEMA.sql (for reference)
```

---

## Next Steps

1. ✅ Run Supabase schema
2. ✅ Start backend (`python main.py`)
3. ✅ Start frontend (`npm run dev`)
4. ✅ Test full flow end-to-end
5. Test edge cases (large files, API failures)
6. Add authentication (JWT)
7. Deploy to production

---

## Quick Commands

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Then open browser: http://localhost:3000
```

Done! Your full stack is now connected. 🎉
