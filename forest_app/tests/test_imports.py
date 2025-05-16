"""
Import verification test module.
"""

import logging
<<<<<<< HEAD
import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import tempfile
import os
import uuid
import pytest
from forest_app.core.services.component_state_manager import ComponentStateManager
from forest_app.core.services.memory_manager import MemoryEntry
# LegacySemanticMemoryManager may not exist; if not, mock it for the test
try:
    from forest_app.core.services.memory_manager import LegacySemanticMemoryManager
except ImportError:
=======
import os
import tempfile
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from forest_app.core.services.component_state_manager import \
    ComponentStateManager
from forest_app.core.services.memory_manager import MemoryEntry

# LegacySemanticMemoryManager may not exist; if not, mock it for the test
try:
    from forest_app.core.services.memory_manager import \
        LegacySemanticMemoryManager
except ImportError:

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    class LegacySemanticMemoryManager:
        def __init__(self, storage_path=None):
            pass

<<<<<<< HEAD
# --- Fix for ModernSemanticMemoryManager import or skip ---
try:
    from forest_app.core.services.memory_manager import ModernSemanticMemoryManager
=======

# --- Fix for ModernSemanticMemoryManager import or skip ---
try:
    from forest_app.core.services.memory_manager import \
        ModernSemanticMemoryManager
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
except ImportError:
    ModernSemanticMemoryManager = None

