import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { mockProjects } from "@/mocks/data";
import { CHARACTER_1_ID, PROVISIONAL_1_ID } from "@/mocks/phase3-data";
import { server } from "@/mocks/server";
import { CharactersPage } from "./CharactersPage";
import { CharacterDetailPage } from "./CharacterDetailPage";
import { CharacterFilters } from "./CharacterFilters";
import { CharacterTable } from "./CharacterTable";
import { ProvisionalInboxPanel } from "./ProvisionalInboxPanel";
import { CharactersEmptyState } from "./CharactersEmptyState";
import { CharacterRelationshipsPanel } from "./CharacterRelationshipsPanel";

let activeTabParam = "";
const replace = vi.fn((url: string) => {
  const query = url.split("?")[1] ?? "";
  activeTabParam = new URLSearchParams(query).get("tab") ?? "";
});
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
  useSearchParams: () => ({
    get: (key: string) => (key === "tab" ? activeTabParam || null : null),
  }),
}));
import { CharactersHeader } from "./CharactersHeader";
import { AddCharacterModal } from "./AddCharacterModal";
import { MergeCharacterModal } from "./MergeCharacterModal";

const projectId = mockProjects[0].id;

describe("CharactersPage", () => {
  beforeEach(() => {
    activeTabParam = "";
  });
  it("renders character list and inbox", async () => {
    render(<CharactersPage projectId={projectId} />);
    expect(await screen.findByRole("heading", { name: "Nhân vật" })).toBeInTheDocument();
    expect(screen.getByText("Lý Phong")).toBeInTheDocument();
    expect(screen.getAllByText("Hộp thư tạm").length).toBeGreaterThan(0);
    expect(screen.getByText("Lý Thanh Vân")).toBeInTheDocument();
  });

  it("filters characters by search", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Lý Phong");
    await user.type(screen.getByLabelText("Tìm kiếm nhân vật"), "Tiểu");
    await waitFor(() => {
      expect(screen.getByText("Tiểu Nguyệt")).toBeInTheDocument();
      expect(screen.queryByText("Ma Vương Hắc Ảnh")).not.toBeInTheDocument();
    });
  });

  it("creates a new character", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await user.click(await screen.findByRole("button", { name: "+ Thêm" }));
    await user.type(screen.getByLabelText("Tên hiển thị"), "Nhân vật mới");
    await user.click(screen.getByRole("button", { name: "Tạo" }));
    await waitFor(() => {
      expect(screen.getByText("Đã tạo nhân vật")).toBeInTheDocument();
    });
  });

  it("promotes new provisional from inbox", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Hắc Ảnh Sứ");
    await user.click(screen.getAllByRole("button", { name: "Promote new" })[0]);
    await waitFor(() => {
      expect(screen.getByText(/Đã promote/)).toBeInTheDocument();
    });
  });

  it("opens merge modal from inbox", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Lý Thanh Vân");
    await user.click(screen.getAllByRole("button", { name: "Merge" })[0]);
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Merge vào nhân vật có sẵn")).toBeInTheDocument();
  });

  it("shows not found for unknown project", async () => {
    render(<CharactersPage projectId="00000000-0000-0000-0000-000000000000" />);
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });

  it("shows error state and retries", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    render(<CharactersPage projectId={projectId} />);
    expect(await screen.findByText("Không tải được dự án")).toBeInTheDocument();
  });

  it("archives character from table", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Ma Vương Hắc Ảnh");
    const archiveButtons = screen.getAllByRole("button", { name: "Lưu trữ" });
    await user.click(archiveButtons[archiveButtons.length - 1]!);
    await waitFor(() => {
      expect(screen.getByText(/Đã lưu trữ Ma Vương Hắc Ảnh/)).toBeInTheDocument();
    });
  });

  it("completes merge flow", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Lý Thanh Vân");
    await user.click(screen.getAllByRole("button", { name: "Merge" })[0]);
    const dialog = await screen.findByRole("dialog");
    await user.selectOptions(
      screen.getByLabelText("Chọn nhân vật"),
      CHARACTER_1_ID,
    );
    await user.click(
      Array.from(dialog.querySelectorAll("button")).find((btn) => btn.textContent === "Merge")!,
    );
    await waitFor(() => {
      expect(screen.getByText(/Đã merge/)).toBeInTheDocument();
    });
  });

  it("rejects provisional from inbox", async () => {
    const user = userEvent.setup();
    render(<CharactersPage projectId={projectId} />);
    await screen.findByText("Tiểu Tuyết");
    await user.click(screen.getAllByRole("button", { name: "Reject" })[0]);
    await waitFor(() => {
      expect(screen.getByText(/Đã reject/)).toBeInTheDocument();
    });
  });
});

