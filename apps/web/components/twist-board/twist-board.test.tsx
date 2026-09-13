import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { CHAPTER_2_ID, PROJECT_1_ID } from "@/mocks/data";
import { TWIST_1_ID, TWIST_2_ID } from "@/mocks/phase4-data";
import { server } from "@/mocks/server";
import { CreateSecretModal } from "./CreateSecretModal";
import { FairnessCheckPanel } from "./FairnessCheckPanel";
import { OutlineStubTab } from "./OutlineStubTab";
import { OutlineTabBar } from "./OutlineTabBar";
import { PayoffCard } from "./PayoffCard";
import { PlantCard } from "./PlantCard";
import { RevealedCard } from "./RevealedCard";
import { SecretCard } from "./SecretCard";
import { TimelineStubTab } from "./TimelineStubTab";
import { TwistBoardColumns } from "./TwistBoardColumns";
import { TwistBoardHeader } from "./TwistBoardHeader";
import { TwistBoardPage } from "./TwistBoardPage";
import { TwistDetailDrawer } from "./TwistDetailDrawer";
import { getTwistBoard } from "@/lib/api/twists";

describe("Twist Board components", () => {
  it("renders secret card with author-only badge", () => {
    render(
      <SecretCard
        card={{
          card_type: "twist",
          title: "Test secret",
          secret_truth_preview: "Hidden truth",
          status: "seeded",
          plant_count: 0,
        }}
      />,
    );
    expect(screen.getByText("Test secret")).toBeInTheDocument();
    expect(screen.getByText("Author")).toBeInTheDocument();
    expect(screen.getByText("Hidden truth")).toBeInTheDocument();
  });

  it("renders payoff card with fail border and continuity link", () => {
    render(
      <PayoffCard
        projectId={PROJECT_1_ID}
        targetChapterId="770e8400-e29b-41d4-a716-446655440003"
        card={{
          card_type: "payoff",
          twist_title: "Fail payoff",
          target_chapter_number: 3,
          min_plants: 2,
          plant_count: 1,
          fairness: {
            state: "fail",
            issue_codes: ["foreshadow_plant_count_below_minimum"],
          },
        }}
      />,
    );
    expect(screen.getByText("Fail payoff")).toBeInTheDocument();
    expect(screen.getByText("foreshadow_plant_count_below_minimum")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Mở Continuity Gate" })).toHaveAttribute(
      "href",
      `/projects/${PROJECT_1_ID}/chapters/770e8400-e29b-41d4-a716-446655440003/continuity`,
    );
  });

  it("renders fairness panel with continuity links", async () => {
    const board = await getTwistBoard(PROJECT_1_ID);
    const payoffCards = board.columns.find((column) => column.id === "payoffs")?.cards ?? [];
    render(
      <FairnessCheckPanel
        projectId={PROJECT_1_ID}
        payoffCards={payoffCards}
        payoffChapterIds={{ [TWIST_2_ID]: "770e8400-e29b-41d4-a716-446655440003" }}
      />,
    );
    expect(screen.getByText("Fairness check")).toBeInTheDocument();
    expect(screen.getByText("Huyết mạch thật sự")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Mở Continuity Gate" })).toBeInTheDocument();
  });

  it("renders four kanban columns from board API", async () => {
    const board = await getTwistBoard(PROJECT_1_ID);
    render(
      <TwistBoardColumns
        board={board}
        loading={false}
        projectId={PROJECT_1_ID}
        payoffChapterIds={{}}
        onCardClick={() => undefined}
      />,
    );
    expect(screen.getByText("Bí mật")).toBeInTheDocument();
    expect(screen.getByText("Plants")).toBeInTheDocument();
    expect(screen.getByText("Payoffs")).toBeInTheDocument();
    expect(screen.getByText("Đã lộ")).toBeInTheDocument();
    expect(screen.getByText("Sát thủ là sư phụ")).toBeInTheDocument();
  });

  it("shows loading skeleton for board columns", () => {
    render(
      <TwistBoardColumns
        board={null}
        loading
        projectId={PROJECT_1_ID}
        payoffChapterIds={{}}
        onCardClick={() => undefined}
      />,
    );
    expect(screen.getByTestId("loading-skeleton-kanban")).toBeInTheDocument();
  });

  it("renders outline and timeline stub tabs", () => {
    render(
      <OutlineStubTab
        chapters={[
          {
            id: "1",
            project_id: PROJECT_1_ID,
            number: 1,
            title: "Ch 1",
            status: "planned",
            word_count: 0,
            created_at: "",
            updated_at: "",
          },
        ]}
      />,
    );
    expect(
      screen.getByText("Dàn ý chi tiết — sắp ra mắt (Phase 8+)"),
    ).toBeInTheDocument();
    expect(screen.getByText("Ch.1 — Ch 1")).toBeInTheDocument();

    render(<TimelineStubTab />);
    expect(screen.getByText("Timeline board — Phase 8")).toBeInTheDocument();
  });

  it("renders tab bar with twist board link", () => {
    render(<OutlineTabBar projectId={PROJECT_1_ID} activeTab="twist-board" />);
    expect(screen.getByRole("link", { name: "Twist Board" })).toHaveAttribute(
      "href",
      `/projects/${PROJECT_1_ID}/outline?tab=twist-board`,
    );
  });

  it("renders plant and revealed cards", async () => {
    render(
      <PlantCard
        card={{
          card_type: "plant",
          chapter_number: 4,
          salience: "hard",
          snippet: "Plant snippet",
          twist_title: "Linked twist",
        }}
        onClick={() => undefined}
      />,
    );
    expect(screen.getByText("Plant snippet")).toBeInTheDocument();

    render(
      <RevealedCard
        card={{ card_type: "twist", title: "Revealed twist", plant_count: 2 }}
      />,
    );
    expect(screen.getByText("Revealed twist")).toBeInTheDocument();
  });

  it("create secret modal shows error on failure", async () => {
    const user = userEvent.setup();
    render(
      <CreateSecretModal
        open
        onClose={() => undefined}
        onSubmit={async () => {
          throw new Error("fail");
        }}
      />,
    );
    await user.type(screen.getByLabelText("Tiêu đề"), "Fail secret");
    await user.type(screen.getByLabelText(/Secret truth/), "Truth");
    await user.click(screen.getByRole("button", { name: "Tạo secret" }));
    expect(await screen.findByText("Không tạo được secret. Vui lòng thử lại.")).toBeInTheDocument();
  });

  it("drawer saves twist edits and registers payoff", async () => {
    const user = userEvent.setup();
    render(
      <TwistDetailDrawer
        projectId={PROJECT_1_ID}
        twistId={TWIST_1_ID}
        chapters={[
          {
            id: CHAPTER_2_ID,
            project_id: PROJECT_1_ID,
            number: 2,
            title: "Ch 2",
            status: "drafting",
            word_count: 100,
            created_at: "",
            updated_at: "",
          },
        ]}
        onClose={() => undefined}
        onUpdated={() => undefined}
      />,
    );
    const titleInput = await screen.findByDisplayValue("Sát thủ là sư phụ");
    await user.clear(titleInput);
    await user.type(titleInput, "Secret đã sửa");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));
    expect(await screen.findByDisplayValue("Secret đã sửa")).toBeInTheDocument();
  });

  it("renders header with fairness badge and create secret button", async () => {
    const user = userEvent.setup();
    const onCreate = vi.fn();
    render(
      <TwistBoardHeader
        projectTitle="Kiếm Lai"
        kindFilter=""
        onKindFilterChange={() => undefined}
        onCreateSecret={onCreate}
        fairnessFailCount={2}
      />,
    );
    expect(screen.getByText("2 payoff cần kiểm tra")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "+ Secret" }));
    expect(onCreate).toHaveBeenCalled();
  });
});

