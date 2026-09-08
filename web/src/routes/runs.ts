// Read model for `SCR-runs` (contracts/ui/screens.yaml).
//
// A read model, not a component: it turns the two source operations of the screen —
// `run.list` and `worker.get_status` — into exactly the fields `screens.yaml` names, and
// decides which of the five display states the screen is in. `RunsList.tsx` renders it and
// makes no decisions of its own, so the whole of REQ-AC15 is testable by string
// comparison without rendering anything (card §8: "so sánh chuỗi, không so ảnh").

import { useQuery } from '@tanstack/react-query';

import type { ApiClient } from '../lib/api';
import { ApiError } from '../lib/api';
import type {
  CollectorOnlineState,
  DeliveryState,
  ScreenDisplayState,
  RunAttention,
  RunOutcome,
  RunPhase,
  RunStateTriple,
  RunStatus,
  RunStatusLabel,
  StopReason,
  StorageHealth,
  StorageNotice,
  TriggerType,
} from '../lib/runState';
import {
  TERMINAL_RUN_STATUSES,
  asCollectorOnlineState,
  asDeliveryState,
  asInteger,
  asRecord,
  asRunOutcome,
  asRunPhase,
  asRunStatus,
  asStopReason,
  asString,
  asStorageHealth,
  asTriggerType,
  asArray,
  errorObligation,
  runAttention,
  runStatusLabel,
  storageNotice,
} from '../lib/runState';

// ---------------------------------------------------------------------------------
// Actions — copied from `screens.yaml` §screens[SCR-runs].actions
// ---------------------------------------------------------------------------------

export interface ScreenAction {
  id: string;
  label_vi: string;
  operation_id: string;
  /** `screens.yaml` `mobile:` on the action itself. */
  mobile: boolean;
}

/**
 * The complete action map of the screen. Card §8: "Mọi hành động trên màn hình đều có
 * trong action map của `contracts/ui/screens.yaml`" — the view may only render actions
 * from this list, and `runReadModel.test.ts` checks the list against the contract.
 */
export const SCR_RUNS_ACTIONS = {
  runNow: {
    id: 'ACT-run-now-from-runs',
    label_vi: 'Chạy ngay',
    operation_id: 'run.run_now',
    mobile: true,
  },
  resume: {
    id: 'ACT-resume-run',
    label_vi: 'Tiếp tục run đang chờ',
    operation_id: 'run.resume',
    mobile: false,
  },
  cancel: {
    id: 'ACT-cancel-run',
    label_vi: 'Hủy run',
    operation_id: 'run.cancel',
    mobile: false,
  },
  openDetail: {
    id: 'ACT-open-run-detail',
    label_vi: 'Mở chi tiết',
    operation_id: 'run.get',
    mobile: true,
  },
} as const satisfies Readonly<Record<string, ScreenAction>>;

// ---------------------------------------------------------------------------------
// Row and screen shapes
// ---------------------------------------------------------------------------------

export interface RunProgress {
  /** `checkpoint.acked_through_ingest_sequence`; `null` when the run has no checkpoint. */
  acked_through_ingest_sequence: number | null;
  posts_ingested_new: number | null;
  posts_observed_total: number | null;
}

export interface RunRow {
  id: string;
  triple: RunStateTriple;
  status: RunStatus;
  outcome: RunOutcome | null;
  stop_reason: StopReason | null;
  phase: RunPhase | null;
  trigger_type: TriggerType | null;
  progress: RunProgress | null;
  /**
   * `screens.yaml`: "Kỳ rỗng KHÔNG có report nhưng CÓ coverage record — hiện ở đây
   * (REQ-D57, AMD-B04)."
   */
  empty_period_note: string | null;
  /** `contracts/state/run.yaml`: NOT NULL when `status = blocked`. */
  unblock_condition_vi: string | null;
  /** `null` when `screens.yaml §run_status_labels` names no label — see runState.ts. */
  status_label: RunStatusLabel | null;
  attention: RunAttention;
  /** Shown in its own column; NEVER folded into the run label (I09). */
  delivery_state: DeliveryState | null;
  is_terminal: boolean;
  /** Actions this row may offer, already filtered by state and storage health. */
  actions: readonly ScreenAction[];
  /** UI-03: why the actions above are disabled, or `null` when they are live. */
  actions_disabled_reason_vi: string | null;
}

export interface RunsReadModel {
  display_state: ScreenDisplayState;
  /** `unknown` is NOT rendered as `offline` (I13, screens.yaml). */
  collector_online_state: CollectorOnlineState | null;
  /** Display only; never a filter boundary (REQ-D12). */
  last_run_at: string | null;
  runs: readonly RunRow[];
  /** UI-01: always present in the model. `null` means the server did not send it. */
  as_of: string | null;
  /** `null` when the body carried no `storage_health` — never silently read as healthy. */
  storage_health: StorageHealth | null;
  storage: StorageNotice;
  /** Present only in the `error` display state. */
  error_code: string | null;
  error_message_safe: string | null;
  error_redirect_to: 'SCR-login' | 'SCR-not-found' | null;
}

