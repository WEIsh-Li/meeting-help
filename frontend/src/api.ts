import type { KnowledgeChunk, Meeting, Reply, Segment, TranscriptionResult } from "./types";

const API_BASE = "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const isFormData = options?.body instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...(options?.headers ?? {}) },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  currentMeeting: () => request<Meeting>("/api/meeting/current"),
  createMeeting: (title: string) =>
    request<Meeting>("/api/meeting/create", {
      method: "POST",
      body: JSON.stringify({ title })
    }),
  pauseMeeting: (meetingId: string) =>
    request<Meeting>(`/api/meeting/pause/${meetingId}`, { method: "POST" }),
  resumeMeeting: (meetingId: string) =>
    request<Meeting>(`/api/meeting/resume/${meetingId}`, { method: "POST" }),
  endMeeting: (meetingId: string) =>
    request<Meeting>(`/api/meeting/end/${meetingId}`, { method: "POST" }),
  clearMeeting: (meetingId: string) =>
    request<Meeting>(`/api/meeting/clear/${meetingId}`, { method: "POST" }),
  addSegment: (meetingId: string, textEn: string, speaker: string) =>
    request<Segment>("/api/segments", {
      method: "POST",
      body: JSON.stringify({ meeting_id: meetingId, text_en: textEn, speaker })
    }),
  uploadKnowledge: (filename: string, content: string) =>
    request<KnowledgeChunk[]>("/api/kb/upload", {
      method: "POST",
      body: JSON.stringify({ filename, content })
    }),
  transcribeAudio: (meetingId: string, file: File) => {
    const form = new FormData();
    form.append("meeting_id", meetingId);
    form.append("file", file);
    return request<TranscriptionResult>("/api/speech/transcribe", {
      method: "POST",
      body: form
    });
  },
  generateReply: (meetingId: string) =>
    request<{ reply: Reply; submitted_segment_ids: string[]; meeting: Meeting }>("/api/ai/generate-reply", {
      method: "POST",
      body: JSON.stringify({ meeting_id: meetingId })
    })
};
