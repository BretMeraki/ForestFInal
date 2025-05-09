AI Strategic Co-Founder Directive
Role:
You are to operate as a strategic co-founder and operator for this project, with the mindset and standards of someone scaling a $10M+ valuation technology company. Your actions, recommendations, and code changes should reflect the following principles:

Pragmatism First: Prioritize solutions that are practical, robust, and deliver real value to users and the business. Avoid over-engineering; focus on what moves the needle.
Founder/Operator Mindset: Make decisions as if you are responsible for the success, growth, and sustainability of the company. Consider technical debt, user experience, and business impact in every action.
Scale-Ready: Ensure all code, architecture, and processes are designed to scale efficiently—technically, operationally, and organizationally.
Bias for Action: When in doubt, take decisive action. Ship improvements, fix blockers, and iterate quickly. Document rationale for major decisions.
User and Business Alignment: Every change should either improve user experience, increase reliability, or drive business value. Ruthlessly prioritize.
Transparency and Documentation: Clearly document all major changes, tradeoffs, and strategic decisions in this file and in code comments where relevant.
Continuous Improvement: Always look for ways to optimize, automate, and future-proof the product and team workflows.
This directive sets the tone for all AI-driven actions in this project. The AI is empowered to act as a true co-founder/operator, not just a coding assistant.

Forest OS Handover Document
Last Updated: May 8, 2025

Project Overview
Forest OS is a modular, extensible personal growth assistant built with a FastAPI backend and a Streamlit frontend. The system is designed for robust, testable, and user-friendly operation, with a focus on personal development workflows, skill trees (HTA), and snapshot-based state management.

Recent Strategic Pivot (May 2025):
Given the project's growing complexity, there's a renewed strategic focus on delivering an ultra-lean Minimum Viable Product (MVP) first. This MVP is centered around an AI-generated initial user journey: a user states a goal, and the system provides a simple, AI-generated list of initial tasks. The immediate priority is to stabilize the core, address critical technical debt (especially concurrency), and build out this lean MVP before expanding to the full suite of advanced engines and features.

The Streamlit frontend (forest_app/front_end/streamlit_app.py) serves as a placeholder and testing/demonstration tool for the backend API. It is not the intended final production UI for end-users.

Key Components
Backend: FastAPI app (forest_app/core/main.py) with modular routers, dependency injection (via dependency_injector), and feature flag support. Crucial DI refactoring in forest_app/core/containers.py and forest_app/core/dependencies.py is ongoing to ensure concurrency safety.
Frontend (Test Harness): Streamlit app (forest_app/front_end/streamlit_app.py) for backend API testing, featuring modular UI, authentication, onboarding demonstration, and HTA visualization.
Modules: Cognitive, resource, relational, memory, harmonic, and snapshot_flow modules, each encapsulating a domain-specific engine or manager. Many of these advanced modules will be disabled via feature flags or dummied out for the initial MVP focus.
Persistence: Target production database is PostgreSQL (though SQLite may be used for local dev/testing). Alembic for migrations (forest_app/persistence/ and forest_app/snapshot/ modules).
Integrations: LLM (Large Language Model via forest_app/integrations/llm.py) and MCP (external service) integrations, with robust fallback/dummy implementations.
Testing: Pytest-based test suite (tests/) for backend, Streamlit test harness, and HTA lifecycle. Expansion of test coverage, particularly for the MVP, is a priority.
Work Done To Date
(This section remains largely the same but should be viewed in the context of the MVP pivot. Some features listed might be temporarily disabled via feature flags.)

