import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from backend.core.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String, nullable=False)  # 'interview','negotiation','leadership'
    root_step_id = Column(UUID(as_uuid=True), ForeignKey("scenario_steps.id", use_alter=True, name="fk_scenario_root_step", ondelete="SET NULL"), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ScenarioStep(Base):
    __tablename__ = "scenario_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    step_type = Column(
        Enum("prompt", "decision", "evaluation", "end", name="step_type_enum"),
        nullable=False
    )
    options = Column(JSON, nullable=True, default=list)  # [{label, next_step_id, score_delta}]
    evaluation_criteria = Column(JSON, nullable=True, default=dict)  # rubric
    knowledge_refs = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, nullable=False)
    current_step = Column(UUID(as_uuid=True), ForeignKey("scenario_steps.id", ondelete="SET NULL"), nullable=True)
    path_taken = Column(JSON, nullable=False, default=list)  # list of step_ids + choices
    scores = Column(JSON, nullable=False, default=lambda: {"content": 0.0, "reasoning": 0.0, "total": 0.0})
    status = Column(
        Enum("active", "completed", "abandoned", name="session_status_enum"),
        nullable=False,
        default="active"
    )
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
