import { afterEach, describe, expect, it } from "vitest";
import { DEFAULT_USER_ID, getUserId, setUserId } from "./session";

describe("session", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns default user id when unset", () => {
    expect(getUserId()).toBe(DEFAULT_USER_ID);
    expect(localStorage.getItem("storyforge-user-id")).toBe(DEFAULT_USER_ID);
  });

  it("persists custom user id", () => {
    setUserId("custom-user");
    expect(getUserId()).toBe("custom-user");
  });
});
