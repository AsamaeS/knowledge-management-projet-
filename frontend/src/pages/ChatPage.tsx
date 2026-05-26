import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { Send, Cpu, CheckSquare, MessageSquare, AlertCircle, FileText } from 'lucide-react';

export default function ChatPage() {
  const {
    messages,
    outputFormat,
    isLoading,
    error,
    sendMessage,
    setOutputFormat,
    initSession
  } = useChatStore();

  const [input, setInput] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initSession();
  }, [initSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input.trim());
    setInput('');
  };

  // Helper to strip statement tags for cleaner rendering
  const cleanMessageContent = (content: string) => {
    return content
      .replace(/\[(FACT|OPINION|INFERENCE)\]/gi, '')
      .replace(/\[SOURCE:[^\]]+\]/gi, '')
      .trim();
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
      {/* Top Header & Settings */}
      <header className="px-8 py-5 border-b border-slate-800 bg-slate-900/40 backdrop-blur-md flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-extrabold tracking-tight text-slate-100 flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-500 animate-pulse" />
            <span>NEXUS Analyst RAG Chat</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Retrieved answers are mathematically grounded in raw database sources with zero hallucinations.</p>
        </div>

        {/* Output Format selector */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          {(['text', 'swot', 'pestel'] as const).map((fmt) => (
            <button
              key={fmt}
              onClick={() => setOutputFormat(fmt)}
              className={`px-4 py-2 rounded-lg font-bold transition-all duration-200 capitalize ${
                outputFormat === fmt
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {fmt}
            </button>
          ))}
        </div>
      </header>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
            <div className="bg-indigo-950/30 p-4 rounded-full border border-indigo-900/50 text-indigo-400">
              <MessageSquare className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <p className="text-slate-300 font-semibold text-sm">Initiate Strategic Q&A Session</p>
              <p className="text-xs text-slate-500 leading-relaxed">
                Query NEXUS about automotive spot pricing, supply chain metrics, EV manufacturing capacity, or threat landscapes.
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={idx}
                  className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-2xl rounded-2xl p-5 border shadow-md ${
                    isUser
                      ? 'bg-indigo-600/10 border-indigo-500/30 text-slate-200'
                      : 'bg-slate-900/60 border-slate-800 text-slate-100'
                  }`}>
                    {/* Role header label */}
                    <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-500 mb-2">
                      <span>{isUser ? 'STRATEGIST USER' : 'NEXUS COGNITIVE SYSTEM'}</span>
                      <span>•</span>
                      <span>{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>

                    {/* Answer content rendering */}
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">
                      {isUser ? msg.content : cleanMessageContent(msg.content)}
                    </div>

                    {/* Statement Fact/Opinion labels pill tags */}
                    {!isUser && msg.content && (
                      <div className="mt-4 pt-3 border-t border-slate-800/50 flex flex-wrap gap-2">
                        {msg.content.includes('[FACT]') && (
                          <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold bg-blue-950/40 border border-blue-900/40 text-blue-400 tracking-wide font-mono uppercase">Grounded Fact</span>
                        )}
                        {msg.content.includes('[OPINION]') && (
                          <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold bg-amber-950/40 border border-amber-900/40 text-amber-400 tracking-wide font-mono uppercase">Expert Opinion</span>
                        )}
                        {msg.content.includes('[INFERENCE]') && (
                          <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold bg-purple-950/40 border border-purple-900/40 text-purple-400 tracking-wide font-mono uppercase">AI Inference</span>
                        )}
                      </div>
                    )}

                    {/* Citations Card Section bottom */}
                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
                        <p className="text-[10px] font-semibold text-slate-500 font-mono tracking-wider uppercase">Retrieved Grounding Sources ({msg.citations.length})</p>
                        <div className="grid grid-cols-1 gap-2">
                          {msg.citations.map((cit, cIdx) => (
                            <div key={cIdx} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-xs flex flex-col space-y-1.5 hover:border-slate-700 transition-colors duration-150">
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-slate-300 truncate max-w-[250px] flex items-center space-x-1.5">
                                  <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                                  <span>{cit.filename}</span>
                                </span>
                                <span className="text-[9px] uppercase font-bold text-slate-500 font-mono tracking-wider border border-slate-800 px-1.5 py-0.5 rounded-full bg-slate-900">{cit.source_type}</span>
                              </div>
                              <blockquote className="text-slate-400 border-l border-slate-700 pl-2 py-0.5 leading-relaxed text-[11px]">
                                {cit.excerpt}
                              </blockquote>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            
            {/* Thinking Loading State */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-900/40 border border-slate-850 rounded-2xl p-5 flex items-center space-x-3 text-slate-400">
                  <div className="flex space-x-1.5">
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-xs font-mono tracking-wide uppercase">Searching cognitive graph vector space...</span>
                </div>
              </div>
            )}

            {/* Error alerts */}
            {error && (
              <div className="bg-rose-950/20 border border-rose-900/50 p-4 rounded-xl text-rose-400 text-xs flex items-center space-x-3 max-w-md mx-auto">
                <AlertCircle className="w-5 h-5 text-rose-500 shrink-0" />
                <p>{error}</p>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Form Input Area Bottom */}
      <footer className="p-6 border-t border-slate-800 bg-slate-900/20 shrink-0">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto flex items-center space-x-3">
          <input
            type="text"
            placeholder={isLoading ? 'Query indexing active...' : 'Query knowledge graph...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-5 py-4 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors duration-200 placeholder-slate-600"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`p-4 rounded-xl text-white transition-all duration-200 ${
              !input.trim() || isLoading
                ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 shadow-lg shadow-indigo-600/10'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </footer>
    </div>
  );
}
