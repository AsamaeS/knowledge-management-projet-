import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.simulation import Scenario, ScenarioStep
from backend.models.graph import Node

logger = logging.getLogger(__name__)

async def seed_scenarios(db: AsyncSession):
    """Seed initial decision-tree simulation scenarios if none exist."""
    # Check if scenarios already exist
    stmt = select(Scenario)
    res = await db.execute(stmt)
    if res.scalars().first():
        logger.info("Scenarios already seeded. Skipping.")
        return

    logger.info("Seeding NEXUS scenarios...")

    # Create dummy referenced knowledge nodes so we can link them
    # EV Adoption Node
    ev_node = Node(
        label="EV Adoption Trends",
        type="theme",
        description="Global structural shift from combustion engines to battery-electric vehicles.",
        source_ids=[],
        properties={}
    )
    db.add(ev_node)
    
    # BYD Node
    byd_node = Node(
        label="BYD",
        type="company",
        description="Chinese manufacturer leading global electric vehicle vehicle sales and vertical battery integration.",
        source_ids=[],
        properties={}
    )
    db.add(byd_node)

    await db.flush()

    # --- SCENARIO 1: Automotive Industry Expert Interview ---
    sc1 = Scenario(
        title="Automotive Industry Expert Interview",
        description="Test your strategic knowledge of EV market trends and Chinese OEM expansion dynamics in Europe.",
        domain="interview",
        metadata={"difficulty": "medium"}
    )
    db.add(sc1)
    await db.flush()

    # Step 1.1: Root Prompt
    step1_1 = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc1.id,
        content=(
            "Welcome to the Strategic Automotive Panel. You are acting as the Chief Strategy Officer "
            "for a major legacy European OEM. The board is alarmed by BYD's aggressive market entry in Germany "
            "and France, offering EVs at 30% below your production cost. How do you respond?"
        ),
        step_type="decision",
        knowledge_refs=[ev_node.id, byd_node.id]
    )
    db.add(step1_1)
    await db.flush()
    sc1.root_step_id = step1_1.id

    # Step 1.2a: Tariffs / Remediation
    step1_2a = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc1.id,
        content=(
            "You chose to lobby for trade tariffs. The European Commission imposes a temporary 20% tariff, but "
            "BYD immediately announces a new localized mega-factory in Hungary to bypass tariffs. Meanwhile, your "
            "input battery costs remain high. The board demands a new cost-restructuring proposal. "
            "Write a short proposal (1-2 sentences) detailing how you will reduce battery cell sourcing costs."
        ),
        step_type="evaluation",
        evaluation_criteria={
            "supply_chain": "Assesses if candidate mentions localized partnerships or cell raw materials.",
            "financial_viability": "Assesses if candidate shows cost-reduction metrics."
        },
        knowledge_refs=[ev_node.id]
    )
    db.add(step1_2a)

    # Step 1.2b: JV and Compact launch
    step1_2b = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc1.id,
        content=(
            "You chose to form a joint venture and accelerate your mid-market compact EV project. Your JV partner "
            "provides immediate LFP battery chemistry capabilities, slicing raw material costs by 25%. The board is "
            "impressed, but demands to know how you will brand and market this vehicle to compete against premium Chinese brands. "
            "Explain your brand differentiation strategy."
        ),
        step_type="evaluation",
        evaluation_criteria={
            "branding": "Evaluates premium European legacy heritage vs digital-first infotainment.",
            "channel": "Evaluates digital sales channel proposals."
        },
        knowledge_refs=[byd_node.id]
    )
    db.add(step1_2b)

    # Step 1.3: End Step (Tariffs path conclusion)
    step1_3a = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc1.id,
        content=(
            "Simulation complete! You successfully negotiated localized tariffs, but were forced to radically restructure "
            "your supply chain. Your overall performance shows solid crisis-management capabilities but slower strategic agility."
        ),
        step_type="end"
    )
    db.add(step1_3a)

    # Step 1.3b: End Step (JV path conclusion)
    step1_3b = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc1.id,
        content=(
            "Simulation complete! You executed a highly successful, proactive JV compact EV model strategy. "
            "By prioritizing localized chemistry and heritage branding, you successfully defended European market share."
        ),
        step_type="end"
    )
    db.add(step1_3b)
    await db.flush()

    # Link transitions
    step1_1.options = [
        {"label": "Lobby for protective trade tariffs and slow down battery investments.", "next_step_id": str(step1_2a.id), "score_delta": 30.0},
        {"label": "Form a fast joint venture with a battery cell producer and launch a compact EV in 24 months.", "next_step_id": str(step1_2b.id), "score_delta": 50.0}
    ]

    # Evaluation adaptive branches
    step1_2a.options = [
        {"label": "Fail", "next_step_id": str(step1_3a.id), "score_threshold_min": 0.0, "score_threshold_max": 5.0},
        {"label": "Pass", "next_step_id": str(step1_3b.id), "score_threshold_min": 5.0, "score_threshold_max": 10.1}
    ]
    step1_2b.options = [
        {"label": "Standard", "next_step_id": str(step1_3b.id), "score_threshold_min": 0.0, "score_threshold_max": 10.1}
    ]


    # --- SCENARIO 2: Strategic Negotiation Simulation ---
    sc2 = Scenario(
        title="Strategic Procurement Negotiation",
        description="Negotiate a major lithium-ion battery cell supply contract with an aggressive supplier representative.",
        domain="negotiation",
        metadata={"difficulty": "hard"}
    )
    db.add(sc2)
    await db.flush()

    # Step 2.1
    step2_1 = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc2.id,
        content=(
            "You are in a closed negotiation room with the VP of Sales from CellTech, your primary battery supplier. "
            "They surprise you by demanding a 15% price increase per kilowatt-hour, citing rising lithium carbonate spot prices. "
            "Your factory margins cannot absorb this. What is your opening negotiation move?"
        ),
        step_type="decision",
        knowledge_refs=[ev_node.id]
    )
    db.add(step2_1)
    await db.flush()
    sc2.root_step_id = step2_1.id

    # Step 2.2a
    step2_2a = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc2.id,
        content=(
            "You threatened to walk away. CellTech calls your bluff, knowing your secondary supplier cannot scale volume "
            "for another 12 months. They offer a final take-it-or-leave-it compromise: a 10% price increase, but with an indexed "
            "clause that lowers prices if raw materials drop. How do you respond to secure the factory margins?"
        ),
        step_type="decision"
    )
    db.add(step2_2a)

    # Step 2.2b
    step2_2b = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc2.id,
        content=(
            "You proposed a long-term supply extension in exchange for holding current prices flat. CellTech is interested "
            "but demands that you guarantee minimum annual volume commitments (offtake agreement) of 15 GWh. "
            "Propose a brief risk-mitigation clause to protect your company if EV retail demand drops."
        ),
        step_type="evaluation",
        evaluation_criteria={
            "flexibility": "Assesses candidate's proposal for volume flexibility +/- 20%.",
            "hedging": "Assesses if candidate suggests supply sharing or penalties."
        }
    )
    db.add(step2_2b)

    # Step 2.3
    step2_3 = ScenarioStep(
        id=uuid.uuid4(),
        scenario_id=sc2.id,
        content=(
            "Simulation complete! You navigated a highly tense procurement deadlock. Your performance shows strong "
            "risk-hedging skills and excellent utilization of contractual flexibility clauses."
        ),
        step_type="end"
    )
    db.add(step2_3)
    await db.flush()

    # Link transitions
    step2_1.options = [
        {"label": "Threaten to immediately terminate the negotiation and source from their competitor.", "next_step_id": str(step2_2a.id), "score_delta": 20.0},
        {"label": "Offer to extend the contract duration from 3 to 5 years if they keep pricing flat.", "next_step_id": str(step2_2b.id), "score_delta": 45.0}
    ]

    step2_2a.options = [
        {"label": "Accept the 10% index increase to secure volume immediately.", "next_step_id": str(step2_3.id), "score_delta": 25.0},
        {"label": "Counter-propose a 5% index increase and threaten immediate arbitration.", "next_step_id": str(step2_3.id), "score_delta": 35.0}
    ]

    step2_2b.options = [
        {"label": "Transition", "next_step_id": str(step2_3.id), "score_threshold_min": 0.0, "score_threshold_max": 10.1}
    ]

    await db.commit()
    logger.info("Seed data provisioned successfully.")
