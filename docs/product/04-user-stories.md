# StoryForge — User Stories

> Format: **As a… I want… so that…** — nhóm theo epic. Acceptance criteria (AC) khi hữu ích.

---

## Epic: Project

### US-P01 — Tạo dự án mới

**As a** tác giả (Kim)  
**I want** tạo dự án mới qua wizard (tên, thể loại, template)  
**So that** tôi có workspace cô lập với bible seed phù hợp genre.

**AC:**
- Wizard 3–5 bước: Basics → Genre → Template → Seed bible (optional) → Confirm
- `project_id` + slug unique; redirect to Project Hub
- Genre chọn rule pack defaults (xianxia / mystery / literary)

### US-P02 — Dashboard dự án

**As a** tác giả  
**I want** xem grid tất cả dự án với progress và last edited  
**So that** tôi chuyển nhanh giữa các truyện.

**AC:**
- Card: cover placeholder, title, genre tag, progress %, last edited date
- Search filter by title; FAB “Dự án mới”
- Empty state: CTA tạo dự án đầu tiên

### US-P03 — Multi-project isolation

**As a** tác giả  
**I want** dữ liệu mỗi dự án hoàn toàn tách biệt  
**So that** nhân vật/ledger dự án A không leak sang dự án B.

**AC:**
- API 403 khi truy cập `project_id` không thuộc user
- Không cross-project trong search/embedding

### US-P04 — Rename / archive project

**As a** tác giả  
**I want** đổi tên hoặc archive dự án  
**So that** dashboard gọn mà không mất dữ liệu.

**AC:**
- Archive ẩn khỏi default grid; có thể restore
- Rename không đổi slug nếu đã share link (hoặc warn)

---

## Epic: Bible

### US-B01 — Browse Story Bible

**As a** tác giả  
**I want** duyệt bible theo cây mục (World Rules, Locations, Factions, …)  
**So that** tôi chỉnh canon có cấu trúc.

**AC:**
- TOC sidebar; markdown content; metadata block (id, type, version, status)
- Wiki-links `[[Entity/Name]]` render clickable
- View vs edit mode

### US-B02 — Version bible on settle

**As a** tác giả  
**I want** bible version tăng chỉ khi settle chapter  
**So that** lịch sử canon không bị ghi đè.

**AC:**
- `bible_versions` immutable; diff vN vs vN+1 viewable
- Draft edits staging area trước settle

### US-B03 — Entity links panel

**As a** tác giả  
**I want** thấy nhân vật/vị trí liên kết entry đang xem  
**So that** tôi hiểu impact của rule change.

**AC:**
- Right panel: linked characters, locations counts + list
- Version history per entry

### US-B04 — Search bible (⌘K)

**As a** tác giả  
**I want** tìm nhanh trong bible  
**So that** tôi không scroll cây mục lớn.

**AC:**
- Full-text + pgvector (Phase 3+); keyboard shortcut
- Results scoped `project_id`

---

## Epic: Outline

### US-O01 — Act / chapter outline

**As a** tác giả  
**I want** outline cấp act và chapter với status  
**So that** tôi plan trước khi viết.

**AC:**
- CRUD chapters; status: planned / writing / reviewing / settled
- Link to TwistPlan targets per chapter

### US-O02 — Timeline board

**As a** tác giả  
**I want** timeline anchor events  
**So that** thứ tự sự kiện thế giới nhất quán.

**AC:**
- Ordered events; link to chapters; continuity uses order

### US-O03 — Twist board

**As a** tác giả  
**I want** board plants / payoffs / secrets  
**So that** tôi visualize fair foreshadow.

**AC:**
- Cards: secret (author-only), plants by chapter, payoff targets
- Warn if payoff chapter lacks plants

---

## Epic: Characters

### US-C01 — Progressive tier promote

**As a** tác giả  
**I want** nhân vật deep dần T0→T3  
**So that** cast lớn không cần full bio lúc đầu.

**AC:**
- Tier badge on character; manual promote + suggest on recurrence
- T3 requires psyche card minimum fields

### US-C02 — Provisional inbox

**As a** tác giả  
**I want** inbox mentions extract từ prose  
**So that** tôi merge/reject trước khi gán ledger.

**AC:**
- Actions: merge, promote new, reject
- No ledger writes to provisional IDs

### US-C03 — Psyche + relationship panels

**As a** tác giả  
**I want** xem/sửa psyche và quan hệ trên character page  
**So that** OOC check có dữ liệu.

**AC:**
- Psyche card form; relationship list with intensity + history tail
- PsychState timeline per chapter

---

## Epic: Writing / Edit

### US-W01 — Chapter editor + scene beats

**As a** tác giả  
**I want** editor với sidebar scene beats  
**So that** tôi viết theo cấu trúc scene.

