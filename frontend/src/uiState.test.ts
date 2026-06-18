import { describe, expect, it } from "vitest";
import { labels } from "./i18n";
import { canAddSegment, canStartLiveTranscription, canUploadAudio, connectionErrorMessage } from "./uiState";

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

  it("allows audio upload only with a loaded meeting and selected file", () => {
    expect(canUploadAudio({ busy: false, meetingLoaded: true, hasFile: true })).toBe(true);
    expect(canUploadAudio({ busy: false, meetingLoaded: false, hasFile: true })).toBe(false);
    expect(canUploadAudio({ busy: false, meetingLoaded: true, hasFile: false })).toBe(false);
    expect(canUploadAudio({ busy: true, meetingLoaded: true, hasFile: true })).toBe(false);
  });

  it("starts live transcription only when meeting is loaded and recorder is idle", () => {
    expect(canStartLiveTranscription({ busy: false, meetingLoaded: true, isLiveTranscribing: false })).toBe(true);
    expect(canStartLiveTranscription({ busy: false, meetingLoaded: false, isLiveTranscribing: false })).toBe(false);
    expect(canStartLiveTranscription({ busy: true, meetingLoaded: true, isLiveTranscribing: false })).toBe(false);
    expect(canStartLiveTranscription({ busy: false, meetingLoaded: true, isLiveTranscribing: true })).toBe(false);
  });

  it("keeps Chinese UI labels readable", () => {
    expect(labels.zh.addSegment).toBe("添加片段");
    expect(labels.zh.uploadAudio).toBe("上传音频");
    expect(labels.zh.startLive).toBe("开始实时转写");
    expect(labels.zh.language).toBe("English");
    expect(labels.en.language).toBe("中文");
  });
});
