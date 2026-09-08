// The run state triple, and the state → display-label mapping.
//
// `contracts/http/openapi.yaml` answers `run.list` / `run.get` / `delivery.get_status`
// with `GenericObject` and `x-schema-source: contracts/state/run.yaml` — that is, the wire
// shape is deliberately open and the *semantics* live in the state contracts, which are
// YAML, not JSON Schema, so the generator has nothing to emit for the body. The unions
// below are therefore not a second copy of a generated type; they are this card's reading
// of `contracts/state/*.yaml §enums`, and `web/tests/contract/runReadModel.test.ts` reads
// those YAML files at test time and fails when a value here and a value there disagree.
// See CR-TC-uiruns-02.
//
// The one rule this file exists to enforce (I13, SRC-SPEC §8.3, REQ-AC15): "collected
// nothing", "stopped at a limit" and "failed" are three different facts and must produce
// three different strings — and none of them may be the phrase the spec forbids.

// ---------------------------------------------------------------------------------
// 1. Enums — contracts/state/run.yaml §enums
// ---------------------------------------------------------------------------------

export const RUN_PHASES = ['collecting', 'enriching', 'analyzing', 'reporting'] as const;
export type RunPhase = (typeof RUN_PHASES)[number];

export const RUN_STATUSES = [
  'queued',
  'running',
  'waiting_retry',
  'needs_user',
  'blocked',
  'completed',
  'failed',
  'cancelled',
] as const;
export type RunStatus = (typeof RUN_STATUSES)[number];

export const RUN_OUTCOMES = ['complete', 'partial', 'empty', 'failed', 'cancelled'] as const;
export type RunOutcome = (typeof RUN_OUTCOMES)[number];

export const STOP_REASONS = [
  'limit_reached',
  'captcha',
  'session_expired',
  'source_blocked',
  'storage_unavailable',
  'worker_lost',
  'source_layout_changed',
  'rate_limited',
] as const;
export type StopReason = (typeof STOP_REASONS)[number];

export const TRIGGER_TYPES = ['scheduled', 'manual'] as const;
export type TriggerType = (typeof TRIGGER_TYPES)[number];

/** `contracts/state/run.yaml §terminal_states`. */
export const TERMINAL_RUN_STATUSES = ['completed', 'failed', 'cancelled'] as const;

// contracts/state/delivery.yaml §enums
export const DELIVERY_STATES = [
  'pending',
  'sending',
  'sent',
  'retry_wait',
  'unknown',
  'failed',
  'cancelled',
] as const;
export type DeliveryState = (typeof DELIVERY_STATES)[number];

export const DELIVERY_PART_STATES = ['pending', 'sending', 'sent', 'unknown', 'failed'] as const;
export type DeliveryPartState = (typeof DELIVERY_PART_STATES)[number];

export const UNKNOWN_DECISIONS = [
  'resend_accepting_duplicate_risk',
  'mark_not_delivered',
  'abandon',
] as const;
export type UnknownDecision = (typeof UNKNOWN_DECISIONS)[number];

// contracts/state/storage.yaml §enums
export const STORAGE_HEALTHS = [
  'healthy',
  'write_blocked',
  'maintenance',
  'recovery_required',
] as const;
export type StorageHealth = (typeof STORAGE_HEALTHS)[number];

/** `contracts/data/entities.yaml ENT-worker-registration.online_state`. */
export const COLLECTOR_ONLINE_STATES = ['online', 'offline', 'unknown'] as const;
export type CollectorOnlineState = (typeof COLLECTOR_ONLINE_STATES)[number];

/** `contracts/ui/screens.yaml §global_rules.five_display_states`. */
export const DISPLAY_STATES = ['loading', 'empty', 'partial', 'error', 'stale_last_known'] as const;
export type DisplayState = (typeof DISPLAY_STATES)[number];

/**
 * The five above are the states the contract requires every screen to DEFINE; they are
 * the exceptional ones. `ready` is the ordinary populated render, named here only so the
 * read model's field is total and no screen has to encode "none of the five" as `null`.
 * It carries no display string of its own.
 */
export type ScreenDisplayState = DisplayState | 'ready';

// ---------------------------------------------------------------------------------
// 2. The triple
// ---------------------------------------------------------------------------------

/**
 * The three fields REQ-AC15 is decided by.
 *
 * `contracts/state/run.yaml §legacy_enum_mapping.ui_three_states_vi`: "Ba trạng thái của
 * SRC-SPEC §8.3 / REQ-AC15 phân biệt bằng BỘ BA (status, outcome, stop_reason), không
 * bằng một enum". `stop_reason` is independent of `status` (AMD-B02): `completed` with
 * `limit_reached` is a normal, common combination and is NOT a failure.
 */
