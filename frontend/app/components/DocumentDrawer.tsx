'use client';

import { useState, useEffect } from 'react';
import { X, Download } from 'lucide-react';

interface DocumentDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  fileName: string;
  fileUrl: string;
  rawText?: string;
}

export default function DocumentDrawer({
  isOpen,
  onClose,
  fileName,
  fileUrl,
  rawText,
}: DocumentDrawerProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  // Disable body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 dark:bg-black/50 z-40 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed left-0 top-0 h-full w-80 max-w-4xl bg-white dark:bg-gray-950 shadow-xl z-50 transform transition-transform duration-300 overflow-y-auto flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 p-4 flex items-center justify-between z-10">
          <div className="flex-1">
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 truncate text-sm">
              {fileName}
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Full Curriculum</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {fileUrl && (
              <a
                href={fileUrl}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                title="Download"
              >
                <Download className="w-4 h-4" />
              </a>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {rawText ? (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                {rawText}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Loading document content...
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
