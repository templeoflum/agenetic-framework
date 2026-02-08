# Directive 001 — Initialize Repository and Scaffold Phase 1

**Date:** 2026-02-07

## Context

This is the first directive for the Agenetic Framework — a biologically-inspired agent architecture where seven information-processing systems operate as a weighted network. The full architecture specification is in `docs/ARCHITECTURE.md`. The directive system documentation is in `docs/DIRECTIVES.md`. Read `CLAUDE.md` for project overview.

The implementation pathway (see `docs/ARCHITECTURE.md`, Section: Implementation Pathway) defines four phases. This directive covers the foundation for **Phase 1 — Minimal Viable Cell**: seven systems as nodes in a LangGraph graph with fixed connection weights, no sleep/homeostasis/apoptosis yet.

This directive does NOT implement the systems themselves. It sets up the repo, installs dependencies, defines interfaces, and creates stubs — so the next directive can focus purely on implementing the first system.

## Objective

Initialize the repository as a proper Python project with LangGraph as the orchestration framework, define the interfaces and base classes that all seven systems will implement, and create stub implementations for each system that can be wired into a runnable (but non-functional) graph.

## Tasks

### Task 1: Initialize Git and Push to GitHub

Initialize this directory as a git repository and push it to GitHub:

- `git init`
- Create the GitHub repository (use `gh repo create agenetic-framework --public --source=. --push` or equivalent)
- Initial commit with all existing files (CLAUDE.md, README.md, docs/, handoff/, references/, empty src/ and tests/ scaffolding)
- Verify the repo is accessible on GitHub

All subsequent work in this directive should be committed and pushed when complete.

### Task 2: Project Setup

Initialize the repo as a Python project:

- Create `pyproject.toml` with project metadata and dependencies:
  - `langgraph` (graph-based agent orchestration)
  - `langchain-anthropic` (Anthropic LLM integration)
  - `pytest` for testing
  - Python 3.11+ required
- Create a `.gitignore` appropriate for Python projects
- Create `src/agenetic/__init__.py` with version string
- Verify the project installs and imports correctly

### Task 3: Define System Interface

Create `src/agenetic/systems/base.py` with a base class that all seven systems must implement. The interface should capture what's common across systems per the architecture spec:

- Each system has a **name** and **description**
- Each system has a **tick_rate** property (for Phase 2, but define it now)
- Each system has a **process()** method that takes system state and returns updated state
- Each system has a **repair_check()** method that validates its own output
- Each system has an **apoptotic_condition()** method that returns whether exit conditions are met (for Phase 3, but define the interface now)
- Each system receives the **orientational field** as part of its input context

The state object passed between systems should be a typed dict or dataclass. At minimum it needs:
- `input`: the current input being processed
- `field`: the orientational field state (read-only for all systems except sleep)
- `immune_log`: the threat log (writable by immune, prunable by sleep)
- `metadata`: tick counter, timestamps, routing history
- `flags`: degradation flags, escalation signals, apoptotic signals

### Task 4: Create System Stubs

Create stub implementations for all seven systems in `src/agenetic/systems/`:

- `sensory.py` — SensorySystem
- `immune.py` — ImmuneSystem
- `subconscious.py` — SubconsciousSystem
- `conscious.py` — ConsciousSystem
- `motor.py` — MotorSystem
- `sleep.py` — SleepSystem
- `genetic.py` — GeneticSystem

Each stub should:
- Inherit from the base class
- Implement all required methods
- Have `process()` pass through the state unchanged (no-op)
- Have `repair_check()` return True (always passes)
- Have `apoptotic_condition()` return False (never triggers)
- Include a docstring describing what this system will do when fully implemented (pull from `docs/ARCHITECTURE.md`)

### Task 5: Define Network Topology

Create `src/agenetic/network/topology.py` that defines the connection matrix from `docs/ARCHITECTURE.md`, Section: Connection Matrix.

This should be a data structure (not executable routing yet) that defines:
- Which systems connect to which
- Connection type: primary (always active) vs. secondary (context-dependent)
- Connection direction (from → to)
- Default weight (1.0 for primary, 0.5 for secondary, 0.0 for absent)

Also create `src/agenetic/network/graph.py` with a function that:
- Takes the topology definition and the seven system instances
- Builds a LangGraph StateGraph wiring them together according to the topology
- Returns a compiled, runnable graph