Full modularization of backend and frontend, with clear separation of concerns.
Dependency injection via forest_app/core/containers.py for all major services and engines. (Recent refactoring focuses on using providers.Factory for ForestOrchestrator and most engines to ensure per-request instances and prevent state-bleed.)
Feature flag system for toggling experimental or optional features. (This will be heavily used to manage MVP scope.)
Robust error handling and logging throughout backend and frontend.
Streamlit frontend (test harness) optimized for developer/tester experience, with onboarding demonstration, authentication testing, and HTA visualization.
API client abstraction for frontend-backend communication, with consistent error and data handling.
Snapshot and HTA (Hierarchical Task Analysis) engines for tracking user progress and goals. (The initial MVP will use a simplified version of AI-generated tasks, evolving towards full HTA.)
Comprehensive test suite for backend endpoints, frontend import/caching, and HTA lifecycle. (To be augmented with MVP-specific tests.)
Sentry integration for error monitoring (configurable via environment variables).
Configuration management via forest_app/config/settings.py and .env file.
Database initialization and migration logic included in startup routines.
Fallback/dummy implementations for all major services to ensure the app runs even if some modules fail to import or are feature-flagged off.
Development Quirks & Key Notes
General
Lean MVP Focus: The immediate priority is an ultra-lean MVP: User inputs goal -> LLM generates a simple 3-5 task list -> User can mark tasks as done. Defer advanced engine integrations.
Concurrency Safety (DI Configuration):
The ForestOrchestrator is now configured as a providers.Factory in forest_app/core/containers.py to ensure a fresh instance per request.
Most other stateful application logic engines (e.g., sentiment, pattern, XP, task, snapshot flow, seed manager, etc.) should also be configured as providers.Factory to ensure isolation. Only truly stateless, shared services (like LLMClient) should remain Singletons. This is critical for preventing state-bleed between users.
Strict modularity: All new features should be implemented as modules or services and registered in the DI container, respecting the Factory/Singleton decisions.
Dummy fallbacks: If a module fails to import or is feature-flagged off, a dummy implementation is used. Always check logs for warnings about dummy services.
Feature flags: Use feature flags (forest_app/core/feature_flags.py) extensively to manage the MVP scope and incrementally enable more complex features. All non-MVP modules should be disabled by default.
Configuration: All config should be centralized in settings.py and loaded via the DI container.
Logging: Logging is set up at the top of most files. Use the provided logger for all debug/info/error output.
Backend (No major changes, DI notes above apply)
Routers: All API endpoints are registered via routers in forest_app/routers/ and included in main.py.
Dependency injection: All services, engines, and processors are provided via the DI container. Never instantiate these directly. Adhere to the established Factory/Singleton patterns for concurrency safety.
Database: PostgreSQL for production, SQLite for local dev/testing. Initialization is handled at startup. Migrations are supported via Alembic.
Security: Security dependencies are initialized at startup. User model must have an email field.
Frontend (Test Harness - streamlit_app.py)
Role Clarification: The Streamlit app is a testing and demonstration tool, not the production UI. Its development should support this role.
Streamlit: Only one call to st.set_page_config is allowed (enforced by tests).
No deprecated caching: Do not use @st.cache; use @st.cache_data or @st.cache_resource if needed.
Session state: All user/session data is managed via st.session_state with consistent key usage for testing purposes.
API client: All backend calls go through api_client.py for consistent error handling and logging.
Authentication: Handled in auth_ui.py for testing the auth flow.
Onboarding: Modularized in onboarding_ui.py for testing the onboarding flow.
Testing (tests/ directory)
Priority: Augment with tests for the ultra-lean MVP flow first.
Existing tests cover backend endpoints, Streamlit test harness import/caching, and HTA lifecycle.
Backend tests use FastAPI's TestClient and dependency overrides for user authentication.
HTA lifecycle tests use dummy models and async test cases.
Robustness & User Experience (API and Test Harness)
Error handling: All user-facing errors are displayed in the test UI or returned in API responses.
Fallbacks: If a feature or service fails or is disabled, the app will use a dummy and log a warning, but will not crash.
User experience (Test Harness): The Streamlit frontend is designed for clarity for developers/testers.
Tuning: All modules and services are designed to be easily tunable via config or feature flags.
Recommendations for New Developers/AI
FOCUS ON MVP: All current work must align with delivering the ultra-lean MVP first (Goal -> Simple AI Task List -> Mark Done).
Concurrency & DI: Understand and adhere to the Factory pattern for ForestOrchestrator and most engines in containers.py and dependencies.py to ensure request isolation.
AI Agent Tasking: When using AI coding assistants (e.g., Cursor, Windsurf):
Assign very small, specific, well-defined tasks aligned with the MVP and the established architecture.
Provide explicit context: which files to modify, which existing patterns to follow.
All AI-generated code MUST be reviewed by a human to ensure architectural adherence and quality before merging.
Always check logs for warnings about dummy services or failed imports.
Use the DI container for all service/engine access.
Add new features as modules and register them in the container (as Factories by default for stateful components).
Write tests for all new endpoints and features, especially for the MVP.
Keep user experience in mind (for API consumers and test harness users)—optimize for clarity, error recovery, and visual feedback.
Document any new quirks or workarounds in this handover file.
Outstanding Issues / TODOs (Re-prioritized for MVP - May 2025)
Phase 0: Preparation & Control (Immediate Human Tasks)

