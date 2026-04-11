'use client';

import { useState, useEffect } from 'react';
import { Filter, ChevronDown, ChevronUp, X, Search } from 'lucide-react';
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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

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

  // Filter topics based on search query
  const filterTopicsBySearch = (curriculumName: string, topics: TopicWithCurriculum[]) => {
    if (!searchQuery.trim()) return topics;
    return topics.filter(topic => 
      topic.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
              <p className="text-gray-600 mt-1">
                {loading ? 'Loading...' : `${resources.length} personalized resources`}
              </p>
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <Filter className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Layout with Sidebar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar - Topics Filter */}
          <div className={`${sidebarOpen ? 'block' : 'hidden'} lg:block lg:col-span-1`}>
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-24 max-h-[calc(100vh-120px)] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Filter className="w-5 h-5" />
                  Topics
                </h2>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="lg:hidden p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Search Topics */}
              <div className="mb-4 relative">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              {/* All Topics Option */}
              <div className="mb-4 pb-4 border-b border-gray-200">
                <button
                  onClick={() => setSelectedTopic(null)}
                  className={`w-full px-3 py-2 rounded-lg font-medium transition-colors text-left text-sm ${
                    !selectedTopic
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  📚 All Topics
                </button>
              </div>

              {/* Topics Grouped by Curriculum */}
              <div className="space-y-2">
                {Object.entries(topicsByFilename).map(([curriculumName, topics]) => {
                  const filteredTopics = filterTopicsBySearch(curriculumName, topics);
                  // Hide curriculum if no topics match search
                  if (searchQuery && filteredTopics.length === 0) return null;

                  return (
                    <div key={curriculumName}>
                      {/* Curriculum Header */}
                      <button
                        onClick={() =>
                          setExpandedCurriculum(
                            expandedCurriculum === curriculumName ? null : curriculumName
                          )
                        }
                        className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100 flex items-center justify-between rounded font-medium text-gray-900 transition-colors text-sm"
                      >
                        <span className="truncate">📄 {curriculumName}</span>
                        {expandedCurriculum === curriculumName ? (
                          <ChevronUp className="w-4 h-4 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-4 h-4 flex-shrink-0" />
                        )}
                      </button>

                      {/* Topics List */}
                      {expandedCurriculum === curriculumName && (
                        <div className="mt-1 ml-2 space-y-1 border-l-2 border-gray-200 pl-3">
                          {filteredTopics.map((topic) => (
                            <button
                              key={`${curriculumName}-${topic.name}`}
                              onClick={() => setSelectedTopic(topic)}
                              className={`w-full px-3 py-1.5 rounded text-left text-sm transition-colors truncate ${
                                selectedTopic?.name === topic.name &&
                                selectedTopic?.curriculumId === topic.curriculumId
                                  ? 'bg-emerald-100 text-emerald-900 font-medium'
                                  : 'text-gray-700 hover:bg-gray-100'
                              }`}
                            >
                              {topic.name}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Main Content - Resources */}
          <div className="lg:col-span-3">
            {/* Current Selection Badge */}
            {selectedTopic && (
              <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-emerald-700 font-medium">Currently viewing</p>
                    <p className="text-lg font-semibold text-emerald-900 truncate">{selectedTopicText}</p>
                  </div>
                  <button
                    onClick={() => setSelectedTopic(null)}
                    className="px-4 py-2 bg-emerald-200 text-emerald-900 rounded hover:bg-emerald-300 text-sm font-medium whitespace-nowrap"
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm font-medium">{error}</p>
              </div>
            )}

            {/* Resources Grid */}
            {loading ? (
              <div className="text-center py-12">
                <p className="text-gray-600">Loading resources...</p>
              </div>
            ) : resources.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {resources.map((resource) => (
                  <ResourceCard 
                    key={`${resource.id}`} 
                    title={resource.title}
                    type={resource.type}
                    topic={resource.topic}
                    relevanceScore={resource.relevance_score}
                    summary={resource.summary}
                    url={resource.url}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-600 mb-2">No resources found for this topic.</p>
                <p className="text-sm text-gray-500">Try selecting a different topic or browse all topics.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
