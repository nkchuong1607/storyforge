import { describe, expect, it } from "vitest";
import { createTranslator } from "./i18n/get-messages";
import {
  formatDate,
  getBibleSectionLabel,
  getChapterStatusLabel,
  getCharacterStatusLabel,
  getCharacterTierLabel,
  getGenreLabel,
  getTemplateLabel,
  useLabelHelpers,
} from "./labels";

describe("labels", () => {
  it("returns vi genre labels", () => {
    expect(getGenreLabel("xianxia")).toBe("Tiên hiệp");
    expect(getGenreLabel("xianxia", "en")).toBe("Xianxia");
  });

  it("returns template labels", () => {
    expect(getTemplateLabel("blank")).toBe("Trống");
  });

  it("returns chapter status labels", () => {
    expect(getChapterStatusLabel("drafting")).toBe("Đang viết");
  });

  it("returns character labels", () => {
    expect(getCharacterStatusLabel("established")).toBe("Chính thức");
    expect(getCharacterTierLabel(1)).toBe("T1");
  });

  it("returns bible section labels with fallback", () => {
    expect(getBibleSectionLabel("world_rules")).toBe("Quy tắc thế giới");
    expect(getBibleSectionLabel("unknown_section")).toBe("unknown_section");
  });

  it("formats dates by locale", () => {
    expect(formatDate("2026-09-12T10:00:00Z", "en")).toBeTruthy();
    expect(formatDate("2026-09-12T10:00:00Z", "vi")).toBeTruthy();
  });

  it("useLabelHelpers returns all helpers", () => {
    const t = createTranslator("vi");
    const helpers = useLabelHelpers(t);
    expect(helpers.genre("mystery")).toBe("Trinh thám");
    expect(helpers.chapterStatus("locked")).toBe("Bị khóa");
    expect(helpers.continuityLevel("fail")).toBe("FAIL");
    expect(helpers.bibleSection("custom")).toBe("custom");
  });
});
