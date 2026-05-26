from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class NodeBase(BaseModel):
    label: str = Field(..., description="Label of the entity node, e.g. 'Tesla'")
    type: str = Field(..., description="Entity type: person, company, theme, concept, insight")
    description: Optional[str] = Field(None, description="Short summary description")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom key-value metadata")

class NodeCreate(NodeBase):
    pass

class NodeResponse(NodeBase):
    id: UUID = Field(..., description="Unique ID of the node")
    source_ids: List[UUID] = Field(default_factory=list, description="IDs of source documents contributing this node")
    created_at: datetime = Field(..., description="Timestamp when created")

    model_config = ConfigDict(from_attributes=True)


class EdgeBase(BaseModel):
    source_node: UUID = Field(..., description="UUID of source node")
    target_node: UUID = Field(..., description="UUID of target node")
    relation: str = Field(..., description="Relationship connection type (e.g. 'works_at', 'opposes')")
    weight: float = Field(1.0, description="Strength weight of relation")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom properties")

class EdgeCreate(EdgeBase):
    pass

class EdgeResponse(EdgeBase):
    id: UUID = Field(..., description="Unique ID of the edge")
    source_ids: List[UUID] = Field(default_factory=list, description="IDs of contributing documents")
    created_at: datetime = Field(..., description="Creation date")

    model_config = ConfigDict(from_attributes=True)


class SubgraphResponse(BaseModel):
    nodes: List[NodeResponse] = Field(..., description="List of nodes in the subgraph")
    edges: List[EdgeResponse] = Field(..., description="List of edges connecting the nodes")


class GraphStatsResponse(BaseModel):
    total_nodes: int = Field(..., description="Total nodes count")
    total_edges: int = Field(..., description="Total edges count")
    type_breakdown: Dict[str, int] = Field(..., description="Counts of nodes broken down by their type")
