# forest_app/modules/task_engine.py
# =============================================================================
# Task Engine - Selects the next GRANULAR task(s) based on HTA, context, and patterns
# MODIFIED: Ensures priority and magnitude always have default float values.
#           Implements batch size limit (max 5) based on priority (desc)
#           and magnitude (desc) as a secondary sort key.
# =============================================================================

import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple, Set

# --- Feature Flag Import ---
try:
    from forest_app.core.feature_flags import Feature, is_enabled
except ImportError:
    # Fallback if flags cannot be imported - assume features are off
    def is_enabled(feature): return False
    class Feature:
        CORE_HTA = "FEATURE_ENABLE_CORE_HTA"
        PATTERN_ID = "FEATURE_ENABLE_PATTERN_ID"
        TASK_RESOURCE_FILTER = "FEATURE_ENABLE_TASK_RESOURCE_FILTER" # For resource checking

# --- Module Imports ---
# Assume HTANode has attributes like id, title, description, children, priority, magnitude, etc.
from forest_app.hta_tree.hta_tree import HTATree, HTANode # For type hinting and tree operations
from forest_app.modules.cognitive.pattern_id import PatternIdentificationEngine # For scoring

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_FALLBACK_TASK_MAGNITUDE = 3.0
DEFAULT_TASK_MAGNITUDE = 5.0 # Default if HTA node lacks magnitude
DEFAULT_TASK_PRIORITY = 0.5 # Default if HTA node lacks priority
MAX_FRONTIER_BATCH_SIZE = 5
# Scoring weights might be less critical now if we select based on depth, but kept for potential future use
BASE_PRIORITY_WEIGHT = 1.0
PATTERN_SCORE_WEIGHT = 0.5
CAPACITY_WEIGHT = 0.2
WITHERING_WEIGHT = -0.3

# --- Helper Functions ---
# [_calculate_node_score remains unchanged]
def _calculate_node_score(
    node: HTANode,
    snapshot: Dict[str, Any],
    pattern_score: float = 0.0,
) -> float:
    """Calculates a weighted score for an HTA node."""
    try:
        # Use the constant default priority here as well
        base_priority = float(getattr(node, 'priority', DEFAULT_TASK_PRIORITY))
    except (ValueError, TypeError):
        logger.warning(f"Could not convert priority '{getattr(node, 'priority', None)}' to float for node {getattr(node, 'id', 'N/A')}. Defaulting to {DEFAULT_TASK_PRIORITY}.")
        base_priority = DEFAULT_TASK_PRIORITY

    capacity = snapshot.get('capacity', 0.5)
    withering = snapshot.get('withering_level', 0.0)

    score = (
        (BASE_PRIORITY_WEIGHT * base_priority) +
        (PATTERN_SCORE_WEIGHT * pattern_score) +
        (CAPACITY_WEIGHT * capacity * base_priority) +
        (WITHERING_WEIGHT * withering * (1 - base_priority))
    )
    return max(0, score)

# Add at the top of the file
FALLBACK_TASK_COUNT = 0

def increment_fallback_count(reason: str = "unknown"):
    global FALLBACK_TASK_COUNT
    FALLBACK_TASK_COUNT += 1
    logger.warning(f"Fallback triggered in TaskEngine due to: {reason} | Fallback count: {FALLBACK_TASK_COUNT}")

