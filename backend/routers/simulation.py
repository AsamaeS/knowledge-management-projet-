import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.dependencies import get_ai_service
from backend.core.ai_service import AIService
from backend.schemas.simulation import (
    ScenarioResponse, ScenarioCreate, SimulationStartRequest, SimulationStartResponse,
    SimulationResponseRequest, SimulationResponseResponse, SimulationSessionResponse,
    SimulationSessionReportResponse
)
from backend.services.simulation_service import SimulationService
from backend.models.simulation import SimulationSession

router = APIRouter()

@router.get("/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Retrieve list of all available simulation scenarios."""
    sim_svc = SimulationService(db, ai_service)
    scenarios = await sim_svc.list_scenarios()
    return scenarios

@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    scenario_in: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Create a new simulation scenario with full decision step tree structure."""
    sim_svc = SimulationService(db, ai_service)
    scenario = await sim_svc.create_scenario(scenario_in)
    return scenario

@router.post("/simulation/start", response_model=SimulationStartResponse)
async def start_simulation(
    request: SimulationStartRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Initialize a new active game play session for a specific scenario."""
    sim_svc = SimulationService(db, ai_service)
    try:
        session, first_step = await sim_svc.start_session(
            scenario_id=request.scenario_id,
            user_id=request.user_id
        )
        return SimulationStartResponse(session_id=session.id, first_step=first_step)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start simulation: {str(e)}"
        )

@router.post("/simulation/respond", response_model=SimulationResponseResponse)
async def respond_to_simulation(
    request: SimulationResponseRequest,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Grade and submit user choice/evaluation and trigger adaptive transitions."""
    sim_svc = SimulationService(db, ai_service)
    try:
        result = await sim_svc.submit_response(
            session_id=request.session_id,
            step_id=request.step_id,
            user_response=request.response
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Step processing failed: {str(e)}"
        )

@router.get("/simulation/session/{session_id}", response_model=SimulationSessionResponse)
async def get_simulation_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch raw status parameters of an active/completed game session."""
    session = await db.get(SimulationSession, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation session {session_id} not found"
        )
    return session

@router.get("/simulation/session/{session_id}/report", response_model=SimulationSessionReportResponse)
async def get_simulation_session_report(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Produce detailed summary scorecard and reviewed knowledge links for a completed session."""
    sim_svc = SimulationService(db, ai_service)
    try:
        report = await sim_svc.get_session_report(session_id)
        return report
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
