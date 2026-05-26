from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# Steps
class StepOption(BaseModel):
    label: str = Field(..., description="Label or text description of the choice option")
    next_step_id: Optional[UUID] = Field(None, description="Step ID to transition to if chosen")
    score_delta: float = Field(0.0, description="Running score change for this choice")
    score_threshold_min: Optional[float] = Field(None, description="Score threshold lower bound for adaptive routing")
    score_threshold_max: Optional[float] = Field(None, description="Score threshold upper bound for adaptive routing")

class ScenarioStepCreate(BaseModel):
    content: str = Field(..., description="Content text presented to user")
    step_type: str = Field(..., description="prompt | decision | evaluation | end")
    options: List[StepOption] = Field(default_factory=list, description="Transition options for decision steps")
    evaluation_criteria: Dict[str, Any] = Field(default_factory=dict, description="Rubric for evaluating free text")
    knowledge_refs: List[UUID] = Field(default_factory=list, description="Referenced nodes in the knowledge graph")

class ScenarioStepResponse(ScenarioStepCreate):
    id: UUID = Field(..., description="Step unique ID")
    scenario_id: UUID = Field(..., description="Scenario ID context")
    created_at: datetime = Field(..., description="Creation date")
    
    # Extra node data attached dynamically on step fetch
    referenced_nodes: Optional[List[Dict[str, Any]]] = Field(None, description="Knowledge graph nodes data attached for UI context")

    model_config = ConfigDict(from_attributes=True)


# Scenarios
class ScenarioCreate(BaseModel):
    title: str = Field(..., description="Scenario title")
    description: Optional[str] = Field(None, description="Short summary context")
    domain: str = Field(..., description="interview | negotiation | leadership")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    steps: List[ScenarioStepCreate] = Field(..., description="Full steps tree structure")

class ScenarioResponse(BaseModel):
    id: UUID = Field(..., description="Scenario ID")
    title: str = Field(..., description="Scenario title")
    description: Optional[str] = Field(None, description="Scenario description")
    domain: str = Field(..., description="Scenario domain")
    root_step_id: Optional[UUID] = Field(None, description="Start step ID")
    metadata: Dict[str, Any] = Field(..., description="Metadata dict")
    created_at: datetime = Field(..., description="Creation date")

    model_config = ConfigDict(from_attributes=True)


# Game Session
class SimulationStartRequest(BaseModel):
    scenario_id: UUID = Field(..., description="UUID of scenario to launch")
    user_id: str = Field(..., description="Simple session user identifier")

class SimulationStartResponse(BaseModel):
    session_id: UUID = Field(..., description="Unique active game session ID")
    first_step: Optional[ScenarioStepResponse] = Field(None, description="Active step object to render first")


class SimulationResponseRequest(BaseModel):
    session_id: UUID = Field(..., description="Active simulation session ID")
    step_id: UUID = Field(..., description="The current step being answered")
    response: Union[int, str] = Field(..., description="Index of selected option (decision) or free-text statement (evaluation)")


class SimulationResponseResponse(BaseModel):
    next_step: Optional[ScenarioStepResponse] = Field(None, description="Next active step to transition to, or null if end")
    score_delta: float = Field(..., description="Immediate impact on the running total")
    feedback: str = Field(..., description="Qualitative evaluation feedback")
    is_complete: bool = Field(..., description="Indicates if scenario is finished")


class SimulationSessionResponse(BaseModel):
    id: UUID = Field(..., description="Session ID")
    scenario_id: UUID = Field(..., description="Scenario ID")
    user_id: str = Field(..., description="User ID")
    current_step: Optional[UUID] = Field(None, description="Current step ID")
    path_taken: List[Dict[str, Any]] = Field(..., description="Step transition history")
    scores: Dict[str, float] = Field(..., description="Breakdown of running scores")
    status: str = Field(..., description="active | completed | abandoned")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(from_attributes=True)


class SimulationSessionReportResponse(BaseModel):
    session: SimulationSessionResponse = Field(..., description="Raw session model information")
    scenario_title: str = Field(..., description="Title of the completed scenario")
    step_breakdown: List[Dict[str, Any]] = Field(..., description="Detailed grading per step completed")
    recommended_nodes: List[Dict[str, Any]] = Field(..., description="Knowledge nodes recommended for review based on references")
