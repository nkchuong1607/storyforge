const USER_ID_KEY = "storyforge-user-id";
export const DEFAULT_USER_ID = "550e8400-e29b-41d4-a716-446655440000";

export function getUserId(): string {
  if (typeof window === "undefined") {
    return DEFAULT_USER_ID;
  }
  const stored = localStorage.getItem(USER_ID_KEY);
  if (stored) {
    return stored;
  }
  localStorage.setItem(USER_ID_KEY, DEFAULT_USER_ID);
  return DEFAULT_USER_ID;
}

export function setUserId(userId: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(USER_ID_KEY, userId);
  }
}
