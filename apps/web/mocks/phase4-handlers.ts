import { http, HttpResponse } from "msw";
import type {
  TwistPayoffCreateRequest,
  TwistPayoffUpdateRequest,
  TwistPlan,
  TwistPlanCreateRequest,
  TwistPlanUpdateRequest,
  TwistPlantCreateRequest,
  TwistPlantUpdateRequest,
  TwistTransitionRequest,
} from "@/lib/api/types";
import { mockChapters, mockProjects, paginate } from "./data";
import {
  buildTwistBoard,
  mockPhase4Payoffs,
  mockPhase4Plants,
  mockPhase4Twists,
} from "./phase4-data";

const BASE = "http://localhost:8000";

function notFound() {
  return HttpResponse.json(
    { error: { code: "not_found", message: "Resource not found" } },
    { status: 404 },
  );
}

function unauthorized() {
  return HttpResponse.json(
    { error: { code: "unauthorized", message: "X-User-Id header is required" } },
    { status: 401 },
  );
}

function projectExists(projectId: string): boolean {
  return mockProjects.some((p) => p.id === projectId);
}

function getTwists(projectId: string): TwistPlan[] {
  return mockPhase4Twists[projectId] ?? [];
}

function findTwist(projectId: string, twistId: string): TwistPlan | undefined {
  return getTwists(projectId).find((twist) => twist.id === twistId);
}

function chapterNumber(projectId: string, chapterId: string): number {
  const chapter = (mockChapters[projectId] ?? []).find((item) => item.id === chapterId);
  return chapter?.number ?? 0;
}

function syncTwistPlantCount(twist: TwistPlan): void {
  twist.plant_count = (mockPhase4Plants[twist.id] ?? []).length;
}

function syncTwistPayoffSummary(twist: TwistPlan): void {
  const payoff = mockPhase4Payoffs[twist.id];
  if (!payoff) {
    twist.payoff = null;
    return;
  }
  twist.payoff = {
    id: payoff.id,
    target_chapter_id: payoff.target_chapter_id,
    target_chapter_number: payoff.target_chapter_number,
    min_plants: payoff.min_plants,
    required_plant_ids: payoff.required_plant_ids,
  };
}