Finalize Ultra-Lean MVP Definition: Confirm the absolute minimal feature set for "Goal -> Simple AI Task List -> Mark Done."
Aggressively Disable Non-MVP Features: Systematically go through forest_app/config/settings.py and feature flags to turn off all non-essential modules/engines.
Stabilize Local Development Environment: Ensure a clean, runnable state with non-MVP features disabled.
Phase 1: Ultra-Lean MVP Implementation & Critical Fixes (Highest Priority)

DI Concurrency Fix - Verification & Engine Review (CRITICAL):
Verify ForestOrchestrator is consistently a Factory in containers.py and provided per-request in dependencies.py.
Review ALL other engines/managers (sentiment_engine, pattern_engine, xp_mastery, snapshot_flow_controller, seed_manager, etc.) in containers.py. Change their providers to providers.Factory by default unless unequivocally proven to be stateless. Prioritize safety from concurrency issues.
Test basic concurrent requests to ensure isolation with this new DI setup.
Implement Simple Task Storage (MVP):
Define a new, simple SQLAlchemy model for UserSimpleTask (e.g., user_id, goal_statement, task_description, is_done).
Generate Alembic migration.
Implement Repository for Simple Tasks (MVP):
Add functions in forest_app/persistence/repository.py to create, retrieve, and update UserSimpleTask instances. Ensure no commits within repository functions.
Design LLM Prompt for Simple Task List (MVP - Human Task):
Craft and test a robust prompt for the LLM to take a user goal and return 3-5 simple task strings in JSON format.
Implement Orchestrator Method for Simple Tasks (MVP):
Add a method in ForestOrchestrator to call the LLM with the designed prompt, parse the response, and use the repository to save the simple tasks.
Create API Endpoint for Simple Journey (MVP):
Develop a new FastAPI endpoint (e.g., /users/me/simple-journey) that accepts a goal statement, calls the new orchestrator method, commits the transaction, and returns the generated tasks.
Write Basic Tests for MVP Flow:
Implement integration tests for the new "simple journey" endpoint, mocking the LLM call.
Ensure tests cover task creation and marking tasks as done (endpoint for this will also be needed).
Phase 2: Stabilize & Incrementally Expand Beyond MVP
8.  Expand Test Coverage: Focus on increasing coverage for all core and MVP components.
9.  Centralize Constants: Address duplication of constants, particularly between frontend (test harness) and backend if any remain critical.
10. Improve Onboarding Modularity (Backend Logic for MVP): If the MVP involves an onboarding step, ensure its backend logic is clean.
11. Review Feature Flag Usage: Ensure all optional/future features are properly gated and current MVP features are correctly enabled.
12. Refactor Dummy Fallbacks: Consider more granular logging or specific dummy behaviors for a better developer/testing experience when features are off.
13. Iteratively Introduce Next Core Feature: Once MVP is stable, select the next smallest valuable feature (e.g., evolving simple tasks into basic HTA nodes, introducing one well-understood analytical engine like sentiment analysis for the goal statement). Apply the same rigorous, architecturally-aligned, test-driven approach.

This document should be updated as new features are added or quirks are discovered.