# Configure logging
logging.basicConfig(
<<<<<<< HEAD
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestImports(unittest.TestCase):
    """Test case for verifying imports."""
    
    def test_core_imports(self):
        """Test importing core components."""
        try:
            from forest_app.core import (
                ReflectionProcessor,
                CompletionProcessor,
                HTAService,
                ComponentStateManager,
                SemanticMemoryManager,
                MemorySnapshot,
                clamp01,
                SilentScoring,
                HarmonicRouting
            )
=======
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestImports(unittest.TestCase):
    """Test case for verifying imports."""

    def test_core_imports(self):
        """Test importing core components."""
        try:
            # Only import what is actually used in the test body
            from forest_app.core import ComponentStateManager

            # Remove unused imports: CompletionProcessor, HarmonicRouting, HTAService, MemorySnapshot, ReflectionProcessor, SemanticMemoryManager, SilentScoring, clamp01

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.info("✓ Core package imports successful")
        except ImportError as e:
            logger.error(f"✗ Core package import failed: {e}")
            raise
<<<<<<< HEAD
            
    def test_direct_package_imports(self):
        """Test importing from specific packages."""
        try:
            from forest_app.core.processors import ReflectionProcessor
            from forest_app.core.services import HTAService
=======

    def test_direct_package_imports(self):
        """Test importing from specific packages."""
        try:
            # Only import what is actually used in the test body
            from forest_app.core.processors import ReflectionProcessor
            from forest_app.core.services import HTAService

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.info("✓ Direct package imports successful")
        except ImportError as e:
            logger.error(f"✗ Direct package import failed: {e}")
            raise
<<<<<<< HEAD
            
    def test_module_imports(self):
        """Test importing modules."""
        try:
            from forest_app.modules.seed import SeedManager
            from forest_app.modules.logging_tracking import TaskFootprintLogger
            from forest_app.modules.task_engine import TaskEngine
=======

    def test_module_imports(self):
        """Test importing modules."""
        try:
            # Only import what is actually used in the test body
            from forest_app.modules.logging_tracking import TaskFootprintLogger
            from forest_app.modules.seed import SeedManager
            from forest_app.modules.task_engine import TaskEngine

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.info("✓ Module imports successful")
        except ImportError as e:
            logger.error(f"✗ Module import failed: {e}")
            raise
<<<<<<< HEAD
            
    def test_integration_imports(self):
        """Test importing integrations."""
        try:
            from forest_app.integrations.llm import LLMClient
=======

    def test_integration_imports(self):
        """Test importing integrations."""
        try:
            # Only import what is actually used in the test body
            from forest_app.integrations.llm import LLMClient

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.info("✓ Integration imports successful")
        except ImportError as e:
            logger.error(f"✗ Integration import failed: {e}")
            raise
<<<<<<< HEAD
            
    def test_container_imports(self):
        """Test importing containers."""
        try:
            from forest_app.containers import Container
=======

    def test_container_imports(self):
        """Test importing containers."""
        try:
            # Only import what is actually used in the test body
            from forest_app.containers import Container

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            logger.info("✓ Container imports successful")
        except ImportError as e:
            logger.error(f"✗ Container import failed: {e}")
            raise

    def test_component_state_manager_import(self):
        # Smoke test for import and instantiation
        mgr = ComponentStateManager({})
        self.assertTrue(isinstance(mgr, ComponentStateManager))

    def test_memory_entry_smoke(self):
        from datetime import datetime
<<<<<<< HEAD
        entry = MemoryEntry('test', 'content', datetime.now())
        d = entry.to_dict()
        self.assertEqual(d['memory_type'], 'test')
=======

        entry = MemoryEntry("test", "content", datetime.now())
        d = entry.to_dict()
        self.assertEqual(d["memory_type"], "test")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def test_legacy_semantic_memory_manager_smoke(self):
        mgr = LegacySemanticMemoryManager(storage_path=None)
        self.assertTrue(isinstance(mgr, LegacySemanticMemoryManager))

    def test_modern_semantic_memory_manager_smoke(self):
        if ModernSemanticMemoryManager is None:
            self.skipTest("ModernSemanticMemoryManager not available in this codebase.")
<<<<<<< HEAD
        class DummyLLM:
            async def get_embedding(self, content):
                return [0.0, 1.0, 2.0]
            async def extract_themes(self, content):
                return ['theme1', 'theme2']
        mgr = ModernSemanticMemoryManager(DummyLLM())
        self.assertTrue(isinstance(mgr, ModernSemanticMemoryManager))

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        from forest_app.core.services.memory_manager import SemanticMemoryManager, MemoryEntry
        import tempfile
=======

        class DummyLLM:
            async def get_embedding(self, content):
                return [0.0, 1.0, 2.0]

            async def extract_themes(self, content):
                return ["theme1", "theme2"]

        mgr = ModernSemanticMemoryManager(DummyLLM())
        self.assertTrue(isinstance(mgr, ModernSemanticMemoryManager))


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        from forest_app.core.services.memory_manager import (
            MemoryEntry, SemanticMemoryManager)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.tempfile = tempfile.NamedTemporaryFile(delete=False)
        # Write valid empty JSON list to the temp file
        self.tempfile.write(b"[]")
        self.tempfile.flush()
        self.manager = SemanticMemoryManager(storage_path=self.tempfile.name)
        self.MemoryEntry = MemoryEntry

    def tearDown(self):
        self.tempfile.close()
        os.unlink(self.tempfile.name)

    def test_memory_entry_to_dict_and_from_dict(self):
        from datetime import datetime
<<<<<<< HEAD
        entry = self.MemoryEntry('type', 'content', datetime.now(), {'foo': 'bar'})
=======

        entry = self.MemoryEntry("type", "content", datetime.now(), {"foo": "bar"})
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        d = entry.to_dict()
        entry2 = self.MemoryEntry.from_dict(d)
        self.assertEqual(entry.memory_type, entry2.memory_type)
        self.assertEqual(entry.content, entry2.content)
        self.assertEqual(entry.metadata, entry2.metadata)

    def test_memory_entry_invalid(self):
        from datetime import datetime
<<<<<<< HEAD
        with self.assertRaises(ValueError):
            self.MemoryEntry('', 'content', datetime.now())
        with self.assertRaises(TypeError):
            self.MemoryEntry('type', 'content', 'notadate')
        with self.assertRaises(TypeError):
            self.MemoryEntry.from_dict('notadict')
        with self.assertRaises(ValueError):
            self.MemoryEntry.from_dict({'memory_type': 'a', 'content': 'b'})

    def test_store_milestone_and_reflection(self):
        node_id = uuid.uuid4()
        self.manager.store_milestone(node_id, 'desc', 0.5)
        self.manager.store_reflection('type', 'something', emotion='happy')
=======

        with self.assertRaises(ValueError):
            self.MemoryEntry("", "content", datetime.now())
        with self.assertRaises(TypeError):
            self.MemoryEntry("type", "content", "notadate")
        with self.assertRaises(TypeError):
            self.MemoryEntry.from_dict("notadict")
        with self.assertRaises(ValueError):
            self.MemoryEntry.from_dict({"memory_type": "a", "content": "b"})

    def test_store_milestone_and_reflection(self):
        node_id = uuid.uuid4()
        self.manager.store_milestone(node_id, "desc", 0.5)
        self.manager.store_reflection("type", "something", emotion="happy")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertTrue(len(self.manager.memories) >= 2)

    def test_store_milestone_invalid(self):
        with self.assertRaises(TypeError):
<<<<<<< HEAD
            self.manager.store_milestone('notauuid', 'desc', 0.5)
        with self.assertRaises(ValueError):
            self.manager.store_milestone(uuid.uuid4(), '', 0.5)
        with self.assertRaises(TypeError):
            self.manager.store_milestone(uuid.uuid4(), 'desc', 'notafloat')
        with self.assertRaises(ValueError):
            self.manager.store_milestone(uuid.uuid4(), 'desc', -1)

    def test_store_reflection_invalid(self):
        with self.assertRaises(ValueError):
            self.manager.store_reflection('', 'content')
        with self.assertRaises(ValueError):
            self.manager.store_reflection('type', '')
        with self.assertRaises(TypeError):
            self.manager.store_reflection('type', 'content', emotion=123)

    def test_get_relevant_memories(self):
        self.manager.store_milestone(uuid.uuid4(), 'desc about foo', 0.9)
        self.manager.store_reflection('type', 'foo bar baz', emotion='happy')
        results = self.manager.get_relevant_memories('foo', limit=2)
=======
            self.manager.store_milestone("notauuid", "desc", 0.5)
        with self.assertRaises(ValueError):
            self.manager.store_milestone(uuid.uuid4(), "", 0.5)
        with self.assertRaises(TypeError):
            self.manager.store_milestone(uuid.uuid4(), "desc", "notafloat")
        with self.assertRaises(ValueError):
            self.manager.store_milestone(uuid.uuid4(), "desc", -1)

    def test_store_reflection_invalid(self):
        with self.assertRaises(ValueError):
            self.manager.store_reflection("", "content")
        with self.assertRaises(ValueError):
            self.manager.store_reflection("type", "")
        with self.assertRaises(TypeError):
            self.manager.store_reflection("type", "content", emotion=123)

    def test_get_relevant_memories(self):
        self.manager.store_milestone(uuid.uuid4(), "desc about foo", 0.9)
        self.manager.store_reflection("type", "foo bar baz", emotion="happy")
        results = self.manager.get_relevant_memories("foo", limit=2)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertTrue(isinstance(results, list))
        self.assertTrue(len(results) > 0)
        with self.assertRaises(TypeError):
            self.manager.get_relevant_memories(123)
        with self.assertRaises(ValueError):
<<<<<<< HEAD
            self.manager.get_relevant_memories('foo', limit=0)

    def test_update_context(self):
        self.manager.update_context({'a': 1})
        self.assertEqual(self.manager.current_context['a'], 1)
        with self.assertRaises(TypeError):
            self.manager.update_context('notadict')

    def test_save_and_load_memories(self):
        self.manager.store_milestone(uuid.uuid4(), 'desc', 0.5)
        self.manager._save_memories()
        from forest_app.core.services.memory_manager import SemanticMemoryManager
        mgr2 = SemanticMemoryManager(storage_path=self.tempfile.name)
        self.assertTrue(len(mgr2.memories) > 0)

class DummyHTANode:
    def __init__(self, node_id, title, priority=0.5, metadata=None, completion_status=0.0):
=======
            self.manager.get_relevant_memories("foo", limit=0)

    def test_update_context(self):
        self.manager.update_context({"a": 1})
        self.assertEqual(self.manager.current_context["a"], 1)
        with self.assertRaises(TypeError):
            self.manager.update_context("notadict")

    def test_save_and_load_memories(self):
        self.manager.store_milestone(uuid.uuid4(), "desc", 0.5)
        self.manager._save_memories()
        from forest_app.core.services.memory_manager import \
            SemanticMemoryManager

        mgr2 = SemanticMemoryManager(storage_path=self.tempfile.name)
        self.assertTrue(len(mgr2.memories) > 0)


class DummyHTANode:
    def __init__(
        self, node_id, title, priority=0.5, metadata=None, completion_status=0.0
    ):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.node_id = node_id
        self.title = title
        self.metadata = metadata or {}
        self.completion_status = completion_status
<<<<<<< HEAD
        self.metadata['priority'] = priority
        self.metadata.setdefault('dependencies', [])
=======
        self.metadata["priority"] = priority
        self.metadata.setdefault("dependencies", [])

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

class DummyHTATree:
    def __init__(self, nodes):
        self.nodes = {n.node_id: n for n in nodes}
<<<<<<< HEAD
    def get_all_frontier_tasks(self):
        return list(self.nodes.values())
    def update_node(self, node_id, data):
        if node_id in self.nodes:
            self.nodes[node_id].completion_status = data.get('completion_status', 0.0)
    def get_node(self, node_id):
        return self.nodes.get(node_id)

=======

    def get_all_frontier_tasks(self):
        return list(self.nodes.values())

    def update_node(self, node_id, data):
        if node_id in self.nodes:
            self.nodes[node_id].completion_status = data.get("completion_status", 0.0)

    def get_node(self, node_id):
        return self.nodes.get(node_id)


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class DummyMemoryManager:
    def __init__(self):
        self.context = None
        self.milestones = []
<<<<<<< HEAD
    def update_context(self, context):
        self.context = context
    def get_relevant_memories(self, context):
        return [{'content': 'foo'}]
    def store_milestone(self, task_id, desc, impact):
        self.milestones.append((task_id, desc, impact))

class TestTaskEngine(unittest.TestCase):
    def setUp(self):
        from forest_app.core.services.task_engine import TaskEngine
        self.TaskEngine = TaskEngine
        self.tree = DummyHTATree([
            DummyHTANode('1', 'Task 1', priority=0.8),
            DummyHTANode('2', 'Task 2', priority=0.2, completion_status=1.0)
        ])
=======

    def update_context(self, context):
        self.context = context

    def get_relevant_memories(self, context):
        return [{"content": "foo"}]

    def store_milestone(self, task_id, desc, impact):
        self.milestones.append((task_id, desc, impact))


class TestTaskEngine(unittest.TestCase):
    def setUp(self):
        from forest_app.core.services.task_engine import TaskEngine

        self.TaskEngine = TaskEngine
        self.tree = DummyHTATree(
            [
                DummyHTANode("1", "Task 1", priority=0.8),
                DummyHTANode("2", "Task 2", priority=0.2, completion_status=1.0),
            ]
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.memory_manager = DummyMemoryManager()
        self.engine = TaskEngine(self.tree, self.memory_manager)

    def test_generate_task_batch(self):
<<<<<<< HEAD
        batch = self.engine.generate_task_batch({'foo': 'bar'})
=======
        batch = self.engine.generate_task_batch({"foo": "bar"})
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertTrue(isinstance(batch, list))
        self.assertTrue(len(batch) > 0)

    def test_recommend_next_tasks(self):
        tasks = self.engine.recommend_next_tasks(count=1)
        self.assertTrue(isinstance(tasks, list))
        self.assertEqual(len(tasks), 1)

    def test_update_task_status(self):
        import uuid
<<<<<<< HEAD
        node_id = uuid.uuid4()
        # Add a node to the tree
        node = DummyHTANode(node_id, 'Task 3', priority=0.5)
=======

        node_id = uuid.uuid4()
        # Add a node to the tree
        node = DummyHTANode(node_id, "Task 3", priority=0.5)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.tree.nodes[node_id] = node
        self.engine.update_task_status(node_id, 1.0)
        self.assertEqual(self.tree.nodes[node_id].completion_status, 1.0)
        self.assertTrue(self.memory_manager.milestones)

    def test_update_task_status_invalid(self):
        import uuid
<<<<<<< HEAD
        with self.assertRaises(TypeError):
            self.engine.update_task_status('notauuid', 1.0)
        with self.assertRaises(TypeError):
            self.engine.update_task_status(uuid.uuid4(), 'notafloat')
=======

        with self.assertRaises(TypeError):
            self.engine.update_task_status("notauuid", 1.0)
        with self.assertRaises(TypeError):
            self.engine.update_task_status(uuid.uuid4(), "notafloat")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        with self.assertRaises(ValueError):
            self.engine.update_task_status(uuid.uuid4(), -1)
        with self.assertRaises(ValueError):
            self.engine.update_task_status(uuid.uuid4(), 2)

    def test_generate_task_batch_invalid(self):
        with self.assertRaises(TypeError):
<<<<<<< HEAD
            self.engine.generate_task_batch('notadict')
=======
            self.engine.generate_task_batch("notadict")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def test_recommend_next_tasks_invalid(self):
        with self.assertRaises(ValueError):
            self.engine.recommend_next_tasks(count=0)

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class DummyEngine:
    def __init__(self):
        self.state = {}
        self.updated = False
        self.saved = False
<<<<<<< HEAD
    def update_from_dict(self, d):
        self.state = d
        self.updated = True
    def to_dict(self):
        self.saved = True
        return {'foo': 'bar'}

class DummyNoUpdate:
    def to_dict(self):
        return {'foo': 'bar'}
=======

    def update_from_dict(self, d):
        self.state = d
        self.updated = True

    def to_dict(self):
        self.saved = True
        return {"foo": "bar"}


class DummyNoUpdate:
    def to_dict(self):
        return {"foo": "bar"}

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

class DummyNoSave:
    def update_from_dict(self, d):
        self.state = d
        self.updated = True

<<<<<<< HEAD
class DummyService:
    pass

class TestComponentStateManager(unittest.TestCase):
    def test_load_states_valid(self):
        from forest_app.core.services.component_state_manager import ComponentStateManager
        from types import SimpleNamespace
        engine = DummyEngine()
        mgr = ComponentStateManager({'engine': engine})
        snapshot = SimpleNamespace(component_state={'engine': {'foo': 1}})
        mgr.load_states(snapshot)
        self.assertTrue(engine.updated)
        self.assertEqual(engine.state['foo'], 1)

    def test_load_states_invalid(self):
        from forest_app.core.services.component_state_manager import ComponentStateManager
        from types import SimpleNamespace
        engine = DummyNoUpdate()
        mgr = ComponentStateManager({'engine': engine})
        snapshot = SimpleNamespace(component_state={'engine': {'foo': 1}})
        mgr.load_states(snapshot)  # Should not raise
        # DummyService should be skipped
        mgr = ComponentStateManager({'dummy': DummyService()})
        snapshot = SimpleNamespace(component_state={'dummy': {'foo': 1}})
        mgr.load_states(snapshot)

    def test_save_states_valid(self):
        from forest_app.core.services.component_state_manager import ComponentStateManager
        from types import SimpleNamespace
        engine = DummyEngine()
        mgr = ComponentStateManager({'engine': engine})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)
        self.assertTrue(engine.saved)
        self.assertIn('engine', snapshot.component_state)
        self.assertIn('last_activity_ts', snapshot.component_state)

    def test_save_states_invalid(self):
        from forest_app.core.services.component_state_manager import ComponentStateManager
        from types import SimpleNamespace
        engine = DummyNoSave()
        mgr = ComponentStateManager({'engine': engine})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)  # Should not raise
        # DummyService should be skipped
        mgr = ComponentStateManager({'dummy': DummyService()})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)

