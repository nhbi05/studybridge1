'use client';

import { useState } from 'react';
import { ChevronDown, FileText } from 'lucide-react';

interface SummaryCardProps {
  summary: string;
  milestones?: string[];
  topicNames?: string[];
  onViewFullDocument?: () => void;
}

export default function CurriculumSummaryCard({
  summary,
  milestones = [],
  topicNames = [],
  onViewFullDocument,
}: SummaryCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Get top 5 topics for badge display
  const displayTopics = topicNames.slice(0, 5);

  return (
    <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950 dark:to-teal-950 rounded-lg border border-emerald-200 dark:border-emerald-800 p-5 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <div className="flex items-start gap-3">
          <div className="bg-emerald-100 dark:bg-emerald-900 rounded-lg p-2 flex-shrink-0">
            <FileText className="w-5 h-5 text-emerald-700 dark:text-emerald-300" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-1">
              📚 Syllabus at a Glance
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {summary}
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors flex-shrink-0"
        >
          <ChevronDown
            className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="space-y-4 pt-3 border-t border-emerald-200 dark:border-emerald-800">
          {/* Milestones */}
          {milestones.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
                ⏰ Key Milestones
              </h4>
              <ul className="space-y-1">
                {milestones.map((milestone, idx) => (
                  <li key={idx} className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold text-xs mt-0.5">▸</span>
                    <span>{milestone}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Topic Cloud */}
          {displayTopics.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
                🏷️ Top Topics
              </h4>
              <div className="flex flex-wrap gap-2">
                {displayTopics.map((topic, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-200 dark:bg-emerald-800 text-emerald-800 dark:text-emerald-200"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Button */}
      {onViewFullDocument && (
        <button
          onClick={onViewFullDocument}
          className="mt-4 w-full px-3 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-900 hover:bg-emerald-200 dark:hover:bg-emerald-800 rounded-md transition-colors flex items-center justify-center gap-2"
        >
          <FileText className="w-4 h-4" />
          View Full Document
        </button>
      )}
    </div>
  );
}
