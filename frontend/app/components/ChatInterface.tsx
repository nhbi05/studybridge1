'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { Send, MessageCircle } from 'lucide-react';
import { useUploadStore } from '@/store/useUploadStore';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  isAwaitingInput?: boolean;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const events = useUploadStore((state) => state.events);
  const isAnalyzing = useUploadStore((state) => state.isAnalyzing);

  // Scroll to bottom whenever messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, events]);

  // Listen to upload events and convert them to chat messages
  useEffect(() => {
    events.forEach((event) => {
      // Check if this event is already displayed
      const isAlreadyDisplayed = messages.some(
        (msg) => msg.id === event.id
      );

      if (!isAlreadyDisplayed) {
        const newMessage: Message = {
          id: event.id,
          role: event.type === 'confirmation_question' ? 'system' : 'assistant',
          content: event.message,
          isAwaitingInput: event.isAwaitingUserInput,
        };

        setMessages((prev) => [...prev, newMessage]);
      }
    });
  }, [events, messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.chat.sendMessage({
        user_message: input,
        conversation_history: messages
          .filter((m) => m.role !== 'system')
          .map((m) => ({
            role: m.role as 'user' | 'assistant',
            content: m.content,
          })),
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.assistant_message || 'I encountered an error. Please try again.',
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content:
          "I'm having trouble connecting to the AI service. Please check your connection and try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-lg">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-2 bg-gradient-to-r from-emerald-50 to-transparent">
        <MessageCircle className="w-5 h-5 text-emerald-600" />
        <div>
          <h2 className="text-lg font-semibold text-gray-900">AI Advisor</h2>
          {isAnalyzing && (
            <p className="text-xs text-emerald-600 font-medium">🔄 Analyzing curriculum...</p>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {/* Welcome message if no messages */}
        {messages.length === 0 && !isAnalyzing && (
          <div className="flex justify-start">
            <div className="bg-blue-50 text-blue-900 border border-blue-200 px-4 py-3 rounded-lg max-w-xs">
              <p className="text-sm leading-relaxed">
                👋 Hi! I'm your AI learning advisor. Upload a curriculum to get started, or ask me questions about your learning path.
              </p>
            </div>
          </div>
        )}

        {/* Regular messages */}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg text-sm leading-relaxed ${
                message.role === 'user'
                  ? 'bg-emerald-600 text-white'
                  : message.role === 'system'
                    ? 'bg-yellow-50 text-yellow-900 border border-yellow-200'
                    : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p>{message.content}</p>
              {message.isAwaitingInput && (
                <p className="text-xs mt-2 opacity-75">💬 Awaiting your response...</p>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-lg">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                  style={{ animationDelay: '0.4s' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isAnalyzing ? "Waiting for analysis..." : "Tell me about your learning needs..."}
            disabled={isLoading || isAnalyzing}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || isAnalyzing}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