// ---------------------------------------------------------------------------------
// Parsing
// ---------------------------------------------------------------------------------

function parseProgress(raw: Record<string, unknown>): RunProgress | null {
  const progress = asRecord(raw['progress']);
  const acked = progress === null ? null : asInteger(progress['acked_through_ingest_sequence']);
  const ingested = asInteger(raw['posts_ingested_new']);
  const observed = asInteger(raw['posts_observed_total']);
  if (acked === null && ingested === null && observed === null) return null;
  return {
    acked_through_ingest_sequence: acked,
    posts_ingested_new: ingested,
    posts_observed_total: observed,
  };
}

/**
 * `worker.get_status` answers `{"workers": [...]}` — one row per registration, each with its
 * own `online_state` and `last_run_at` (`server/app/jobs/service.py::get_worker_status`),
 * not the two flat fields `screens.yaml §screens[SCR-runs].read_model` names. The collector
 * row is the one this screen is about.
 *
 * With no collector registration at all the answer is `null`, rendered as "—". It is
 * deliberately not `offline`: `screens.yaml` says in so many words that `unknown` must not
 * be shown as `offline` (I13), and "never registered" is even further from `offline` than
 * `unknown` is.
 */
function parseCollector(worker: Record<string, unknown> | null): {
  online_state: CollectorOnlineState | null;
  last_run_at: string | null;
} {
  if (worker === null) return { online_state: null, last_run_at: null };
  const flat = asCollectorOnlineState(worker['collector_online_state']);
  if (flat !== null) {
    return { online_state: flat, last_run_at: asString(worker['last_run_at']) };
  }
  for (const entry of asArray(worker['workers'])) {
    const record = asRecord(entry);
    if (record === null) continue;
    const kind = asString(record['worker_kind']);
    if (kind !== null && kind !== 'collector') continue;
    return {
      online_state: asCollectorOnlineState(record['online_state']),
      last_run_at: asString(record['last_run_at']),
    };
  }
  return { online_state: null, last_run_at: asString(worker['last_run_at']) };
}

function parseRunRow(raw: unknown, storage: StorageNotice): RunRow | null {
  const record = asRecord(raw);
  if (record === null) return null;
  // `run_id` is what the server actually sends (`server/app/jobs/service.py::_run_view`);
  // `id` is what `contracts/data/entities.yaml ENT-run` calls the column. Both are accepted
  // so the read model survives whichever the closed schema of CR-TC-uiruns-02 settles on.
  const id = asString(record['run_id']) ?? asString(record['id']);
  const status = asRunStatus(record['status']);
  if (id === null || status === null) return null;

  const outcome = asRunOutcome(record['outcome']);
  const stopReason = asStopReason(record['stop_reason']);
  const triple: RunStateTriple = { status, outcome, stop_reason: stopReason };
  const unblock = asString(record['unblock_condition_vi']);
  const attention = runAttention(triple, unblock);
  const isTerminal = (TERMINAL_RUN_STATUSES as readonly string[]).includes(status);

  const actions: ScreenAction[] = [SCR_RUNS_ACTIONS.openDetail, SCR_RUNS_ACTIONS.runNow];
  // `ACT-resume-run` is `visible_when: run.status = needs_user` — the ONLY place, with Run
  // detail, where resume appears (B10/AMD-B10). A `blocked` run does not get it.
  if (attention.resume_available) actions.push(SCR_RUNS_ACTIONS.resume);
  // `run.cancel` is "Hủy một run CHƯA KẾT THÚC" (openapi.yaml) — the non-terminal states of
  // contracts/state/run.yaml, which is the set SC35 exercises.
  if (!isTerminal) actions.push(SCR_RUNS_ACTIONS.cancel);

  return {
    id,
    triple,
    status,
    outcome,
    stop_reason: stopReason,
    phase: asRunPhase(record['phase']),
    trigger_type: asTriggerType(record['trigger_type']),
    progress: parseProgress(record),
    // `screens.yaml` names this `empty_period_note`; the server sends the coverage sentence
    // as `x_coverage_note_vi` (`run.yaml §coverage_metadata`) and sends no `empty_period_note`
    // at all. Both are read, the contract's name first.
    empty_period_note:
      asString(record['empty_period_note']) ?? asString(record['x_coverage_note_vi']),
    unblock_condition_vi: unblock,
    status_label: runStatusLabel(triple),
    attention,
    delivery_state: asDeliveryState(record['delivery_state']),
    is_terminal: isTerminal,
    actions,
    actions_disabled_reason_vi: storage.reason_vi,
  };
}

