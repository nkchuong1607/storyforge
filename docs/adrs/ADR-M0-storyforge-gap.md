# ADR-M0 — StoryForge Gap Architecture (Phase 11a/11b)

| Field | Value |
|-------|-------|
| **Status** | Accepted + schema frozen (Manager/Product/StoryMaker/Architect 2026-09-22) — P11a ready for implement |
| **Date** | 2026-09-22 (Asia/Saigon) |
| **Repo** | `nkchuong1607/storyforge` |
| **Authors** | System Architect |
| **SoT inputs** | Product brief v0.1→v0.2.1 · StoryMaker Phase 1–10 map · `docs/domain-model.md` · `docs/specs/phase-{2,6,9,10}/*` · `docs/product/06-build-plan.md` |
| **Manager locks** | Craft pack #1 = **Mystery** · no video · DOCX+MD export path · M0→… order remapped against live Phase 1–10 |

See [Phase 11 specs](../specs/phase-11/README.md) for implementation contracts derived from this ADR.

---

## 1. Context

Manager greenlit **M0 ADR** from Product brief v0.1 covering Bible entity graph, ContinuityIssue types, CraftPack schema, and Export targets (DOCX+MD), with craft pack #1 = Mystery and non-goal = video.

StoryMaker confirmed **Phase 1–10 already live on main**. Product brief v0.2 remapped greenfield M0–M6:

| v0.1 item | Reality | Decision |
|-----------|---------|----------|
| M0 ADR + domain | Specs exist | **Gap-ADR only** — do not rewrite domain |
| M1 Bible CRUD | Phase 1 | **CUT** (harden only if QC fails) |
| M2 Continuity | Phase 2–8 | **MERGE** → golden MS + regression |
| M3 Craft pack #1 | Only Phase 6 *rule* packs | **KEEP = P11a Mystery craft pack** |
| M4 Export | Phase 9 skeleton | **MERGE = P11b harden** |
| M5 In-world fact-check | Continuity Gate live; P10 = real-world | **CUT as rebuild** |
| Video | Rapidstory | **Non-goal forever for StoryForge** |

This ADR is the **M0 deliverable**: map as-is contracts, define the missing CraftPack schema, and bound P11a/P11b work.

---

## 2. Decision

**Adopt gap architecture, not greenfield domain redesign.**

1. Treat existing bible / continuity / fact-check / export specs as **frozen SoT**.
2. Introduce a new **CraftPack** domain (distinct from Phase 6 `genre_rule_pack_json`).
3. First pack: **Mystery** (fair-play craft + continuity hooks).
4. Harden Phase 9 export UX/quality for DOCX + Markdown (git-md); EPUB remains shipped but P11b AC focuses DOCX+MD per Product lock.
5. No video pipeline, no Neo4j, no generate-race, no multi-model zoo in P11.

---

## 3. As-is domain map (do not rewrite)

See Phase 11 [README](../specs/phase-11/README.md) for craft-pack additions. Bible, continuity, fact-check, and export semantics remain frozen per Phase 1–10 specs.

---

## 4. CraftPack schema (NEW — P11a)

Canonical contract: [mystery-craft-pack.md](../specs/phase-11/mystery-craft-pack.md).

---

## 5–10. Export harden, build sequence, consequences, alternatives, review asks

Unchanged from accepted ADR — P11b export harden follows P11a schema freeze. See full ADR in repo history or Product brief v0.2.

**P11a AC:** bind without rule-pack overwrite; golden ≥3 seeded craft/foreshadow flags; FakeLLM hooks ≥90%; Prompt Edit inject-only.
