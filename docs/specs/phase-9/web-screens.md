# Phase 9 Web Screens — Slice 1

> Maps [openapi.yaml](./openapi.yaml) → UI. Reuses Phase 7 design system and i18n infrastructure.  
> **Phase 9 screens:** Research inbox/notes, Series hub, Export panel.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| Design system | Phase 7 tokens, `Button`, `Badge`, `Table`, `Modal`, `Skeleton`, `Empty` — [design-system.md](../phase-7/design-system.md) |
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–8 |
| Types | Generated / hand-written from Phase 9 OpenAPI |
| MSW | Handlers for research, series, export routes |
| i18n | New namespaces `research.*`, `series.*`, `export.*` — VI primary, EN secondary |
| a11y | WCAG AA; keyboard nav on tables and modals |
| Route loading | `loading.tsx` skeletons per Phase 7 [performance.md](../phase-7/performance.md) |

---

## i18n namespaces (implementers)

Add keys under `apps/web/messages/vi.json` and `en.json`:

### `research.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `research.inbox.title` | Nghiên cứu | Page title |
| `research.inbox.search_placeholder` | Tìm ghi chú... | Search input |
| `research.inbox.empty` | Chưa có ghi chú nghiên cứu | Empty state |
| `research.note.new` | Ghi chú mới | CTA |
| `research.note.title` | Tiêu đề | Form label |
| `research.note.body` | Nội dung | Markdown editor |
| `research.note.source_url` | Nguồn tham khảo | Optional URL |
| `research.note.tags` | Thẻ | Tag input |
| `research.note.status.active` | Đang dùng | Status pill |
| `research.note.status.promoted` | Đã đưa vào staging | |
| `research.links.title` | Liên kết | Links panel |
| `research.links.character` | Nhân vật | Link type |
| `research.links.place` | Địa điểm | |
| `research.links.fact` | Sự kiện / fact | |
| `research.links.chapter` | Chương | |
| `research.promote.title` | Đưa vào Story Bible (staging) | Modal title |
| `research.promote.section` | Mục bible | Section select |
| `research.promote.confirm` | Tạo staging | Primary CTA |
| `research.promote.hint` | Cần settle riêng để ghi canon | Footer note |
| `research.gate.category` | Nghiên cứu | Gate filter (WARN only) |

### `series.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `series.hub.title` | Series | Series list / hub |
| `series.hub.books` | Các cuốn | Book list column |
| `series.hub.shared_bible` | Bible dùng chung | Tab |
| `series.badge` | Thuộc series | Hub badge on child project |
| `series.inherited.title` | Nội dung kế thừa | Child read-only panel |
| `series.inherited.read_only` | Chỉ đọc — từ series | Banner |
| `series.inherited.drift_warn` | Series bible đã cập nhật | Drift banner |
| `series.override.title` | Ghi đè cho cuốn này | Override modal |
| `series.override.reason` | Lý do ghi đè | Optional field |
| `series.override.confirm` | Tạo staging ghi đè | CTA |
| `series.attach.title` | Gắn dự án vào series | Modal |
| `series.book_order` | Thứ tự cuốn | Number input |
| `series.gate.category` | Series | Gate filter |

### `export.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `export.panel.title` | Xuất bản | Hub panel / settings section |
| `export.format.epub` | EPUB | Format radio |
| `export.format.docx` | DOCX | |
| `export.format.git_md` | Git Markdown (zip) | |
| `export.scope.settled_only` | Chỉ chương đã settle | Scope select |
| `export.scope.include_drafts` | Bao gồm bản nháp | |
| `export.scope.selected` | Chọn chương | Opens chapter picker |
| `export.options.include_bible` | Kèm Story Bible | Checkbox |
| `export.options.strip_secrets` | Ẩn twist chưa lộ | Checkbox default on |
| `export.options.author_notes` | Ghi chú tác giả | Checkbox |
| `export.jobs.title` | Lịch sử xuất | Job table |
| `export.jobs.status.pending` | Đang chờ | Status pill |
| `export.jobs.status.running` | Đang xử lý | |
| `export.jobs.status.done` | Hoàn tất | |
| `export.jobs.status.failed` | Lỗi | |
| `export.jobs.download` | Tải xuống | Link when done |
| `export.jobs.error` | {message} | Failed row tooltip |
| `export.enqueue` | Bắt đầu xuất | Primary CTA |
| `export.polling` | Đang tạo file... | Progress text |

---

## Screen — Research inbox