class TaskEngine:
    """
    Selects the next set of granular, actionable task(s) based on HTA structure
    and status, potentially influenced by pattern matching and resource availability.
    Limits the output to a defined batch size based on priority (desc) and
    magnitude (desc). Ensures generated tasks always have valid priority/magnitude.
    """
    def __init__(
        self,
        pattern_engine: PatternIdentificationEngine,
        task_templates: Optional[Dict[str, Any]] = None,
    ):
        """
        Initializes the TaskEngine.

        Args:
            pattern_engine: An instance of PatternIdentificationEngine.
            task_templates: Optional dictionary containing task templates.
        """
        self.is_real_pattern_engine = isinstance(pattern_engine, PatternIdentificationEngine)
        if not self.is_real_pattern_engine:
             if type(pattern_engine).__name__ == 'DummyService':
                 logger.warning("TaskEngine received a dummy PatternIdentificationEngine. Pattern scoring will be skipped.")
             else:
                 logger.error(f"TaskEngine received an invalid type for pattern_engine: {type(pattern_engine).__name__}. Pattern scoring disabled.")
        self.pattern_engine = pattern_engine
        self.task_templates = task_templates if task_templates else self._load_default_templates()
        self.generated_task_ids = set()  # Track generated task IDs for current session
        self.session_id = str(uuid.uuid4())  # Add session tracking
        logger.debug(f"TaskEngine initialized with session {self.session_id}")

    # [_load_default_templates method remains unchanged]
    def _load_default_templates(self) -> Dict[str, Any]:
        """Loads default fallback task templates."""
        return {
            "default_reflection": {
                "id_prefix": "reflect",
                "tier": "Bud",
                "title": "Deep Reflection Session: Uncovering Insights",
                "description": "A guided session to explore your recent progress and current state.",
                "magnitude": DEFAULT_FALLBACK_TASK_MAGNITUDE,
                "metadata": {"fallback": True},
                "introspective_prompt": "What feels most alive or challenging in your journey right now?"
            }
        }

    # [_get_fallback_task method remains unchanged]
    def _get_fallback_task(self, template_key: str = "default_reflection") -> Dict[str, Any]:
        """Generates a fallback task using a template."""
        template = self.task_templates.get(template_key)
        if not template:
            increment_fallback_count("template_missing")
            return {
                "id": f"fallback_{uuid.uuid4().hex[:8]}",
                "tier": "Bud",
                "title": "Review Progress",
                "description": "Take a moment to review your current situation.",
                "magnitude": DEFAULT_FALLBACK_TASK_MAGNITUDE,
                "metadata": {"fallback": True, "error": "Template missing"},
                "hta_node_id": None,
            }
        task = template.copy()
        task["id"] = f"{template.get('id_prefix', 'task')}_{uuid.uuid4().hex[:8]}"
        task["created_at"] = datetime.now(timezone.utc).isoformat()
        task.pop("id_prefix", None)
        task["hta_node_id"] = None
        increment_fallback_count("normal_fallback")
        return task

    # [_check_dependencies method remains unchanged]
    def _check_dependencies(self, node: HTANode, tree: HTATree) -> bool:
        """
        Checks if all dependencies for a node are met.
        
        Args:
            node: The node to check dependencies for
            tree: The HTA tree containing all nodes
            
        Returns:
            bool: True if all dependencies are met, False otherwise
        """
        try:
            # Validate inputs
            if not isinstance(node, HTANode):
                logger.error(f"Invalid node type: {type(node)}")
                return False
                
            if not isinstance(tree, HTATree):
                logger.error(f"Invalid tree type: {type(tree)}")
                return False
                
            # Check if node has dependencies
            if not hasattr(node, 'depends_on') or not node.depends_on:
                return True
                
            # Get node map
            try:
                node_map = tree.get_node_map()
            except Exception as e:
                logger.error(f"Error getting node map: {e}")
                return False
                
            # Check each dependency
            for dep_id in node.depends_on:
                if not isinstance(dep_id, str):
                    logger.warning(f"Invalid dependency ID type: {type(dep_id)}")
                    continue
                    
                dep_node = node_map.get(dep_id)
                if not dep_node:
                    logger.warning(f"Dependency node ID '{dep_id}' not found in tree map for node '{getattr(node, 'id', 'N/A')}'. Assuming dependency not met.")
                    return False
                    
                dep_status = getattr(dep_node, 'status', 'pending')
                if not isinstance(dep_status, str):
                    logger.warning(f"Invalid dependency status type: {type(dep_status)}")
                    return False
                    
                if dep_status.lower() != "completed":
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False

    # [_check_resources method remains unchanged]
    def _check_resources(self, node: HTANode, snapshot: Dict[str, Any]) -> bool:
        """Checks resource requirements (if flag enabled)."""
        if not is_enabled(Feature.TASK_RESOURCE_FILTER):
            return True
        required_energy = getattr(node, 'estimated_energy', 'low').lower()
        capacity = snapshot.get('capacity', 0.5)
        energy_map = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
        passes_energy = capacity >= energy_map.get(required_energy, 0.0)
        if not passes_energy:
            logger.debug(f"-> Node {getattr(node, 'id', 'N/A')} rejected: Insufficient energy (requires {required_energy}, capacity {capacity:.2f}).")
            return False
        return True

    def _filter_candidate_nodes(self, flat_nodes: List[HTANode], tree: HTATree, snapshot: Dict[str, Any]) -> List[HTANode]:
        """Filters flattened HTA nodes to find viable candidates."""
        candidates = []
        logger.debug(f"Filtering {len(flat_nodes)} flattened nodes...")
        
        # Get node map for dependency checking
        node_map = tree.get_node_map()
        
        # Get current batch IDs from snapshot
        current_batch_ids = set(snapshot.get('current_frontier_batch_ids', []))
        
        for node in flat_nodes:
            if not isinstance(node, HTANode):
                continue
                
            node_id = getattr(node, 'id', 'N/A')
            status = getattr(node, 'status', 'pending')
            
            # Skip completed or non-pending nodes
            if status.lower() not in ['pending', 'suggested']:
                logger.debug(f"Node {node_id} skipped: status is {status}")
                continue
                
            # Skip nodes that are already in the current batch
            if node_id in current_batch_ids:
                logger.debug(f"Node {node_id} skipped: already in current batch")
                continue
                
            # Skip nodes with completed parents
            parent_id = getattr(node, 'parent_id', None)
            if parent_id:
                parent = node_map.get(parent_id)
                if parent and getattr(parent, 'status', 'pending').lower() == 'completed':
                    logger.debug(f"Node {node_id} skipped: parent {parent_id} is completed")
                    continue
                
            # Check dependencies
            if not self._check_dependencies(node, tree):
                logger.debug(f"Node {node_id} skipped: dependencies not met")
                continue
                
            # Check resources
            if not self._check_resources(node, snapshot):
                logger.debug(f"Node {node_id} skipped: insufficient resources")
                continue
                
            candidates.append(node)
            
        logger.info(f"Found {len(candidates)} candidate HTA nodes after filtering.")
        return candidates

    def _get_persisted_task_ids(self, snapshot: Dict[str, Any]) -> Set[str]:
        """Get persisted task IDs from snapshot."""
        try:
            # Get task IDs for current session only
            persisted_ids = snapshot.get('generated_task_ids', {})
            return set(persisted_ids.get(self.session_id, []))
        except Exception as e:
            logger.error(f"Error getting persisted task IDs: {e}")
            return set()

    def _update_persisted_task_ids(self, snapshot: Dict[str, Any], task_ids: Set[str]) -> None:
        """Update persisted task IDs in snapshot."""
        try:
            if not isinstance(snapshot, dict):
                logger.error("Invalid snapshot type for updating task IDs")
                return
                
            # Update task IDs for current session
            persisted_ids = snapshot.get('generated_task_ids', {})
            if not isinstance(persisted_ids, dict):
                persisted_ids = {}
            persisted_ids[self.session_id] = list(task_ids)
            snapshot['generated_task_ids'] = persisted_ids
            
        except Exception as e:
            logger.error(f"Error updating persisted task IDs: {e}")

    def _clear_persisted_task_ids(self, snapshot: Dict[str, Any]) -> None:
        """Clear persisted task IDs from snapshot."""
        try:
            if not isinstance(snapshot, dict):
                logger.error("Invalid snapshot type for clearing task IDs")
                return
                
            # Clear only current session's task IDs
            persisted_ids = snapshot.get('generated_task_ids', {})
            if isinstance(persisted_ids, dict):
                persisted_ids.pop(self.session_id, None)
                snapshot['generated_task_ids'] = persisted_ids
            else:
                snapshot['generated_task_ids'] = {}
                
            self.generated_task_ids.clear()
            logger.info(f"Cleared persisted task IDs for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error clearing persisted task IDs: {e}")

    def _validate_task_status(self, task: Dict[str, Any]) -> bool:
        """Validate task status and properties."""
        try:
            if not isinstance(task, dict):
                logger.error("Invalid task type")
                return False

            required_fields = ["id", "title", "description", "hta_node_id"]
            for field in required_fields:
                if field not in task:
                    logger.error(f"Task missing required field: {field}")
                    return False

            if "status" in task and task["status"] not in ["pending", "completed", "failed"]:
                logger.error(f"Invalid task status: {task['status']}")
                return False

            if "metadata" not in task:
                logger.error("Task missing metadata")
                return False

            if "priority_raw" not in task["metadata"]:
                logger.error("Task missing priority in metadata")
                return False

            if "magnitude" not in task:
                logger.error("Task missing magnitude")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating task: {e}")
            return False

    def get_next_step(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the next best step(s) based on the snapshot, prioritizing
        the most granular actionable HTA nodes (the "frontier") up to a
        defined batch size, sorted by priority (desc) then magnitude (desc).
        Enhanced for robust state management and reliable task generation.

        Args:
            snapshot: The current MemorySnapshot dictionary.

        Returns:
            A dictionary representing the next task bundle. Contains 'tasks' (a list
            of task dicts up to MAX_FRONTIER_BATCH_SIZE) if HTA tasks are found,
            otherwise contains a single 'fallback_task'.
        """
        tasks_list: List[Dict[str, Any]] = []
        fallback_task: Optional[Dict[str, Any]] = None

        # Load tree from snapshot
        tree = self._load_tree_from_snapshot(snapshot)
        if not tree:
            logger.warning("No valid tree found in snapshot")
            return {"tasks": [], "fallback_task": self._get_fallback_task("no_tree")}

        # Check if tree has evolved
        if snapshot.get('tree_evolved', False):
            logger.info("Tree has evolved, clearing task IDs")
            self._clear_persisted_task_ids(snapshot)
            snapshot['tree_evolved'] = False

        # Get all nodes
        try:
            flat_nodes = tree.flatten_tree()
            if not isinstance(flat_nodes, list):
                logger.error("Invalid flat_nodes type: expected list")
                return {"tasks": [], "fallback_task": self._get_fallback_task("invalid_nodes")}
        except Exception as e:
            logger.error(f"Error flattening tree: {e}")
            return {"tasks": [], "fallback_task": self._get_fallback_task("flatten_error")}

        # Get persisted task IDs and merge with current session
        persisted_ids = self._get_persisted_task_ids(snapshot)
        self.generated_task_ids.update(persisted_ids)

        # Filter candidate nodes
        candidate_nodes = self._filter_candidate_nodes(flat_nodes, tree, snapshot)
        if not candidate_nodes:
            logger.warning("No candidate nodes found after filtering.")
            return {"tasks": [], "fallback_task": self._get_fallback_task("no_candidates")}

        # Find frontier nodes (nodes at maximum depth)
        max_depth = -1
        nodes_with_depth = []
        
        for node in candidate_nodes:
            if not isinstance(node, HTANode):
                continue
            node_id = getattr(node, 'id', None)
            if node_id and hasattr(tree, 'get_node_depth'):
                try:
                    depth = tree.get_node_depth(node_id)
                    if depth >= 0:
                        nodes_with_depth.append((node, depth))
                        max_depth = max(max_depth, depth)
                except Exception as e:
                    logger.warning(f"Error getting depth for node {node_id}: {e}")
                    continue

        if max_depth >= 0:
            frontier_nodes_at_depth = [
                node for node, depth in nodes_with_depth 
                if depth == max_depth
            ]
            
            # Sort nodes by priority and magnitude
            def get_priority(node: HTANode) -> float:
                try:
                    return float(getattr(node, 'priority', DEFAULT_TASK_PRIORITY))
                except (ValueError, TypeError):
                    return DEFAULT_TASK_PRIORITY

            def get_magnitude(node: HTANode) -> float:
                try:
                    return float(getattr(node, 'magnitude', DEFAULT_TASK_MAGNITUDE))
                except (ValueError, TypeError):
                    return DEFAULT_TASK_MAGNITUDE

            frontier_nodes_sorted = sorted(
                frontier_nodes_at_depth,
                key=lambda node: (-get_priority(node), -get_magnitude(node))
            )

            # Limit to batch size and ensure no duplicates
            final_frontier_nodes = []
            for node in frontier_nodes_sorted:
                if len(final_frontier_nodes) >= MAX_FRONTIER_BATCH_SIZE:
                    break
                node_id = getattr(node, 'id', None)
                if node_id and node_id not in self.generated_task_ids:
                    final_frontier_nodes.append(node)
                    self.generated_task_ids.add(node_id)

            logger.info(f"Selected {len(final_frontier_nodes)} nodes (Max Batch: {MAX_FRONTIER_BATCH_SIZE})")

            # Convert nodes to tasks
            for node in final_frontier_nodes:
                if not isinstance(node, HTANode):
                    continue
                try:
                    task = self._create_task_from_hta_node(snapshot, node, tree)
                    if task and isinstance(task, dict) and self._validate_task_status(task):
                        tasks_list.append(task)
                    else:
                        logger.error(f"Invalid task generated from node {getattr(node, 'id', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error creating task from node {getattr(node, 'id', 'unknown')}: {e}")
                    continue

        else:
            logger.warning("Could not determine max depth or find nodes at max depth.")

        # Generate fallback task if no tasks found
        if not tasks_list:
            logger.warning("No HTA tasks generated. Generating fallback.")
            fallback_task = self._get_fallback_task()

        # Update persisted task IDs in snapshot
        self._update_persisted_task_ids(snapshot, self.generated_task_ids)

        # Prepare and return bundle
        task_bundle = {
            "tasks": tasks_list if tasks_list else [],
            "fallback_task": fallback_task,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Validate final bundle
        if not task_bundle["tasks"] and not task_bundle["fallback_task"]:
            logger.error("Generated empty task bundle")
            task_bundle["fallback_task"] = self._get_fallback_task("empty_bundle")
        
        return task_bundle

    # --- MODIFIED: _create_task_from_hta_node with robust magnitude ---
    def _create_task_from_hta_node(self, snapshot: Dict[str, Any], hta_node: HTANode, tree: Optional[HTATree]) -> Dict[str, Any]:
        """Creates a task dictionary from an HTA node."""
        try:
            if not isinstance(hta_node, HTANode):
                logger.error("Invalid node type")
                return self._get_fallback_task()

            # Get node properties with validation
            node_id = getattr(hta_node, 'id', None)
            if not node_id:
                logger.error("Node missing ID")
                return self._get_fallback_task()

            title = getattr(hta_node, 'title', '')
            if not title:
                logger.error(f"Node {node_id} missing title")
                return self._get_fallback_task()

            description = getattr(hta_node, 'description', '')
            if not description:
                logger.error(f"Node {node_id} missing description")
                return self._get_fallback_task()

            # Generate unique task ID
            task_id = f"task_{self.session_id}_{uuid.uuid4().hex[:8]}"
            
            # Get priority with validation
            try:
                priority = float(getattr(hta_node, 'priority', DEFAULT_TASK_PRIORITY))
                priority = max(0.0, min(1.0, priority))  # Clamp between 0 and 1
            except (ValueError, TypeError):
                logger.warning(f"Invalid priority for node {node_id}, using default")
                priority = DEFAULT_TASK_PRIORITY

            # Get magnitude with validation
            try:
                magnitude = float(getattr(hta_node, 'magnitude', DEFAULT_TASK_MAGNITUDE))
                magnitude = max(0.0, min(10.0, magnitude))  # Clamp between 0 and 10
            except (ValueError, TypeError):
                logger.warning(f"Invalid magnitude for node {node_id}, using default")
                magnitude = DEFAULT_TASK_MAGNITUDE

            # Get energy and time estimates
            estimated_energy = getattr(hta_node, 'estimated_energy', 'medium')
            if estimated_energy not in ['low', 'medium', 'high']:
                estimated_energy = 'medium'
                
            estimated_time = getattr(hta_node, 'estimated_time', 'medium')
            if estimated_time not in ['low', 'medium', 'high']:
                estimated_time = 'medium'

            # Create task dictionary
            task = {
                "id": task_id,
                "title": title,
                "description": description,
                "magnitude": magnitude,
                "hta_node_id": node_id,
                "estimated_energy": estimated_energy,
                "estimated_time": estimated_time,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "priority_raw": priority,
                    "hta_depth": self._get_node_depth(tree, hta_node) if tree else 0,
                    "session_id": self.session_id
                }
            }

            # Track the task ID
            self.generated_task_ids.add(task_id)
            
            return task

        except Exception as e:
            logger.exception(f"Error creating task from node: {e}")
            return self._get_fallback_task()

    def _get_node_depth(self, tree: Optional[HTATree], node: HTANode) -> int:
        """Calculate the depth of a node in the tree."""
        if not tree or not node:
            return 0
            
        # Check if depth was pre-calculated
        if hasattr(node, "depth"):
            return getattr(node, "depth", 0)
            
        # Calculate depth using tree method
        if hasattr(node, 'id') and hasattr(tree, 'get_node_depth'):
            try:
                node_id = getattr(node, 'id', None)
                if node_id:
                    depth_result = tree.get_node_depth(node_id)
                    return depth_result if depth_result >= 0 else 0
                else:
                    logger.warning("Cannot calculate depth: node is missing 'id'.")
            except Exception as depth_err:
                logger.error(f"Error calculating node depth for {getattr(node, 'id', 'N/A')}: {depth_err}")
        else:
            logger.debug(f"Could not calculate depth for node {getattr(node, 'id', 'N/A')}: Tree or method missing.")
            
        return 0

    def _load_tree_from_snapshot(self, snapshot: Dict[str, Any]) -> Optional[HTATree]:
        """Load and validate the HTA tree from the snapshot."""
        try:
            # Validate snapshot structure
            if not isinstance(snapshot, dict):
                logger.error("Invalid snapshot type: expected dict")
                return None

            # Get HTA tree data
            hta_data = snapshot.get("core_state", {}).get("hta_tree")
            if not hta_data or not isinstance(hta_data, dict) or "root" not in hta_data:
                logger.warning("No valid HTA tree found in snapshot core_state.")
                return None

            # Load and validate HTA tree
            try:
                hta_tree_obj = HTATree.from_dict(hta_data)
                if not hta_tree_obj or not hta_tree_obj.root:
                    logger.error("Failed to load HTA tree root from data.")
                    return None
                return hta_tree_obj
            except Exception as e:
                logger.error(f"Error loading HTA tree: {e}")
                return None

        except Exception as e:
            logger.exception(f"Error loading tree from snapshot: {e}")
            return None