class DummyLLMClient:
    async def get_embedding(self, content):
        return [1.0, 0.0, 0.0]
    async def extract_themes(self, content):
        return ['theme1', 'theme2']

class TestSemanticMemoryManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from forest_app.core.services.semantic_memory import SemanticMemoryManager
        self.manager = SemanticMemoryManager(DummyLLMClient())

    async def test_store_memory_and_query(self):
        mem = await self.manager.store_memory('task_completion', 'did something', {'foo': 'bar'}, 0.8)
        self.assertIn('content', mem)
        # Add a second memory
        await self.manager.store_memory('reflection', 'thoughts', {'bar': 'baz'}, 0.5)
        # Query
        results = await self.manager.query_memories('did', k=1)
=======

class DummyService:
    pass


class TestComponentStateManager(unittest.TestCase):
    def test_load_states_valid(self):
        from types import SimpleNamespace

        from forest_app.core.services.component_state_manager import \
            ComponentStateManager

        engine = DummyEngine()
        mgr = ComponentStateManager({"engine": engine})
        snapshot = SimpleNamespace(component_state={"engine": {"foo": 1}})
        mgr.load_states(snapshot)
        self.assertTrue(engine.updated)
        self.assertEqual(engine.state["foo"], 1)

    def test_load_states_invalid(self):
        from types import SimpleNamespace

        from forest_app.core.services.component_state_manager import \
            ComponentStateManager

        engine = DummyNoUpdate()
        mgr = ComponentStateManager({"engine": engine})
        snapshot = SimpleNamespace(component_state={"engine": {"foo": 1}})
        mgr.load_states(snapshot)  # Should not raise
        # DummyService should be skipped
        mgr = ComponentStateManager({"dummy": DummyService()})
        snapshot = SimpleNamespace(component_state={"dummy": {"foo": 1}})
        mgr.load_states(snapshot)

    def test_save_states_valid(self):
        from types import SimpleNamespace

        from forest_app.core.services.component_state_manager import \
            ComponentStateManager

        engine = DummyEngine()
        mgr = ComponentStateManager({"engine": engine})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)
        self.assertTrue(engine.saved)
        self.assertIn("engine", snapshot.component_state)
        self.assertIn("last_activity_ts", snapshot.component_state)

    def test_save_states_invalid(self):
        from types import SimpleNamespace

        from forest_app.core.services.component_state_manager import \
            ComponentStateManager

        engine = DummyNoSave()
        mgr = ComponentStateManager({"engine": engine})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)  # Should not raise
        # DummyService should be skipped
        mgr = ComponentStateManager({"dummy": DummyService()})
        snapshot = SimpleNamespace(component_state={})
        mgr.save_states(snapshot)


