# Phase 10 Web Screens — Real-World Fact Check

> Maps [openapi.yaml](./openapi.yaml) → UI. Reuses Phase 7 design system and i18n infrastructure.  
> **Phase 10 screens:** Fact Check panel (chapter editor), Project reality settings.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| Design system | Phase 7 tokens, `Button`, `Badge`, `Table`, `Modal`, `Skeleton`, `Empty` — [design-system.md](../phase-7/design-system.md) |
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–9 |
| Types | Generated / hand-written from Phase 10 OpenAPI |
| MSW | Handlers for reality-settings, fact-check runs, claim actions |
| i18n | New namespace `factCheck.*` — VI primary, EN secondary |
| a11y | WCAG AA; issue rows keyboard navigable; citation links external with `rel="noopener"` |
| Route loading | `loading.tsx` skeletons per Phase 7 [performance.md](../phase-7/performance.md) |

---

## Continuity Gate vs Fact Check (UI boundary)

| Aspect | Continuity Gate | Fact Check panel |
|--------|-----------------|------------------|
| Location | Chapter editor — existing Gate tab/panel | Chapter editor — **separate tab** `Fact Check` |
| Issue source | Bible, ledgers, beats | External providers + research notes |
| Severity display | FAIL blocks settle (default) | FAIL advisory unless project setting |
| Bridge | May show `fact_check` WARN rows when strict | Primary home for all fact-check issues |
| Actions | Mark intentional (continuity override) | Disposition, accept fix, promote evidence |

**Do not** merge fact-check issues into Gate category filters by default. Strict-mode bridge rows link **Open in Fact Check** deep link.

---

## i18n namespaces (implementers)

Add keys under `apps/web/messages/vi.json` and `en.json`:

### `factCheck.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `factCheck.panel.title` | Kiểm tra sự thật | Panel title |
| `factCheck.panel.subtitle` | Đối chiếu với nguồn bên ngoài | Subtitle |
| `factCheck.panel.empty` | Chưa chạy kiểm tra | Empty state |
| `factCheck.panel.run` | Chạy kiểm tra | Primary CTA |
| `factCheck.panel.running` | Đang kiểm tra... | Polling state |
| `factCheck.panel.skipped_off` | Reality anchors tắt — không kiểm tra | When `reality_off` |
| `factCheck.panel.last_run` | Lần chạy gần nhất | Timestamp |
| `factCheck.severity.pass` | Khớp | Badge |
| `factCheck.severity.warn` | Cần xem lại | |
| `factCheck.severity.fail` | Mâu thuẫn | |
| `factCheck.category.date` | Ngày tháng | Category pill |
| `factCheck.category.place` | Địa điểm | |
| `factCheck.category.organization` | Tổ chức | |
| `factCheck.category.technology` | Công nghệ | |
| `factCheck.category.historical_event` | Sự kiện lịch sử | |
| `factCheck.category.scientific_medical` | Khoa học / y học | |
| `factCheck.category.public_figure` | Nhân vật thực | |
| `factCheck.claim.excerpt` | Trích đoạn | Row header |
| `factCheck.claim.confidence` | Độ tin cậy {percent}% | |
| `factCheck.claim.proposed_fix` | Đề xuất sửa | |
| `factCheck.citations.title` | Nguồn tham khảo | |
| `factCheck.citations.retrieved` | Lấy lúc {date} | |
| `factCheck.actions.accept_fix` | Áp dụng đề xuất | Opens Prompt Edit |
| `factCheck.actions.intentional` | Cố ý / hư cấu | Disposition |
| `factCheck.actions.dismiss` | Bỏ qua | |
| `factCheck.actions.promote_evidence` | Lưu vào nghiên cứu | → research note |
| `factCheck.actions.open_research` | Mở ghi chú nghiên cứu | After promote |
| `factCheck.disposition.intentional_fiction` | Đánh dấu hư cấu | Status pill |
| `factCheck.disposition.dismissed` | Đã bỏ qua | |
| `factCheck.disposition.accepted_fix` | Đã chấp nhận sửa | |
| `factCheck.disposition.evidence_promoted` | Đã lưu nguồn | |
| `factCheck.error.run_failed` | Kiểm tra thất bại: {message} | |
| `factCheck.error.load_failed` | Không tải được báo cáo | |
| `factCheck.gate.bridge_hint` | Cũng hiện ở Continuity Gate (WARN) | Strict mode banner |
| `factCheck.gate.category` | Kiểm tra sự thật | Gate filter label |

