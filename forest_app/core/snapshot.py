# forest_app/core/snapshot.py (MODIFIED FOR BATCH TRACKING)
import json
import logging
<<<<<<< HEAD
from datetime import datetime, timezone # Use timezone-aware
# --- Ensure necessary typing imports ---
from typing import Dict, List, Any, Optional
=======
from datetime import datetime, timezone  # Use timezone-aware
# --- Ensure necessary typing imports ---
from typing import Any, Dict, List, Optional
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# --- Import Feature enum and is_enabled ---
try:
    from .feature_flags import Feature, is_enabled
except ImportError:
<<<<<<< HEAD
    logging.warning("Feature flags module not found. Feature flag recording in snapshot will be disabled.")
    class Feature: pass
    def is_enabled(feature: Any) -> bool: return False
=======
    logging.warning(
        "Feature flags module not found. Feature flag recording in snapshot will be disabled."
    )

    class Feature:
        pass

    def is_enabled(feature: Any) -> bool:
        return False

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# --- ADDED: Import Field from Pydantic if needed ---
# If you transition this class to Pydantic, you'll use Field
# from pydantic import Field, BaseModel
# For now, we'll add attributes directly

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG) # Can uncomment for verbose debug

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class MemorySnapshot:
    """Serializable container for user journey state with semantic memory integration."""

    def __init__(self) -> None:
        # ---- Core progress & wellbeing gauges ----
        self.shadow_score: float = 0.50
        self.capacity: float = 0.50
        self.magnitude: float = 5.00
        self.resistance: float = 0.00
        self.relationship_index: float = 0.50

        # ---- Narrative scaffolding ----
        self.story_beats: List[Dict[str, Any]] = []
        self.totems: List[Dict[str, Any]] = []

        # ---- Desire & pairing caches ----
        self.wants_cache: Dict[str, float] = {}
        self.partner_profiles: Dict[str, Dict[str, Any]] = {}

        # ---- Engagement maintenance ----
        self.withering_level: float = 0.00

        # ---- Activation & core pathing ----
        self.activated_state: Dict[str, Any] = {
<<<<<<< HEAD
            "activated": False, "mode": None, "goal_set": False,
        }
        self.core_state: Dict[str, Any] = {} # Holds HTA Tree under 'hta_tree' key
=======
            "activated": False,
            "mode": None,
            "goal_set": False,
        }
        self.core_state: Dict[str, Any] = {}  # Holds HTA Tree under 'hta_tree' key
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.decor_state: Dict[str, Any] = {}

        # ---- Path & deadlines ----
        self.current_path: str = "structured"
        self.estimated_completion_date: Optional[str] = None

        # ---- Logs / context ----
        self.reflection_context: Dict[str, Any] = {
<<<<<<< HEAD
            "themes": [], "recent_insight": "", "current_priority": "",
=======
            "themes": [],
            "recent_insight": "",
            "current_priority": "",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }
        self.reflection_log: List[Dict[str, Any]] = []
        self.task_backlog: List[Dict[str, Any]] = []
        self.task_footprints: List[Dict[str, Any]] = []

        # ---- Conversation History ----
        self.conversation_history: List[Dict[str, str]] = []

        # --- Feature flag state ---
        self.feature_flags: Dict[str, bool] = {}

        # --- Batch Tracking ---
        self.current_frontier_batch_ids: List[str] = []
        # --- MODIFIED: Added field for accumulating reflections ---
        self.current_batch_reflections: List[str] = []
        # --- END MODIFIED ---

        # ---- Component state stubs ----
        # Stores serializable state from various engines/managers
        self.component_state: Dict[str, Any] = {
<<<<<<< HEAD
            "sentiment_engine_calibration": {}, "metrics_engine": {},
            "seed_manager": {}, "archetype_manager": {}, "dev_index": {},
            "memory_system": {}, "xp_mastery": {}, "pattern_engine_config": {},
            "emotional_integrity_index": {}, "desire_engine": {},
            "resistance_engine": {}, "reward_index": {},
            "last_issued_task_id": None, "last_activity_ts": None,
=======
            "sentiment_engine_calibration": {},
            "metrics_engine": {},
            "seed_manager": {},
            "archetype_manager": {},
            "dev_index": {},
            "memory_system": {},
            "xp_mastery": {},
            "pattern_engine_config": {},
            "emotional_integrity_index": {},
            "desire_engine": {},
            "resistance_engine": {},
            "reward_index": {},
            "last_issued_task_id": None,
            "last_activity_ts": None,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Removed direct engine instances from __init__ as they should be managed via DI
            # and their state loaded/saved via component_state
        }

        # ---- Semantic Memory ----
        self.semantic_memories: Dict[str, Any] = {
            "memories": [],  # List of memory objects with embeddings
            "stats": {
                "total_memories": 0,
                "memory_types": {},
                "avg_importance": 0.0,
<<<<<<< HEAD
                "avg_access_count": 0.0
            }
=======
                "avg_access_count": 0.0,
            },
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }

        # ---- Memory Context ----
        self.memory_context: Dict[str, Any] = {
            "recent_memories": [],  # Recently accessed memories
            "relevant_memories": [],  # Memories relevant to current context
            "memory_themes": [],  # Extracted themes from memories
            "last_memory_query": None,  # Last memory query and results
            "memory_stats": {
                "total_queries": 0,
                "avg_relevance_score": 0.0,
<<<<<<< HEAD
                "most_common_themes": []
            }
=======
                "most_common_themes": [],
            },
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }

        # ---- Misc meta ----
        self.template_metadata: Dict[str, Any] = {}
        self.last_ritual_mode: str = "Trail"
