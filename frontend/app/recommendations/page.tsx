'use client';

import { useState, useEffect } from 'react';
import { Filter } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import ResourceCard from '../components/ResourceCard';

export default function RecommendationsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [resources, setResources] = useState<any[]>([]);
  const [topics, setTopics] = useState<string[]>(['All']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enforce login
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch curriculums and extract unique topics
  useEffect(() => {
    if (!isAuthenticated || authLoading) return;

    const fetchCurriculumsAndTopics = async () => {
      try {
        const response = await api.curriculum.list();
        const curriculums = response.curriculums || [];

        // Extract unique topic names from all curriculums
        const topicSet = new Set<string>();
        curriculums.forEach((curriculum: any) => {
          if (curriculum.topics_extracted && Array.isArray(curriculum.topics_extracted)) {
            curriculum.topics_extracted.forEach((topic: any) => {
              if (topic.name) {
                topicSet.add(topic.name);
              }
            });
          }
        });

        // Convert to sorted array and prepend 'All'
        const uniqueTopics = ['All', ...Array.from(topicSet).sort()];
        setTopics(uniqueTopics);
      } catch (err) {
        console.error('Failed to fetch curriculums:', err);
        // Keep default topics if fetch fails
      }
    };

    fetchCurriculumsAndTopics();
  }, [isAuthenticated, authLoading]);

  // Fetch recommendations
  useEffect(() => {
    if (!isAuthenticated || authLoading) return;

    const fetchResources = async () => {
      try {
        setLoading(true);
        const data = await api.recommendations.get({
          topic: selectedTopic || undefined,
          limit: 20,
        });
        setResources(data.recommendations || []);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        console.error('Failed to fetch resources:', err);
        setResources([]);
        setError(`❌ ${errorMessage}`);
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, [selectedTopic, isAuthenticated, authLoading]);

  if (authLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
          <p className="text-gray-600 mt-1">
            {loading ? 'Loading...' : `${resources.length} personalized resources selected for you`}
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Filter */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="font-semibold text-gray-900">Filter by topic</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {topics.map((topic) => (
              <button
                key={topic}
                onClick={() => setSelectedTopic(topic === 'All' ? null : topic)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  (topic === 'All' && !selectedTopic) ||
                  selectedTopic === topic
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-700 hover:border-emerald-300'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading resources...</p>
          </div>
        )}

        {/* Resources Grid */}
        {!loading && (
          <>
            <div className="space-y-4">
              {resources.map((resource, idx) => (
                <ResourceCard 
                  key={idx} 
                  title={resource.title}
                  type={resource.type}
                  topic={resource.topic}
                  relevanceScore={resource.relevance_score}
                  summary={resource.summary}
                />
              ))}
            </div>

            {resources.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">
                  No resources found. Try uploading a curriculum to get started.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
