import { create } from 'zustand';
import { GraphNode, GraphEdge, SubgraphResponse, GraphStats } from '../types';
import * as graphApi from '../api/graph';

interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNode: GraphNode | null;
  subgraph: SubgraphResponse | null;
  stats: GraphStats | null;
  isLoading: boolean;
  error: string | null;
  
  fetchStats: () => Promise<void>;
  searchGraph: (q: string) => Promise<void>;
  fetchSubgraph: (nodeId: string, depth?: number) => Promise<void>;
  selectNode: (node: GraphNode | null) => void;
  createManualNode: (node: { label: string; type: string; description?: string }) => Promise<void>;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  subgraph: null,
  stats: null,
  isLoading: false,
  error: null,

  fetchStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const stats = await graphApi.getGraphStats();
      // Also load all nodes/edges by default to render full graph initially
      const nodes = await graphApi.listNodes(undefined, undefined, 100, 0);
      const edges = await graphApi.listEdges();
      set({ stats, nodes, edges, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to load graph stats', isLoading: false });
    }
  },

  searchGraph: async (q: string) => {
    if (!q.trim()) {
      // If empty query, reload all
      const nodes = await graphApi.listNodes(undefined, undefined, 100, 0);
      set({ nodes, error: null });
      return;
    }
    set({ isLoading: true, error: null });
    try {
      const nodes = await graphApi.searchNodes(q);
      set({ nodes, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to search nodes', isLoading: false });
    }
  },

  fetchSubgraph: async (nodeId: string, depth = 1) => {
    set({ isLoading: true, error: null });
    try {
      const subgraph = await graphApi.getSubgraph(nodeId, depth);
      set({
        subgraph,
        nodes: subgraph.nodes,
        edges: subgraph.edges,
        isLoading: false
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch subgraph', isLoading: false });
    }
  },

  selectNode: (node: GraphNode | null) => {
    set({ selectedNode: node });
    if (node) {
      get().fetchSubgraph(node.id, 1);
    } else {
      set({ subgraph: null });
    }
  },

  createManualNode: async (nodeData) => {
    set({ isLoading: true, error: null });
    try {
      const newNode = await graphApi.createNode(nodeData);
      set((state) => ({
        nodes: [newNode, ...state.nodes],
        isLoading: false
      }));
      await get().fetchStats();
    } catch (err: any) {
      set({ error: err.message || 'Failed to create manual node', isLoading: false });
    }
  }
}));