class DummyLLMClient:
    async def get_embedding(self, content):
        return [1.0, 0.0, 0.0]

    async def extract_themes(self, content):
        return ["theme1", "theme2"]


class TestSemanticMemoryManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from forest_app.core.services.semantic_memory import \
            SemanticMemoryManager

        self.manager = SemanticMemoryManager(DummyLLMClient())

    async def test_store_memory_and_query(self):
        mem = await self.manager.store_memory(
            "task_completion", "did something", {"foo": "bar"}, 0.8
        )
        self.assertIn("content", mem)
        # Add a second memory
        await self.manager.store_memory("reflection", "thoughts", {"bar": "baz"}, 0.5)
        # Query
        results = await self.manager.query_memories("did", k=1)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertTrue(isinstance(results, list))
        self.assertGreaterEqual(len(results), 1)

    async def test_query_memories_filters(self):
<<<<<<< HEAD
        await self.manager.store_memory('task_completion', 'foo', {}, 0.5)
        await self.manager.store_memory('reflection', 'bar', {}, 0.5)
        # Filter by event_types
        results = await self.manager.query_memories('foo', k=2, event_types=['task_completion'])
        self.assertTrue(all(m['event_type'] == 'task_completion' for m in results))

    async def test_get_recent_memories(self):
        await self.manager.store_memory('task_completion', 'foo', {}, 0.5)
        await self.manager.store_memory('reflection', 'bar', {}, 0.5)
