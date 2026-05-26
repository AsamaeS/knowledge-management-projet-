import { request } from './client';
import { IngestionResponse, Document } from '../types';

export async function ingestFile(
  file: File,
  sourceType: string,
  author?: string,
  docDate?: string
): Promise<IngestionResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_type', sourceType);
  if (author) formData.append('author', author);
  if (docDate) formData.append('doc_date', docDate);

  return request<IngestionResponse>('/ingest/file', {
    method: 'POST',
    body: formData, // fetch sets boundary automatically
  });
}

export async function getIngestionStatus(documentId: string): Promise<any> {
  return request<any>(`/ingest/status/${documentId}`);
}

export async function listDocuments(limit = 20, offset = 0): Promise<Document[]> {
  return request<Document[]>(`/documents?limit=${limit}&offset=${offset}`);
}