**Route:** `/projects/[projectId]/research`  
**Stories:** Domain §13 (research module)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `ResearchInboxHeader` | — |
| Search + filters | `ResearchSearchBar` | `GET .../research/notes/search` or list |
| Note list | `ResearchNoteTable` | `GET .../research/notes` |
| Detail drawer | `ResearchNoteDrawer` | `GET .../research/notes/{id}` |
| Links panel | `ResearchLinksPanel` | note.links |
| Promote modal | `ResearchPromoteModal` | `POST .../promote` |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| List notes | `GET .../research/notes?status=active` |
| Search | `GET .../research/notes/search?q=` |
| Create note | `POST .../research/notes` |
| Save edits | `PATCH .../research/notes/{id}` |
| Add link | `POST .../links` |
| Promote | `POST .../promote` |

### States

| State | UI |
|-------|-----|
| **Empty** | Illustration + "Ghi chú mới" CTA |
| **Loading** | Table skeleton |
| **Active note** | Editable markdown body |
| **Promoted note** | Read-only; link to staging entry in Bible browser |
| **Search no results** | Empty search state |
| **Promote success** | Toast + navigate to Bible staging highlight |

---

## Screen — Series hub

**Route:** `/series` (list), `/series/[seriesId]` (detail)  
**Stories:** Domain §12

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Series list | `SeriesListPage` | `GET /series` |
| Detail header | `SeriesHubHeader` | `GET /series/{id}` |
| Book grid | `SeriesBookGrid` | detail.projects |
| Shared bible tab | `SeriesSharedBiblePanel` | `GET .../bible-slice` |
| Attach modal | `SeriesAttachProjectModal` | `POST .../projects` |

### Child project delta — inherited slice panel

**Route:** `/projects/[projectId]/bible` (tab or sidebar)  
**Component:** `SeriesInheritedSlicePanel`

| Element | Behavior |
|---------|----------|
| Read-only JSON/markdown view | `GET .../series/inherited-slice` |
| Drift banner | When `drift_warning=true` |
| Override CTA | Opens `SeriesOverrideModal` → `POST .../series/overrides` |
| Series badge | On `ProjectHubPage` when `series_id` set |

### States

| State | UI |
|-------|-----|
| **No series** | Dashboard CTA "Tạo series" |
| **Empty books** | Attach project CTA |
| **Drift WARN** | Amber banner with "Xem thay đổi" |
| **Hub project link** | Navigate to hub bible staging |

---

## Screen — Export panel

**Route:** `/projects/[projectId]/settings/export` or Hub section  
**Stories:** US-E01, US-E02

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Format + scope form | `ExportJobForm` | local state |
| Enqueue button | `ExportEnqueueButton` | `POST .../export/jobs` |
| Job history | `ExportJobTable` | `GET .../export/jobs` |
| Poll hook | `useExportJobPoll` | `GET .../jobs/{id}` every 2s until terminal |
| Download | `ExportDownloadLink` | `GET .../download` |

### Scope UX

| `chapter_scope` | UI control |
|-----------------|------------|
| `settled_only` | Default radio — helper text explains draft exclusion |
| `include_drafts` | Radio — shows draft count badge |
| `selected` | Multi-select chapter table |

### States

| State | UI |
|-------|-----|
| **Idle** | Form enabled |
| **Pending/running** | Row spinner; disable duplicate enqueue same type (optional) |
| **Done** | Download button + file size |
| **Failed** | Red status + error_message |
| **No settled chapters** | Inline warn before enqueue |

---

## Project Hub delta

| Addition | Component |
|----------|-----------|
| Research card | Link to inbox + active note count |
| Series badge | `SeriesHubBadge` when attached |
| Export quick action | Opens export panel drawer |
| Recent export jobs | Last 3 rows mini-table |

---

## Continuity Gate delta

| Addition | Component |
|----------|-----------|
| Category filter | `research`, `series` in `ContinuityCategoryFilter` |
| WARN-only badge | Tooltip "Không chặn settle" |

---

## MSW fixtures (web tests)

| Fixture | Path |
|---------|------|
| Research notes list | `tests/fixtures/phase9/research-notes.json` |
| Promote response | `tests/fixtures/phase9/research-promote.json` |
| Series detail | `tests/fixtures/phase9/series-detail.json` |
| Inherited slice | `tests/fixtures/phase9/inherited-slice.json` |
| Export job lifecycle | `tests/fixtures/phase9/export-job-done.json` |

---

## Wireframe parity

Phase 9 extends wireframe **Hub** (export action) and adds Research/Series routes not in original 10 wireframes — follow Phase 7 empty/loading/error patterns from [screen-parity.md](../phase-7/screen-parity.md).

---

## Links

- [openapi.yaml](./openapi.yaml)
- [api-contracts.md](./api-contracts.md)
- [test-strategy.md](./test-strategy.md)