### `factCheck.settings.*` (project settings section)

| Key | VI example | Usage |
|-----|------------|-------|
| `factCheck.settings.title` | Reality anchors | Settings section |
| `factCheck.settings.reality_anchors` | Chế độ neo thực tế | |
| `factCheck.settings.mode.off` | Tắt | Radio |
| `factCheck.settings.mode.soft` | Mềm (chỉ đoạn đánh dấu) | |
| `factCheck.settings.mode.strict` | Nghiêm (toàn chương) | |
| `factCheck.settings.categories` | Danh mục kiểm tra | Multi-select |
| `factCheck.settings.blocks_settle` | Chặn settle khi FAIL | Checkbox default off |
| `factCheck.settings.auto_run` | Tự chạy khi lưu | Checkbox |
| `factCheck.settings.include_research` | Dùng ghi chú nghiên cứu làm bằng chứng | Checkbox |
| `factCheck.settings.saved` | Đã lưu cài đặt | Toast |

---

## Screen — Fact Check panel (chapter editor)

**Route:** `/projects/[projectId]/chapters/[chapterId]` — tab `fact-check`  
**Stories:** External verification workflow (new; complements US-W01)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `FactCheckPanelHeader` | — |
| Run bar | `FactCheckRunBar` | `POST .../fact-check/runs`, poll latest |
| Summary chips | `FactCheckSummaryChips` | run.summary |
| Issue list | `FactCheckIssueList` | run.claims |
| Issue row | `FactCheckIssueRow` | claim + citations |
| Citation drawer | `FactCheckCitationDrawer` | claim.citations |
| Accept fix modal | `FactCheckAcceptFixModal` | accept-fix handoff → Prompt Edit |
| Disposition confirm | `FactCheckDispositionDialog` | disposition API |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load latest run | `GET .../fact-check/runs?page=1` or cached run id |
| Run check | `POST .../fact-check/runs` |
| Poll status | `GET .../runs/{run_id}` every 2s until done/failed |
| Mark fiction | `POST .../claims/{id}/disposition` |
| Dismiss | `POST .../claims/{id}/disposition` |
| Accept fix | `POST .../claims/{id}/accept-fix` → navigate Prompt Edit |
| Promote evidence | `POST .../claims/{id}/promote-evidence` |

### States

| State | UI |
|-------|-----|
| Empty | Illustration + "Chạy kiểm tra" CTA |
| Loading | Skeleton issue rows |
| Running | Progress + disable re-run |
| Done (no issues) | Success empty — "Không phát hiện vấn đề" |
| Done (issues) | Filterable list by severity/category |
| Failed | Error banner + retry |
| Skipped (`reality_off`) | Info banner — link to settings |

### Prose highlight (optional enhancement)

When issue row focused, scroll editor to `span.start/end` and highlight excerpt — read-only; no auto-edit.

---

## Screen — Project reality settings

**Route:** `/projects/[projectId]/settings` — section `reality`  
**Also:** New Project wizard optional step (genre = historical → suggest `strict`)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Section | `RealitySettingsSection` | `GET/PATCH .../reality-settings` |
| Mode radios | `RealityAnchorsModeRadio` | |
| Category multi-select | `FactCheckCategorySelect` | |
| Advanced toggles | `FactCheckAdvancedToggles` | blocks_settle, auto_run, include_research |

### Validation

- At least one category when mode ≠ `off`
- Warn when enabling `blocks_settle`: "FAIL kiểm tra sự thật sẽ chặn settle"

---

## MSW handlers (Vitest)

| Handler | Notes |
|---------|-------|
| `GET/PATCH .../reality-settings` | Default soft |
| `POST .../fact-check/runs` | Returns pending → poll to done |
| `GET .../runs/:id` | Fixture with 2 claims (warn + fail) |
| `POST .../disposition` | Updates claim in store |
| `POST .../accept-fix` | Returns prompt_edit handoff |
| `POST .../promote-evidence` | Returns research note stub |

---

## Coverage targets (web)

| Module | Path glob | Gate |
|--------|-----------|------|
| Fact Check panel | `**/fact-check/**` | ≥ 90% line |
| Reality settings | `**/settings/**/reality*` | ≥ 90% line |

See [test-strategy.md](./test-strategy.md).

---

## Links

- [fact-check.md](./fact-check.md)
- [Phase 7 design system](../phase-7/design-system.md)
- [Phase 9 research screens](../phase-9/web-screens.md)