=======
        await self.manager.store_memory("task_completion", "foo", {}, 0.5)
        await self.manager.store_memory("reflection", "bar", {}, 0.5)
        # Filter by event_types
        results = await self.manager.query_memories(
            "foo", k=2, event_types=["task_completion"]
        )
        self.assertTrue(all(m["event_type"] == "task_completion" for m in results))

    async def test_get_recent_memories(self):
        await self.manager.store_memory("task_completion", "foo", {}, 0.5)
        await self.manager.store_memory("reflection", "bar", {}, 0.5)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        recents = await self.manager.get_recent_memories(limit=1)
        self.assertEqual(len(recents), 1)

    async def test_extract_themes(self):
<<<<<<< HEAD
        await self.manager.store_memory('task_completion', 'foo', {}, 0.5)
        await self.manager.store_memory('reflection', 'bar', {}, 0.5)
        memories = await self.manager.get_recent_memories(limit=2)
        themes = await self.manager.extract_themes(memories)
        self.assertIn('theme1', themes)

    async def test_update_memory_stats(self):
        mem = await self.manager.store_memory('task_completion', 'foo', {'id': 'mem1'}, 0.5)
        mem['id'] = 'mem1'
        self.manager.memories[-1]['id'] = 'mem1'
        updated = await self.manager.update_memory_stats('mem1', 2)
        self.assertTrue(updated)
        notfound = await self.manager.update_memory_stats('notfound', 1)
        self.assertFalse(notfound)

    def test_cosine_similarity(self):
        from forest_app.core.services.semantic_memory import SemanticMemoryManager
        sim = self.manager._cosine_similarity([1,0,0], [1,0,0])
        self.assertAlmostEqual(sim, 1.0)
        sim2 = self.manager._cosine_similarity([1,0,0], [0,1,0])
        self.assertAlmostEqual(sim2, 0.0)

    async def test_get_memory_stats_and_to_dict(self):
        await self.manager.store_memory('task_completion', 'foo', {}, 0.5)
        stats = await self.manager.get_memory_stats()
        self.assertIn('total_memories', stats)
        d = self.manager.to_dict()
        self.assertIn('memories', d)

    async def test_from_dict(self):
        await self.manager.store_memory('task_completion', 'foo', {}, 0.5)
