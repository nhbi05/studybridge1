'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import CurriculumUpload from '../components/CurriculumUpload';
import { api } from '@/lib/api';

export default function CurriculumPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [curriculums, setCurriculums] = useState<any[]>([]);
  const [loadingCurriculums, setLoadingCurriculums] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Enforce login
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  // Fetch curriculums
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchCurriculums = async () => {
      try {
        setLoadingCurriculums(true);
        const response = await api.curriculum.list();
        setCurriculums(response.curriculums || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load curriculums');
      } finally {
        setLoadingCurriculums(false);
      }
    };

    fetchCurriculums();
  }, [isAuthenticated]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
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
        <CurriculumUpload />

        {/* Uploaded Curriculums */}
        <div className="mt-12">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Your Uploaded Curriculums
          </h2>

          {error && (
            <div className="bg-red-50 rounded-lg p-4 border border-red-200 mb-6">
              <p className="text-red-900 font-medium">{error}</p>
            </div>
          )}

          {loadingCurriculums ? (
            <div className="text-center py-8 text-gray-600">
              Loading your curriculums...
            </div>
          ) : curriculums.length === 0 ? (
            <div className="text-center py-8 text-gray-600">
              No curriculums uploaded yet. Upload one above to get started!
            </div>
          ) : (
            <div className="space-y-4">
              {curriculums.map((curriculum) => {
                const topicCount = curriculum.topics?.length || 0;
                const uploadedDate = new Date(curriculum.created_at).toLocaleDateString();
                
                return (
                  <div
                    key={curriculum.id}
                    className="bg-white rounded-lg border border-gray-200 p-6 hover:border-emerald-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {curriculum.file_name || 'Curriculum'}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Uploaded {uploadedDate} • {topicCount} topics
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-4 py-2 text-emerald-600 font-medium hover:bg-emerald-50 rounded-lg transition-colors">
                          View Topics
                        </button>
                        <button className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors">
                          Re-analyze
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
