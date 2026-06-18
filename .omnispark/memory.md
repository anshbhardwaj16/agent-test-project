# Repo Memory — agent-test-project

<!-- omnispark:repo-memory v1 -->
> Loaded into the Claude Code / Copilot session context at every session
> start (`<workspace>/omnispark/.claude/CLAUDE.md` G-3). Anything below this
> line is what your AI assistant sees about this repo BEFORE you ask
> anything.
>
> Hand-curated by the team. Delete the `<!-- omnispark:hint -->` blocks
> below as you populate each section. The framework's docs-readiness gate
> WARNs (does not fail) when all three sections still have only hint text,
> so the team knows to come back and finish them.
>
> **Verifying entries (since 1.23):** each entry can carry a
> `<!-- verified: YYYY-MM-DD -->` annotation. `/omni:refresh` surfaces
> entries unverified for more than the configured staleness window
> (currently 90 days — sourced from
> `omnispark.lib.repo_memory.STALE_DAYS_THRESHOLD`) as "stale" — a
> nudge to re-confirm or remove. Annotation is optional; entries
> without it never go stale, but they're also never marked as "still
> true". Update the date when you re-confirm an entry is still accurate.

## Decisions made

<!-- omnispark:hint
Examples (replace this comment block once you have real entries):
- Tenant: `prod-1` (DEV uses `sandbox-east`) <!-- verified: 2026-05-22 -->
- Primary entity: Location <!-- verified: 2026-05-22 -->
- Survivorship: source-system priority — Salesforce wins over GBL <!-- verified: 2026-05-22 -->
- All new attributes default to nullable <!-- verified: 2026-05-22 -->
-->

## Known quirks / pitfalls

<!-- omnispark:hint
Examples:
- Field `external_id` is unique but case-sensitive — caused INC-4421 <!-- verified: 2026-05-22 -->
- Lambda cold-start adds ~30s to first request after deploy <!-- verified: 2026-05-22 -->
- The `/sync` endpoint silently truncates payloads >256KB (we hit it on attachment uploads) <!-- verified: 2026-05-22 -->
- Schema migrations require running `alembic upgrade head` BEFORE the new container deploys <!-- verified: 2026-05-22 -->
-->

## Conventions

<!-- omnispark:hint
Examples:
- Branch naming: `feature/EDAA-NNN-kebab-slug-YYYYMMDD` <!-- verified: 2026-05-22 -->
- PR titles MUST contain the Jira key <!-- verified: 2026-05-22 -->
- All schema migrations land in `alembic/versions/` only <!-- verified: 2026-05-22 -->
- Tests for new endpoints go in `tests/integration/` not `tests/unit/` <!-- verified: 2026-05-22 -->
-->

## Cross-references

- Repo type: unknown
- Registered: 2026-06-18T11:49:03+00:00
- Framework version at registration: 1.36.0