export interface RunStateTriple {
  status: RunStatus;
  outcome: RunOutcome | null;
  stop_reason: StopReason | null;
}

export type RunStatusLabelId = 'no_matching_content' | 'stopped_early' | 'run_failed';

export interface RunStatusLabel {
  id: RunStatusLabelId;
  /** Verbatim from `contracts/ui/screens.yaml §global_rules.run_status_labels`. */
  label_vi: string;
}

/**
 * The label table, copied verbatim from
 * `contracts/ui/screens.yaml §global_rules.run_status_labels`, in the order the contract
 * lists it. `runReadModel.test.ts` re-reads that file and asserts the strings are equal.
 */
export const RUN_STATUS_LABELS: Readonly<Record<RunStatusLabelId, RunStatusLabel>> = {
  no_matching_content: { id: 'no_matching_content', label_vi: 'Không có nội dung phù hợp' },
  stopped_early: { id: 'stopped_early', label_vi: 'Đợt dừng sớm' },
  run_failed: { id: 'run_failed', label_vi: 'Đợt thất bại' },
};

/**
 * SRC-SPEC §8.3 forbids this phrase outright, on every screen, including empty states
 * (`screens.yaml §run_status_labels.forbidden_globally`). It is exported so tests can
 * grep the app's own strings for it.
 */
export const FORBIDDEN_RUN_LABEL_VI = 'Không có nghiên cứu mới';

/** The stop reasons `screens.yaml` puts in the `stopped_early` condition. */
const STOPPED_EARLY_STOP_REASONS: readonly StopReason[] = [
  'limit_reached',
  'captcha',
  'session_expired',
  'source_blocked',
];

/**
 * State triple → the label of `screens.yaml §global_rules.run_status_labels`, or `null`
 * when the contract's table names no label for that triple.
 *
 * Two defects in the table, both reported as CR-TC-uiruns-01, both handled
 * here WITHOUT inventing a display string (card §10 SG-01: "không tự đặt nhãn hiển thị"):
 *
 * (a) The three `condition` expressions OVERLAP and no precedence is stated — unlike
 *     `delivery_status_labels`, which cites DP-03 explicitly. `(failed, failed,
 *     source_blocked)` satisfies both `stopped_early` and `run_failed`; `(completed,
 *     empty, limit_reached)` satisfies both `no_matching_content` and `stopped_early`.
 *     Order used, which is the only one both oracles allow:
 *
 *       run_failed  >  stopped_early  >  no_matching_content
 *
 *      - `run_failed` first: the fixture decides it. `acceptance/fixtures/telegram/
 *        m-three-run-states-distinct-text.json` run `01JRVNC…` is `(failed, failed,
 *        source_blocked)` and its `expected.ui_labels` entry is "Đợt thất bại".
 *      - `stopped_early` before `no_matching_content`: I13. A run that stopped at a limit
 *        did not finish looking, so calling it "không có nội dung phù hợp" would report
 *        missing data as an established absence — the exact counterexample I13 names.
 *
 *     The order changes nothing for the three triples of REQ-AC15, which are unambiguous.
 *
 * (b) The table is INCOMPLETE with respect to `contracts/state/run.yaml §enums.status`:
 *     `queued`, `running`, `waiting_retry`, `cancelled`, and a plain successful
 *     `(completed, complete, null)` match none of the three conditions. This function
 *     returns `null` for them and the read model falls back to the machine value of
 *     `status`, which is data the server sent, not copy this card wrote. Labelling those
 *     states is a contract change, not a UI decision.
 */
export function runStatusLabel(triple: RunStateTriple): RunStatusLabel | null {
  if (triple.status === 'failed') return RUN_STATUS_LABELS.run_failed;
  if (
    triple.status === 'needs_user' ||
    triple.status === 'blocked' ||
    (triple.stop_reason !== null && STOPPED_EARLY_STOP_REASONS.includes(triple.stop_reason))
  ) {
    return RUN_STATUS_LABELS.stopped_early;
  }
  if (triple.status === 'completed' && triple.outcome === 'empty') {
    return RUN_STATUS_LABELS.no_matching_content;
  }
  return null;
}

// ---------------------------------------------------------------------------------
// 3. needs_user vs blocked — same label, different obligations
// ---------------------------------------------------------------------------------

/**
 * What a run needs from the owner, if anything.
 *
 * `needs_user` and `blocked` share the `stopped_early` label in `screens.yaml`, so the
 * screen must separate them by what it OFFERS, not by the label: `screens.yaml`
 * `ACT-resume-run` is `visible_when: run.status = needs_user`, and `blocked` instead
 * carries `run.unblock_condition_vi` (`contracts/state/run.yaml §fields.added_by_pc03`:
 * NOT NULL when `status = blocked`). This card invents no Vietnamese copy for either: the
 * resume affordance is the contract's own action label, and the unblock text is a value
 * the server stores on the run.
 */
