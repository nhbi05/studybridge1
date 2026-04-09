'use client';

import { useState, useEffect } from 'react';
import { Filter, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import ResourceCard from '../components/ResourceCard';

interface TopicWithCurriculum {
  name: string;
  curriculumName: string;
  curriculumId: string;
}

export default function RecommendationsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [selectedTopic, setSelectedTopic] = useState<TopicWithCurriculum | null>(null);
  const [resources, setResources] = useState<any[]>([]);
  const [topicsByName, setTopicsByName] = useState<string[]>(['All']);
  const [topicsByFilename, setTopicsByFilename] = useState<{
    [curriculumName: string]: TopicWithCurriculum[];
  }>({});
  const [expandedCurriculum, setExpandedCurriculum] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enforce login
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch curriculums and group topics by curriculum filename
  useEffect(() => {
    if (!isAuthenticated || authLoading) return;

    const fetchCurriculumsAndTopics = async () => {
      try {
        const response = await api.curriculum.list();
        const curriculums = response.curriculums || [];

        // Group topics by curriculum filename
        const topicsGrouped: {
          [curriculumName: string]: TopicWithCurriculum[];
        } = {};
        const allTopicNames = new Set<string>();

        curriculums.forEach((curriculum: any) => {
          const curriculumName = curriculum.file_name || 'Unknown Curriculum';
          if (curriculum.topics_extracted && Array.isArray(curriculum.topics_extracted)) {
            topicsGrouped[curriculumName] = curriculum.topics_extracted.map(
              (topic: any) => ({
                name: topic.name,
                curriculumName,
                curriculumId: curriculum.curriculum_id,
              })
            );
            curriculum.topics_extracted.forEach((topic: any) => {
              if (topic.name) allTopicNames.add(topic.name);
            });
          }
        });

        setTopicsByFilename(topicsGrouped);
        setTopicsByName(['All', ...Array.from(allTopicNames).sort()]);
        
        // Auto-expand first curriculum
        if (Object.keys(topicsGrouped).length > 0) {
          setExpandedCurriculum(Object.keys(topicsGrouped)[0]);
        }
      } catch (err) {
        console.error('Failed to fetch curriculums:', err);
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
          topic: selectedTopic ? selectedTopic.name : undefined,
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

  const selectedTopicText = selectedTopic
    ? `${selectedTopic.name} (${selectedTopic.curriculumName})`
    : 'All Topics';

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

        {/* Current Selection Display */}
        {selectedTopic && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-emerald-700">Currently viewing</p>
                <p className="text-lg font-semibold text-emerald-900">{selectedTopicText}</p>
              </div>
              <button
                onClick={() => setSelectedTopic(null)}
                className="px-3 py-1 bg-emerald-200 text-emerald-900 rounded hover:bg-emerald-300 text-sm font-medium"
              >
                Clear
              </button>
            </div>
          </div>
        )}

        {/* Filter by Curriculum and Topic */}
        <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-6">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="font-semibold text-gray-900">Filter by Curriculum & Topic</span>
          </div>

          {/* All Topics Option */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <button
              onClick={() => setSelectedTopic(null)}
              className={`w-full px-4 py-2 rounded-lg font-medium transition-colors text-left ${
                !selectedTopic
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📚 All Topics
            </button>
          </div>

          {/* Topics Grouped by Curriculum */}
          <div className="space-y-3">
            {Object.entries(topicsByFilename).map(([curriculumName, topics]) => (
              <div key={curriculumName} className="border border-gray-200 rounded-lg">
                {/* Curriculum Header */}
                <button
                  onClick={() =>
                    setExpandedCurriculum(
                      expandedCurriculum === curriculumName ? null : curriculumName
                    )
                  }
                  className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between font-medium text-gray-900 transition-colors"
                >
                  <span className="text-sm">📄 {curriculumName}</span>
                  {expandedCurriculum === curriculumName ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>

                {/* Topics List */}
                {expandedCurriculum === curriculumName && (
                  <div className="bg-white border-t border-gray-200 p-3 space-y-2">
                    {topics.map((topic) => (
                      <button
                        key={`${topic.curriculumId}-${topic.name}`}
                        onClick={() => setSelectedTopic(topic)}
                        className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors text-left ${
                          selectedTopic?.name === topic.name &&
                          selectedTopic?.curriculumId === topic.curriculumId
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                            : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        {topic.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
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
                  key={`${resource.id}-${idx}`}
                  title={resource.title}
                  type={resource.type}
                  topic={resource.topic}
                  relevanceScore={resource.relevance_score}
                  summary={resource.summary}
                  url={resource.url}
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
