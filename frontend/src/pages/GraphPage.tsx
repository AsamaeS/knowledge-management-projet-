import React, { useEffect, useState, useCallback } from 'react';
import { ReactFlow, Background, Controls, useNodesState, useEdgesState, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useGraphStore } from '../store/graphStore';
import { useChatStore } from '../store/chatStore';
import { useNavigate } from 'react-router-dom';
import { Network, Search, PlusCircle, HelpCircle, FileText, Share2, Cpu, Database } from 'lucide-react';

export default function GraphPage() {
  const navigate = useNavigate();
  
  const {
    nodes: storeNodes,
    edges: storeEdges,
    selectedNode,
    subgraph,
    stats,
    isLoading,
    error,
    fetchStats,
    searchGraph,
    fetchSubgraph,
    selectNode,
    createManualNode
  } = useGraphStore();

  const {
    sendMessage,
    setOutputFormat
  } = useChatStore();

  const [q, setQ] = useState<string>('');
  const [depth, setDepth] = useState<number>(1);
  const [showAddNode, setShowAddNode] = useState<boolean>(false);
  
  // Form for manual node creation
  const [manualLabel, setManualLabel] = useState<string>('');
  const [manualType, setManualType] = useState<string>('concept');
  const [manualDesc, setManualDesc] = useState<string>('');

  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState([]);
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Synchronize React Flow nodes & edges when store updates
  useEffect(() => {
    // Generate simple grid or circular layout positions for nodes
    const flowNodes = storeNodes.map((node, index) => {
      // Circle layout calculation
      const angle = (index / (storeNodes.length || 1)) * 2 * Math.PI;
      const radius = 250 + Math.min(storeNodes.length * 15, 200);
      const x = 400 + radius * Math.cos(angle);
      const y = 350 + radius * Math.sin(angle);

      // Node colors based on type
      let colorClass = 'bg-orange-500 border-orange-600 text-orange-100';
      if (node.type === 'person') colorClass = 'bg-blue-600 border-blue-700 text-blue-100';
      else if (node.type === 'company') colorClass = 'bg-emerald-600 border-emerald-700 text-emerald-100';
      else if (node.type === 'theme') colorClass = 'bg-purple-600 border-purple-700 text-purple-100';
      else if (node.type === 'insight') colorClass = 'bg-pink-600 border-pink-700 text-pink-100';

      return {
        id: node.id,
        position: { x, y },
        data: {
          label: (
            <div className="flex flex-col items-center space-y-0.5">
              <span className="font-extrabold text-[11px] uppercase tracking-wide opacity-50 font-mono text-[8px]">{node.type}</span>
              <span className="font-semibold text-xs">{node.label}</span>
            </div>
          )
        },
        className: `${colorClass} border-2 rounded-xl p-3 shadow-lg hover:shadow-indigo-500/10 cursor-pointer min-w-[120px] text-center transition-all duration-200`,
        style: {
          color: '#fff',
          boxShadow: selectedNode?.id === node.id ? '0 0 0 4px rgba(99, 102, 241, 0.4)' : undefined,
          transform: selectedNode?.id === node.id ? 'scale(1.05)' : undefined
        }
      };
    });

    const flowEdges = storeEdges.map((edge) => {
      return {
        id: edge.id,
        source: edge.source_node,
        target: edge.target_node,
        label: edge.relation,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 14,
          height: 14,
          color: '#475569'
        },
        style: {
          stroke: '#475569',
          strokeWidth: 1.5
        },
        labelStyle: {
          fill: '#94a3b8',
          fontSize: 8,
          fontWeight: 600,
          fontFamily: 'monospace'
        },
        labelBgPadding: [6, 4],
        labelBgBorderRadius: 4,
        labelBgStyle: {
          fill: '#0f172a',
          fillOpacity: 0.8
        }
      };
    });

    setReactFlowNodes(flowNodes);
    setReactFlowEdges(flowEdges);
  }, [storeNodes, storeEdges, selectedNode, setReactFlowNodes, setReactFlowEdges]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchGraph(q);
  };

  const handleNodeClick = useCallback((event: React.MouseEvent, node: any) => {
    const storeNode = storeNodes.find((n) => n.id === node.id);
    if (storeNode) {
      selectNode(storeNode);
    }
  }, [storeNodes, selectNode]);

  const handleDepthChange = (newDepth: number) => {
    setDepth(newDepth);
    if (selectedNode) {
      fetchSubgraph(selectedNode.id, newDepth);
    }
  };

  const handleDiscussInChat = () => {
    if (!selectedNode) return;
    sendMessage(`Analyze the strategic implications of the entity: ${selectedNode.label} (${selectedNode.type}). Description: ${selectedNode.description || 'N/A'}`);
    setOutputFormat('text');
    navigate('/chat');
  };

  const handleAddNodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualLabel.trim()) return;
    
    await createManualNode({
      label: manualLabel.trim(),
      type: manualType,
      description: manualDesc.trim() || undefined
    });

    setManualLabel('');
    setManualDesc('');
    setShowAddNode(false);
  };

  return (
    <div className="flex-1 flex flex-row min-h-screen overflow-hidden">
      {/* Central Graph Visualizer Canvas */}
      <div className="flex-1 flex flex-col relative min-h-screen">
        {/* Top Controls Overlay */}
        <div className="absolute top-6 left-6 z-10 flex flex-col md:flex-row items-stretch md:items-center gap-4 w-[calc(100%-3rem)] max-w-4xl">
          {/* Search bar */}
          <form onSubmit={handleSearch} className="flex bg-slate-950/80 backdrop-blur border border-slate-800 rounded-xl px-4 py-3 flex-1 items-center space-x-3 shadow-lg">
            <Search className="w-4 h-4 text-slate-500 shrink-0" />
            <input
              type="text"
              placeholder="Search entities label..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="bg-transparent focus:outline-none text-xs text-slate-200 flex-1 placeholder-slate-600"
            />
            {q && (
              <button
                type="button"
                onClick={() => { setQ(''); searchGraph(''); }}
                className="text-[10px] text-slate-500 hover:text-slate-300 font-mono"
              >
                Clear
              </button>
            )}
          </form>

          {/* Depth Controller (Only if node selected) */}
          {selectedNode && (
            <div className="bg-slate-950/80 backdrop-blur border border-slate-800 rounded-xl px-4 py-3 flex items-center space-x-4 shadow-lg shrink-0">
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wide">Graph Hops Depth</span>
              <div className="flex items-center space-x-2">
                {[1, 2, 3].map((d) => (
                  <button
                    key={d}
                    onClick={() => handleDepthChange(d)}
                    className={`w-6 h-6 rounded-md text-xs font-mono font-bold flex items-center justify-center transition-all ${
                      depth === d
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-900 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Create manual node button */}
          <button
            onClick={() => setShowAddNode(!showAddNode)}
            className="bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white text-xs font-semibold px-4 py-3 rounded-xl flex items-center space-x-1.5 shadow-lg shadow-indigo-600/10 shrink-0"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Add Entity</span>
          </button>
        </div>

        {/* Floating statistics panel Bottom Left */}
        {stats && (
          <div className="absolute bottom-6 left-6 z-10 bg-slate-950/80 backdrop-blur border border-slate-800 rounded-2xl p-4 shadow-lg space-y-1 w-60">
            <p className="text-[9px] font-mono text-slate-500 uppercase tracking-widest">Knowledge Density</p>
            <div className="flex items-baseline space-x-3 pt-1">
              <div className="flex flex-col">
                <span className="text-xl font-bold font-mono text-indigo-400">{stats.total_nodes}</span>
                <span className="text-[8px] text-slate-500 font-mono uppercase">Entities</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold font-mono text-indigo-400">{stats.total_edges}</span>
                <span className="text-[8px] text-slate-500 font-mono uppercase">Relations</span>
              </div>
            </div>
          </div>
        )}

        {/* Loading spinners */}
        {isLoading && (
          <div className="absolute top-24 left-6 z-10 bg-slate-950/80 backdrop-blur border border-slate-800 rounded-xl px-4 py-2.5 flex items-center space-x-2.5 shadow">
            <svg className="animate-spin h-4 w-4 text-indigo-500" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wide">Syncing graph elements...</span>
          </div>
        )}

        {/* Add node drawer overlay */}
        {showAddNode && (
          <div className="absolute top-24 right-6 z-20 bg-slate-950/90 backdrop-blur border border-slate-800 rounded-2xl p-6 shadow-xl w-80 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <PlusCircle className="w-4.5 h-4.5 text-indigo-500" />
              <span>Create Manual Entity Node</span>
            </h3>
            
            <form onSubmit={handleAddNodeSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Entity Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tesla Motors"
                  value={manualLabel}
                  onChange={(e) => setManualLabel(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Entity Type</label>
                <select
                  value={manualType}
                  onChange={(e) => setManualType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="person">Person</option>
                  <option value="company">Company</option>
                  <option value="theme">Strategic Theme</option>
                  <option value="concept">Concept/Core</option>
                  <option value="insight">Key Insight</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Short Description</label>
                <textarea
                  placeholder="Summarize context and definitions..."
                  value={manualDesc}
                  onChange={(e) => setManualDesc(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddNode(false)}
                  className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold"
                >
                  Create Node
                </button>
              </div>
            </form>
          </div>
        )}

        {/* React Flow Graph render */}
        <div className="flex-1 bg-slate-950/20">
          <ReactFlow
            nodes={reactFlowNodes}
            edges={reactFlowEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            minZoom={0.2}
            maxZoom={2.0}
          >
            <Background color="#1e293b" gap={24} size={1} />
            <Controls className="bg-slate-900 border border-slate-850 rounded-lg shadow-lg [&_button]:bg-transparent [&_button]:border-slate-800 [&_button]:text-slate-400 [&_button:hover]:bg-slate-800" />
          </ReactFlow>
        </div>
      </div>

      {/* Right Slide-over Node Detail Side Panel */}
      {selectedNode && (
        <aside className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col min-h-screen shrink-0 shadow-2xl relative z-30">
          {/* Panel Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between shrink-0">
            <div className="space-y-1">
              <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider border font-mono ${
                selectedNode.type === 'person' ? 'bg-blue-950/30 border-blue-900/50 text-blue-400' :
                selectedNode.type === 'company' ? 'bg-emerald-950/30 border-emerald-900/50 text-emerald-400' :
                selectedNode.type === 'theme' ? 'bg-purple-950/30 border-purple-900/50 text-purple-400' :
                'bg-orange-950/30 border-orange-900/50 text-orange-400'
              }`}>
                {selectedNode.type}
              </span>
              <h2 className="text-xl font-extrabold text-slate-100">{selectedNode.label}</h2>
            </div>
            <button
              onClick={() => selectNode(null)}
              className="text-xs text-slate-500 hover:text-slate-300 font-mono"
            >
              Close
            </button>
          </div>

          {/* Details Scroll Content */}
          <div className="flex-1 p-6 space-y-6 overflow-y-auto">
            {/* Description */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-slate-500 font-mono tracking-wider uppercase">Context Summary</h3>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-850 border-dashed">
                {selectedNode.description || 'No description provided for this knowledge graph entity.'}
              </p>
            </div>

            {/* Connected sub-entities checklist */}
            {subgraph && subgraph.nodes.length > 1 && (
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-slate-500 font-mono tracking-wider uppercase flex items-center space-x-1.5">
                  <Share2 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Connected Relations ({subgraph.edges.length})</span>
                </h3>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {subgraph.edges.map((edge) => {
                    const otherNode = subgraph.nodes.find(
                      (n) => n.id === (edge.source_node === selectedNode.id ? edge.target_node : edge.source_node)
                    );
                    if (!otherNode) return null;
                    return (
                      <div
                        key={edge.id}
                        onClick={() => selectNode(otherNode)}
                        className="bg-slate-950/50 hover:bg-slate-950 border border-slate-850 p-3 rounded-xl text-xs flex items-center justify-between cursor-pointer transition-colors duration-150"
                      >
                        <span className="font-semibold text-slate-300 truncate max-w-[120px]">{otherNode.label}</span>
                        <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wide bg-slate-900 px-1.5 py-0.5 border border-slate-850 rounded-md">
                          {edge.relation}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="space-y-3 pt-4 border-t border-slate-800">
              <button
                onClick={handleDiscussInChat}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold py-3.5 flex items-center justify-center space-x-1.5 transition-all duration-150 active:scale-95 shadow-md shadow-indigo-600/10"
              >
                <Cpu className="w-4 h-4" />
                <span>Discuss in Chat</span>
              </button>
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
