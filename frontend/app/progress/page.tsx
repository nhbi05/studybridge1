'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';

interface TopicProgress {
  topic: string;
  completed: number;
  total: number;
  percentage: number;
}

export default function ProgressPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [progressData, setProgressData] = useState<TopicProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enforce login
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch progress data
  useEffect(() => {
    if (!isAuthenticated || authLoading) return;

    const fetchProgress = async () => {
      try {
        setLoading(true);
        const response = await api.recommendations.getUserRecommendations(100);
        
        // Group recommendations by topic
        const topicMap = new Map<string, { completed: number; total: number }>();
        
        response.recommendations?.forEach((rec: any) => {
          const topic = rec.topic || 'General';
          if (!topicMap.has(topic)) {
            topicMap.set(topic, { completed: 0, total: 0 });
          }
          
          const current = topicMap.get(topic)!;
          current.total += 1;
          // Assume resources with higher relevance scores are "completed"
          if ((rec.relevance_score || 0) > 0.5) {
            current.completed += 1;
          }
        });

        // Convert to array and calculate percentages
        const progress: TopicProgress[] = Array.from(topicMap.entries()).map(
          ([topic, { completed, total }]) => ({
            topic,
            completed,
            total,
            percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
          })
        );

        setProgressData(progress);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch progress data:', err);
        setError('Failed to load progress data');
        setProgressData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [isAuthenticated, authLoading]);

  if (authLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  // Calculate aggregate stats
  const totalCompleted = progressData.reduce((sum, p) => sum + p.completed, 0);
  const totalResources = progressData.reduce((sum, p) => sum + p.total, 0);
  const overallPercentage = totalResources > 0 ? Math.round((totalCompleted / totalResources) * 100) : 0;
  const resourcesInProgress = Math.max(0, totalResources - totalCompleted);
  const averagePercentage = progressData.length > 0 
    ? Math.round(progressData.reduce((sum, p) => sum + p.percentage, 0) / progressData.length)
    : 0;

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-emerald-600" />
            <h1 className="text-3xl font-bold text-gray-900">Your Progress</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Track your learning journey across all topics
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading your progress...</p>
          </div>
        ) : (
          <>
            {/* Overall Progress */}
            <div className="bg-white rounded-lg border border-gray-200 p-8 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Overall Progress</h2>
                  <p className="text-gray-600 mt-1">
                    {totalCompleted} of {totalResources} resources completed
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-emerald-600">{overallPercentage}%</p>
                  <p className="text-sm text-gray-600 mt-1">Completion rate</p>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-emerald-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${overallPercentage}%` }}
                ></div>
              </div>
            </div>

            {/* By Topic */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Progress by Topic</h2>
              {progressData.length === 0 ? (
                <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
                  <p className="text-gray-600">No progress data yet. Get started by uploading a curriculum!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {progressData.map((topic, idx) => (
                    <div
                      key={idx}
                      className="bg-white rounded-lg border border-gray-200 p-6"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900">{topic.topic}</h3>
                        <span className="text-emerald-600 font-bold">
                          {topic.percentage}%
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${topic.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">
                          {topic.completed}/{topic.total}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <p className="text-gray-600 text-sm">Resources in Progress</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{resourcesInProgress}</p>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <p className="text-gray-600 text-sm">Topics Tracked</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{progressData.length}</p>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <p className="text-gray-600 text-sm">Average Progress</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{averagePercentage}%</p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
