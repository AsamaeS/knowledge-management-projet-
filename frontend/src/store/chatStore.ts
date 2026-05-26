import { create } from 'zustand';
import { MessageHistoryItem } from '../types';
import * as chatApi from '../api/chat';

interface ChatState {
  sessionId: string | null;
  messages: MessageHistoryItem[];
  outputFormat: 'text' | 'swot' | 'pestel';
  isLoading: boolean;
  error: string | null;

  initSession: () => Promise<string>;
  sendMessage: (message: string) => Promise<void>;
  setOutputFormat: (format: 'text' | 'swot' | 'pestel') => void;
  loadHistory: (sessId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: null,
  messages: [],
  outputFormat: 'text',
  isLoading: false,
  error: null,

  initSession: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await chatApi.createChatSession();
      set({ sessionId: res.session_id, messages: [], isLoading: false });
      return res.session_id;
    } catch (err: any) {
      set({ error: err.message || 'Failed to initialize chat session', isLoading: false });
      throw err;
    }
  },

  sendMessage: async (message: string) => {
    let sessId = get().sessionId;
    if (!sessId) {
      sessId = await get().initSession();
    }
    
    // Optimistic user message update
    const userMsg: MessageHistoryItem = {
      role: 'user',
      content: message,
      citations: [],
      timestamp: new Date().toISOString(),
    };
    
    set((state) => ({
      messages: [...state.messages, userMsg],
      isLoading: true,
      error: null
    }));

    try {
      const res = await chatApi.sendChatMessage(sessId!, message, get().outputFormat);
      
      const assistantMsg: MessageHistoryItem = {
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        timestamp: new Date().toISOString(),
      };
      
      set((state) => ({
        messages: [...state.messages, assistantMsg],
        isLoading: false
      }));
    } catch (err: any) {
      set({ error: err.message || 'Failed to send message', isLoading: false });
    }
  },

  setOutputFormat: (format) => {
    set({ outputFormat: format });
  },

  loadHistory: async (sessId: string) => {
    set({ isLoading: true, error: null });
    try {
      const history = await chatApi.getChatSessionHistory(sessId);
      set({
        sessionId: history.session_id,
        messages: history.messages,
        isLoading: false
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to load chat history', isLoading: false });
    }
  }
}));
