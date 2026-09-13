# Phase 9 — Series Projects

> **Skill:** `storyforge-domain-canon`, `storyforge-architecture`  
> **Product:** [03-domain-and-subsystems.md](../../product/03-domain-and-subsystems.md) §12

---

## Purpose

Multi-book **series** share a parent bible slice (world rules, glossary, shared factions) while each **child project** maintains its own chapters, ledgers, and project-local canon. Inheritance is **read-only** in the child UI; overrides are **explicit** staging entries — never silent overwrite of child or parent settled canon.

---

## Key entities

| Entity | Role |
|--------|------|
| `series` | Parent container: title, slug, owner |
| `series_bible_slice` | JSON document of inheritable sections (subset of bible shape) |
| `series_projects` | Join: child `project_id` ↔ `series_id` with `book_order` |
| `series_inheritance_config` | Per child: which sections inherited, override policy |
| `bible_entry_staging.series_override` | Flag when child intentionally overrides inherited key |

---

## Bible slice shape

Inheritable sections (configurable per series, default all):

```json
{
  "world": { "rules": {}, "locations": {}, "factions": {} },
  "glossary": {},
  "style": {},
  "power_system": {}
}
```

**Not inherited by default:** `characters` (cast differs per book), `timeline` (book-local), `objects`, chapter-specific content.

Parent slice updates when series owner settles staging on the **series hub project** (see below) or via dedicated series bible staging routes.

---

## Series hub project

Each `series` has optional `hub_project_id` — a normal `projects` row used as the authoring surface for the shared slice. Child projects reference `series_id` but do not mutate hub settled versions directly.

| Action | Where |
|--------|-------|
| Edit shared world rules | Hub project bible staging → settle |
| Write Book 2 chapters | Child project only |
| View inherited rules | Child read-only panel |

---

## Inheritance rules

1. **Read path:** Child API merges `series_bible_slice` (settled) under inherited keys + child `bible_versions` snapshot for non-inherited sections. Inherited keys display with badge **"Series"** in UI.
2. **Write path:** Child cannot PATCH inherited keys directly. Author clicks **Override in this book** → creates `bible_entry_staging` with `series_override: true`, `overrides_series_key`, `base_bible_version`.
3. **Settle:** Child settle applies overrides into child snapshot only; parent slice unchanged.
4. **Conflict:** If child override key matches inherited key, child snapshot wins locally after settle; parent unchanged.
5. **Never silent:** No background sync from parent to child settled canon. Parent slice update surfaces **WARN** in child continuity check (`series_parent_slice_updated`) — author reviews overrides.

---

## Attach / detach child

| Operation | Rule |
|-----------|------|
| Attach | Project must not belong to another series; sets `projects.series_id`, `book_order` |
| Detach | Clears `series_id`; inherited content already in child snapshots remains; future reads stop merging parent slice |
| Reattach | Inheritance config reset to defaults; does not delete child overrides |

---

## API surface (summary)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/series` | List series for current user |
| POST | `/series` | Create series + optional hub project |
| GET | `/series/{series_id}` | Detail + child list |
| PATCH | `/series/{series_id}` | Update title/slug |
| GET | `/series/{series_id}/bible-slice` | Current settled slice (read) |
| PATCH | `/series/{series_id}/bible-slice/staging` | Upsert hub staging entries for slice sections |
| POST | `/series/{series_id}/projects` | Attach child `{ project_id, book_order }` |
| DELETE | `/series/{series_id}/projects/{project_id}` | Detach child |
| GET | `/projects/{project_id}/series/inherited-slice` | Merged read model for child UI |
| POST | `/projects/{project_id}/series/overrides` | Create override staging entry |

See [openapi.yaml](./openapi.yaml).

---

## Continuity (WARN-only)

| Code | Severity | When |
|------|----------|------|
| `series_parent_slice_updated` | WARN | Parent slice version > child's `last_seen_series_slice_version` |
| `series_override_without_reason` | WARN | Override staging row missing `override_reason` (optional field) |
| `series_inherited_key_conflict` | WARN | Child staging edits same key as inherited without `series_override` flag |

No FAIL from series category in Phase 9 — avoids blocking Book N settle when parent hub updates.

---

## ACL

- Series owner = creator; same stub as project owner (`X-User-Id`).
- Child project members can read inherited slice; override requires `editor`+ on child project.
- Phase 10+: multi-user series admin roles.

---

## Web touchpoints

- **Series hub:** list books, shared bible browser (read-only in child context)
- **Child project:** inherited slice panel + override flow
- Hub badge on Project Hub when `series_id` set

See [web-screens.md](./web-screens.md).

---

## Multi-tenant isolation

Series and projects scoped by owner membership. Foreign series id → `404`.

---

## Deferred (Phase 10+)

- `motifs`, `ending_promises` cross-book tracking
- Automatic parent→child diff notification email
- Neo4j for cross-book character appearance graph
