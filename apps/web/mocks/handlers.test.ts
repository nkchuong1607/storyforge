import { describe, expect, it } from "vitest";
import { DEFAULT_USER_ID } from "@/lib/session";

const BASE = "http://localhost:8000";
const headers = { "X-User-Id": DEFAULT_USER_ID };

describe("MSW OpenAPI contract smoke", () => {
  it("GET /health", async () => {
    const res = await fetch(`${BASE}/health`);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ status: "ok" });
  });

  it("GET /projects requires auth", async () => {
    const res = await fetch(`${BASE}/projects`);
    expect(res.status).toBe(401);
  });

  it("GET /projects", async () => {
    const res = await fetch(`${BASE}/projects`, { headers });
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.items).toBeDefined();
    expect(body.pagination).toBeDefined();
  });

  it("GET /projects/:id returns 404 for unknown", async () => {
    const res = await fetch(`${BASE}/projects/00000000-0000-0000-0000-000000000000`, {
      headers,
    });
    expect(res.status).toBe(404);
  });

  it("GET chapters and characters", async () => {
    const projectId = "660e8400-e29b-41d4-a716-446655440001";
    const chapters = await fetch(`${BASE}/projects/${projectId}/chapters`, { headers });
    expect(chapters.status).toBe(200);
    const characters = await fetch(`${BASE}/projects/${projectId}/characters`, { headers });
    expect(characters.status).toBe(200);
  });

  it("POST /projects returns 409 on slug conflict", async () => {
    const res = await fetch(`${BASE}/projects`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Kiếm Lai",
        language: "vi",
        genre_profile: "xianxia",
        template: "blank",
      }),
    });
    expect(res.status).toBe(409);
  });
});
