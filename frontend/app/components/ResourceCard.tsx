import { Star, ExternalLink } from 'lucide-react';

interface ResourceCardProps {
  title: string;
  type: 'video' | 'article' | 'exercise';
  topic: string;
  relevanceScore: number;
  summary: string;
  url?: string;
}

const typeStyles = {
  video: 'bg-blue-50 text-blue-700',
  article: 'bg-purple-50 text-purple-700',
  exercise: 'bg-amber-50 text-amber-700',
};

export default function ResourceCard({
  title,
  type,
  topic,
  relevanceScore,
  summary,
  url,
}: ResourceCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:border-emerald-300 hover:shadow-md transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-xs font-medium px-2 py-1 rounded ${typeStyles[type]}`}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </span>
            <span className="text-xs font-medium px-2 py-1 rounded bg-emerald-50 text-emerald-700">
              {topic}
            </span>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-600 mb-4">{summary}</p>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
          <span className="text-sm font-medium text-gray-700">
            {(relevanceScore * 100).toFixed(0)}% relevant
          </span>
        </div>
        <button
          onClick={() => {
            if (url) {
              window.open(url, '_blank');
            }
          }}
          disabled={!url}
          className={`inline-flex items-center gap-1 text-sm font-medium transition-colors ${
            url
              ? 'text-emerald-600 hover:text-emerald-700 cursor-pointer'
              : 'text-gray-400 cursor-not-allowed'
          }`}
        >
          View Resource
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
