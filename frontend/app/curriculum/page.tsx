'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import CurriculumUpload from '../components/CurriculumUpload';
import { api } from '@/lib/api';
import { BookOpen, Eye, RotateCw, X, Link as LinkIcon } from 'lucide-react';

interface Topic {
  name: string;
  description: string;
  subtopics?: string[];
  difficulty_level?: string;
}

interface Curriculum {
  curriculum_id: string;
  file_name: string;
  summary: string;
  topics_extracted: Topic[];
  total_topics: number;
}

export default function CurriculumPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [curriculums, setCurriculums] = useState<Curriculum[]>([]);
  const [loadingCurriculums, setLoadingCurriculums] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopicsCurriculum, setSelectedTopicsCurriculum] = useState<Curriculum | null>(null);
  const [reanalyzingId, setReanalyzingId] = useState<string | null>(null);

  // Enforce login
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch curriculums
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchCurriculums = async () => {
      try {
        setLoadingCurriculums(true);
        const response = await api.curriculum.list();
        setCurriculums(response.curriculums || []);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load curriculums';
        console.error('Failed to fetch curriculums:', err);
        setError(errorMessage);
      } finally {
        setLoadingCurriculums(false);
      }
    };

    fetchCurriculums();
  }, [isAuthenticated]);

  const handleUploadSuccess = async () => {
    // Refresh curriculum list after successful upload
    try {
      const response = await api.curriculum.list();
      setCurriculums(response.curriculums || []);
    } catch (err) {
      console.error('Failed to refresh curriculums:', err);
    }
  };

  const handleReanalyze = async (curriculum: Curriculum) => {
    setReanalyzingId(curriculum.curriculum_id);
    try {
      // Simulating re-analysis - in a real implementation, you'd call an API endpoint
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Refresh the curriculum data
      const response = await api.curriculum.get(curriculum.curriculum_id);
      setCurriculums((prev) =>
        prev.map((c) => (c.curriculum_id === curriculum.curriculum_id ? response : c))
      );
    } catch (err) {
      console.error('Failed to re-analyze curriculum:', err);
      setError(err instanceof Error ? err.message : 'Failed to re-analyze');
    } finally {
      setReanalyzingId(null);
    }
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900">Loading...</h2>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">My Curriculum</h1>
          <p className="text-gray-600 mt-1">
            Upload your syllabus to get AI-powered resource recommendations
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-8 py-8">
        <CurriculumUpload onUploadSuccess={handleUploadSuccess} />

        {/* Error Message */}
        {error && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Uploaded Curriculums */}
        <div className="mt-12">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Your Uploaded Curriculums
          </h2>

          {loadingCurriculums ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Loading your curriculums...</p>
            </div>
          ) : curriculums.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No curriculums yet</h3>
              <p className="text-gray-600">Upload your first curriculum to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {curriculums.map((curriculum) => (
                <div
                  key={curriculum.curriculum_id}
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:border-emerald-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {curriculum.file_name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-2">
                        {curriculum.total_topics} topics extracted • {curriculum.summary}
                      </p>
                    </div>
                  </div>

                  {/* Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedTopicsCurriculum(curriculum)}
                      className="inline-flex items-center gap-2 px-4 py-2 text-emerald-600 font-medium hover:bg-emerald-50 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      View Topics
                    </button>
                    <button
                      onClick={() => handleReanalyze(curriculum)}
                      disabled={reanalyzingId === curriculum.curriculum_id}
                      className="inline-flex items-center gap-2 px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <RotateCw
                        className={`w-4 h-4 ${
                          reanalyzingId === curriculum.curriculum_id ? 'animate-spin' : ''
                        }`}
                      />
                      Re-analyze
                    </button>
                    <button
                      onClick={() => router.push(`/recommendations/${curriculum.curriculum_id}`)}
                      className="inline-flex items-center gap-2 px-4 py-2 text-emerald-600 font-medium hover:bg-emerald-50 rounded-lg transition-colors ml-auto"
                    >
                      <LinkIcon className="w-4 h-4" />
                      View Resources
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Topics Modal */}
      {selectedTopicsCurriculum && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                Topics: {selectedTopicsCurriculum.file_name}
              </h2>
              <button
                onClick={() => setSelectedTopicsCurriculum(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="px-6 py-4 space-y-4">
              {!selectedTopicsCurriculum.topics_extracted || selectedTopicsCurriculum.topics_extracted.length === 0 ? (
                <p className="text-gray-600 text-center py-8">No topics extracted</p>
              ) : (
                selectedTopicsCurriculum.topics_extracted.map((topic, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{topic.name}</h3>
                      {topic.difficulty_level && (
                        <span
                          className={`text-xs font-medium px-2 py-1 rounded-full ${
                            topic.difficulty_level === 'beginner'
                              ? 'bg-green-100 text-green-800'
                              : topic.difficulty_level === 'intermediate'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {topic.difficulty_level}
                        </span>
                      )}
                    </div>
                    {topic.description && (
                      <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
                    )}
                    {topic.subtopics && topic.subtopics.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Subtopics:</p>
                        <ul className="space-y-1">
                          {topic.subtopics.map((subtopic, subIdx) => (
                            <li key={subIdx} className="text-sm text-gray-600">
                              • {subtopic}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
