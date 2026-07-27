# Hermes Agent Lite — Product Scope

## Goal

Preserve the proven Hermes Agent conversation runtime while reducing the repository and installation surface for an enterprise air-gapped machine.

Upstream baseline: `NousResearch/hermes-agent@760112adb6458417da8614d2269e5325f0739ed5`.

## Required capabilities

- Existing `run_agent.py` conversation and tool-call loop
- Prompt caching and strict message-role invariants
- Streaming, cancellation, retry, compression, and session persistence
- OpenAI-compatible model endpoints configured by the operator
- Local workspace, file, terminal, process, approval, clarify, skills, and memory paths
- Existing WebUI runtime integration until a separately tested stable contract replaces it
- Python 3.11–3.13
- Standard wheel build suitable for an internal package index

## Explicitly out of scope

- Messaging platform gateways and delivery adapters
- Public account onboarding and OAuth flows
- Runtime package installation
- Online update checks, skills catalogs, plugin catalogs, and release discovery
- Public SaaS integrations not explicitly approved for the enterprise build
- Product website, showcase applications, contributor galleries, and bundled optional content
- TUI, desktop, mobile, Nix, Termux, and container distributions unless later required

## Air-gap contract

1. Installation uses only an operator-provided internal Python index or wheelhouse.
2. Runtime never invokes `pip`, `uv pip`, npm, curl installers, GitHub, or a package catalog.
3. Runtime network destinations are limited to model/MCP endpoints explicitly configured by the operator.
4. Missing optional capabilities fail closed with a clear `not included in this build` error.
5. Production JavaScript has zero npm runtime dependencies.
6. All shipped dependencies are lockable, auditable, and representable in an SBOM.

## Change policy

- Subtract at the edges before changing the runtime.
- No agent-loop rewrite or architecture cleanup during pruning.
- Each feature-family removal must have import, unit, and live-path verification.
- Upstream runtime/security fixes are selectively ported; feature expansion is not merged wholesale.
