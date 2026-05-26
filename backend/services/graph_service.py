import logging
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from backend.models.graph import Node, Edge
from backend.schemas.graph import NodeCreate, GraphStatsResponse, SubgraphResponse
from backend.core.ai_service import AIService

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    async def list_nodes(
        self,
        node_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Node]:
        """Query and filter nodes from the database."""
        stmt = select(Node)
        
        if node_type:
            stmt = stmt.where(Node.type == node_type)
        if search:
            stmt = stmt.where(Node.label.ilike(f"%{search}%"))
            
        stmt = stmt.offset(offset).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_edges(
        self,
        source_node: Optional[UUID] = None,
        target_node: Optional[UUID] = None,
        relation: Optional[str] = None
    ) -> List[Edge]:
        """Query and filter edges from the database."""
        stmt = select(Edge)
        
        if source_node:
            stmt = stmt.where(Edge.source_node == source_node)
        if target_node:
            stmt = stmt.where(Edge.target_node == target_node)
        if relation:
            stmt = stmt.where(Edge.relation == relation)
            
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search_nodes_semantic(self, query: str, limit: int = 20) -> List[Node]:
        """Find matching nodes using pgvector cosine similarity."""
        query_vector = await self.ai_service.embed(query)
        stmt = (
            select(Node)
            .order_by(Node.embedding.cosine_distance(query_vector))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_subgraph(self, node_id: UUID, depth: int = 1) -> SubgraphResponse:
        """Runs iterative BFS to retrieve a subgraph up to depth limits (1-3)."""
        # Ensure depth is within acceptable range
        depth = max(1, min(depth, 3))
        
        visited_nodes: Set[UUID] = {node_id}
        collected_edges: List[Edge] = []
        current_layer: Set[UUID] = {node_id}

        for _ in range(depth):
            if not current_layer:
                break
                
            # Find all edges connecting to the current layer
            stmt = select(Edge).where(
                or_(
                    Edge.source_node.in_(list(current_layer)),
                    Edge.target_node.in_(list(current_layer))
                )
            )
            res = await self.db.execute(stmt)
            edges = res.scalars().all()
            
            next_layer = set()
            for edge in edges:
                # Add to collected edges if not already present
                if edge not in collected_edges:
                    collected_edges.append(edge)
                
                # Trace new nodes to traverse in next iteration
                if edge.source_node not in visited_nodes:
                    visited_nodes.add(edge.source_node)
                    next_layer.add(edge.source_node)
                if edge.target_node not in visited_nodes:
                    visited_nodes.add(edge.target_node)
                    next_layer.add(edge.target_node)
                    
            current_layer = next_layer

        # If no visited nodes, make sure the root node is loaded at least
        if not visited_nodes:
            visited_nodes.add(node_id)

        # Retrieve full details of all visited nodes
        nodes_stmt = select(Node).where(Node.id.in_(list(visited_nodes)))
        nodes_res = await self.db.execute(nodes_stmt)
        collected_nodes = list(nodes_res.scalars().all())

        return SubgraphResponse(nodes=collected_nodes, edges=collected_edges)

    async def create_node(self, node_in: NodeCreate) -> Node:
        """Manually create an entity node (embedding created dynamically)."""
        node_embedding = await self.ai_service.embed(node_in.label)
        node = Node(
            label=node_in.label,
            type=node_in.type.lower(),
            description=node_in.description,
            properties=node_in.properties,
            embedding=node_embedding,
            source_ids=[]
        )
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def get_stats(self) -> GraphStatsResponse:
        """Computes counts and breakdowns of knowledge graph entities."""
        # Total nodes
        node_count_query = await self.db.execute(select(func.count(Node.id)))
        total_nodes = node_count_query.scalar() or 0

        # Total edges
        edge_count_query = await self.db.execute(select(func.count(Edge.id)))
        total_edges = edge_count_query.scalar() or 0

        # Breakdown by type
        breakdown_stmt = select(Node.type, func.count(Node.id)).group_by(Node.type)
        breakdown_res = await self.db.execute(breakdown_stmt)
        type_breakdown = {t: c for t, c in breakdown_res.all()}

        return GraphStatsResponse(
            total_nodes=total_nodes,
            total_edges=total_edges,
            type_breakdown=type_breakdown
        )
