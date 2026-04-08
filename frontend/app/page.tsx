'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Brain, Zap, BarChart3 } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { api } from '@/lib/api';
import MetricCard from './components/MetricCard';
import ResourceCard from './components/ResourceCard';
import ChatInterface from './components/ChatInterface';

export default function Dashboard() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch recommendations only when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const data = await api.recommendations.get({
          user_id: user?.id || 'user-default',
          limit: 3,
        });
        setRecommendations(data.recommendations || []);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        console.error('Failed to fetch recommendations:', err);
        setRecommendations([]);
        setError(`❌ ${errorMessage}`);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [isAuthenticated, user?.id]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Loading...</h2>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated (handled by useEffect, but keep as fallback)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.name || user?.email}!</h1>
          <p className="text-gray-600 mt-1">
            Here's your learning progress and personalized recommendations
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {error && (
          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
            <p className="text-amber-800 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Resources Recommended"
            value={24}
            subtitle="This week"
            icon={<BookOpen className="w-8 h-8" />}
          />
          <MetricCard
            title="Topics Covered"
            value={12}
            subtitle="From your curriculum"
            icon={<Brain className="w-8 h-8" />}
          />
          <MetricCard
            title="Completion Rate"
            value="68%"
            subtitle="2 more to reach 75%"
            icon={<Zap className="w-8 h-8" />}
          />
          <MetricCard
            title="Active Sessions"
            value={3}
            subtitle="Ongoing learning"
            icon={<BarChart3 className="w-8 h-8" />}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Recommendations */}
          <div className="lg:col-span-2">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Recent Recommendations
              </h2>
              <p className="text-gray-600 text-sm mt-1">
                {loading ? 'Loading...' : 'AI-selected resources based on your curriculum'}
              </p>
            </div>

            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">Loading recommendations...</p>
                </div>
              ) : recommendations.length > 0 ? (
                recommendations.map((resource) => (
                  <ResourceCard
                    key={resource.id}
                    title={resource.title}
                    type={resource.type}
                    topic={resource.topic}
                    relevance_score={resource.relevance_score}
                    summary={resource.summary}
                  />
                ))
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">
                    No recommendations yet. Upload a curriculum to get started.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <ChatInterface />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
