import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';

interface CurriculumUploadProps {
  onUploadSuccess?: () => void;
}

export default function CurriculumUpload({ onUploadSuccess }: CurriculumUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      setUploadedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.curriculum.upload(uploadedFile);
      setResult(response);
      setUploadedFile(null);
      
      // Call the success callback
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative rounded-lg border-2 border-dashed transition-colors p-12 text-center ${
          isDragOver
            ? 'border-emerald-400 bg-emerald-50'
            : 'border-gray-300 hover:border-emerald-300 hover:bg-gray-50'
        }`}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Drop your syllabus here
        </h3>
        <p className="text-gray-600 mb-4">
          or click to browse (PDF, DOC, or TXT)
        </p>
        <input
          type="file"
          className="absolute inset-0 cursor-pointer opacity-0"
          onChange={handleFileSelect}
          accept=".pdf,.doc,.docx,.txt"
        />
      </div>

      {uploadedFile && (
        <div className="bg-emerald-50 rounded-lg p-4 flex items-center gap-3 border border-emerald-200">
          <FileText className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-emerald-900">{uploadedFile.name}</p>
            <p className="text-sm text-emerald-700">Ready to analyze</p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 rounded-lg p-4 flex items-center gap-3 border border-red-200">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <div>
            <p className="font-medium text-red-900">Upload failed</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="font-semibold text-green-900">✓ File Stored & Analyzed!</p>
          <p className="text-sm text-green-700 mt-1">
            Extracted {result.total_topics} topics from {result.file_name}
          </p>
          <p className="text-sm text-green-700 mt-2">{result.summary}</p>
          {result.file_url && (
            <a
              href={result.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-green-600 hover:text-green-800 mt-3 inline-block"
            >
              View stored file →
            </a>
          )}
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">What happens next?</h3>
        <ol className="space-y-3 text-sm text-gray-600">
          <li className="flex gap-3">
            <span className="font-bold text-emerald-600">1</span>
            <span>We analyze your syllabus to identify key topics</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-emerald-600">2</span>
            <span>AI finds personalized resources matching your curriculum</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-emerald-600">3</span>
            <span>Resources appear in your Recommendations</span>
          </li>
        </ol>
      </div>
    </div>
  );
}
