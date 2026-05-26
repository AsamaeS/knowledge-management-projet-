import { request } from './client';
import { ChatSessionResponse, ChatMessageResponse, ChatHistoryResponse } from '../types';

export async function createChatSession(userId = 'default_user'): Promise<ChatSessionResponse> {
  return request<ChatSessionResponse>('/chat/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  });
}

export async function sendChatMessage(
  sessionId: string,
  message: string,
  outputFormat: 'text' | 'swot' | 'pestel' = 'text'
): Promise<ChatMessageResponse> {
  return request<ChatMessageResponse>('/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      output_format: outputFormat,
    }),
  });
}

export async function getChatSessionHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return request<ChatHistoryResponse>(`/chat/session/${sessionId}`);
}
