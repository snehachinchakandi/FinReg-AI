import React, { useEffect, useState } from 'react';
import { 
  Network, 
  Layers, 
  Info, 
  FileText, 
  ExternalLink,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { apiClient } from '../api/client';
import { GraphNode, GraphEdge, RegulatoryGraph } from '../types';

export const GraphView: React.FC = () => {
  const [graph, setGraph] = useState<RegulatoryGraph | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGraph() {
      try {
        const res = await apiClient.getDependencyGraph();
        setGraph(res);
        if (res.nodes.length > 0) {
          setSelectedNode(res.nodes[0]);
        }
      } catch (err) {
        console.error('Failed to load dependency graph:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, []);

  // Compute layout positions for nodes in an aesthetically pleasing radial / clustered layout
  const getNodePosition = (index: number, total: number) => {
    const centerX = 400;
    const centerY = 280;
    if (index === 0) return { x: centerX, y: centerY }; // Center node: Master Directions 2025
    const angle = ((index - 1) / (total - 1)) * 2 * Math.PI;
    const radius = index % 2 === 0 ? 210 : 170;
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  };

  const nodePositions = graph
    ? graph.nodes.reduce((acc, node, idx) => {
        acc[node.id] = getNodePosition(idx, graph.nodes.length);
        return acc;
      }, {} as Record<string, { x: number; y: number }>)
    : {};

  const incomingEdges = graph && selectedNode
    ? graph.edges.filter((e) => e.target === selectedNode.id)
    : [];

  const outgoingEdges = graph && selectedNode
    ? graph.edges.filter((e) => e.source === selectedNode.id)
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="border-b border-slate-200/80 pb-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <Network className="w-5 h-5 text-blue-600" />
          <span>Cross-Circular Regulatory Impact & Dependency Graph</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Visual network showing how Master Directions repeal, amend, enforce, and cross-reference earlier RBI regulations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[650px]">
        {/* Left: SVG Canvas (8 cols) */}
        <div className="lg:col-span-8 bg-white border border-slate-200/90 rounded-2xl p-4 flex flex-col relative overflow-hidden shadow-xs">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2 px-2">
            <span className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block"></span>
              <span>Active Master Directions</span>
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block ml-3"></span>
              <span>Repealed Circulars</span>
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400 inline-block ml-3"></span>
              <span>Circulars / Standards</span>
            </span>
            <span className="font-mono text-[11px] text-slate-400">12 Nodes &bull; 8 Statutory Links</span>
          </div>

          <div className="flex-1 bg-slate-50/70 rounded-xl border border-slate-200/90 overflow-hidden relative flex items-center justify-center">
            {graph && (
              <svg className="w-full h-[540px] select-none" viewBox="0 0 800 560">
                <defs>
                  <marker
                    id="arrow-repeal"
                    viewBox="0 0 10 10"
                    refX="22"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
                  </marker>
                  <marker
                    id="arrow-default"
                    viewBox="0 0 10 10"
                    refX="22"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
                  </marker>
                </defs>

                {/* Render Edges */}
                {graph.edges.map((edge, idx) => {
                  const p1 = nodePositions[edge.source];
                  const p2 = nodePositions[edge.target];
                  if (!p1 || !p2) return null;
                  const isRepeal = edge.relation === 'REPEALS';
                  return (
                    <g key={idx}>
                      <line
                        x1={p1.x}
                        y1={p1.y}
                        x2={p2.x}
                        y2={p2.y}
                        stroke={isRepeal ? '#ef4444' : '#cbd5e1'}
                        strokeWidth={isRepeal ? 2 : 1.5}
                        strokeDasharray={isRepeal ? '4,4' : undefined}
                        markerEnd={isRepeal ? 'url(#arrow-repeal)' : 'url(#arrow-default)'}
                      />
                      <text
                        x={(p1.x + p2.x) / 2}
                        y={(p1.y + p2.y) / 2 - 4}
                        fill={isRepeal ? '#dc2626' : '#64748b'}
                        fontSize="9"
                        textAnchor="middle"
                        fontFamily="monospace"
                        className="pointer-events-none font-semibold"
                      >
                        {edge.relation}
                      </text>
                    </g>
                  );
                })}

                {/* Render Nodes */}
                {graph.nodes.map((node) => {
                  const pos = nodePositions[node.id];
                  if (!pos) return null;
                  const isSelected = selectedNode?.id === node.id;
                  const isRepealed = node.status === 'REPEALED';
                  const isMD = node.type === 'MASTER_DIRECTIONS';

                  return (
                    <g
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className="cursor-pointer group"
                    >
                      <circle
                        cx={pos.x}
                        cy={pos.y}
                        r={node.id === 'RBI_DL_2025' ? 24 : 16}
                        fill={
                          isSelected
                            ? '#2563eb'
                            : isRepealed
                            ? '#fee2e2'
                            : isMD
                            ? '#1e3a8a'
                            : '#f1f5f9'
                        }
                        stroke={
                          isSelected
                            ? '#1d4ed8'
                            : isRepealed
                            ? '#ef4444'
                            : isMD
                            ? '#3b82f6'
                            : '#94a3b8'
                        }
                        strokeWidth={isSelected ? 3 : 2}
                        className="transition-all duration-200 group-hover:scale-110"
                      />
                      <text
                        x={pos.x}
                        y={pos.y + 28}
                        fill="#0f172a"
                        fontSize="10"
                        fontWeight={isSelected ? 'bold' : '600'}
                        textAnchor="middle"
                        className="pointer-events-none"
                      >
                        {node.id}
                      </text>
                    </g>
                  );
                })}
              </svg>
            )}
          </div>
        </div>

        {/* Right: Node Details Inspector (4 cols) */}
        <div className="lg:col-span-4 bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs space-y-5">
          <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center space-x-2">
            <Info className="w-4 h-4 text-blue-600" />
            <span>Circular Node Inspector</span>
          </h3>

          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                  {selectedNode.id}
                </span>
                <h4 className="text-base font-bold text-slate-900 mt-2 leading-snug">
                  {selectedNode.label}
                </h4>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block">Year</span>
                  <span className="font-mono font-semibold text-slate-800">{selectedNode.year}</span>
                </div>
                <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-500 uppercase block">Pages</span>
                  <span className="font-mono font-semibold text-slate-800">{selectedNode.pages} pages</span>
                </div>
                <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 col-span-2">
                  <span className="text-[10px] text-slate-500 uppercase block">Status</span>
                  <span className={`text-xs font-semibold ${
                    selectedNode.status === 'ACTIVE' ? 'text-emerald-700' : 'text-rose-700'
                  }`}>
                    {selectedNode.status}
                  </span>
                </div>
              </div>

              {/* Connected Relationships */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                  Regulatory Relationships:
                </span>

                {outgoingEdges.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[10px] text-slate-400 uppercase font-mono">Governs / Affects:</span>
                    {outgoingEdges.map((e, idx) => (
                      <div key={idx} className="bg-slate-50 p-2 rounded-lg border border-slate-200 text-xs">
                        <span className="text-blue-700 font-mono font-semibold">{e.relation}</span> &rarr;{' '}
                        <span className="text-slate-900 font-medium">{e.target}</span>
                        <p className="text-[11px] text-slate-600 mt-0.5">{e.detail}</p>
                      </div>
                    ))}
                  </div>
                )}

                {incomingEdges.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[10px] text-slate-400 uppercase font-mono">Affected by:</span>
                    {incomingEdges.map((e, idx) => (
                      <div key={idx} className="bg-slate-50 p-2 rounded-lg border border-slate-200 text-xs">
                        <span className="text-slate-900 font-medium">{e.source}</span> &rarr;{' '}
                        <span className="text-rose-700 font-mono font-semibold">{e.relation}</span>
                        <p className="text-[11px] text-slate-600 mt-0.5">{e.detail}</p>
                      </div>
                    ))}
                  </div>
                )}

                {incomingEdges.length === 0 && outgoingEdges.length === 0 && (
                  <p className="text-xs text-slate-500 italic">No direct statutory parent links mapped in graph.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-400 text-center py-8">
              Click any circular node in the network to view its legal lineage.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
