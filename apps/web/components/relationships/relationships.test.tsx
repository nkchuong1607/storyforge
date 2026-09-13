import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { PROJECT_1_ID } from "@/mocks/data";
import { CHARACTER_1_ID, CHARACTER_2_ID, CHARACTER_3_ID } from "@/mocks/phase3-data";
import { renderWithProviders } from "@/lib/test/render-with-providers";
import relationshipGraphFixture from "@/tests/fixtures/phase8/relationship-graph.json";
import type { RelationshipGraphResponse } from "@/lib/api/types";
import { RelationshipDetailPanel } from "./RelationshipDetailPanel";
import { RelationshipGraphFilters } from "./RelationshipGraphFilters";
import { RelationshipGraphCanvas, RelationshipGraphList } from "./RelationshipGraphCanvas";
import { RelationshipGraphPage } from "./RelationshipGraphPage";
import { RelationshipRegisterModal } from "./RelationshipRegisterModal";

vi.mock("next/navigation", () => {
  const params = new URLSearchParams();
  return {
    useRouter: () => ({ push: vi.fn() }),
    useSearchParams: () => params,
  };
});

const graph = relationshipGraphFixture as RelationshipGraphResponse;

describe("relationship graph components", () => {
  it("RelationshipGraphCanvas returns null without nodes", () => {
    renderWithProviders(
      <RelationshipGraphCanvas
        nodes={[]}
        edges={[]}
        selectedEdgeId={null}
        onSelectEdge={vi.fn()}
      />,
    );
    expect(document.querySelector("svg")).toBeNull();
  });

  it("RelationshipGraphList shows empty state", () => {
    renderWithProviders(
      <RelationshipGraphList
        nodes={[]}
        edges={[]}
        selectedEdgeId={null}
        onSelectEdge={vi.fn()}
      />,
    );
    expect(screen.getByText("Chưa có quan hệ")).toBeInTheDocument();
  });

  it("RelationshipGraphList renders a11y table fallback", () => {
    renderWithProviders(
      <RelationshipGraphList
        nodes={graph.nodes}
        edges={graph.edges}
        selectedEdgeId={null}
        onSelectEdge={vi.fn()}
      />,
    );
    expect(screen.getByRole("table", { name: "Quan hệ nhân vật" })).toBeInTheDocument();
    expect(screen.getAllByText("Lý Phong").length).toBeGreaterThan(0);
    expect(screen.getByText("Đồng minh")).toBeInTheDocument();
  });

  it("RelationshipGraphCanvas renders svg graph", () => {
    renderWithProviders(
      <RelationshipGraphCanvas
        nodes={graph.nodes}
        edges={graph.edges}
        selectedEdgeId={graph.edges[0].id}
        onSelectEdge={vi.fn()}
      />,
    );
    expect(document.querySelector("svg")).toBeInTheDocument();
  });

  it("RelationshipGraphPage toggles canvas view", async () => {
    const user = userEvent.setup();
    renderWithProviders(<RelationshipGraphPage projectId={PROJECT_1_ID} />);
    await screen.findByText("Sơ đồ quan hệ");
    await user.click(screen.getByRole("button", { name: "Chế độ đồ thị" }));
    await waitFor(() => {
      expect(document.querySelector("svg")).toBeInTheDocument();
    });
  });

  it("RelationshipGraphFilters toggles act and types", async () => {
    const user = userEvent.setup();
    const onActChange = vi.fn();
    const onTypesChange = vi.fn();
    renderWithProviders(
      <RelationshipGraphFilters
        actNumber=""
        minIntensity={-5}
        relationTypes={[]}
        onActChange={onActChange}
        onMinIntensityChange={vi.fn()}
        onRelationTypesChange={onTypesChange}
        onApply={vi.fn()}
      />,
    );
    await user.selectOptions(screen.getByLabelText("Hồi"), "2");
    expect(onActChange).toHaveBeenCalledWith(2);
    await user.click(screen.getByRole("button", { name: "Đồng minh" }));
    expect(onTypesChange).toHaveBeenCalledWith(["ally"]);
  });

  it("RelationshipGraphFilters calls apply handler", async () => {
    const user = userEvent.setup();
    const onApply = vi.fn();
    renderWithProviders(
      <RelationshipGraphFilters
        actNumber=""
        minIntensity={-5}
        relationTypes={[]}
        onActChange={vi.fn()}
        onMinIntensityChange={vi.fn()}
        onRelationTypesChange={vi.fn()}
        onApply={onApply}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Áp dụng bộ lọc" }));
    expect(onApply).toHaveBeenCalled();
  });

  it("RelationshipGraphPage loads graph data", async () => {
    renderWithProviders(<RelationshipGraphPage projectId={PROJECT_1_ID} />);
    expect(await screen.findByText("Sơ đồ quan hệ")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole("table", { name: "Quan hệ nhân vật" })).toBeInTheDocument();
    });
  });

  it("RelationshipDetailPanel loads event timeline", async () => {
    const graph = relationshipGraphFixture as RelationshipGraphResponse;
    renderWithProviders(
      <RelationshipDetailPanel
        projectId={PROJECT_1_ID}
        edge={graph.edges[0]}
        nodes={graph.nodes}
      />,
    );
    expect(await screen.findByText("Lịch sử")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/Ch\. 2/)).toBeInTheDocument();
    });
  });

  it("RelationshipRegisterModal submits new pair", async () => {
    const user = userEvent.setup();
    const onCreated = vi.fn();
    renderWithProviders(
      <RelationshipRegisterModal
        open
        projectId={PROJECT_1_ID}
        characters={[
          {
            id: CHARACTER_1_ID,
            project_id: PROJECT_1_ID,
            display_name: "A",
            tier: 1,
            status: "established",
            aliases: [],
            appearance_count: 1,
            created_at: "",
            updated_at: "",
          },
          {
            id: CHARACTER_2_ID,
            project_id: PROJECT_1_ID,
            display_name: "B",
            tier: 1,
            status: "established",
            aliases: [],
            appearance_count: 1,
            created_at: "",
            updated_at: "",
          },
          {
            id: CHARACTER_3_ID,
            project_id: PROJECT_1_ID,
            display_name: "C",
            tier: 1,
            status: "established",
            aliases: [],
            appearance_count: 1,
            created_at: "",
            updated_at: "",
          },
        ]}
        onClose={vi.fn()}
        onCreated={onCreated}
      />,
    );
    await user.selectOptions(screen.getByLabelText("Nhân vật A"), CHARACTER_2_ID);
    await user.selectOptions(screen.getByLabelText("Nhân vật B"), CHARACTER_3_ID);
    await user.click(screen.getByRole("button", { name: "Đăng ký" }));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("relationship graph list a11y smoke", async () => {
    const graph = relationshipGraphFixture as RelationshipGraphResponse;
    const { container } = renderWithProviders(
      <RelationshipGraphList
        nodes={graph.nodes}
        edges={graph.edges}
        selectedEdgeId={null}
        onSelectEdge={vi.fn()}
      />,
    );
    const results = await axe(container);
    const critical = results.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious",
    );
    expect(critical).toHaveLength(0);
  });
});
