import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.dependencies import get_ai_service
from backend.core.ai_service import AIService
from backend.schemas.graph import NodeResponse, EdgeResponse, SubgraphResponse, NodeCreate, GraphStatsResponse
from backend.services.graph_service import GraphService

router = APIRouter()

@router.get("/nodes", response_model=List[NodeResponse])
async def list_nodes(
    type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Retrieve all entity nodes in the database, with optional filtering by type or name match."""
    graph_svc = GraphService(db, ai_service)
    nodes = await graph_svc.list_nodes(node_type=type, search=search, limit=limit, offset=offset)
    return nodes

@router.get("/edges", response_model=List[EdgeResponse])
async def list_edges(
    source_node: Optional[uuid.UUID] = None,
    target_node: Optional[uuid.UUID] = None,
    relation: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Retrieve all relationship edges in the database, with optional node filters."""
    graph_svc = GraphService(db, ai_service)
    edges = await graph_svc.list_edges(source_node=source_node, target_node=target_node, relation=relation)
    return edges

@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    node_id: uuid.UUID,
    depth: int = 1,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Fetch nodes and edges forming a local neighborhood subgraph around a specific node (1-3 hops)."""
    graph_svc = GraphService(db, ai_service)
    subgraph = await graph_svc.get_subgraph(node_id=node_id, depth=depth)
    return subgraph

@router.get("/search", response_model=List[NodeResponse])
async def search_nodes(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Execute pgvector semantic search over all knowledge graph nodes using query text."""
    graph_svc = GraphService(db, ai_service)
    nodes = await graph_svc.search_nodes_semantic(query=q, limit=limit)
    return nodes

@router.post("/nodes", response_model=NodeResponse)
async def create_node(
    node_in: NodeCreate,
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Manually insert an entity node with automatic vector embedding computation."""
    graph_svc = GraphService(db, ai_service)
    node = await graph_svc.create_node(node_in)
    return node

@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats(
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service)
):
    """Retrieve statistical metadata about graph node densities and relationship types."""
    graph_svc = GraphService(db, ai_service)
    stats = await graph_svc.get_stats()
    return stats
