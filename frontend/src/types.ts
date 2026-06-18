export type Lang = "zh" | "en";

export interface Segment {
  id: string;
  meeting_id: string;
  source: string;
  speaker: string;
  text_en: string;
  text_cn_local: string;
  start_time: number;
  end_time: number;
  submitted: boolean;
  created_at: string;
}

export interface Meeting {
  id: string;
  title: string;
  status: "active" | "paused" | "ended";
  summary: string;
  segments: Segment[];
  created_at: string;
  ended_at: string | null;
}

export interface KnowledgeChunk {
  id: string;
  source: string;
  content: string;
  chunk_index: number;
  score: number;
}

export interface Reply {
  intent: string;
  need_response: boolean;
  summary_cn: string;
  strategy_cn: string;
  answer_cn: string;
  answer_en: string;
  short_answer_en: string;
  follow_up_question_en: string;
  knowledge_used: Array<{ source: string; reason: string }>;
  confidence: string;
}

export interface TranscriptionResult {
  transcript_en: string;
  segment: Segment;
  meeting: Meeting;
}