describe("CharacterDetailPage", () => {
  beforeEach(() => {
    activeTabParam = "";
  });

  it("renders overview tab", async () => {
    render(<CharacterDetailPage projectId={projectId} characterId={CHARACTER_1_ID} />);
    expect(await screen.findByRole("heading", { name: "Lý Phong" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tổng quan" })).toBeInTheDocument();
    expect(screen.getByDisplayValue("Lý Phong")).toBeInTheDocument();
  });

  it("shows psyche tab with editor and timeline", async () => {
    activeTabParam = "psyche";
    render(<CharacterDetailPage projectId={projectId} characterId={CHARACTER_1_ID} />);
    await screen.findByRole("heading", { name: "Lý Phong" });
    const driveField = await screen.findByLabelText("Drive");
    expect(driveField).toHaveValue("Trở thành kiếm tiên mạnh nhất Thanh Vân Tông");
    expect(screen.getByText("PsychState timeline")).toBeInTheDocument();
  });

  it("updates URL when switching tabs", async () => {
    const user = userEvent.setup();
    render(<CharacterDetailPage projectId={projectId} characterId={CHARACTER_1_ID} />);
    await screen.findByRole("heading", { name: "Lý Phong" });
    await user.click(screen.getByRole("button", { name: "Tâm lý" }));
    expect(replace).toHaveBeenCalledWith(
      `/projects/${projectId}/characters/${CHARACTER_1_ID}?tab=psyche`,
    );
  });

  it("saves overview changes", async () => {
    const user = userEvent.setup();
    render(<CharacterDetailPage projectId={projectId} characterId={CHARACTER_1_ID} />);
    await screen.findByDisplayValue("Lý Phong");
    const roleInput = screen.getByLabelText("Vai trò");
    await user.clear(roleInput);
    await user.type(roleInput, "Vai trò mới");
    await user.click(screen.getByRole("button", { name: "Lưu" }));
    await waitFor(() => {
      expect(screen.getByText("Đã lưu nhân vật")).toBeInTheDocument();
    });
  });

  it("shows not found for unknown character", async () => {
    render(
      <CharacterDetailPage
        projectId={projectId}
        characterId="00000000-0000-0000-0000-000000000000"
      />,
    );
    expect(await screen.findByText("Không tìm thấy nhân vật")).toBeInTheDocument();
  });

  it("shows relationships panel with trust list", async () => {
    activeTabParam = "relationships";
    render(<CharacterDetailPage projectId={projectId} characterId={CHARACTER_1_ID} />);
    await screen.findByRole("heading", { name: "Lý Phong" });
    expect(await screen.findByText("Đồ thị con nhân vật")).toBeInTheDocument();
    expect(screen.getByText("Đồng môn thân thiết")).toBeInTheDocument();
  });

  it("promotes tier from detail page", async () => {
    const user = userEvent.setup();
    render(
      <CharacterDetailPage projectId={projectId} characterId="990e8400-e29b-41d4-a716-446655440003" />,
    );
    await screen.findByRole("heading", { name: "Ma Vương Hắc Ảnh" });
    await user.click(screen.getByRole("button", { name: "Promote tier" }));
    await waitFor(() => {
      expect(screen.getByText("Đã promote tier")).toBeInTheDocument();
    });
  });

  it("archives from detail page", async () => {
    const user = userEvent.setup();
    render(
      <CharacterDetailPage projectId={projectId} characterId="990e8400-e29b-41d4-a716-446655440003" />,
    );
    await screen.findByRole("heading", { name: "Ma Vương Hắc Ảnh" });
    await user.click(screen.getByRole("button", { name: "Lưu trữ" }));
    await waitFor(() => {
      expect(screen.getByText("Đã lưu trữ nhân vật")).toBeInTheDocument();
    });
  });
});

describe("character components", () => {
  it("CharacterFilters emits changes", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <CharacterFilters
        values={{ tier: "", status: "", q: "" }}
        onChange={onChange}
      />,
    );
    await user.selectOptions(screen.getByLabelText("Lọc theo hạng"), "1");
    expect(onChange).toHaveBeenCalled();
  });

  it("CharacterTable renders actions", async () => {
    const user = userEvent.setup();
    const onPromote = vi.fn();
    render(
      <CharacterTable
        projectId={projectId}
        characters={[
          {
            id: "c1",
            project_id: projectId,
            display_name: "Test",
            role_one_liner: "Role",
            tier: 0,
            status: "established",
            aliases: [],
            appearance_count: 1,
            created_at: "2026-01-01",
            updated_at: "2026-01-01",
          },
        ]}
        onPromote={onPromote}
        onArchive={vi.fn()}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Promote tier" }));
    expect(onPromote).toHaveBeenCalled();
  });

  it("ProvisionalInboxPanel handles actions", async () => {
    const user = userEvent.setup();
    const onReject = vi.fn();
    render(
      <ProvisionalInboxPanel
        provisionals={[
          {
            id: PROVISIONAL_1_ID,
            project_id: projectId,
            mention_text: "Test mention",
            chapter_id: "ch",
            chapter_number: 1,
            prose_version: 1,
            snippet: "snippet",
            status: "pending",
            extractor_source: "heuristic",
            created_at: "2026-01-01",
          },
        ]}
        characters={[]}
        onMerge={vi.fn()}
        onPromoteNew={vi.fn()}
        onReject={onReject}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Reject" }));
    expect(onReject).toHaveBeenCalled();
  });

  it("CharactersEmptyState triggers add", async () => {
    const user = userEvent.setup();
    const onAdd = vi.fn();
    render(<CharactersEmptyState onAdd={onAdd} />);
    await user.click(screen.getByRole("button", { name: "Thêm nhân vật" }));
    expect(onAdd).toHaveBeenCalled();
  });

  it("CharacterRelationshipsPanel shows empty trust list", async () => {
    render(
      <CharacterRelationshipsPanel
        projectId={projectId}
        character={{
          id: "990e8400-e29b-41d4-a716-446655440003",
          project_id: projectId,
          display_name: "Empty",
          tier: 0,
          status: "established",
          aliases: [],
          appearance_count: 0,
          created_at: "2026-01-01",
          updated_at: "2026-01-01",
        }}
      />,
    );
    expect(await screen.findByText("Chưa có quan hệ được ghi nhận.")).toBeInTheDocument();
  });

  it("CharactersHeader toggles inbox", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    render(
      <CharactersHeader pendingCount={3} showInbox onToggleInbox={onToggle} onAdd={vi.fn()} />,
    );
    await user.click(screen.getByRole("button", { name: /Hộp thư tạm/ }));
    expect(onToggle).toHaveBeenCalled();
  });

  it("AddCharacterModal shows error on failure", async () => {
    const user = userEvent.setup();
    render(
      <AddCharacterModal
        open
        onClose={vi.fn()}
        onSubmit={async () => {
          throw new Error("fail");
        }}
      />,
    );
    await user.type(screen.getByLabelText("Tên hiển thị"), "Bad");
    await user.click(screen.getByRole("button", { name: "Tạo" }));
    expect(await screen.findByText("Không thể tạo nhân vật")).toBeInTheDocument();
  });

  it("MergeCharacterModal submits merge", async () => {
    const user = userEvent.setup();
    const onMerge = vi.fn().mockResolvedValue(undefined);
    render(
      <MergeCharacterModal
        open
        projectId={projectId}
        mentionText="Test"
        characters={[
          {
            id: CHARACTER_1_ID,
            project_id: projectId,
            display_name: "Lý Phong",
            tier: 3,
            status: "established",
            aliases: [],
            appearance_count: 1,
            created_at: "2026-01-01",
            updated_at: "2026-01-01",
          },
        ]}
        onClose={vi.fn()}
        onMerge={onMerge}
      />,
    );
    await user.selectOptions(screen.getByLabelText("Chọn nhân vật"), CHARACTER_1_ID);
    const dialog = screen.getByRole("dialog");
    await user.click(
      Array.from(dialog.querySelectorAll("button")).find((btn) => btn.textContent === "Merge")!,
    );
    await waitFor(() => expect(onMerge).toHaveBeenCalledWith(CHARACTER_1_ID));
  });
});
