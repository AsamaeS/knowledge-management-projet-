import { request } from './client';
import {
  Scenario,
  SimulationStartResponse,
  SimulationResponseResponse,
  SimulationSession,
  SimulationReportResponse
} from '../types';

export async function listScenarios(): Promise<Scenario[]> {
  return request<Scenario[]>('/scenarios');
}

export async function createScenario(scenario: any): Promise<Scenario> {
  return request<Scenario>('/scenarios', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scenario),
  });
}

export async function startSimulation(scenarioId: string, userId = 'default_user'): Promise<SimulationStartResponse> {
  return request<SimulationStartResponse>('/simulation/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId, user_id: userId }),
  });
}

export async function respondToSimulation(
  sessionId: string,
  stepId: string,
  response: string | number
): Promise<SimulationResponseResponse> {
  return request<SimulationResponseResponse>('/simulation/respond', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      step_id: stepId,
      response,
    }),
  });
}

export async function getSimulationSession(sessionId: string): Promise<SimulationSession> {
  return request<SimulationSession>(`/simulation/session/${sessionId}`);
}

export async function getSimulationReport(sessionId: string): Promise<SimulationReportResponse> {
  return request<SimulationReportResponse>(`/simulation/session/${sessionId}/report`);
}
