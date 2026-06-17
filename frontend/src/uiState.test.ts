import { describe, expect, it } from "vitest";
import { canAddSegment, connectionErrorMessage } from "./uiState";

describe("ui state guards", () => {
  it("prevents add segment when meeting has not loaded", () => {
    expect(canAddSegment({ busy: false, meetingLoaded: false, text: "hello" })).toBe(false);
  });

  it("allows add segment only with loaded meeting and non-empty text", () => {
    expect(canAddSegment({ busy: false, meetingLoaded: true, text: "hello" })).toBe(true);
    expect(canAddSegment({ busy: false, meetingLoaded: true, text: "   " })).toBe(false);
    expect(canAddSegment({ busy: true, meetingLoaded: true, text: "hello" })).toBe(false);
  });

  it("formats backend connection failures as actionable text", () => {
    expect(connectionErrorMessage("Failed to fetch")).toContain("backend");
  });
});