export interface RunAttention {
  /** `screens.yaml` ACT-resume-run / ACT-resume-run-detail. */
  resume_available: boolean;
  /** The server's own sentence; only a `blocked` run has one. */
  unblock_condition_vi: string | null;
}

export function runAttention(
  triple: RunStateTriple,
  unblockConditionVi: string | null,
): RunAttention {
  return {
    resume_available: triple.status === 'needs_user',
    unblock_condition_vi: triple.status === 'blocked' ? unblockConditionVi : null,
  };
}

// ---------------------------------------------------------------------------------
// 4. Delivery labels — a fourth, independent dimension (I09, I13)
// ---------------------------------------------------------------------------------

export type DeliveryStatusLabelId =
  | 'delivery_sent'
  | 'delivery_pending'
  | 'delivery_unknown'
  | 'delivery_failed'
  | 'delivery_cancelled';

export interface DeliveryStatusLabel {
  id: DeliveryStatusLabelId;
  /** Verbatim from `screens.yaml §global_rules.delivery_status_labels`. */
  label_vi: string;
}

export const DELIVERY_STATUS_LABELS: Readonly<Record<DeliveryStatusLabelId, DeliveryStatusLabel>> =
  {
    delivery_sent: { id: 'delivery_sent', label_vi: 'Đã gửi Telegram' },
    delivery_pending: { id: 'delivery_pending', label_vi: 'Đang chờ gửi' },
    delivery_unknown: { id: 'delivery_unknown', label_vi: 'Chưa xác định — có thể đã gửi' },
    delivery_failed: { id: 'delivery_failed', label_vi: 'Không gửi được' },
    delivery_cancelled: { id: 'delivery_cancelled', label_vi: 'Đã hủy (liên kết đổi)' },
  };

/**
 * `unknown` must never be shown as `sent` or `failed` (I13, AMD-B03), and delivery state
 * must never be folded into the run label (I09): a Telegram failure does not make a
 * collection run fail.
 */
export function deliveryStatusLabel(state: DeliveryState): DeliveryStatusLabel {
  switch (state) {
    case 'sent':
      return DELIVERY_STATUS_LABELS.delivery_sent;
    case 'pending':
    case 'sending':
    case 'retry_wait':
      return DELIVERY_STATUS_LABELS.delivery_pending;
    case 'unknown':
      return DELIVERY_STATUS_LABELS.delivery_unknown;
    case 'failed':
      return DELIVERY_STATUS_LABELS.delivery_failed;
    case 'cancelled':
      return DELIVERY_STATUS_LABELS.delivery_cancelled;
  }
}

/**
 * DP-03 precedence, verbatim: `unknown > failed > retry_wait > sending > pending > sent`
 * — "the state that needs attention most wins, so the UI never says 'đã gửi' while one
 * part is still unresolved". `cancelled` is not in that list because DP-03 defines it
 * separately (the intent was cancelled before any part was `sent`); it is ranked last so
 * that any live part outranks it.
 */
export const DELIVERY_STATE_PRECEDENCE: readonly DeliveryState[] = [
  'unknown',
  'failed',
  'retry_wait',
  'sending',
  'pending',
  'sent',
  'cancelled',
];

/** Aggregate state derived from parts (DP-03: the aggregate is derived, never stored truth). */
export function aggregateDeliveryState(parts: readonly DeliveryPartState[]): DeliveryState | null {
  let best: DeliveryState | null = null;
  let bestRank = Number.POSITIVE_INFINITY;
  for (const part of parts) {
    const rank = DELIVERY_STATE_PRECEDENCE.indexOf(part);
    if (rank >= 0 && rank < bestRank) {
      bestRank = rank;
      best = part;
    }
  }
  return best;
}

// ---------------------------------------------------------------------------------
// 5. Storage health — the fifth, independent dimension (UI-01..UI-04)
// ---------------------------------------------------------------------------------

export interface StorageNotice {
  /** True when the screen must label its data as last-known (UI-02). */
  last_known: boolean;
  /** Reason text for the disabled mutation buttons (UI-03); `null` when healthy. */
  reason_vi: string | null;
}

