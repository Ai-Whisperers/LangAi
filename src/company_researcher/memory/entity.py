"""
Entity Memory - Knowledge graph-style entity storage.

Provides:
- Entity extraction and storage
- Relationship tracking
- Entity-based retrieval
- Graph traversal
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class EntityType(str, Enum):
    """Types of entities."""
    COMPANY = "company"
    PERSON = "person"
    PRODUCT = "product"
    LOCATION = "location"
    EVENT = "event"
    METRIC = "metric"
    DATE = "date"
    MONEY = "money"
    CONCEPT = "concept"
    CUSTOM = "custom"


class RelationType(str, Enum):
    """Types of relationships between entities."""
    # Organizational
    OWNS = "owns"
    SUBSIDIARY_OF = "subsidiary_of"
    COMPETES_WITH = "competes_with"
    PARTNERS_WITH = "partners_with"

    # People
    CEO_OF = "ceo_of"
    FOUNDED_BY = "founded_by"
    WORKS_AT = "works_at"
    REPORTS_TO = "reports_to"

    # Products/Services
    PRODUCES = "produces"
    SUPPLIES_TO = "supplies_to"
    USES = "uses"

    # Financial
    INVESTED_IN = "invested_in"
    ACQUIRED = "acquired"

    # Location
    HEADQUARTERED_IN = "headquartered_in"
    OPERATES_IN = "operates_in"

    # Temporal
    OCCURRED_ON = "occurred_on"
    ANNOUNCED_ON = "announced_on"

    # Generic
    RELATED_TO = "related_to"
    MENTIONS = "mentions"


@dataclass
class Entity:
    """A stored entity."""
    id: str
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    source: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "attributes": self.attributes,
            "aliases": self.aliases,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source": self.source,
            "confidence": self.confidence
        }

    def matches_name(self, query: str) -> bool:
        """Check if entity matches a name query."""
        query_lower = query.lower()
        if self.name.lower() == query_lower:
            return True
        for alias in self.aliases:
            if alias.lower() == query_lower:
                return True
        return False


@dataclass
class Relationship:
    """A relationship between two entities."""
    source_id: str
    target_id: str
    relation_type: RelationType
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source_doc: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "attributes": self.attributes,
            "confidence": self.confidence,
            "source_doc": self.source_doc,
            "created_at": self.created_at.isoformat()
        }


class EntityMemory:
    """
    Knowledge graph-style entity memory.

    Usage:
        memory = EntityMemory()

        # Add entities
        tesla = memory.add_entity("Tesla", EntityType.COMPANY)
        elon = memory.add_entity("Elon Musk", EntityType.PERSON)

        # Add relationship
        memory.add_relationship(tesla.id, elon.id, RelationType.CEO_OF)

        # Query
        ceos = memory.get_related(tesla.id, RelationType.CEO_OF)
        entities = memory.search("Tesla")

        # Get entity graph
        graph = memory.get_entity_graph(tesla.id, depth=2)
    """

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._relationships: List[Relationship] = []
        self._name_index: Dict[str, Set[str]] = {}  # name -> entity_ids

    def add_entity(
        self,
        name: str,
        entity_type: EntityType,
        attributes: Dict[str, Any] = None,
        aliases: List[str] = None,
        entity_id: str = None,
        **kwargs
    ) -> Entity:
        """
        Add or update an entity.

        Args:
            name: Entity name
            entity_type: Type of entity
            attributes: Entity attributes
            aliases: Alternative names
            entity_id: Custom ID (auto-generated if not provided)

        Returns:
            Created or updated Entity
        """
        import uuid

        # Check for existing entity by name
        existing = self.get_by_name(name, entity_type)
        if existing:
            # Update existing
            existing.attributes.update(attributes or {})
            existing.updated_at = _utcnow()
            if aliases:
                existing.aliases.extend([a for a in aliases if a not in existing.aliases])
            return existing

        # Create new entity
        eid = entity_id or str(uuid.uuid4())[:8]
        entity = Entity(
            id=eid,
            name=name,
            entity_type=entity_type,
            attributes=attributes or {},
            aliases=aliases or [],
            **kwargs
        )

        self._entities[eid] = entity
        self._index_entity(entity)

        return entity

    def _index_entity(self, entity: Entity) -> None:
        """Index entity for fast lookup."""
        names = [entity.name.lower()] + [a.lower() for a in entity.aliases]
        for name in names:
            if name not in self._name_index:
                self._name_index[name] = set()
            self._name_index[name].add(entity.id)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def get_by_name(
        self,
        name: str,
        entity_type: EntityType = None
    ) -> Optional[Entity]:
        """Get entity by name."""
        entity_ids = self._name_index.get(name.lower(), set())
        for eid in entity_ids:
            entity = self._entities.get(eid)
            if entity:
                if entity_type is None or entity.entity_type == entity_type:
                    return entity
        return None

    def search(
        self,
        query: str,
        entity_type: EntityType = None,
        limit: int = 10
    ) -> List[Entity]:
        """
        Search for entities.

        Args:
            query: Search query
            entity_type: Filter by type
            limit: Maximum results

        Returns:
            List of matching entities
        """
        results = []
        query_lower = query.lower()

        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue

            # Check name and aliases
            if entity.matches_name(query):
                results.append((entity, 1.0))  # Exact match
            elif query_lower in entity.name.lower():
                results.append((entity, 0.8))  # Partial match
            else:
                for alias in entity.aliases:
                    if query_lower in alias.lower():
                        results.append((entity, 0.6))
                        break

        # Sort by score and return
        results.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in results[:limit]]

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        attributes: Dict[str, Any] = None,
        bidirectional: bool = False,
        **kwargs
    ) -> Relationship:
        """
        Add a relationship between entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Type of relationship
            attributes: Relationship attributes
            bidirectional: Create reverse relationship too

        Returns:
            Created Relationship
        """
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            attributes=attributes or {},
            **kwargs
        )
        self._relationships.append(relationship)

        if bidirectional:
            reverse = Relationship(
                source_id=target_id,
                target_id=source_id,
                relation_type=relation_type,
                attributes=attributes or {},
                **kwargs
            )
            self._relationships.append(reverse)

        return relationship

    def get_relationships(
        self,
        entity_id: str,
        relation_type: RelationType = None,
        as_source: bool = True,
        as_target: bool = True
    ) -> List[Relationship]:
        """
        Get relationships for an entity.

        Args:
            entity_id: Entity ID
            relation_type: Filter by type
            as_source: Include where entity is source
            as_target: Include where entity is target

        Returns:
            List of relationships
        """
        results = []
        for rel in self._relationships:
            if relation_type and rel.relation_type != relation_type:
                continue
            if as_source and rel.source_id == entity_id:
                results.append(rel)
            elif as_target and rel.target_id == entity_id:
                results.append(rel)
        return results

    def get_related(
        self,
        entity_id: str,
        relation_type: RelationType = None,
        direction: str = "outgoing"  # outgoing, incoming, both
    ) -> List[Entity]:
        """
        Get entities related to a given entity.

        Args:
            entity_id: Entity ID
            relation_type: Filter by relationship type
            direction: Relationship direction

        Returns:
            List of related entities
        """
        related_ids = set()

        for rel in self._relationships:
            if relation_type and rel.relation_type != relation_type:
                continue

            if direction in ("outgoing", "both") and rel.source_id == entity_id:
                related_ids.add(rel.target_id)
            if direction in ("incoming", "both") and rel.target_id == entity_id:
                related_ids.add(rel.source_id)

        return [self._entities[eid] for eid in related_ids if eid in self._entities]

    def get_entity_graph(
        self,
        entity_id: str,
        depth: int = 2,
        relation_types: List[RelationType] = None
    ) -> Dict[str, Any]:
        """
        Get subgraph around an entity.

        Args:
            entity_id: Starting entity ID
            depth: How many hops to traverse
            relation_types: Types to include

        Returns:
            Graph with nodes and edges
        """
        nodes: Dict[str, Entity] = {}
        edges: List[Relationship] = []
        visited: Set[str] = set()
        queue: List[Tuple[str, int]] = [(entity_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited:
                continue
            visited.add(current_id)

            entity = self._entities.get(current_id)
            if entity:
                nodes[current_id] = entity

            if current_depth >= depth:
                continue

            # Get relationships
            for rel in self._relationships:
                if relation_types and rel.relation_type not in relation_types:
                    continue

                if rel.source_id == current_id:
                    edges.append(rel)
                    if rel.target_id not in visited:
                        queue.append((rel.target_id, current_depth + 1))
                elif rel.target_id == current_id:
                    edges.append(rel)
                    if rel.source_id not in visited:
                        queue.append((rel.source_id, current_depth + 1))

        return {
            "nodes": {nid: n.to_dict() for nid, n in nodes.items()},
            "edges": [e.to_dict() for e in edges],
            "root": entity_id
        }

    def get_all_entities(
        self,
        entity_type: EntityType = None
    ) -> List[Entity]:
        """Get all entities, optionally filtered by type."""
        if entity_type is None:
            return list(self._entities.values())
        return [e for e in self._entities.values() if e.entity_type == entity_type]

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships."""
        if entity_id not in self._entities:
            return False

        # Remove from index
        entity = self._entities[entity_id]
        for name in [entity.name.lower()] + [a.lower() for a in entity.aliases]:
            if name in self._name_index:
                self._name_index[name].discard(entity_id)

        # Remove relationships
        self._relationships = [
            r for r in self._relationships
            if r.source_id != entity_id and r.target_id != entity_id
        ]

        # Remove entity
        del self._entities[entity_id]
        return True

    def merge_entities(
        self,
        entity_id1: str,
        entity_id2: str
    ) -> Optional[Entity]:
        """Merge two entities into one."""
        e1 = self._entities.get(entity_id1)
        e2 = self._entities.get(entity_id2)

        if not e1 or not e2:
            return None

        # Merge attributes and aliases
        e1.attributes.update(e2.attributes)
        e1.aliases.extend([a for a in e2.aliases if a not in e1.aliases])
        if e2.name not in e1.aliases and e2.name != e1.name:
            e1.aliases.append(e2.name)
        e1.updated_at = _utcnow()

        # Update relationships
        for rel in self._relationships:
            if rel.source_id == entity_id2:
                rel.source_id = entity_id1
            if rel.target_id == entity_id2:
                rel.target_id = entity_id1

        # Delete merged entity
        self.delete_entity(entity_id2)
        self._index_entity(e1)

        return e1

    def to_dict(self) -> Dict[str, Any]:
        """Export memory as dictionary."""
        return {
            "entities": {eid: e.to_dict() for eid, e in self._entities.items()},
            "relationships": [r.to_dict() for r in self._relationships]
        }

    def clear(self) -> None:
        """Clear all entities and relationships."""
        self._entities.clear()
        self._relationships.clear()
        self._name_index.clear()


# Convenience functions


def create_entity_memory() -> EntityMemory:
    """Create an entity memory."""
    return EntityMemory()