=======
        await self.manager.store_memory("task_completion", "foo", {}, 0.5)
        await self.manager.store_memory("reflection", "bar", {}, 0.5)
        memories = await self.manager.get_recent_memories(limit=2)
        themes = await self.manager.extract_themes(memories)
        self.assertIn("theme1", themes)

    async def test_update_memory_stats(self):
        mem = await self.manager.store_memory(
            "task_completion", "foo", {"id": "mem1"}, 0.5
        )
        mem["id"] = "mem1"
        self.manager.memories[-1]["id"] = "mem1"
        updated = await self.manager.update_memory_stats("mem1", 2)
        self.assertTrue(updated)
        notfound = await self.manager.update_memory_stats("notfound", 1)
        self.assertFalse(notfound)

    def test_cosine_similarity(self):
        sim = self.manager._cosine_similarity([1, 0, 0], [1, 0, 0])
        self.assertAlmostEqual(sim, 1.0)
        sim2 = self.manager._cosine_similarity([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(sim2, 0.0)

    async def test_get_memory_stats_and_to_dict(self):
        await self.manager.store_memory("task_completion", "foo", {}, 0.5)
        stats = await self.manager.get_memory_stats()
        self.assertIn("total_memories", stats)
        d = self.manager.to_dict()
        self.assertIn("memories", d)

    async def test_from_dict(self):
        await self.manager.store_memory("task_completion", "foo", {}, 0.5)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        d = self.manager.to_dict()
        await self.manager.from_dict(d)
        self.assertTrue(isinstance(self.manager.memories, list))

<<<<<<< HEAD
class TestHTAService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from forest_app.core.services.hta_service import HTAService
=======

class TestHTAService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from forest_app.core.services.hta_service import HTAService

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.llm_client = MagicMock()
        self.semantic_memory_manager = MagicMock()
        self.service = HTAService(self.llm_client, self.semantic_memory_manager)

    async def test_initialize_and_get_task_hierarchy(self):
<<<<<<< HEAD
        await self.service.initialize_task_hierarchy('task1', {'foo': 'bar'})
        h = await self.service.get_task_hierarchy('task1')
        self.assertEqual(h['foo'], 'bar')

    async def test_update_task_state(self):
        await self.service.initialize_task_hierarchy('task2', {'foo': 'bar'})
        await self.service.update_task_state('task2', {'baz': 1})
        h = await self.service.get_task_hierarchy('task2')
        self.assertEqual(h['baz'], 1)

    async def test_update_task_state_missing(self):
        # Should not raise
        await self.service.update_task_state('notfound', {'baz': 1})

    async def test_get_task_hierarchy_missing(self):
        h = await self.service.get_task_hierarchy('notfound')
=======
        await self.service.initialize_task_hierarchy("task1", {"foo": "bar"})
        h = await self.service.get_task_hierarchy("task1")
        self.assertEqual(h["foo"], "bar")

    async def test_update_task_state(self):
        await self.service.initialize_task_hierarchy("task2", {"foo": "bar"})
        await self.service.update_task_state("task2", {"baz": 1})
        h = await self.service.get_task_hierarchy("task2")
        self.assertEqual(h["baz"], 1)

    async def test_update_task_state_missing(self):
        # Should not raise
        await self.service.update_task_state("notfound", {"baz": 1})

    async def test_get_task_hierarchy_missing(self):
        h = await self.service.get_task_hierarchy("notfound")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertIsNone(h)

    async def test_load_tree_and_save_tree(self):
        # Mock snapshot and dependencies
        snapshot = MagicMock()
<<<<<<< HEAD
        snapshot.component_state = {'seed_manager': {'active_seed_id': 'seed1'}}
        self.semantic_memory_manager.get_seed_by_id = AsyncMock(return_value=MagicMock(hta_tree={'root': {'id': 'root1', 'title': 'Root'}}))
        from forest_app.modules.hta_tree import HTATree
        HTATree.from_dict = MagicMock(return_value=MagicMock(root=MagicMock(id='root1', title='Root')))
        tree = await self.service.load_tree(snapshot)
        self.assertTrue(tree.root.id == 'root1')
        # Save tree
        tree.to_dict = MagicMock(return_value={'root': {'id': 'root1'}})
=======
        snapshot.component_state = {"seed_manager": {"active_seed_id": "seed1"}}
        self.semantic_memory_manager.get_seed_by_id = AsyncMock(
            return_value=MagicMock(hta_tree={"root": {"id": "root1", "title": "Root"}})
        )
        from forest_app.modules.hta_tree import HTATree

        HTATree.from_dict = MagicMock(
            return_value=MagicMock(root=MagicMock(id="root1", title="Root"))
        )
        tree = await self.service.load_tree(snapshot)
        self.assertTrue(tree.root.id == "root1")
        # Save tree
        tree.to_dict = MagicMock(return_value={"root": {"id": "root1"}})
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        snapshot.core_state = {}
        ok = await self.service.save_tree(snapshot, tree)
        self.assertTrue(ok)

<<<<<<< HEAD
class TestContextInfusedGenerator(unittest.TestCase):
    def setUp(self):
        from forest_app.core.context_infused_generator import ContextInfusedGenerator
=======

class TestContextInfusedGenerator(unittest.TestCase):
    def setUp(self):
        from forest_app.core.context_infused_generator import \
            ContextInfusedGenerator

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.generator = ContextInfusedGenerator()

    def test_generate_context_block(self):
        # Should handle minimal input
<<<<<<< HEAD
        result = self.generator.generate_context_block('goal', 'summary', ['task1', 'task2'])
        self.assertIn('goal', result)
        self.assertIn('summary', result)
        self.assertIn('task1', result)

    def test_generate_context_block_empty(self):
        # Should handle empty lists
        result = self.generator.generate_context_block('', '', [])
=======
        result = self.generator.generate_context_block(
            "goal", "summary", ["task1", "task2"]
        )
        self.assertIn("goal", result)
        self.assertIn("summary", result)
        self.assertIn("task1", result)

    def test_generate_context_block_empty(self):
        # Should handle empty lists
        result = self.generator.generate_context_block("", "", [])
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertIsInstance(result, str)

    def test_generate_context_block_error(self):
        # Should not raise on bad input
        try:
            self.generator.generate_context_block(None, None, None)
        except Exception as e:
            self.fail(f"Should not raise: {e}")

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- Additional tests for modules with 0% coverage ---
class TestHTAModelsModule(unittest.TestCase):
    def setUp(self):
        from forest_app.core.models import HTANode, HTATree
<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.HTANode = HTANode
        self.HTATree = HTATree
        self.node_id = uuid.uuid4()
        self.child_id = uuid.uuid4()
<<<<<<< HEAD
        self.root = HTANode('Root', 'Root node')
        self.child = HTANode('Child', 'Child node', parent_id=self.root.node_id, node_id=self.child_id)
=======
        self.root = HTANode("Root", "Root node")
        self.child = HTANode(
            "Child", "Child node", parent_id=self.root.node_id, node_id=self.child_id
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.root.add_child(self.child)
        self.tree = HTATree(self.root)

    def test_node_completion_status(self):
        self.assertEqual(self.root.completion_status, 0.0)
        self.child.completion_status = 1.0
        self.root.update_completion()
        self.assertTrue(0.0 <= self.root.completion_status <= 1.0)
        with self.assertRaises(ValueError):
            self.child.completion_status = 2.0
        with self.assertRaises(ValueError):
            self.child.completion_status = -1.0

    def test_add_and_remove_child(self):
<<<<<<< HEAD
        new_child = self.HTANode('New', 'New node')
=======
        new_child = self.HTANode("New", "New node")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.root.add_child(new_child)
        self.assertIn(new_child, self.root.children)
        self.root.remove_child(new_child.node_id)
        self.assertNotIn(new_child, self.root.children)
        with self.assertRaises(ValueError):
            self.root.remove_child(uuid.uuid4())
        with self.assertRaises(TypeError):
<<<<<<< HEAD
            self.root.add_child('notanode')
        with self.assertRaises(ValueError):
            self.root.add_child(self.root)
        dup = self.HTANode('Dup', 'Dup node', node_id=self.child_id)
=======
            self.root.add_child("notanode")
        with self.assertRaises(ValueError):
            self.root.add_child(self.root)
        dup = self.HTANode("Dup", "Dup node", node_id=self.child_id)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        with self.assertRaises(ValueError):
            self.root.add_child(dup)

    def test_get_frontier_tasks(self):
        tasks = self.root.get_frontier_tasks()
        self.assertTrue(isinstance(tasks, list))
        self.assertTrue(self.child in tasks)

    def test_tree_get_node_and_update(self):
        node = self.tree.get_node(self.child.node_id)
        self.assertEqual(node, self.child)
        with self.assertRaises(TypeError):
<<<<<<< HEAD
            self.tree.get_node('notauuid')
        with self.assertRaises(TypeError):
            self.tree.update_node(self.child.node_id, 'notadict')
        with self.assertRaises(ValueError):
            self.tree.update_node(uuid.uuid4(), {'title': 'x'})
        with self.assertRaises(ValueError):
            self.tree.update_node(self.child.node_id, {'notanattr': 1})
        self.tree.update_node(self.child.node_id, {'completion_status': 1.0})
=======
            self.tree.get_node("notauuid")
        with self.assertRaises(TypeError):
            self.tree.update_node(self.child.node_id, "notadict")
        with self.assertRaises(ValueError):
            self.tree.update_node(uuid.uuid4(), {"title": "x"})
        with self.assertRaises(ValueError):
            self.tree.update_node(self.child.node_id, {"notanattr": 1})
        self.tree.update_node(self.child.node_id, {"completion_status": 1.0})
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertEqual(self.child.completion_status, 1.0)

    def test_propagate_completion(self):
        self.child.completion_status = 1.0
        self.tree.propagate_completion(self.child.node_id)
        with self.assertRaises(TypeError):
<<<<<<< HEAD
            self.tree.propagate_completion('notauuid')
=======
            self.tree.propagate_completion("notauuid")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        with self.assertRaises(ValueError):
            self.tree.propagate_completion(uuid.uuid4())
        # Circular reference
        self.child.parent_id = self.child.node_id
        with self.assertRaises(ValueError):
            self.tree.propagate_completion(self.child.node_id)
        self.child.parent_id = self.root.node_id  # restore

    def test_get_all_frontier_tasks(self):
        tasks = self.tree.get_all_frontier_tasks()
        self.assertTrue(isinstance(tasks, list))

<<<<<<< HEAD
class TestOnboardingServiceModule(unittest.TestCase):
    def setUp(self):
        from forest_app.core.onboarding_service import OnboardingService
=======

class TestOnboardingServiceModule(unittest.TestCase):
    def setUp(self):
        from forest_app.core.onboarding_service import OnboardingService

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        mock_llm = MagicMock()
        self.service = OnboardingService(mock_llm)

    def test_get_predefined_questions(self):
        questions = self.service.get_predefined_questions()
        self.assertIsInstance(questions, list)

    def test_process_qa_responses(self):
<<<<<<< HEAD
        result = self.service.process_qa_responses('goal', 'context', {'foo': 'bar'})
        self.assertIn('user_goal', result)
        self.assertIn('q_and_a_responses', result)

    @pytest.mark.asyncio
    async def test_get_dynamic_questions(self):
        questions = await self.service.get_dynamic_questions('goal', 'context')
=======
        result = self.service.process_qa_responses("goal", "context", {"foo": "bar"})
        self.assertIn("user_goal", result)
        self.assertIn("q_and_a_responses", result)

    @pytest.mark.asyncio
    async def test_get_dynamic_questions(self):
        questions = await self.service.get_dynamic_questions("goal", "context")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        self.assertEqual(questions, [])

    @pytest.mark.asyncio
    async def test_create_manifest_from_onboarding(self):
        from uuid import uuid4
<<<<<<< HEAD
        result = await self.service.create_manifest_from_onboarding('goal', 'context', uuid4())
        self.assertTrue(hasattr(result, 'tree_id'))
        self.assertTrue(hasattr(result, 'user_goal'))

if __name__ == '__main__':
    unittest.main() 
=======

        result = await self.service.create_manifest_from_onboarding(
            "goal", "context", uuid4()
        )
        self.assertTrue(hasattr(result, "tree_id"))
        self.assertTrue(hasattr(result, "user_goal"))


if __name__ == "__main__":
    unittest.main()
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