export const phase4Handlers = [
  http.get(`${BASE}/projects/:projectId/twists`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") ?? "1");
    const pageSize = Number(url.searchParams.get("page_size") ?? "20");
    const audience = url.searchParams.get("audience") ?? "author";
    let items = [...getTwists(params.projectId as string)];
    const status = url.searchParams.get("status");
    if (status) items = items.filter((twist) => twist.status === status);
    const kind = url.searchParams.get("kind");
    if (kind) items = items.filter((twist) => twist.kind === kind);
    const q = url.searchParams.get("q")?.toLowerCase() ?? "";
    if (q) items = items.filter((twist) => twist.title.toLowerCase().includes(q));
    if (audience === "writer") {
      items = items.map(({ secret_truth: _secret, misdirection: _mis, ...rest }) => rest);
    }
    return HttpResponse.json(paginate(items, page, pageSize));
  }),

  http.get(`${BASE}/projects/:projectId/twists/board`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const url = new URL(request.url);
    const kind = url.searchParams.get("kind") ?? undefined;
    return HttpResponse.json(buildTwistBoard(params.projectId as string, kind));
  }),

  http.post(`${BASE}/projects/:projectId/twists`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const body = (await request.json()) as TwistPlanCreateRequest;
    const now = new Date().toISOString();
    const twist: TwistPlan = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      title: body.title,
      secret_truth: body.secret_truth,
      status: "seeded",
      kind: body.kind ?? "twist",
      misdirection: body.misdirection ?? null,
      constraints_json: body.constraints_json ?? {},
      genre_strictness: body.genre_strictness ?? null,
      plant_count: 0,
      payoff: null,
      created_at: now,
      updated_at: now,
    };
    const list = getTwists(params.projectId as string);
    list.push(twist);
    mockPhase4Twists[params.projectId as string] = list;
    mockPhase4Plants[twist.id] = [];
    return HttpResponse.json(twist, { status: 201 });
  }),

  http.get(`${BASE}/projects/:projectId/twists/:twistId`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const twist = findTwist(params.projectId as string, params.twistId as string);
    if (!twist) return notFound();
    return HttpResponse.json(twist);
  }),

  http.patch(`${BASE}/projects/:projectId/twists/:twistId`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const twists = getTwists(params.projectId as string);
    const index = twists.findIndex((twist) => twist.id === params.twistId);
    if (index === -1) return notFound();
    if (twists[index].status === "paid_off") {
      return HttpResponse.json(
        { error: { code: "twist_paid_off_immutable", message: "Twist is paid off" } },
        { status: 409 },
      );
    }
    const body = (await request.json()) as TwistPlanUpdateRequest;
    twists[index] = {
      ...twists[index],
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(twists[index]);
  }),

  http.post(
    `${BASE}/projects/:projectId/twists/:twistId/transition`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const twist = findTwist(params.projectId as string, params.twistId as string);
      if (!twist) return notFound();
      const body = (await request.json()) as TwistTransitionRequest;
      if (body.status === "abandoned" && twist.status === "paid_off") {
        return HttpResponse.json(
          { error: { code: "twist_paid_off_immutable", message: "Twist is paid off" } },
          { status: 409 },
        );
      }
      twist.status = body.status;
      twist.updated_at = new Date().toISOString();
      return HttpResponse.json(twist);
    },
  ),

  http.get(`${BASE}/projects/:projectId/twists/:twistId/plants`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!findTwist(params.projectId as string, params.twistId as string)) return notFound();
    return HttpResponse.json({ items: mockPhase4Plants[params.twistId as string] ?? [] });
  }),

  http.post(`${BASE}/projects/:projectId/twists/:twistId/plants`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const twist = findTwist(params.projectId as string, params.twistId as string);
    if (!twist) return notFound();
    const body = (await request.json()) as TwistPlantCreateRequest;
    const now = new Date().toISOString();
    const plant = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      twist_id: params.twistId as string,
      chapter_id: body.chapter_id,
      chapter_number: chapterNumber(params.projectId as string, body.chapter_id),
      beat_id: body.beat_id ?? null,
      salience: body.salience ?? "soft",
      snippet: body.snippet,
      prose_span_start: body.prose_span_start ?? null,
      prose_span_end: body.prose_span_end ?? null,
      sort_order: body.sort_order ?? 0,
      created_at: now,
      updated_at: now,
    };
    const plants = mockPhase4Plants[params.twistId as string] ?? [];
    plants.push(plant);
    mockPhase4Plants[params.twistId as string] = plants;
    if (twist.status === "seeded") twist.status = "planted";
    syncTwistPlantCount(twist);
    twist.updated_at = now;
    return HttpResponse.json(plant, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/twists/:twistId/plants/:plantId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const plants = mockPhase4Plants[params.twistId as string] ?? [];
      const index = plants.findIndex((plant) => plant.id === params.plantId);
      if (index === -1) return notFound();
      const body = (await request.json()) as TwistPlantUpdateRequest;
      plants[index] = {
        ...plants[index],
        ...body,
        chapter_number: body.chapter_id
          ? chapterNumber(params.projectId as string, body.chapter_id)
          : plants[index].chapter_number,
        updated_at: new Date().toISOString(),
      };
      return HttpResponse.json(plants[index]);
    },
  ),

  http.delete(
    `${BASE}/projects/:projectId/twists/:twistId/plants/:plantId`,
    ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const twist = findTwist(params.projectId as string, params.twistId as string);
      const plants = mockPhase4Plants[params.twistId as string] ?? [];
      const index = plants.findIndex((plant) => plant.id === params.plantId);
      if (!twist || index === -1) return notFound();
      plants.splice(index, 1);
      syncTwistPlantCount(twist);
      return new HttpResponse(null, { status: 204 });
    },
  ),

  http.get(`${BASE}/projects/:projectId/twists/:twistId/payoffs`, ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!findTwist(params.projectId as string, params.twistId as string)) return notFound();
    const payoff = mockPhase4Payoffs[params.twistId as string];
    if (!payoff) return notFound();
    return HttpResponse.json(payoff);
  }),

  http.post(`${BASE}/projects/:projectId/twists/:twistId/payoffs`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    const twist = findTwist(params.projectId as string, params.twistId as string);
    if (!twist) return notFound();
    if (mockPhase4Payoffs[params.twistId as string]) {
      return HttpResponse.json(
        { error: { code: "payoff_already_exists", message: "Payoff already exists" } },
        { status: 422 },
      );
    }
    const body = (await request.json()) as TwistPayoffCreateRequest;
    const now = new Date().toISOString();
    const payoff = {
      id: crypto.randomUUID(),
      project_id: params.projectId as string,
      twist_id: params.twistId as string,
      target_chapter_id: body.target_chapter_id,
      target_chapter_number: chapterNumber(params.projectId as string, body.target_chapter_id),
      required_plant_ids: body.required_plant_ids ?? [],
      min_plants: body.min_plants ?? 1,
      revealed_at: null,
      created_at: now,
      updated_at: now,
    };
    mockPhase4Payoffs[params.twistId as string] = payoff;
    twist.status = "armed";
    syncTwistPayoffSummary(twist);
    twist.updated_at = now;
    return HttpResponse.json(payoff, { status: 201 });
  }),

  http.patch(
    `${BASE}/projects/:projectId/twists/:twistId/payoffs/:payoffId`,
    async ({ request, params }) => {
      if (!request.headers.get("X-User-Id")) return unauthorized();
      const payoff = mockPhase4Payoffs[params.twistId as string];
      if (!payoff || payoff.id !== params.payoffId) return notFound();
      const body = (await request.json()) as TwistPayoffUpdateRequest;
      Object.assign(payoff, {
        ...body,
        target_chapter_number: body.target_chapter_id
          ? chapterNumber(params.projectId as string, body.target_chapter_id)
          : payoff.target_chapter_number,
        updated_at: new Date().toISOString(),
      });
      const twist = findTwist(params.projectId as string, params.twistId as string);
      if (twist) syncTwistPayoffSummary(twist);
      return HttpResponse.json(payoff);
    },
  ),

  http.post(`${BASE}/projects/:projectId/context-packs/twists`, async ({ request, params }) => {
    if (!request.headers.get("X-User-Id")) return unauthorized();
    if (!projectExists(params.projectId as string)) return notFound();
    const body = (await request.json()) as { chapter_number: number; audience?: string };
    const audience = body.audience ?? "writer";
    const plants = Object.values(mockPhase4Plants)
      .flat()
      .filter((plant) => plant.chapter_number === body.chapter_number)
      .map((plant) => {
        const twist = Object.values(mockPhase4Twists)
          .flat()
          .find((item) => item.id === plant.twist_id);
        return {
          plant_id: plant.id,
          twist_id: plant.twist_id,
          twist_title: twist?.title ?? "",
          chapter_number: plant.chapter_number ?? body.chapter_number,
          salience: plant.salience,
          snippet: plant.snippet,
        };
      });
    const response = {
      twist_relevant: plants,
      meta: {
        audience,
        secret_truth_stripped: audience === "writer",
        plant_count: plants.length,
      },
    };
    return HttpResponse.json(response);
  }),
];