<<<<<<< HEAD
        self.timestamp: str = datetime.now(timezone.utc).isoformat() # Use timezone aware
=======
        self.timestamp: str = datetime.now(
            timezone.utc
        ).isoformat()  # Use timezone aware
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def record_feature_flags(self) -> None:
        """
        Updates the internal feature_flags dictionary with the current state
        of all defined features using the is_enabled function.
        This should be called *before* serializing the snapshot (calling to_dict).
        """
<<<<<<< HEAD
        self.feature_flags = {} # Clear previous state first
        if Feature is not None and hasattr(Feature, '__members__'):
            # Ensure Feature has members before iterating
            if hasattr(Feature, '__members__'):
                 for feature_name, feature_enum in Feature.__members__.items():
=======
        self.feature_flags = {}  # Clear previous state first
        if Feature is not None and hasattr(Feature, "__members__"):
            # Ensure Feature has members before iterating
            if hasattr(Feature, "__members__"):
                for feature_name, feature_enum in Feature.__members__.items():
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                    try:
                        self.feature_flags[feature_name] = is_enabled(feature_enum)
                    except Exception as e:
                        logger.error(f"Error checking feature flag {feature_name}: {e}")
<<<<<<< HEAD
                        self.feature_flags[feature_name] = False # Default to False on error
            else:
                 logger.warning("Feature enum has no members, cannot record flags.")
        else:
             logger.warning("Feature enum not available, cannot record feature flags.")