**AC:**
- Beat list 7.1…; select highlights; mark complete
- Prose auto-save; word count vs target

### US-W02 — Versioned prose

**As a** tác giả  
**I want** mỗi save tạo version (v1, v2, …)  
**So that** tôi rollback hoặc compare.

**AC:**
- Dropdown version; source tag human / ai_writer / ai_editor
- Compare diff between versions

### US-W03 — Prompt Edit loop

**As a** tác giả  
**I want** mô tả chỉnh sửa AI và Apply / Regenerate / Compare  
**So that** human-in-the-loop tinh chỉnh nhanh.

**AC:**
- Chat log user instruction + AI response
- Apply creates new prose version; Regenerate retries; Compare shows diff
- Edit history link

### US-W04 — Lock chapter

**As a** tác giả  
**I want** lock chapter đã settled  
**So that** không sửa nhầm canon đã chốt.

**AC:**
- Locked chapters read-only until explicit unlock with warn

---

## Epic: Continuity

### US-CO01 — Run continuity check

**As a** tác giả  
**I want** chạy check trên draft hiện tại  
**So that** tôi thấy lỗi trước settle.

**AC:**
- Result PASS/WARN/FAIL; stats errors/warnings/passed
- Issue table: severity, category, description, chapter refs

### US-CO02 — Mark intentional

**As a** tác giả  
**I want** đánh dấu WARN là cố ý  
**So that** twist hợp lệ không block settle.

**AC:**
- Override stored with note; re-run skips fingerprint
- FAIL still blocks unless explicit override with reason

### US-CO03 — State diff preview

**As a** tác giả  
**I want** xem thay đổi ledger/bible đề xuất trước settle  
**So that** tôi không commit nhầm state.

**AC:**
- Character state changes; new canon candidates listed
- Approve & Settle atomic; Reject returns to editor

### US-CO04 — Fix in editor

**As a** tác giả  
**I want** jump từ issue row sang editor đúng chỗ  
**So that** sửa nhanh.

**AC:**
- Deep link chapter + optional beat highlight

---

## Epic: Twists

### US-T01 — Register secret + plants

**As a** tác giả  
**I want** đăng ký secret và plants theo chapter  
**So that** payoff được fairness gate bảo vệ.

**AC:**
- secret_truth author-only; plants with strength enum
- Continuity links plant IDs to payoff

### US-T02 — Payoff alert

**As a** tác giả  
**I want** cảnh báo khi viết payoff chapter thiếu plant  
**So that** twist không “rơi từ trời”.

**AC:**
- FAIL or WARN based on genre_profile; intentional override path

---

## Epic: Power

### US-PW01 — Define rank ladder

**As a** tác giả (xianxia)  
**I want** define cultivation ranks trong bible  
**So that** anti-creep rules có baseline.

**AC:**
- Ordered ranks; optional sub-stages; priority_gap config

### US-PW02 — Cultivation change on settle

**As a** tác giả  
**I want** breakthrough chỉ canonize khi settle  
**So that** draft không làm tăng rank giả.

**AC:**
- cultivation_change in state diff; deterministic check rank jump

---

## Epic: Export / Admin

### US-E01 — Export chapter / novel

**As a** tác giả  
**I want** export DOCX/EPUB (later)  
**So that** publish ngoài platform.

**AC:**
- Settled chapters only option; include/exclude author notes

### US-E02 — Git mirror canon

**As a** tác giả (power user)  
**I want** export bible markdown to Git  
**So that** diff canon trong git history.

**AC:**
- Derived from settled versions; not SoT

### US-E03 — Project members ACL

**As a** owner  
**I want** mời editor/viewer  
**So that** cộng tác an toàn.

**AC:**
- Roles enforced API + RLS; viewer no settle

---

## Epic: Project Hub (cross)

### US-H01 — Project hub overview

**As a** tác giả  
**I want** hub với stats chapters, open topics, continuity status  
**So that** tôi biết “viết tiếp gì”.

**AC:**
- Summary cards; chapter table paginated; recent activity feed
- Next action AI suggestion + “Bắt đầu viết” CTA

---

## Story → Screen → Phase map

| Epic | Primary screens | Build phase |
|------|-----------------|-------------|
| Project | Dashboard, New Project wizard | Phase 1 |
| Bible | Story Bible | Phase 1 |
| Outline | Outline / Timeline / Twist board | Phase 4, 8 |
| Characters | Characters + Provisional inbox | Phase 3 |
| Writing | Chapter Editor | Phase 2 |
| Continuity | Continuity Gate | Phase 2 |
| Twists | Twist board | Phase 4 |
| Power | Power System bible | Phase 6 |
| Export | Admin settings | Phase 8+ |

Chi tiết wireframe: [05-wireframes.md](./05-wireframes.md).  
Lộ trình: [06-build-plan.md](./06-build-plan.md).
