import { create } from 'zustand';
import { Scenario, ScenarioStep, SimulationSession, SimulationReportResponse } from '../types';
import * as simApi from '../api/simulation';

interface SimulationState {
  scenarios: Scenario[];
  currentSessionId: string | null;
  currentStep: ScenarioStep | null;
  runningScore: number;
  stepFeedback: string;
  isComplete: boolean;
  report: SimulationReportResponse | null;
  isLoading: boolean;
  error: string | null;

  fetchScenarios: () => Promise<void>;
  startSimulation: (scenarioId: string) => Promise<void>;
  submitResponse: (response: string | number) => Promise<void>;
  fetchReport: (sessId: string) => Promise<void>;
  resetSimulation: () => void;
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  scenarios: [],
  currentSessionId: null,
  currentStep: null,
  runningScore: 0,
  stepFeedback: '',
  isComplete: false,
  report: null,
  isLoading: false,
  error: null,

  fetchScenarios: async () => {
    set({ isLoading: true, error: null });
    try {
      const scenarios = await simApi.listScenarios();
      set({ scenarios, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch scenarios', isLoading: false });
    }
  },

  startSimulation: async (scenarioId: string) => {
    set({ isLoading: true, error: null, isComplete: false, report: null, stepFeedback: '', runningScore: 0 });
    try {
      const res = await simApi.startSimulation(scenarioId);
      set({
        currentSessionId: res.session_id,
        currentStep: res.first_step || null,
        isLoading: false
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to start simulation', isLoading: false });
    }
  },

  submitResponse: async (response: string | number) => {
    const sessId = get().currentSessionId;
    const step = get().currentStep;
    if (!sessId || !step) {
      set({ error: 'No active simulation session or step' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      const res = await simApi.respondToSimulation(sessId, step.id, response);
      
      set((state) => ({
        currentStep: res.next_step || null,
        runningScore: state.runningScore + res.score_delta,
        stepFeedback: res.feedback,
        isComplete: res.is_complete,
        isLoading: false
      }));

      if (res.is_complete) {
        await get().fetchReport(sessId);
      }
    } catch (err: any) {
      set({ error: err.message || 'Failed to submit simulation response', isLoading: false });
    }
  },

  fetchReport: async (sessId: string) => {
    set({ isLoading: true, error: null });
    try {
      const report = await simApi.getSimulationReport(sessId);
      set({ report, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch session report', isLoading: false });
    }
  },

  resetSimulation: () => {
    set({
      currentSessionId: null,
      currentStep: null,
      runningScore: 0,
      stepFeedback: '',
      isComplete: false,
      report: null,
      error: null
    });
  }
}));
