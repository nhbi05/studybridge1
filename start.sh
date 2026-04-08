#!/bin/bash
# StudyBridge - Full Stack Startup Script

echo "🚀 StudyBridge Full Stack Startup"
echo "=================================="

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the studybridge1 root directory"
    exit 1
fi

echo ""
echo "✅ Starting Backend (FastAPI)..."
cd backend

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ backend/.env file not found!"
    echo "Please create it with:"
    echo "  SUPABASE_URL=your-url"
    echo "  SUPABASE_KEY=your-key"
    echo "  ANTHROPIC_API_KEY=your-key"
    exit 1
fi

# Start backend in background
python main.py &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"

echo ""
echo "✅ Starting Frontend (Next.js)..."
cd ../frontend

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo "  App: http://localhost:3000"

echo ""
echo "🎉 Both servers are running!"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Handle cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