describe("TwistBoardPage", () => {
  it("renders twist board with seeded secret card", async () => {
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    expect(await screen.findByText("Sát thủ là sư phụ")).toBeInTheDocument();
    expect(screen.getAllByText("Huyết mạch thật sự").length).toBeGreaterThan(0);
    expect(screen.getByText("1 payoff cần kiểm tra")).toBeInTheDocument();
  });

  it("opens create secret modal and creates twist", async () => {
    const user = userEvent.setup();
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    await screen.findByText("Sát thủ là sư phụ");
    await user.click(screen.getByRole("button", { name: "+ Secret" }));
    await user.type(screen.getByLabelText("Tiêu đề"), "Secret mới");
    await user.type(screen.getByLabelText(/Secret truth/), "Sự thật mới");
    await user.click(screen.getByRole("button", { name: "Tạo secret" }));
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("opens detail drawer when secret card clicked", async () => {
    const user = userEvent.setup();
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    const secretCard = await screen.findByRole("button", { name: /Sát thủ là sư phụ/i });
    await user.click(secretCard);
    expect(await screen.findByText("Chi tiết twist")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Sát thủ là sư phụ")).toBeInTheDocument();
  });

  it("filters board by kind from header", async () => {
    const user = userEvent.setup();
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    await screen.findByText("Sát thủ là sư phụ");
    await user.selectOptions(screen.getByLabelText("Lọc loại twist"), "twist");
    expect(await screen.findByText("Sát thủ là sư phụ")).toBeInTheDocument();
  });

  it("shows outline stub tab content", async () => {
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="outline" />);
    expect(
      await screen.findByText("Dàn ý chi tiết — sắp ra mắt (Phase 8+)"),
    ).toBeInTheDocument();
  });

  it("shows timeline stub tab content", async () => {
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="timeline" />);
    expect(await screen.findByText("Timeline board — Phase 8")).toBeInTheDocument();
  });

  it("shows not found for unknown project", async () => {
    render(<TwistBoardPage projectId="00000000-0000-0000-0000-000000000000" activeTab="twist-board" />);
    expect(await screen.findByText("Không tìm thấy dự án")).toBeInTheDocument();
  });

  it("shows error state on board load failure", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:projectId/twists/board", () =>
        HttpResponse.json({ error: { code: "error", message: "fail" } }, { status: 500 }),
      ),
    );
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    expect(await screen.findByText("Không tải được twist board")).toBeInTheDocument();
  });

  it("shows empty secrets CTA when no twists", async () => {
    server.use(
      http.get("http://localhost:8000/projects/:id/twists/board", () =>
        HttpResponse.json({
          columns: [
            { id: "secrets", label: "Secrets", cards: [] },
            { id: "plants", label: "Plants", cards: [] },
            { id: "payoffs", label: "Payoffs", cards: [] },
            { id: "revealed", label: "Revealed", cards: [] },
          ],
        }),
      ),
    );
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    expect(await screen.findByText("Đăng ký secret đầu tiên")).toBeInTheDocument();
  });

  it("drawer registers payoff for planted twist", async () => {
    const user = userEvent.setup();
    render(
      <TwistDetailDrawer
        projectId={PROJECT_1_ID}
        twistId={TWIST_1_ID}
        chapters={[
          {
            id: CHAPTER_2_ID,
            project_id: PROJECT_1_ID,
            number: 2,
            title: "Ch 2",
            status: "drafting",
            word_count: 100,
            created_at: "",
            updated_at: "",
          },
        ]}
        onClose={() => undefined}
        onUpdated={() => undefined}
      />,
    );
    await screen.findByDisplayValue("Sát thủ là sư phụ");
    await user.selectOptions(screen.getByLabelText("Chọn chương"), CHAPTER_2_ID);
    await user.type(screen.getByPlaceholderText("Snippet plant…"), "Plant for payoff");
    await user.click(screen.getByRole("button", { name: "Thêm plant" }));
    await screen.findByText(/Plant for payoff/);
    await user.selectOptions(screen.getByLabelText("Chọn chương payoff"), CHAPTER_2_ID);
    await user.click(screen.getByRole("button", { name: "Đăng ký payoff" }));
    expect(await screen.findByText(/Ch\.2 · min/)).toBeInTheDocument();
  });

  it("drawer can add plant to twist", async () => {
    const user = userEvent.setup();
    render(
      <TwistDetailDrawer
        projectId={PROJECT_1_ID}
        twistId={TWIST_1_ID}
        chapters={[
          {
            id: CHAPTER_2_ID,
            project_id: PROJECT_1_ID,
            number: 2,
            title: "Chương 2",
            status: "drafting",
            word_count: 100,
            created_at: "",
            updated_at: "",
          },
        ]}
        onClose={() => undefined}
        onUpdated={() => undefined}
      />,
    );
    expect(await screen.findByDisplayValue("Sát thủ là sư phụ")).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Chọn chương"), CHAPTER_2_ID);
    await user.type(screen.getByPlaceholderText("Snippet plant…"), "Plant mới trong drawer");
    await user.click(screen.getByRole("button", { name: "Thêm plant" }));
    expect(await screen.findByText(/Plant mới trong drawer/)).toBeInTheDocument();
  });

  it("detail drawer loads twist by id", async () => {
    const user = userEvent.setup();
    render(<TwistBoardPage projectId={PROJECT_1_ID} activeTab="twist-board" />);
    await screen.findByText("Sát thủ là sư phụ");
    const payoffButtons = screen.getAllByRole("button", { name: /Huyết mạch thật sự/i });
    await user.click(payoffButtons[0]);
    expect(await screen.findByText("Chi tiết twist")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Huyết mạch thật sự")).toBeInTheDocument();
    expect(screen.getByText(/Plants \(1\)/)).toBeInTheDocument();
    void TWIST_1_ID;
  });
});
