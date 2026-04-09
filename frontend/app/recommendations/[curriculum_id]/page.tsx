'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';
import { ChevronLeft, BookOpen } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import ChatInterface from '@/app/components/ChatInterface';
import { useUploadStore } from '@/store/useUploadStore';

interface TopicWithResources {
  topic_name: string;
  topic_id: string;
  matching_resources: Array<{
    id: string;
    title: string;
    url: string;
    type: string;
    difficulty: string;
    similarity: number;
  }>;
  match_count: number;
}

interface RecommendationsResponse {
  curriculum_id: string;
  topics_with_resources: TopicWithResources[];
  total_resources: number;
}

export default function CurriculumRecommendationsPage({
  params,
}: {
  params: { curriculum_id: string };
}) {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [curriculum, setCurriculum] = useState<any>(null);
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Subscribe to upload events for dynamic updates
  const events = useUploadStore((state) => state.events);

  // Initialize Supabase client
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY || ''
  );

  // Function to fetch recommendations
  const fetchRecommendations = async (showRefreshingState = false) => {
    try {
      if (showRefreshingState) setIsRefreshing(true);
      
      if (!params.curriculum_id) {
        setError('Invalid curriculum ID');
        return;
      }

      // Fetch recommendations from FastAPI backend
      const fastApiUrl = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';
      const response = await fetch(
        `${fastApiUrl}/api/recommendations/semantic/${params.curriculum_id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${user?.id}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 403) {
          setError('You do not have permission to view this curriculum.');
          return;
        }
        throw new Error(`API error: ${response.statusText}`);
      }

      const recommendationsData: RecommendationsResponse = await response.json();
      setData(recommendationsData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred.';
      console.error('Error fetching recommendations:', err);
      if (!data) setError(errorMessage); // Only set error if no data loaded yet
    } finally {
      if (showRefreshingState) setIsRefreshing(false);
    }
  };

  // Redirect if not authenticated and fetch data
  useEffect(() => {
    if (authLoading) return;

    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    const initializeData = async () => {
      try {
        if (!params.curriculum_id) {
          setError('Invalid curriculum ID');
          return;
        }

        setLoading(true);
        
        // Fetch recommendations
        await fetchRecommendations();

        // Get curriculum details for header
        const { data: curriculumData } = await supabase
          .from('curriculums')
          .select('*')
          .eq('id', params.curriculum_id)
          .single();

        setCurriculum(curriculumData);
      } catch (err) {
        console.error('Error initializing:', err);
      } finally {
        setLoading(false);
      }
    };

    initializeData();
  }, [isAuthenticated, authLoading, params.curriculum_id, router, supabase]);

  // Refetch recommendations when embedding completes (dynamic updates)
  useEffect(() => {
    if (!isAuthenticated) return;

    // Check if embedding just completed
    const embeddingEvent = events.find((e) => e.type === 'embedding');
    const completeEvent = events.find((e) => e.type === 'complete');

    if ((embeddingEvent && !isRefreshing) || completeEvent) {
      // Debounce refetch - wait a moment for backend to index
      const timer = setTimeout(() => {
        fetchRecommendations(true);
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [events, isAuthenticated, isRefreshing]);

  // Show loading state
  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Loading...</h2>
        </div>
      </div>
    );
  }

  // Show auth required
  if (!isAuthenticated) {
    return null; // useEffect will redirect
  }

  // Show access denied
  if (error && error.includes('permission')) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-6">You don't have permission to view this curriculum.</p>
          <Link href="/curriculum" className="text-emerald-600 hover:underline font-medium">
            Back to Curriculums
          </Link>
        </div>
      </div>
    );
  }

  // Show error
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Recommendations</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link href="/curriculum" className="text-emerald-600 hover:underline font-medium">
            Back to Curriculums
          </Link>
        </div>
      </div>
    );
  }

  // Show content
  if (!data) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4 mb-4">
            <Link
              href="/curriculum"
              className="inline-flex items-center text-emerald-600 hover:text-emerald-700 font-medium"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Back to Curriculums
            </Link>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Personalized Recommendations</h1>
            <p className="text-gray-600 mt-2">
              {curriculum?.summary || 'Based on your curriculum'}
            </p>
            <div className="mt-4 flex gap-6 text-sm">
              <div className="flex items-center text-gray-600">
                <span className="font-semibold text-gray-900 mr-1">
                  {data?.topics_with_resources.length || 0}
                </span>
                Topics extracted
              </div>
              <div className="flex items-center text-gray-600">
                <span className="font-semibold text-gray-900 mr-1">{data?.total_resources || 0}</span>
                Resources matched
              </div>
              {isRefreshing && (
                <div className="flex items-center text-blue-600">
                  <div className="animate-spin mr-2 w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full" />
                  Updating recommendations...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Recommendations */}
        <div className="lg:col-span-2">
          {!data ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto" />
                <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto" />
              </div>
            </div>
          ) : data.topics_with_resources.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">No topics found</h2>
              <p className="text-gray-600">
                Upload a curriculum file to extract topics and find matching resources.
              </p>
            </div>
          ) : (
          <div className="space-y-8">
            {data.topics_with_resources.map((topic) => (
              <div key={topic.topic_id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                {/* Topic Header */}
                <div className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200 px-6 py-4">
                  <h2 className="text-xl font-bold text-gray-900">{topic.topic_name}</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {topic.match_count} resource{topic.match_count !== 1 ? 's' : ''} found
                  </p>
                </div>

                {/* Resources Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
                  {topic.matching_resources.length === 0 ? (
                    <div className="col-span-full text-center py-8 text-gray-500">
                      <p>No matching resources for this topic yet.</p>
                    </div>
                  ) : (
                    topic.matching_resources.map((resource) => (
                      <a
                        key={resource.id}
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group flex flex-col p-4 border border-gray-200 rounded-lg hover:border-emerald-300 hover:shadow-md transition-all duration-200"
                      >
                        {/* Resource Metadata */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex gap-2">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                resource.type === 'video'
                                  ? 'bg-blue-100 text-blue-800'
                                  : resource.type === 'article'
                                    ? 'bg-purple-100 text-purple-800'
                                    : 'bg-orange-100 text-orange-800'
                              }`}
                            >
                              {resource.type}
                            </span>
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                resource.difficulty === 'beginner'
                                  ? 'bg-green-100 text-green-800'
                                  : resource.difficulty === 'intermediate'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {resource.difficulty}
                            </span>
                          </div>
                          {/* Similarity Score */}
                          <div className="text-right">
                            <div className="text-xs text-gray-500 mb-1">Match</div>
                            <div className="text-sm font-semibold text-emerald-600">
                              {Math.round(resource.similarity * 100)}%
                            </div>
                          </div>
                        </div>

                        {/* Title */}
                        <h3 className="font-semibold text-gray-900 group-hover:text-emerald-600 transition-colors line-clamp-2 flex-grow">
                          {resource.title}
                        </h3>

                        {/* CTA */}
                        <div className="mt-3 text-sm font-medium text-emerald-600 group-hover:text-emerald-700">
                          Open Resource →
                        </div>
                      </a>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        </div>

        {/* Right: Chat Sidebar */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 h-fit">
            <ChatInterface />
          </div>
        </div>
      </div>
    </div>
  );
}
