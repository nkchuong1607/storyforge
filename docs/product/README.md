# StoryForge — Product Documentation

> Tài liệu sản phẩm & kỹ thuật cho StoryForge. **Tiếng Việt** cho nội dung product; code identifiers và file paths **tiếng Anh**.

StoryForge là hệ thống viết tiểu thuyết dài có AI: bible/canon có phiên bản, ledger append-only, continuity gate, và human-in-the-loop settle.

---

## Ai nên đọc gì?

| Đối tượng | Bắt đầu từ |
|-----------|------------|
| **Product / Kim** | [01-vision-and-outcomes.md](./01-vision-and-outcomes.md) → [05-wireframes.md](./05-wireframes.md) |
| **Engineering / Agent** | [AGENTS.md](../../AGENTS.md) → [02-architecture.md](./02-architecture.md) → skills `skills/storyforge-*/` |
| **Planning** | [06-build-plan.md](./06-build-plan.md) |

---

## Mục lục

| # | Document | Nội dung |
|---|----------|----------|
| 01 | [Vision & Outcomes](./01-vision-and-outcomes.md) | “Viết được truyện tốt” — success criteria, outcome → subsystem map |
| 02 | [Architecture](./02-architecture.md) | **Canonical** stack, agents, ledgers, data flow, security |
| 03 | [Domain & Subsystems](./03-domain-and-subsystems.md) | Deep dive: characters, twists, psych, power, genre, scene engine, … |
| 04 | [User Stories](./04-user-stories.md) | Epics + acceptance criteria |
| 05 | [Wireframes](./05-wireframes.md) | 5 images + text specs màn hình còn lại |
| 06 | [Build Plan](./06-build-plan.md) | Phase 0–8+, MVP scope, PR order |

---

## Wireframes

Images: [`docs/wireframes/images/`](../wireframes/images/)

| File | Screen |
|------|--------|
| `dashboard-projects.png` | Dashboard dự án |
| `project-hub.png` | Project hub / chapter list |
| `chapter-editor.png` | Chapter editor + Prompt Edit |
| `story-bible.png` | Story Bible / World |
| `continuity-gate.png` | Continuity Gate + state diff |

---

## Engineering docs (bổ sung)

| Doc | Purpose |
|-----|---------|
| [docs/architecture.md](../architecture.md) | Stub → [02-architecture.md](./02-architecture.md) |
| [docs/domain-model.md](../domain-model.md) | Entity reference ngắn |
| [docs/schema-draft.md](../schema-draft.md) | Postgres sketch |
| [docs/roadmap.md](../roadmap.md) | Stub → [06-build-plan.md](./06-build-plan.md) |
| [docs/agent-setup.md](../agent-setup.md) | External UI skills |
| [docs/aas-selection.md](../aas-selection.md) | Vendored AAS stack |

---

## Agent skills index

Domain skills trong `skills/` — đọc khi implement subsystem tương ứng:

| Skill | Subsystem |
|-------|-----------|
| `storyforge-architecture` | Layer boundaries, context packs |
| `storyforge-domain-canon` | Bible, settle, ledgers |
| `storyforge-continuity` | Continuity Gate |
| `storyforge-characters` | Progressive cast, inbox |
| `storyforge-twists` | TwistPlan |
| `storyforge-psychology` | Psyche, PsychState, OOC |
| `storyforge-power-system` | Cultivation, anti-creep |
| `storyforge-api-python` | FastAPI |
| `storyforge-web-next` | Next.js |
| `storyforge-db-design` | Migrations, Postgres |
| `storyforge-ui-external` | UI polish |
| `storyforge-aas-stack` | Vendored craft skills |

---

## Trạng thái repo

**Bootstrap / Phase 0 done** — product UI chưa implement; docs mô tả target state cho Phase 1+.

```bash
make setup && make check
```