=======
                        self.feature_flags[feature_name] = (
                            False  # Default to False on error
                        )
            else:
                logger.warning("Feature enum has no members, cannot record flags.")
        else:
            logger.warning("Feature enum not available, cannot record feature flags.")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        logger.debug(f"Recorded feature flags: {self.feature_flags}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialise entire snapshot to a dict (JSON‑safe)."""
        # Ensure timestamp is current at serialization time
        self.timestamp = datetime.now(timezone.utc).isoformat()

        data = {
            # Core gauges
<<<<<<< HEAD
            "shadow_score": self.shadow_score, "capacity": self.capacity,
            "magnitude": self.magnitude, "resistance": self.resistance,
            "relationship_index": self.relationship_index,
            # Narrative
            "story_beats": self.story_beats, "totems": self.totems,
            # Desire / pairing
            "wants_cache": self.wants_cache, "partner_profiles": self.partner_profiles,
            # Engagement
            "withering_level": self.withering_level,
            # Activation / state
            "activated_state": self.activated_state, "core_state": self.core_state,
=======
            "shadow_score": self.shadow_score,
            "capacity": self.capacity,
            "magnitude": self.magnitude,
            "resistance": self.resistance,
            "relationship_index": self.relationship_index,
            # Narrative
            "story_beats": self.story_beats,
            "totems": self.totems,
            # Desire / pairing
            "wants_cache": self.wants_cache,
            "partner_profiles": self.partner_profiles,
            # Engagement
            "withering_level": self.withering_level,
            # Activation / state
            "activated_state": self.activated_state,
            "core_state": self.core_state,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            "decor_state": self.decor_state,
            # Path & deadlines
            "current_path": self.current_path,
            "estimated_completion_date": self.estimated_completion_date,
            # Logs
            "reflection_context": self.reflection_context,
            "reflection_log": self.reflection_log,
            "task_backlog": self.task_backlog,
            "task_footprints": self.task_footprints,
            # Conversation History
            "conversation_history": self.conversation_history,
            # Feature flags
            "feature_flags": self.feature_flags,
            # --- MODIFIED: Batch Tracking Serialization ---
            "current_frontier_batch_ids": self.current_frontier_batch_ids,
<<<<<<< HEAD
            "current_batch_reflections": self.current_batch_reflections, # <-- Added
=======
            "current_batch_reflections": self.current_batch_reflections,  # <-- Added
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # --- END MODIFIED ---
            # Component states
            "component_state": self.component_state,
            # Semantic Memory
            "semantic_memories": self.semantic_memories,
            "memory_context": self.memory_context,
            # Misc
            "template_metadata": self.template_metadata,
            "last_ritual_mode": self.last_ritual_mode,
            "timestamp": self.timestamp,
        }
<<<<<<< HEAD
        return data # Return the constructed dictionary
=======
        return data  # Return the constructed dictionary
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Rehydrate snapshot from dict, preserving unknown fields defensively."""
        if not isinstance(data, dict):
<<<<<<< HEAD
            logger.error("Invalid data passed to update_from_dict: expected dict, got %s", type(data))
=======
            logger.error(
                "Invalid data passed to update_from_dict: expected dict, got %s",
                type(data),
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            return

        # --- MODIFIED: Added batch lists to attributes list ---
        attributes_to_load = [
<<<<<<< HEAD
            "shadow_score", "capacity", "magnitude", "resistance",
            "relationship_index", # Removed hardware_config as it wasn't in __init__
            "activated_state", "core_state", "decor_state", "reflection_context",
            "reflection_log", "task_backlog", "task_footprints",
            "story_beats", "totems", "wants_cache", "partner_profiles",
            "withering_level", "current_path", "estimated_completion_date",
            "template_metadata", "last_ritual_mode", "timestamp",
            "conversation_history", "feature_flags",
            "current_frontier_batch_ids", # <-- Added
            "current_batch_reflections", # <-- Added
            "semantic_memories",
            "memory_context"
=======
            "shadow_score",
            "capacity",
            "magnitude",
            "resistance",
            "relationship_index",  # Removed hardware_config as it wasn't in __init__
            "activated_state",
            "core_state",
            "decor_state",
            "reflection_context",
            "reflection_log",
            "task_backlog",
            "task_footprints",
            "story_beats",
            "totems",
            "wants_cache",
            "partner_profiles",
            "withering_level",
            "current_path",
            "estimated_completion_date",
            "template_metadata",
            "last_ritual_mode",
            "timestamp",
            "conversation_history",
            "feature_flags",
            "current_frontier_batch_ids",  # <-- Added
            "current_batch_reflections",  # <-- Added
            "semantic_memories",
            "memory_context",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        ]
        # --- END MODIFIED ---

        for attr in attributes_to_load:
            if attr in data:
                value = data[attr]
                # Default expectation is list, adjust based on attr name
                expected_type = list
                default_value = []
<<<<<<< HEAD
                if attr in ["core_state", "feature_flags", "component_state", "activated_state", "decor_state", "reflection_context", "wants_cache", "partner_profiles", "template_metadata", "semantic_memories", "memory_context"]: # Removed hardware_config
                     expected_type = dict; default_value = {}
                elif attr in ["current_path", "estimated_completion_date", "last_ritual_mode", "timestamp"]:
                     expected_type = str; default_value = "" if attr != "current_path" else "structured"
                elif attr in ["shadow_score", "capacity", "magnitude", "resistance", "relationship_index", "withering_level"]:
                     expected_type = float; default_value = 0.0
                # --- MODIFIED: Explicit check for the new list ---
                elif attr in ["current_batch_reflections", "current_frontier_batch_ids"]:
                     expected_type = list; default_value = [] # Should be list of strings
=======
                if attr in [
                    "core_state",
                    "feature_flags",
                    "component_state",
                    "activated_state",
                    "decor_state",
                    "reflection_context",
                    "wants_cache",
                    "partner_profiles",
                    "template_metadata",
                    "semantic_memories",
                    "memory_context",
                ]:  # Removed hardware_config
                    expected_type = dict
                    default_value = {}
                elif attr in [
                    "current_path",
                    "estimated_completion_date",
                    "last_ritual_mode",
                    "timestamp",
                ]:
                    expected_type = str
                    default_value = "" if attr != "current_path" else "structured"
                elif attr in [
                    "shadow_score",
                    "capacity",
                    "magnitude",
                    "resistance",
                    "relationship_index",
                    "withering_level",
                ]:
                    expected_type = float
                    default_value = 0.0
                # --- MODIFIED: Explicit check for the new list ---
                elif attr in [
                    "current_batch_reflections",
                    "current_frontier_batch_ids",
                ]:
                    expected_type = list
                    default_value = []  # Should be list of strings
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # --- END MODIFIED ---

                if isinstance(value, expected_type):
                    setattr(self, attr, value)
                # Handle None for types that support it or reset to default
                elif value is None and expected_type in [str, list, dict]:
<<<<<<< HEAD
                     setattr(self, attr, None if expected_type is str else default_value)
                # --- ADDED: Handle potential int conversion for floats ---
                elif expected_type is float and isinstance(value, int):
                     logger.debug("Converting int value for '%s' to float.", attr)
                     setattr(self, attr, float(value))
                # --- END ADDED ---
                else:
                     logger.warning("Loaded '%s' has wrong type (%s, expected %s), resetting to default.", attr, type(value).__name__, expected_type.__name__)
                     setattr(self, attr, default_value)
            elif attr in [ # Ensure list/dict types default correctly if missing
                "conversation_history", "feature_flags", "core_state", "component_state",
                "task_backlog", "reflection_log", "task_footprints", "story_beats", "totems",
                "current_frontier_batch_ids", "current_batch_reflections", # <-- Added batch lists here
                "semantic_memories", "memory_context"
                ]:
                 # Use getattr with default to safely check/set default
                 if getattr(self, attr, None) is None:
                     default_value = [] if 'list' in str(self.__annotations__.get(attr,'')).lower() or 'List' in str(self.__annotations__.get(attr,'')) else {}
                     logger.debug("Attribute '%s' missing in loaded data, setting default.", attr)
                     setattr(self, attr, default_value)

        # Ensure type consistency *after* loading attempt
        # --- MODIFIED: Added checks for batch tracking list types ---
        if not isinstance(getattr(self, 'conversation_history', []), list): self.conversation_history = []
        if not isinstance(getattr(self, 'core_state', {}), dict): self.core_state = {}
        if not isinstance(getattr(self, 'feature_flags', {}), dict): self.feature_flags = {}
        if not isinstance(getattr(self, 'component_state', {}), dict): self.component_state = {}
        if not isinstance(getattr(self, 'current_frontier_batch_ids', []), list):
            logger.warning("Post-load current_frontier_batch_ids is not a list (%s), resetting.", type(getattr(self, 'current_frontier_batch_ids', None)))
            self.current_frontier_batch_ids = []
        if not isinstance(getattr(self, 'current_batch_reflections', []), list):
            logger.warning("Post-load current_batch_reflections is not a list (%s), resetting.", type(getattr(self, 'current_batch_reflections', None)))
=======
                    setattr(self, attr, None if expected_type is str else default_value)
                # --- ADDED: Handle potential int conversion for floats ---
                elif expected_type is float and isinstance(value, int):
                    logger.debug("Converting int value for '%s' to float.", attr)
                    setattr(self, attr, float(value))
                # --- END ADDED ---
                else:
                    logger.warning(
                        "Loaded '%s' has wrong type (%s, expected %s), resetting to default.",
                        attr,
                        type(value).__name__,
                        expected_type.__name__,
                    )
                    setattr(self, attr, default_value)
            elif attr in [  # Ensure list/dict types default correctly if missing
                "conversation_history",
                "feature_flags",
                "core_state",
                "component_state",
                "task_backlog",
                "reflection_log",
                "task_footprints",
                "story_beats",
                "totems",
                "current_frontier_batch_ids",
                "current_batch_reflections",  # <-- Added batch lists here
                "semantic_memories",
                "memory_context",
            ]:
                # Use getattr with default to safely check/set default
                if getattr(self, attr, None) is None:
                    default_value = (
                        []
                        if "list" in str(self.__annotations__.get(attr, "")).lower()
                        or "List" in str(self.__annotations__.get(attr, ""))
                        else {}
                    )
                    logger.debug(
                        "Attribute '%s' missing in loaded data, setting default.", attr
                    )
                    setattr(self, attr, default_value)

        # Ensure type consistency *after* loading attempt
        # --- MODIFIED: Added checks for batch tracking list types ---
        if not isinstance(getattr(self, "conversation_history", []), list):
            self.conversation_history = []
        if not isinstance(getattr(self, "core_state", {}), dict):
            self.core_state = {}
        if not isinstance(getattr(self, "feature_flags", {}), dict):
            self.feature_flags = {}
        if not isinstance(getattr(self, "component_state", {}), dict):
            self.component_state = {}
        if not isinstance(getattr(self, "current_frontier_batch_ids", []), list):
            logger.warning(
                "Post-load current_frontier_batch_ids is not a list (%s), resetting.",
                type(getattr(self, "current_frontier_batch_ids", None)),
            )
            self.current_frontier_batch_ids = []
        if not isinstance(getattr(self, "current_batch_reflections", []), list):
            logger.warning(
                "Post-load current_batch_reflections is not a list (%s), resetting.",
                type(getattr(self, "current_batch_reflections", None)),
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            self.current_batch_reflections = []
        # --- END MODIFIED ---

        # Component_state blob loading remains unchanged
        loaded_cs = data.get("component_state")
        if isinstance(loaded_cs, dict):
            self.component_state = loaded_cs
        elif loaded_cs is not None:
<<<<<<< HEAD
            logger.warning("Loaded component_state is not a dict (%s), ignoring.", type(loaded_cs))
            if not hasattr(self, 'component_state') or not isinstance(self.component_state, dict): self.component_state = {}
        else:
             if not hasattr(self, 'component_state') or not isinstance(self.component_state, dict): self.component_state = {}

        # Ensure type consistency for semantic memory fields
        if not isinstance(getattr(self, 'semantic_memories', {}), dict):
=======
            logger.warning(
                "Loaded component_state is not a dict (%s), ignoring.", type(loaded_cs)
            )
            if not hasattr(self, "component_state") or not isinstance(
                self.component_state, dict
            ):
                self.component_state = {}
        else:
            if not hasattr(self, "component_state") or not isinstance(
                self.component_state, dict
            ):
                self.component_state = {}

        # Ensure type consistency for semantic memory fields
        if not isinstance(getattr(self, "semantic_memories", {}), dict):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.warning("Post-load semantic_memories is not a dict, resetting.")
            self.semantic_memories = {
                "memories": [],
                "stats": {
                    "total_memories": 0,
                    "memory_types": {},
                    "avg_importance": 0.0,
<<<<<<< HEAD
                    "avg_access_count": 0.0
                }
            }

        if not isinstance(getattr(self, 'memory_context', {}), dict):
=======
                    "avg_access_count": 0.0,
                },
            }

        if not isinstance(getattr(self, "memory_context", {}), dict):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.warning("Post-load memory_context is not a dict, resetting.")
            self.memory_context = {
                "recent_memories": [],
                "relevant_memories": [],
                "memory_themes": [],
                "last_memory_query": None,
                "memory_stats": {
                    "total_queries": 0,
                    "avg_relevance_score": 0.0,
<<<<<<< HEAD
                    "most_common_themes": []
                }
=======
                    "most_common_themes": [],
                },
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemorySnapshot":
        """Creates a new MemorySnapshot instance from dictionary data."""
        # [Logging remains largely unchanged, ensure sensitive data isn't logged excessively]
        snap = cls()
        if isinstance(data, dict):
            snap.update_from_dict(data)
            # Log state *after* update_from_dict has run
<<<<<<< HEAD
            logger.debug("FROM_DICT: Value of instance.core_state['hta_tree'] AFTER update: %s",
                         snap.core_state.get('hta_tree', 'MISSING_POST_ASSIGNMENT'))
            logger.debug("FROM_DICT: Loaded feature flags AFTER update: %s", snap.feature_flags)
            # --- ADDED: Log batch state ---
            logger.debug("FROM_DICT: Loaded batch IDs AFTER update: %s", snap.current_frontier_batch_ids)
            logger.debug("FROM_DICT: Loaded batch reflections count AFTER update: %s", len(snap.current_batch_reflections))
            # --- END ADDED ---
        else:
            logger.error("Invalid data passed to MemorySnapshot.from_dict: expected dict, got %s. Returning default snapshot.", type(data))
=======
            logger.debug(
                "FROM_DICT: Value of instance.core_state['hta_tree'] AFTER update: %s",
                snap.core_state.get("hta_tree", "MISSING_POST_ASSIGNMENT"),
            )
            logger.debug(
                "FROM_DICT: Loaded feature flags AFTER update: %s", snap.feature_flags
            )
            # --- ADDED: Log batch state ---
            logger.debug(
                "FROM_DICT: Loaded batch IDs AFTER update: %s",
                snap.current_frontier_batch_ids,
            )
            logger.debug(
                "FROM_DICT: Loaded batch reflections count AFTER update: %s",
                len(snap.current_batch_reflections),
            )
            # --- END ADDED ---
        else:
            logger.error(
                "Invalid data passed to MemorySnapshot.from_dict: expected dict, got %s. Returning default snapshot.",
                type(data),
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        return snap

    def __str__(self) -> str:
        """Provides a string representation, robust against serialization errors."""
        try:
            # Use a limited set of keys for basic string representation
            repr_dict = {
<<<<<<< HEAD
                "shadow_score": round(getattr(self, 'shadow_score', 0.0), 2),
                "capacity": round(getattr(self, 'capacity', 0.0), 2),
                "magnitude": round(getattr(self, 'magnitude', 0.0), 1),
                "feature_flags_count": len(getattr(self, 'feature_flags', {})),
                "batch_ids_count": len(getattr(self, 'current_frontier_batch_ids', [])), # <-- Modified
                "batch_refl_count": len(getattr(self, 'current_batch_reflections', [])), # <-- Added
                "semantic_memories_count": len(self.semantic_memories.get("memories", [])),
                "memory_themes": len(self.memory_context.get("memory_themes", [])),
                "timestamp": getattr(self, 'timestamp', 'N/A')
=======
                "shadow_score": round(getattr(self, "shadow_score", 0.0), 2),
                "capacity": round(getattr(self, "capacity", 0.0), 2),
                "magnitude": round(getattr(self, "magnitude", 0.0), 1),
                "feature_flags_count": len(getattr(self, "feature_flags", {})),
                "batch_ids_count": len(
                    getattr(self, "current_frontier_batch_ids", [])
                ),  # <-- Modified
                "batch_refl_count": len(
                    getattr(self, "current_batch_reflections", [])
                ),  # <-- Added
                "semantic_memories_count": len(
                    self.semantic_memories.get("memories", [])
                ),
                "memory_themes": len(self.memory_context.get("memory_themes", [])),
                "timestamp": getattr(self, "timestamp", "N/A"),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            }
            return f"<Snapshot {json.dumps(repr_dict, default=str)} ...>"
        except Exception as exc:
            logger.error("Snapshot __str__ error: %s", exc)
<<<<<<< HEAD
            return f"<Snapshot ts={getattr(self, 'timestamp', 'N/A')} (error rendering)>"

    def update_memory_context(self, 
                            recent_memories: Optional[List[Dict[str, Any]]] = None,
                            relevant_memories: Optional[List[Dict[str, Any]]] = None,
                            memory_themes: Optional[List[str]] = None,
                            query_info: Optional[Dict[str, Any]] = None) -> None:
=======
            return (
                f"<Snapshot ts={getattr(self, 'timestamp', 'N/A')} (error rendering)>"
            )

    def update_memory_context(
        self,
        recent_memories: Optional[List[Dict[str, Any]]] = None,
        relevant_memories: Optional[List[Dict[str, Any]]] = None,
        memory_themes: Optional[List[str]] = None,
        query_info: Optional[Dict[str, Any]] = None,
    ) -> None:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """Update memory context with new information."""
        if recent_memories is not None:
            self.memory_context["recent_memories"] = recent_memories

        if relevant_memories is not None:
            self.memory_context["relevant_memories"] = relevant_memories

        if memory_themes is not None:
            self.memory_context["memory_themes"] = memory_themes

        if query_info is not None:
            self.memory_context["last_memory_query"] = query_info
<<<<<<< HEAD
            
            # Update stats
            stats = self.memory_context["memory_stats"]
            stats["total_queries"] += 1
            
=======

            # Update stats
            stats = self.memory_context["memory_stats"]
            stats["total_queries"] += 1

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Update average relevance score
            if "relevance_score" in query_info:
                current_avg = stats["avg_relevance_score"]
                stats["avg_relevance_score"] = (
<<<<<<< HEAD
                    (current_avg * (stats["total_queries"] - 1) + query_info["relevance_score"]) 
                    / stats["total_queries"]
                )
=======
                    current_avg * (stats["total_queries"] - 1)
                    + query_info["relevance_score"]
                ) / stats["total_queries"]
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

            # Update theme statistics
            if "themes" in query_info:
                current_themes = set(stats["most_common_themes"])
                new_themes = set(query_info["themes"])
                combined_themes = list(current_themes.union(new_themes))
                stats["most_common_themes"] = combined_themes[:10]  # Keep top 10 themes

<<<<<<< HEAD
    def update_semantic_memories(self, 
                               new_memories: Optional[List[Dict[str, Any]]] = None,
                               stats_update: Optional[Dict[str, Any]] = None) -> None:
=======
    def update_semantic_memories(
        self,
        new_memories: Optional[List[Dict[str, Any]]] = None,
        stats_update: Optional[Dict[str, Any]] = None,
    ) -> None:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """Update semantic memories and stats."""
        if new_memories is not None:
            self.semantic_memories["memories"].extend(new_memories)

        if stats_update is not None:
            self.semantic_memories["stats"].update(stats_update)

<<<<<<< HEAD
    def get_relevant_memories(self, 
                            context: str,
                            limit: int = 5,
                            memory_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
=======
    def get_relevant_memories(
        self, context: str, limit: int = 5, memory_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """
        Get memories relevant to the given context.
        This is a helper method that returns memories from the current context,
        filtered by type if specified.
        """
        memories = self.memory_context["relevant_memories"]
<<<<<<< HEAD
        
        if memory_types:
            memories = [
                m for m in memories 
                if m.get("type") in memory_types
            ]

        # Sort by relevance if available
        memories.sort(
            key=lambda x: x.get("relevance", 0.0),
            reverse=True
        )
=======

        if memory_types:
            memories = [m for m in memories if m.get("type") in memory_types]

        # Sort by relevance if available
        memories.sort(key=lambda x: x.get("relevance", 0.0), reverse=True)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        return memories[:limit]