For Phase 1 this can use a simplified routing strategy — process all every-cycle systems, then conditionally route to conscious/motor. The full network routing comes in Phase 2.

### Task 6: Create Basic Test Suite

Create tests in `tests/`:

- `test_systems.py` — verify all seven system stubs instantiate, implement the interface, and pass through state correctly
- `test_topology.py` — verify the connection matrix matches the architecture spec (correct connections exist, absent connections don't)
- `test_graph.py` — verify the graph compiles and can process a trivial input end-to-end (even if all systems are no-ops)

### Task 7: Orientational Field Stub

Create `src/agenetic/field/orientational.py` with:

- A data structure holding the eighteen Asparśa limbs as the initial field values
- A read method that returns the current field state
- A write method that only accepts writes from the sleep system (enforce this with a caller check or token)
- The field is a shared state object, not a processing layer

The eighteen limbs and their descriptions can be pulled from `docs/ARCHITECTURE.md`, Section: The Asparśa Limbs as Field Specification.

## Scope Boundaries

**DO:**
- Set up the Python project with proper packaging
- Define interfaces and base classes
- Create stub implementations
- Define the network topology as data
- Wire stubs into a runnable LangGraph graph
- Write tests that verify structure and wiring
- Commit with a clear message

**DO NOT:**
- Implement actual system behavior (that's Directive 002+)
- Make architecture decisions not in the spec — if something is ambiguous, note it in the response
- Add dependencies beyond what's listed (LangGraph, langchain-anthropic, pytest)
- Modify `docs/ARCHITECTURE.md` or `docs/DIRECTIVES.md`
- Create any files outside the paths specified

## Deliverables

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Create | Project config with dependencies |
| `.gitignore` | Create | Python gitignore |
| `src/agenetic/__init__.py` | Create | Package init with version |
| `src/agenetic/systems/__init__.py` | Create | Systems subpackage |
| `src/agenetic/systems/base.py` | Create | Base system interface |
| `src/agenetic/systems/sensory.py` | Create | Sensory stub |
| `src/agenetic/systems/immune.py` | Create | Immune stub |
| `src/agenetic/systems/subconscious.py` | Create | Subconscious stub |
| `src/agenetic/systems/conscious.py` | Create | Conscious stub |
| `src/agenetic/systems/motor.py` | Create | Motor stub |
| `src/agenetic/systems/sleep.py` | Create | Sleep stub |
| `src/agenetic/systems/genetic.py` | Create | Genetic stub |
| `src/agenetic/network/__init__.py` | Create | Network subpackage |
| `src/agenetic/network/topology.py` | Create | Connection matrix definition |
| `src/agenetic/network/graph.py` | Create | LangGraph wiring |
| `src/agenetic/field/__init__.py` | Create | Field subpackage |
| `src/agenetic/field/orientational.py` | Create | Orientational field stub |
| `src/agenetic/regulation/__init__.py` | Create | Regulation subpackage (empty for now) |
| `tests/test_systems.py` | Create | System interface tests |
| `tests/test_topology.py` | Create | Topology verification tests |
| `tests/test_graph.py` | Create | End-to-end graph test |
| `handoff/001_response.md` | Create | Completion report |

## Verification Checklist

- [ ] Git repository initialized and pushed to GitHub
- [ ] Repo is publicly accessible on GitHub
- [ ] `pyproject.toml` exists with langgraph, langchain-anthropic, pytest dependencies
- [ ] Project installs without errors (`pip install -e .`)
- [ ] All seven system stubs exist and inherit from base class
- [ ] Base class defines process(), repair_check(), apoptotic_condition(), tick_rate
- [ ] State object is typed with input, field, immune_log, metadata, flags
- [ ] Topology defines all primary connections from architecture spec
- [ ] Topology defines all secondary connections from architecture spec
- [ ] Absent connections (any→genetic write, motor→sensory, genetic→motor) are explicitly absent
- [ ] LangGraph graph compiles without errors
- [ ] Graph processes a trivial input end-to-end
- [ ] Orientational field contains all eighteen Asparśa limbs
- [ ] Orientational field write access is restricted to sleep system
- [ ] All tests pass
- [ ] No files outside deliverables list modified
- [ ] No historical handoff files edited
- [ ] Git commit with descriptive message and pushed to GitHub