/**
 * `contracts/state/storage.yaml §ui_read_model`:
 *   UI-01 every business screen carries `as_of` and `storage_health`;
 *   UI-02 when not healthy, data is LAST-KNOWN and must say so, with `as_of`;
 *   UI-03 mutation buttons are explicitly disabled WITH a readable reason, never silently
 *         inert;
 *   UI-04 storage health is a fifth dimension: a `completed/empty` run read during
 *         `write_blocked` is still `empty`.
 *
 * The sentence is a rendering of UI-02's own wording plus the two machine values; it is
 * not a new display label (the card forbids inventing those, SG-01).
 *
 * `health` is nullable because the running server does not send it: the recorded bodies of
 * `run.list` and `run.get` (see `threeStatesDistinct.test.ts` §RECORDED) carry neither
 * `storage_health` nor `as_of`, which UI-01 requires of every business screen. A missing
 * value is reported as missing — it is NOT read as `healthy`, because "we were not told"
 * and "the database is fine" are exactly the two things I13 forbids merging.
 */
export function storageNotice(health: StorageHealth | null, asOf: string | null): StorageNotice {
  if (health === null || health === 'healthy') return { last_known: false, reason_vi: null };
  const at = asOf ?? 'không rõ';
  return {
    last_known: true,
    reason_vi: `Dữ liệu last-known đọc lúc ${at}; storage_health = ${health}; các thay đổi mới chưa lưu được.`,
  };
}

// ---------------------------------------------------------------------------------
// 6. Error obligations — card §7
// ---------------------------------------------------------------------------------

export interface ErrorObligation {
  /** Navigate here, or `null` to stay on the screen. */
  redirect_to: 'SCR-login' | 'SCR-not-found' | null;
  /** False only for `UNAUTHORIZED`: `CSRF_REJECTED` must NOT log the user out. */
  end_session: boolean;
  /** Banner headline; `null` means "render the envelope's `message_safe` alone". */
  banner_vi: string | null;
}

/**
 * Card §7. The user-facing sentence always comes from the envelope's `message_safe`
 * (server-rendered from `contracts/errors.yaml`); this table only decides the BEHAVIOUR,
 * plus the one banner headline the card names in words ("chưa lưu được").
 */
export const ERROR_OBLIGATIONS: Readonly<Record<string, ErrorObligation>> = {
  UNAUTHORIZED: { redirect_to: 'SCR-login', end_session: true, banner_vi: null },
  CSRF_REJECTED: { redirect_to: null, end_session: false, banner_vi: null },
  NOT_FOUND: { redirect_to: 'SCR-not-found', end_session: false, banner_vi: null },
  STORAGE_WRITE_FAILED: { redirect_to: null, end_session: false, banner_vi: 'Chưa lưu được' },
};

export const DEFAULT_ERROR_OBLIGATION: ErrorObligation = {
  redirect_to: null,
  end_session: false,
  banner_vi: null,
};

export function errorObligation(code: string | null): ErrorObligation {
  if (code === null) return DEFAULT_ERROR_OBLIGATION;
  return ERROR_OBLIGATIONS[code] ?? DEFAULT_ERROR_OBLIGATION;
}

// ---------------------------------------------------------------------------------
// 7. Narrowing helpers for the open wire shape
// ---------------------------------------------------------------------------------

/**
 * The 200 bodies of `run.list`, `run.get` and `delivery.get_status` are `GenericObject` in
 * the wire contract, so the generated types give `Record<string, unknown>` and every field
 * has to be narrowed before it can be displayed. Reading an absent or wrong-typed field as
 * `null` (rather than coercing it) is what lets the read model report "missing" instead of
 * quietly showing a default — I13 again, one layer down.
 */
export function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export function asArray(value: unknown): readonly unknown[] {
  return Array.isArray(value) ? (value as readonly unknown[]) : [];
}

export function asString(value: unknown): string | null {
  return typeof value === 'string' && value !== '' ? value : null;
}

export function asInteger(value: unknown): number | null {
  return typeof value === 'number' && Number.isInteger(value) ? value : null;
}

function member<T extends string>(values: readonly T[], value: unknown): T | null {
  return typeof value === 'string' && (values as readonly string[]).includes(value)
    ? (value as T)
    : null;
}

export const asRunStatus = (v: unknown): RunStatus | null => member(RUN_STATUSES, v);
export const asRunOutcome = (v: unknown): RunOutcome | null => member(RUN_OUTCOMES, v);
export const asStopReason = (v: unknown): StopReason | null => member(STOP_REASONS, v);
export const asRunPhase = (v: unknown): RunPhase | null => member(RUN_PHASES, v);
export const asTriggerType = (v: unknown): TriggerType | null => member(TRIGGER_TYPES, v);
export const asDeliveryState = (v: unknown): DeliveryState | null => member(DELIVERY_STATES, v);
export const asDeliveryPartState = (v: unknown): DeliveryPartState | null =>
  member(DELIVERY_PART_STATES, v);
export const asStorageHealth = (v: unknown): StorageHealth | null => member(STORAGE_HEALTHS, v);
export const asCollectorOnlineState = (v: unknown): CollectorOnlineState | null =>
  member(COLLECTOR_ONLINE_STATES, v);
