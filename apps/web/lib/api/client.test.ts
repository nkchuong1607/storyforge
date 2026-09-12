import { afterEach, describe, expect, it, vi } from "vitest";
import { apiFetch, ApiError, buildQuery, getApiBaseUrl } from "./client";

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("builds query strings", () => {
    expect(buildQuery({ page: 1, q: "test" })).toBe("?page=1&q=test");
    expect(buildQuery({ page: 1, q: undefined })).toBe("?page=1");
    expect(buildQuery()).toBe("");
  });

  it("returns default base url", () => {
    expect(getApiBaseUrl()).toBe("http://localhost:8000");
  });

  it("sends X-User-Id header", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [] }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiFetch("/projects", { userId: "test-user-id" });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/projects",
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get("X-User-Id")).toBe("test-user-id");
  });

  it("throws ApiError on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({
          error: { code: "not_found", message: "Missing" },
        }),
      }),
    );

    await expect(apiFetch("/projects/x")).rejects.toMatchObject({
      status: 404,
      code: "not_found",
      message: "Missing",
    });
  });

  it("returns undefined for 204", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
      }),
    );

    const result = await apiFetch<void>("/resource", { userId: "u" });
    expect(result).toBeUndefined();
  });

  it("ApiError exposes details", () => {
    const err = new ApiError(409, "slug_conflict", "Conflict", [{ suggested_slug: "x-2" }]);
    expect(err).toBeInstanceOf(Error);
    expect(err.details?.[0]?.suggested_slug).toBe("x-2");
  });
});
