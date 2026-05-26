import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Models
from backend.models.simulation import Scenario, ScenarioStep, SimulationSession
from backend.models.graph import Node

# Schemas
from backend.schemas.simulation import (
    ScenarioCreate, ScenarioStepResponse, SimulationResponseResponse,
    SimulationSessionResponse, SimulationSessionReportResponse
)

# Services
from backend.core.ai_service import AIService

logger = logging.getLogger(__name__)

class SimulationService:
    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    async def list_scenarios(self) -> List[Scenario]:
        """Fetch all scenarios from the database."""
        stmt = select(Scenario)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_scenario(self, sc_in: ScenarioCreate) -> Scenario:
        """Saves a new scenario and compiles its decision tree of steps."""
        try:
            # 1. Create Scenario instance
            scenario = Scenario(
                title=sc_in.title,
                description=sc_in.description,
                domain=sc_in.domain,
                metadata=sc_in.metadata
            )
            self.db.add(scenario)
            await self.db.flush()  # get scenario.id

            step_label_to_id = {}
            db_steps = []

            # 2. Insert all steps first to obtain UUIDs
            for step_in in sc_in.steps:
                temp_id = uuid.uuid4()
                step = ScenarioStep(
                    id=temp_id,
                    scenario_id=scenario.id,
                    content=step_in.content,
                    step_type=step_in.step_type,
                    evaluation_criteria=step_in.evaluation_criteria,
                    knowledge_refs=step_in.knowledge_refs,
                    options=[]  # populate transitions later
                )
                self.db.add(step)
                db_steps.append((step, step_in))
                
            await self.db.flush()

            # Map the steps sequentially if they don't have explicit ids
            for i, (db_step, step_in) in enumerate(db_steps):
                step_label_to_id[f"step_{i}"] = db_step.id

            # Set root step
            if db_steps:
                scenario.root_step_id = db_steps[0][0].id

            # 3. Resolve transition options mapping
            for i, (db_step, step_in) in enumerate(db_steps):
                resolved_options = []
                for opt in step_in.options:
                    next_id = opt.next_step_id
                    # If next_step_id is not specified but we have relative indexing
                    if not next_id and i + 1 < len(db_steps):
                        next_id = db_steps[i + 1][0].id
                    
                    resolved_options.append({
                        "label": opt.label,
                        "next_step_id": str(next_id) if next_id else None,
                        "score_delta": opt.score_delta,
                        "score_threshold_min": opt.score_threshold_min,
                        "score_threshold_max": opt.score_threshold_max
                    })
                db_step.options = resolved_options

            await self.db.commit()
            await self.db.refresh(scenario)
            return scenario

        except Exception as e:
            logger.error(f"Failed to create scenario: {e}")
            await self.db.rollback()
            raise

    async def get_step_response(self, step_id: uuid.UUID) -> Optional[ScenarioStepResponse]:
        """Fetch step data and dynamically attach referenced knowledge graph entities."""
        step = await self.db.get(ScenarioStep, step_id)
        if not step:
            return None

        # Build referenced nodes context
        ref_nodes = []
        if step.knowledge_refs:
            stmt = select(Node).where(Node.id.in_(step.knowledge_refs))
            res = await self.db.execute(stmt)
            for node in res.scalars().all():
                ref_nodes.append({
                    "id": str(node.id),
                    "label": node.label,
                    "type": node.type,
                    "description": node.description
                })

        return ScenarioStepResponse(
            id=step.id,
            scenario_id=step.scenario_id,
            content=step.content,
            step_type=step.step_type,
            options=step.options or [],
            evaluation_criteria=step.evaluation_criteria or {},
            knowledge_refs=step.knowledge_refs,
            referenced_nodes=ref_nodes,
            created_at=step.created_at
        )

    async def start_session(self, scenario_id: uuid.UUID, user_id: str) -> Tuple[SimulationSession, Optional[ScenarioStepResponse]]:
        """Instantiate a new active simulation game play session."""
        scenario = await self.db.get(Scenario, scenario_id)
        if not scenario:
            raise ValueError("Scenario not found")

        # Create session
        session = SimulationSession(
            scenario_id=scenario_id,
            user_id=user_id,
            current_step=scenario.root_step_id,
            path_taken=[],
            scores={"content": 0.0, "reasoning": 0.0, "total": 0.0},
            status="active"
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        # Get first step
        first_step = None
        if scenario.root_step_id:
            first_step = await self.get_step_response(scenario.root_step_id)

        return session, first_step

    async def submit_response(
        self,
        session_id: uuid.UUID,
        step_id: uuid.UUID,
        user_response: Union[int, str]
    ) -> SimulationResponseResponse:
        """Process user action, evaluate/grade it, route to next step using adaptive branching, and commit."""
        session = await self.db.get(SimulationSession, session_id)
        if not session or session.status != "active":
            raise ValueError("Session is not active or not found")

        step = await self.db.get(ScenarioStep, step_id)
        if not step:
            raise ValueError("Step not found")

        # 1. Scoring & Evaluation
        score_delta = 0.0
        feedback = ""
        next_step_id = None
        step_score = 0.0

        if step.step_type == "decision":
            # Options choice
            try:
                opt_index = int(user_response)
                options = step.options or []
                if 0 <= opt_index < len(options):
                    chosen_opt = options[opt_index]
                    score_delta = float(chosen_opt.get("score_delta", 0.0))
                    feedback = f"You chose: {chosen_opt.get('label')}"
                    next_step_id = chosen_opt.get("next_step_id")
                    if next_step_id:
                        next_step_id = uuid.UUID(next_step_id)
                    step_score = score_delta
                else:
                    feedback = "Invalid decision index."
            except Exception as e:
                logger.error(f"Error parsing decision index: {e}")
                feedback = "Failed to parse decision."

        elif step.step_type == "evaluation":
            # Open-ended text graded by LLM
            logger.info("Invoking LLM evaluator for simulation open response...")
            eval_res = await self.ai_service.score_simulation_response(
                step_content=step.content,
                evaluation_criteria=step.evaluation_criteria or {},
                user_response=str(user_response)
            )
            
            scores = eval_res.get("scores", {"total": 5.0})
            feedback = eval_res.get("feedback", "No feedback provided.")
            step_score = float(scores.get("total", 5.0))
            score_delta = step_score
            
            # 2. Adaptive Branching Logic
            # Look for options matching the score boundaries
            # min <= step_score < max
            options = step.options or []
            for opt in options:
                min_val = opt.get("score_threshold_min")
                max_val = opt.get("score_threshold_max")
                
                # Check bounds
                if min_val is not None and max_val is not None:
                    if float(min_val) <= step_score < float(max_val):
                        next_step_id = opt.get("next_step_id")
                        if next_step_id:
                            next_step_id = uuid.UUID(next_step_id)
                        break

            # Standard sequentially fallback if no matching branch found
            if not next_step_id and options:
                # Use first option next step
                next_step_id = options[0].get("next_step_id")
                if next_step_id:
                    next_step_id = uuid.UUID(next_step_id)

        # 3. Update Session Running Score
        current_scores = dict(session.scores)
        current_scores["total"] = max(0.0, min(100.0, current_scores.get("total", 0.0) + score_delta))
        if step.step_type == "evaluation":
            # also accumulate detailed scores if applicable
            current_scores["content"] = current_scores.get("content", 0.0) + eval_res.get("scores", {}).get("content", 0.0)
            current_scores["reasoning"] = current_scores.get("reasoning", 0.0) + eval_res.get("scores", {}).get("reasoning", 0.0)
        
        session.scores = current_scores

        # 4. Save Path taken history
        path = list(session.path_taken)
        path.append({
            "step_id": str(step_id),
            "step_type": step.step_type,
            "response": user_response,
            "score_delta": score_delta,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.path_taken = path

        # 5. Check transition to next step
        is_complete = False
        next_step = None

        if next_step_id:
            next_step = await self.get_step_response(next_step_id)
            if next_step and next_step.step_type == "end":
                is_complete = True
                session.status = "completed"
                session.completed_at = datetime.utcnow()
                session.current_step = next_step_id
            else:
                session.current_step = next_step_id
        else:
            # No next step means simulation concludes
            is_complete = True
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.current_step = None

        await self.db.commit()

        return SimulationResponseResponse(
            next_step=next_step,
            score_delta=score_delta,
            feedback=feedback,
            is_complete=is_complete
        )

    async def get_session_report(self, session_id: uuid.UUID) -> SimulationSessionReportResponse:
        """Generates a detailed summary scorecard report with reviewed knowledge graph elements."""
        db_session = await self.db.get(SimulationSession, session_id)
        if not db_session:

            raise ValueError("Session not found")

        scenario = await self.db.get(Scenario, db_session.scenario_id)
        scenario_title = scenario.title if scenario else "Unknown Scenario"

        # 1. Compile per step breakdown
        breakdown = []
        referenced_node_ids = set()

        for path_item in db_session.path_taken:
            step_uuid = uuid.UUID(path_item["step_id"])
            step = await self.db.get(ScenarioStep, step_uuid)
            
            if step:
                # accumulate node references to suggest for review
                for nid in step.knowledge_refs:
                    referenced_node_ids.add(nid)

                breakdown.append({
                    "step_id": path_item["step_id"],
                    "step_content": step.content,
                    "step_type": path_item["step_type"],
                    "user_response": path_item["response"],
                    "score_delta": path_item["score_delta"],
                    "feedback": path_item["feedback"]
                })

        # 2. Query recommended nodes
        recommended_nodes = []
        if referenced_node_ids:
            nodes_stmt = select(Node).where(Node.id.in_(list(referenced_node_ids)))
            res = await self.db.execute(nodes_stmt)
            for node in res.scalars().all():
                recommended_nodes.append({
                    "id": str(node.id),
                    "label": node.label,
                    "type": node.type,
                    "description": node.description
                })

        session_res = SimulationSessionResponse.model_validate(db_session)

        return SimulationSessionReportResponse(
            session=session_res,
            scenario_title=scenario_title,
            step_breakdown=breakdown,
            recommended_nodes=recommended_nodes
        )
