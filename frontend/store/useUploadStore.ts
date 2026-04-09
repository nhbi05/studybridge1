import { create } from 'zustand';

interface UploadEvent {
  id: string;
  type: 'file_received' | 'confirming_topics' | 'confirmation_question' | 'embedding' | 'complete' | 'error';
  message: string;
  timestamp: number;
  fileName?: string;
  topics?: string[];
  userResponse?: string;
  isAwaitingUserInput?: boolean;
}

interface UploadStore {
  isAnalyzing: boolean;
  events: UploadEvent[];
  currentFileName: string | null;
  
  // Actions
  addEvent: (event: Omit<UploadEvent, 'id' | 'timestamp'>) => void;
  startAnalysis: (fileName: string) => void;
  completeAnalysis: () => void;
  handleUserResponse: (response: string) => void;
  clearEvents: () => void;
}

export const useUploadStore = create<UploadStore>((set) => ({
  isAnalyzing: false,
  events: [],
  currentFileName: null,

  addEvent: (event) =>
    set((state) => ({
      events: [
        ...state.events,
        {
          ...event,
          id: `event-${Date.now()}`,
          timestamp: Date.now(),
        },
      ],
    })),

  startAnalysis: (fileName) =>
    set({
      isAnalyzing: true,
      currentFileName: fileName,
      events: [],
    }),

  completeAnalysis: () =>
    set({
      isAnalyzing: false,
    }),

  handleUserResponse: (response) =>
    set((state) => ({
      events: state.events.map((e) =>
        e.isAwaitingUserInput ? { ...e, userResponse: response, isAwaitingUserInput: false } : e
      ),
    })),

  clearEvents: () =>
    set({
      events: [],
      currentFileName: null,
      isAnalyzing: false,
    }),
}));