export interface RunsInput {
  /** Body of `run.list`, or `undefined` while it has not arrived. */
  runList?: unknown;
  /** Body of `worker.get_status`, or `undefined`. */
  workerStatus?: unknown;
  /** The read failed; the previous body, if any, is still shown as last-known. */
  error?: unknown;
  isLoading?: boolean;
}

const EMPTY_MODEL: Omit<RunsReadModel, 'display_state'> = {
  collector_online_state: null,
  last_run_at: null,
  runs: [],
  as_of: null,
  storage_health: null,
  storage: { last_known: false, reason_vi: null },
  error_code: null,
  error_message_safe: null,
  error_redirect_to: null,
};

/**
 * Builds the screen from whatever arrived.
 *
 * The five display states of `screens.yaml §global_rules.five_display_states` are decided
 * here and only here. `stale_last_known` outranks the others because UI-02 says
 * `storage_health != healthy` data must be labelled last-known whatever it contains, and
 * UI-04 says the run's own state does not change because of it: a `completed/empty` run
 * read during `write_blocked` is still `empty`, it is only stamped with `as_of`.
 */
export function buildRunsReadModel(input: RunsInput): RunsReadModel {
  const list = asRecord(input.runList);
  const worker = asRecord(input.workerStatus);
  const health = asStorageHealth(list?.['storage_health']);
  const asOf = list === null ? null : asString(list['as_of']);
  const storage = storageNotice(health, asOf);

  const collector = parseCollector(worker);
  const rows: RunRow[] = [];
  for (const raw of asArray(list?.['runs'])) {
    const row = parseRunRow(raw, storage);
    if (row !== null) rows.push(row);
  }

  const base: Omit<RunsReadModel, 'display_state'> = {
    ...EMPTY_MODEL,
    collector_online_state: collector.online_state,
    last_run_at: collector.last_run_at,
    runs: rows,
    as_of: asOf,
    storage_health: health,
    storage,
  };

  if (input.error !== undefined && input.error !== null) {
    const apiError = input.error instanceof ApiError ? input.error : null;
    const obligation = errorObligation(apiError?.code ?? null);
    return {
      ...base,
      display_state: 'error',
      error_code: apiError?.code ?? null,
      error_message_safe: apiError?.envelope?.message_safe ?? null,
      error_redirect_to: obligation.redirect_to,
    };
  }
  if (storage.last_known) return { ...base, display_state: 'stale_last_known' };
  if (list === null) return { ...base, display_state: 'loading' };
  if (rows.length === 0) return { ...base, display_state: 'empty' };
  // `screens.yaml §screens[SCR-runs].states.partial_vi`: "Run `outcome = partial` hiện
  // 'một phần' + số mục thiếu." A missing `worker.get_status` is the other known-missing
  // part of this screen's data.
  if (rows.some((row) => row.outcome === 'partial') || worker === null) {
    return { ...base, display_state: 'partial' };
  }
  return { ...base, display_state: 'ready' };
}

// ---------------------------------------------------------------------------------
// Query wiring (TanStack Query — ADR-0011 "TanStack Query cho read model")
// ---------------------------------------------------------------------------------

export const RUNS_QUERY_KEY = ['SCR-runs'] as const;

export async function fetchRuns(client: ApiClient): Promise<RunsInput> {
  const [runList, workerStatus] = await Promise.all([
    client.get('/v1/runs'),
    client.get('/v1/workers/status'),
  ]);
  return { runList, workerStatus };
}

// ---------------------------------------------------------------------------------
// Mutations — every one of them carries the session cookie AND `X-CSRF-Token`
// ---------------------------------------------------------------------------------

/**
 * `run.run_now`. B10/AMD-B10: this does NOT step over a `needs_user` or `blocked` run —
 * the server returns the current run with its reason instead, and the UI must not paper
 * over that by also offering resume here.
 */
export async function runNow(client: ApiClient): Promise<unknown> {
  return client.mutate('/v1/runs/run-now', { body: {} });
}

/** `run.resume` — the app-only action of B10; there is no Telegram equivalent. */
export async function resumeRun(client: ApiClient, runId: string): Promise<unknown> {
  return client.mutate('/v1/runs/{run_id}/resume', { path: { run_id: runId }, body: {} });
}

/** `run.cancel` from any non-terminal state (SC35). */
export async function cancelRun(client: ApiClient, runId: string): Promise<unknown> {
  return client.mutate('/v1/runs/{run_id}/cancel', { path: { run_id: runId }, body: {} });
}

export function useRunsReadModel(client: ApiClient): RunsReadModel {
  const query = useQuery({
    queryKey: RUNS_QUERY_KEY,
    queryFn: () => fetchRuns(client),
  });
  return buildRunsReadModel({
    ...(query.data ?? {}),
    ...(query.error === null ? {} : { error: query.error }),
    isLoading: query.isPending,
  });
}
