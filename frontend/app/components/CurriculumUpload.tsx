import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';
import { useUploadStore } from '@/store/useUploadStore';

interface CurriculumUploadProps {
  onUploadSuccess?: () => void;
}

export default function CurriculumUpload({ onUploadSuccess }: CurriculumUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  const startAnalysis = useUploadStore((state) => state.startAnalysis);
  const addEvent = useUploadStore((state) => state.addEvent);
  const completeAnalysis = useUploadStore((state) => state.completeAnalysis);

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
    
    // Start the analysis sequence in the chat
    startAnalysis(uploadedFile.name);
    
    addEvent({
      type: 'file_received',
      message: `Received ${uploadedFile.name}! I'm starting the deep analysis now. 🔍`,
      fileName: uploadedFile.name,
    });

    try {
      // Simulate LLM confirming topics after a brief delay
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      addEvent({
        type: 'confirming_topics',
        message: `I've identified the primary topics in your curriculum. Let me confirm what I found...`,
      });

      // Main upload and extraction
      const response = await api.curriculum.upload(uploadedFile);
      
      // Add topics confirmation question
      const topicNames = response.topics_extracted?.map((t: any) => t.name) || [];
      
      if (topicNames.length > 0) {
        const topicList = topicNames.slice(0, 3).join(', ') + (topicNames.length > 3 ? `, and ${topicNames.length - 3} more` : '');
        
        addEvent({
          type: 'confirmation_question',
          message: `I've identified "${topicList}" as your primary goals. Should I include all of these in your resource bridge?`,
          topics: topicNames,
          isAwaitingUserInput: true,
        });
        
        // Simulate user response after a delay (auto-confirm)
        await new Promise((resolve) => setTimeout(resolve, 2000));
        
        addEvent({
          type: 'confirmation_question',
          message: `Got it. Including all ${topicNames.length} topics in your analysis...`,
          userResponse: 'Yes, include all',
        });
      }

      // BERT embedding phase
      await new Promise((resolve) => setTimeout(resolve, 1000));
      addEvent({
        type: 'embedding',
        message: `Extraction complete! I'm now running these through our BERT model to find the best MIT and Coursera matches. Check your Recommendations tab in 3... 2... 1... ✨`,
      });

      setResult(response);
      setUploadedFile(null);
      
      // Complete the analysis
      await new Promise((resolve) => setTimeout(resolve, 1500));
      completeAnalysis();
      
      addEvent({
        type: 'complete',
        message: `Done! I've updated your curriculum profile with ${topicNames.length} topics and generated personalized recommendations.`,
      });
      
      // Call the success callback
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMsg);
      addEvent({
        type: 'error',
        message: `❌ Error during analysis: ${errorMsg}`,
      });
      completeAnalysis();
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
