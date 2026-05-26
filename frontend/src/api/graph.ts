import { request } from './client';
import { GraphNode, GraphEdge, SubgraphResponse, GraphStats } from '../types';

export async function listNodes(
  type?: string,
  search?: string,
  limit = 100,
  offset = 0
): Promise<GraphNode[]> {
  let params = `limit=${limit}&offset=${offset}`;
  if (type) params += `&type=${type}`;
  if (search) params += `&search=${encodeURIComponent(search)}`;
  
  return request<GraphNode[]>(`/graph/nodes?${params}`);
}

export async function listEdges(
  sourceNode?: string,
  targetNode?: string,
  relation?: string
): Promise<GraphEdge[]> {
  let params = '';
  const queryParts = [];
  if (sourceNode) queryParts.push(`source_node=${sourceNode}`);
  if (targetNode) queryParts.push(`target_node=${targetNode}`);
  if (relation) queryParts.push(`relation=${relation}`);
  if (queryParts.length > 0) params = '?' + queryParts.join('&');

  return request<GraphEdge[]>(`/graph/edges${params}`);
}

export async function getSubgraph(nodeId: string, depth = 1): Promise<SubgraphResponse> {
  return request<SubgraphResponse>(`/graph/subgraph?node_id=${nodeId}&depth=${depth}`);
}

export async function searchNodes(q: string, limit = 20): Promise<GraphNode[]> {
  return request<GraphNode[]>(`/graph/search?q=${encodeURIComponent(q)}&limit=${limit}`);
}

export async function createNode(node: { label: string; type: string; description?: string; properties?: Record<string, any> }): Promise<GraphNode> {
  return request<GraphNode>('/graph/nodes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(node),
  });
}

export async function getGraphStats(): Promise<GraphStats> {
  return request<GraphStats>('/graph/stats');
}
