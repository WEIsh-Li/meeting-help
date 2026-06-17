import { Clipboard, FileText, Globe2, Pause, Play, Plus, RotateCcw, Send, Trash2, Upload } from "lucide-react";
import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { labels } from "./i18n";
import type { KnowledgeChunk, Lang, Meeting, Reply, Segment } from "./types";
import { canAddSegment, connectionErrorMessage } from "./uiState";

function App() {
  const [lang, setLang] = useState<Lang>("zh");
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [reply, setReply] = useState<Reply | null>(null);
  const [textEn, setTextEn] = useState("");
  const [speaker, setSpeaker] = useState("Other");
  const [knowledge, setKnowledge] = useState<KnowledgeChunk[]>([]);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const t = labels[lang];

  const pendingCount = useMemo(
    () => meeting?.segments.filter((segment) => !segment.submitted).length ?? 0,
    [meeting]
  );

  useEffect(() => {
    api.currentMeeting().then(setMeeting).catch((err) => setError(connectionErrorMessage(err.message, t.backendUnavailable)));
  }, [t.backendUnavailable]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (err) {
      setError(connectionErrorMessage(err instanceof Error ? err.message : String(err), t.backendUnavailable));
    } finally {
      setBusy(false);
    }
  }

  async function createMeeting() {
    await run(async () => {
      const next = await api.createMeeting(t.meeting);
      setMeeting(next);
      setReply(null);
    });
  }

  async function togglePause() {
    if (!meeting) return;
    await run(async () => {
      setMeeting(meeting.status === "paused" ? await api.resumeMeeting(meeting.id) : await api.pauseMeeting(meeting.id));
    });
  }

  async function endMeeting() {
    if (!meeting) return;
    await run(async () => setMeeting(await api.endMeeting(meeting.id)));
  }

  async function clearMeeting() {
    if (!meeting) return;
    await run(async () => {
      setMeeting(await api.clearMeeting(meeting.id));
      setReply(null);
    });
  }

  async function addSegment() {
    if (!meeting) {
      setError(t.backendUnavailable);
      return;
    }
    if (!textEn.trim()) return;
    await run(async () => {
      const segment = await api.addSegment(meeting.id, textEn, speaker);
      setMeeting({ ...meeting, segments: [...meeting.segments, segment] });
      setTextEn("");
    });
  }

  async function uploadKnowledge(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".txt") && !file.name.toLowerCase().endsWith(".md")) {
      setError(t.fileUnsupported);
      return;
    }
    await run(async () => {
      const content = await file.text();
      const chunks = await api.uploadKnowledge(file.name, content);
      setKnowledge((current) => [...current, ...chunks]);
    });
  }

  async function generateReply() {
    if (!meeting) return;
    await run(async () => {
      const result = await api.generateReply(meeting.id);
      setReply(result.reply);
      setMeeting(result.meeting);
    });
  }

  async function copyEnglish() {
    if (!reply?.answer_en) return;
    await navigator.clipboard.writeText(reply.answer_en);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  const segments = meeting?.segments ?? [];
  const firstSubmittedIndex = segments.findIndex((segment) => !segment.submitted);
  const submittedBoundary = firstSubmittedIndex <= 0 ? null : firstSubmittedIndex;

  return (
    <div className="app">
      <header className="topbar">
        <div className="identity">
          <div className="product-mark">MH</div>
          <div>
            <h1>{t.appName}</h1>
            <p>
              {meeting?.title ?? t.meeting} · {t.status}: {meeting ? t[meeting.status] : "-"} · {pendingCount} {t.pending}
            </p>
          </div>
        </div>
        <div className="actions">
          <button onClick={createMeeting} disabled={busy}>
            <Plus size={16} /> {t.newMeeting}
          </button>
          <button onClick={togglePause} disabled={busy || !meeting || meeting.status === "ended"}>
            {meeting?.status === "paused" ? <Play size={16} /> : <Pause size={16} />}{" "}
            {meeting?.status === "paused" ? t.resume : t.pause}
          </button>
          <button onClick={endMeeting} disabled={busy || !meeting || meeting.status === "ended"}>
            <RotateCcw size={16} /> {t.end}
          </button>
          <button onClick={clearMeeting} disabled={busy || !meeting}>
            <Trash2 size={16} /> {t.clear}
          </button>
          <label className="upload-button">
            <Upload size={16} /> {t.uploadKb}
            <input type="file" accept=".txt,.md" onChange={uploadKnowledge} />
          </label>
          <button className="primary" onClick={generateReply} disabled={busy || !meeting || pendingCount === 0}>
            <Send size={16} /> {t.generate}
          </button>
          <button onClick={() => setLang(lang === "zh" ? "en" : "zh")}>
            <Globe2 size={16} /> {t.language}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <strong>{t.error}</strong>
          <span>{error}</span>
        </div>
      )}

      <main className="workspace">
        <section className="pane transcript-pane">
          <div className="pane-heading">
            <div>
              <h2>{t.transcript}</h2>
              <p>{t.privacyNotice}</p>
            </div>
            <span className="status-pill">{pendingCount} {t.pending}</span>
          </div>

          <div className="segments">
            {segments.length === 0 && <div className="empty">{t.emptyTranscript}</div>}
            {segments.map((segment, index) => (
              <div key={segment.id}>
                {submittedBoundary === index && <div className="submitted-divider">{t.submittedDivider}</div>}
                <SegmentCard segment={segment} submittedLabel={t.submitted} pendingLabel={t.pending} />
              </div>
            ))}
          </div>

          <div className="composer">
            <input value={speaker} onChange={(event) => setSpeaker(event.target.value)} aria-label={t.speaker} />
            <textarea
              value={textEn}
              onChange={(event) => setTextEn(event.target.value)}
              rows={4}
              placeholder={t.inputPlaceholder}
            />
            <button
              className="primary"
              onClick={addSegment}
              disabled={!canAddSegment({ busy, meetingLoaded: Boolean(meeting), text: textEn })}
              title={!meeting ? t.backendUnavailable : undefined}
            >
              <Plus size={16} /> {t.addSegment}
            </button>
          </div>
        </section>

        <section className="pane reply-pane">
          <div className="pane-heading">
            <div>
              <h2>{t.aiReply}</h2>
              <p>{t.modelNotice}</p>
            </div>
            <span className="status-pill">
              <FileText size={14} /> {knowledge.length} {t.kbLoaded}
            </span>
          </div>

          {!reply && <div className="empty">{t.emptyReply}</div>}
          {reply && (
            <div className="reply-grid">
              <InfoBlock label={t.intent} value={`${reply.intent} · ${reply.need_response ? "response" : "no response"}`} />
              <InfoBlock label={t.understanding} value={reply.summary_cn} />
              <InfoBlock label={t.strategy} value={reply.strategy_cn} />
              <InfoBlock label={t.answerCn} value={reply.answer_cn} />
              <div className="info-block accent-block">
                <div className="info-label">{t.answerEn}</div>
                <p>{reply.answer_en}</p>
                <button onClick={copyEnglish}>
                  <Clipboard size={16} /> {copied ? t.copied : t.copyEnglish}
                </button>
              </div>
              <InfoBlock label={t.shortAnswer} value={reply.short_answer_en} />
              <InfoBlock label={t.followUp} value={reply.follow_up_question_en} />
              <InfoBlock
                label={t.knowledge}
                value={reply.knowledge_used.length ? reply.knowledge_used.map((item) => item.source).join(", ") : "-"}
              />
              <InfoBlock label={t.confidence} value={reply.confidence} />
            </div>
          )}

          <div className="follow-up">
            <input disabled placeholder={t.followUpDisabled} />
          </div>
        </section>
      </main>
    </div>
  );
}

function SegmentCard({
  segment,
  submittedLabel,
  pendingLabel
}: {
  segment: Segment;
  submittedLabel: string;
  pendingLabel: string;
}) {
  return (
    <article className={`segment-card ${segment.submitted ? "submitted" : "pending"}`}>
      <div className="segment-meta">
        <span>{segment.speaker}</span>
        <span>{formatTime(segment.start_time)}</span>
        <span>{segment.submitted ? submittedLabel : pendingLabel}</span>
      </div>
      <p className="segment-en">{segment.text_en}</p>
      <p className="segment-cn">{segment.text_cn_local}</p>
    </article>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-block">
      <div className="info-label">{label}</div>
      <p>{value}</p>
    </div>
  );
}

function formatTime(seconds: number) {
  const mins = Math.floor(seconds / 60).toString().padStart(2, "0");
  const secs = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${mins}:${secs}`;
}

export default App;
