import React, { useEffect, useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { PlaySquare, Award, ArrowRight, CornerDownRight, RotateCcw, HelpCircle, CheckCircle, Database } from 'lucide-react';

export default function SimulationPage() {
  const {
    scenarios,
    currentSessionId,
    currentStep,
    runningScore,
    stepFeedback,
    isComplete,
    report,
    isLoading,
    error,
    fetchScenarios,
    startSimulation,
    submitResponse,
    resetSimulation
  } = useSimulationStore();

  const [openText, setOpenText] = useState<string>('');

  useEffect(() => {
    fetchScenarios();
  }, [fetchScenarios]);

  const handleSubmitText = (e: React.FormEvent) => {
    e.preventDefault();
    if (!openText.trim() || isLoading) return;
    submitResponse(openText.trim());
    setOpenText('');
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
      {/* Top Header */}
      <header className="px-8 py-5 border-b border-slate-800 bg-slate-900/40 backdrop-blur-md flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-extrabold tracking-tight text-slate-100 flex items-center space-x-2">
            <PlaySquare className="w-5 h-5 text-indigo-500" />
            <span>NEXUS Decision Simulation Sandbox</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Test corporate decision paths, negotiate supply deals, and solve strategic gridlocks.</p>
        </div>

        {currentSessionId && (
          <button
            onClick={resetSimulation}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-800 text-xs text-slate-400 hover:text-slate-200 bg-slate-950 transition-all duration-150 active:scale-95"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Scenario</span>
          </button>
        )}
      </header>

      {/* Main Sandbox Area */}
      <div className="flex-1 overflow-hidden flex flex-row">
        {/* Left Interactive Play Window */}
        <div className="flex-1 overflow-y-auto p-8">
          {!currentSessionId ? (
            /* SCENARIO CHOICE CARDS LIST */
            <div className="max-w-4xl mx-auto space-y-6">
              <h2 className="text-sm font-semibold text-slate-500 font-mono tracking-wider uppercase mb-2">Available Corporate Sandboxes</h2>
              
              {isLoading ? (
                <div className="py-20 flex flex-col items-center justify-center space-y-3">
                  <svg className="animate-spin h-8 w-8 text-indigo-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-sm text-slate-500 font-mono">Syncing sandbox trees...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {scenarios.map((sc) => (
                    <div
                      key={sc.id}
                      className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 flex flex-col space-y-4 hover:border-slate-700 transition-all duration-200 group relative"
                    >
                      <div className="space-y-1">
                        <span className="text-[9px] uppercase font-bold tracking-widest text-indigo-400 font-mono border border-indigo-900/50 bg-indigo-950/20 px-2 py-0.5 rounded-full">{sc.domain}</span>
                        <h3 className="text-lg font-bold text-slate-100 group-hover:text-white pt-1">{sc.title}</h3>
                        <p className="text-slate-400 text-xs leading-relaxed line-clamp-2">{sc.description}</p>
                      </div>

                      <div className="pt-2 flex items-center justify-between border-t border-slate-800/50">
                        <span className="text-[10px] text-slate-500 font-mono">Diff: {sc.metadata.difficulty || 'Normal'}</span>
                        <button
                          onClick={() => startSimulation(sc.id)}
                          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all duration-150 active:scale-95 shadow shadow-indigo-600/10"
                        >
                          <span>Launch Sandbox</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : isComplete && report ? (
            /* SCORECARD REPORT PANEL */
            <div className="max-w-4xl mx-auto bg-slate-900/20 border border-slate-800 rounded-2xl p-8 space-y-8">
              {/* Report Header Scorecard */}
              <div className="flex flex-col md:flex-row items-center justify-between border-b border-slate-800 pb-6 gap-6">
                <div>
                  <span className="text-[9px] uppercase font-mono text-emerald-400 font-bold tracking-widest bg-emerald-950/30 border border-emerald-900/50 px-2.5 py-1 rounded-full">Sandbox Successful</span>
                  <h2 className="text-2xl font-extrabold text-slate-100 mt-2">{report.scenario_title}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Overall tactical scorecard evaluated on multiple criteria channels.</p>
                </div>
                
                {/* Visual Gauge */}
                <div className="flex items-center space-x-4 bg-slate-950 p-4 border border-slate-800 rounded-2xl shrink-0">
                  <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
                    <svg className="w-full h-full rotate-[-90deg]">
                      <circle cx="40" cy="40" r="34" className="stroke-slate-800" strokeWidth="6" fill="transparent" />
                      <circle
                        cx="40"
                        cy="40"
                        r="34"
                        className="stroke-indigo-500 transition-all duration-500"
                        strokeWidth="6"
                        fill="transparent"
                        strokeDasharray={`${2 * Math.PI * 34}`}
                        strokeDashoffset={`${2 * Math.PI * 34 * (1 - report.session.scores.total / 100)}`}
                      />
                    </svg>
                    <span className="absolute text-lg font-extrabold font-mono text-slate-100">{Math.round(report.session.scores.total)}</span>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wide">Final Evaluation</p>
                    <p className="text-sm font-extrabold text-slate-200">Scorecard Grade</p>
                  </div>
                </div>
              </div>

              {/* Per Step Breakdown */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-slate-500 font-mono tracking-wider uppercase">Step-wise Grading & Feedback</h3>
                <div className="space-y-4">
                  {report.step_breakdown.map((item, idx) => (
                    <div key={idx} className="bg-slate-950 border border-slate-800/80 rounded-2xl p-5 space-y-3 relative hover:border-slate-800 transition-colors duration-150">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 pr-4">
                          <p className="text-slate-300 text-xs font-semibold">{item.step_content}</p>
                          <div className="flex items-center space-x-2 text-[10px] text-indigo-400 font-mono">
                            <CornerDownRight className="w-3.5 h-3.5" />
                            <span>Action: {item.user_response}</span>
                          </div>
                        </div>
                        <span className={`text-xs font-bold font-mono px-2.5 py-1 rounded-full shrink-0 border ${
                          item.score_delta >= 0
                            ? 'bg-emerald-950/20 border-emerald-900/50 text-emerald-400'
                            : 'bg-rose-950/20 border-rose-900/50 text-rose-400'
                        }`}>
                          {item.score_delta >= 0 ? '+' : ''}{item.score_delta} XP
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 bg-slate-900/50 p-3 rounded-xl border border-slate-850 border-dashed leading-relaxed">{item.feedback}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Seeding review node links */}
              {report.recommended_nodes && report.recommended_nodes.length > 0 && (
                <div className="space-y-3 pt-4 border-t border-slate-800">
                  <h3 className="text-xs font-semibold text-slate-500 font-mono tracking-wider uppercase flex items-center space-x-1.5">
                    <Database className="w-4 h-4 text-indigo-500" />
                    <span>Recommended Knowledge Entities to Review</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {report.recommended_nodes.map((node) => (
                      <div key={node.id} className="bg-slate-950 border border-slate-850 p-4 rounded-xl space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200 text-xs">{node.label}</span>
                          <span className="text-[9px] font-bold uppercase text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full font-mono">{node.type}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed truncate-2-lines">{node.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reset Control */}
              <div className="flex justify-end pt-4">
                <button
                  onClick={resetSimulation}
                  className="px-5 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-2 transition-all duration-150 active:scale-95"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Start New Sandbox</span>
                </button>
              </div>
            </div>
          ) : currentStep ? (
            /* ACTIVE SCENARIO PLAYER INTERACTIVE SCREEN */
            <div className="max-w-2xl mx-auto space-y-8">
              {/* Running Score bar header */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex items-center justify-between shadow shadow-slate-950/20">
                <div className="space-y-1">
                  <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wide">Tactical Performance</p>
                  <div className="flex items-baseline space-x-1">
                    <span className="text-xl font-bold font-mono text-indigo-400">{Math.round(runningScore)}</span>
                    <span className="text-xs text-slate-500 font-mono">/ 100 XP</span>
                  </div>
                </div>

                <div className="w-40 bg-slate-950 h-2.5 rounded-full border border-slate-800 overflow-hidden relative">
                  <div className="bg-indigo-500 h-full transition-all duration-300" style={{ width: `${runningScore}%` }} />
                </div>
              </div>

              {/* Feedback Alert if applicable */}
              {stepFeedback && (
                <div className="p-4 rounded-xl border border-indigo-900/30 bg-indigo-950/10 text-xs leading-relaxed text-indigo-300">
                  <span className="font-bold text-[9px] font-mono uppercase text-indigo-400 border border-indigo-900/50 bg-indigo-950/30 px-1.5 py-0.5 rounded-md mr-2">Grading Insights</span>
                  {stepFeedback}
                </div>
              )}

              {/* Step Main Prompt Content */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-500">
                    <HelpCircle className="w-4 h-4 text-indigo-500 shrink-0" />
                    <span className="uppercase">Cognitive Prompt Step ({currentStep.step_type})</span>
                  </div>
                  <p className="text-sm font-semibold text-slate-100 leading-relaxed">{currentStep.content}</p>
                </div>

                {/* Transitions Inputs */}
                {isLoading ? (
                  <div className="py-8 flex flex-col items-center justify-center space-y-2">
                    <svg className="animate-spin h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-[10px] text-slate-500 font-mono">Evaluating strategic routing parameters...</span>
                  </div>
                ) : currentStep.step_type === 'decision' ? (
                  /* DECISION OPTION BUTTONS */
                  <div className="grid grid-cols-1 gap-3 pt-2">
                    {currentStep.options.map((opt, oIdx) => (
                      <button
                        key={oIdx}
                        onClick={() => submitResponse(oIdx)}
                        className="w-full text-left bg-slate-950 hover:bg-slate-800 border border-slate-850 p-4 rounded-xl text-xs text-slate-300 font-semibold leading-relaxed flex items-center space-x-3 transition-all duration-150 active:scale-[0.98]"
                      >
                        <span className="w-5 h-5 flex items-center justify-center bg-indigo-950 text-indigo-400 border border-indigo-900/50 text-[10px] font-bold rounded-lg shrink-0">{oIdx + 1}</span>
                        <span>{opt.label}</span>
                      </button>
                    ))}
                  </div>
                ) : currentStep.step_type === 'evaluation' ? (
                  /* EVALUATION TEXT WRITING INPUT */
                  <form onSubmit={handleSubmitText} className="space-y-4 pt-2">
                    <textarea
                      placeholder="Write your detailed strategic proposal or statement..."
                      value={openText}
                      onChange={(e) => setOpenText(e.target.value)}
                      required
                      rows={4}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors duration-200 placeholder-slate-700 leading-relaxed"
                    />
                    
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={!openText.trim() || isLoading}
                        className={`px-5 py-3 font-semibold text-xs rounded-xl text-white transition-all duration-150 flex items-center space-x-1.5 ${
                          !openText.trim() || isLoading
                            ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                            : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 shadow-md shadow-indigo-600/10'
                        }`}
                      >
                        <span>Submit Strategic Proposal</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </form>
                ) : null}
              </div>
            </div>
          ) : (
            <div className="text-center py-20">
              <p className="text-slate-500">Something went wrong. Please reset the scenario Sandbox.</p>
            </div>
          )}
        </div>

        {/* Right Collapsible Contextual Graph Sidebar */}
        {currentSessionId && currentStep && currentStep.referenced_nodes && currentStep.referenced_nodes.length > 0 && (
          <aside className="w-80 bg-slate-900 border-l border-slate-800 p-6 flex flex-col space-y-6 overflow-y-auto shrink-0">
            <div className="space-y-1">
              <h3 className="text-xs font-bold text-slate-200 flex items-center space-x-2">
                <Database className="w-4 h-4 text-indigo-400" />
                <span>Contextual Knowledge Nodes</span>
              </h3>
              <p className="text-[10px] text-slate-500">These entities from the core Knowledge Graph are automatically linked as learning context.</p>
            </div>

            <div className="space-y-4">
              {currentStep.referenced_nodes.map((node) => (
                <div key={node.id} className="bg-slate-950 border border-slate-850 p-4 rounded-xl space-y-2 hover:border-slate-800 transition-colors duration-150">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 text-xs">{node.label}</span>
                    <span className="text-[8px] font-bold uppercase text-slate-500 bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded-full font-mono">{node.type}</span>
                  </div>
                  <p className="text-[10px] text-slate-400 leading-relaxed font-sans">{node.description}</p>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
