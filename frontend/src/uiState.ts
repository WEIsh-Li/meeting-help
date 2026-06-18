export interface AddSegmentState {
  busy: boolean;
  meetingLoaded: boolean;
  text: string;
}

export interface UploadAudioState {
  busy: boolean;
  meetingLoaded: boolean;
  hasFile: boolean;
}

export function canAddSegment(state: AddSegmentState): boolean {
  return !state.busy && state.meetingLoaded && state.text.trim().length > 0;
}

export function canUploadAudio(state: UploadAudioState): boolean {
  return !state.busy && state.meetingLoaded && state.hasFile;
}

export function connectionErrorMessage(message: string, fallback = "Cannot connect to backend API. Start FastAPI at http://127.0.0.1:8000, then refresh this page."): string {
  const normalized = message.toLowerCase();
  if (
    normalized.includes("failed to fetch") ||
    normalized.includes("load failed") ||
    normalized.includes("networkerror") ||
    normalized.includes("无法连接") ||
    normalized.includes("connection")
  ) {
    return fallback;
  }
  return message;
}
