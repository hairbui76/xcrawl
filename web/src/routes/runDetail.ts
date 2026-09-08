// Read model for `SCR-run-detail` (contracts/ui/screens.yaml).
//
// Two source operations, `run.get` and `delivery.get_status`, and one rule that decides
// the shape of the whole screen: the delivery dimension is INDEPENDENT of the run
// dimension (I09). A Telegram send that failed, or whose result is unknown, does not make
// the collection run a failed run, and the screen must show the two side by side rather
// than folding one into the other.

import { useQuery } from '@tanstack/react-query';

import type { ApiClient } from '../lib/api';
import { ApiError } from '../lib/api';
import type {
  DeliveryPartState,
  DeliveryState,
  DeliveryStatusLabel,
  RunAttention,
  RunOutcome,
  RunPhase,
  RunStateTriple,
  RunStatus,
  RunStatusLabel,
  ScreenDisplayState,
  StopReason,
  StorageHealth,
  StorageNotice,
  TriggerType,
  UnknownDecision,
} from '../lib/runState';
import {
  UNKNOWN_DECISIONS,
  aggregateDeliveryState,
  asArray,
  asDeliveryPartState,
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
  deliveryStatusLabel,
  errorObligation,
  runAttention,
  runStatusLabel,
  storageNotice,
} from '../lib/runState';
import type { ScreenAction } from './runs';

// ---------------------------------------------------------------------------------
// Actions — `screens.yaml` §screens[SCR-run-detail].actions
// ---------------------------------------------------------------------------------

export const SCR_RUN_DETAIL_ACTIONS = {
  resume: {
    id: 'ACT-resume-run-detail',
    label_vi: 'Tiếp tục',
    operation_id: 'run.resume',
    mobile: false,
  },
  cancel: {
    id: 'ACT-cancel-run-detail',
    label_vi: 'Hủy',
    operation_id: 'run.cancel',
    mobile: false,
  },
  decideUnknown: {
    id: 'ACT-decide-unknown-delivery',
    label_vi: 'Quyết định về lần gửi chưa xác định',
    operation_id: 'delivery.decide_unknown',
    mobile: false,
  },
} as const satisfies Readonly<Record<string, ScreenAction>>;

/**
 * `screens.yaml` ACT-decide-unknown-delivery: "`resend_accepting_duplicate_risk` (UI phải
 * nói rõ NGUY CƠ TIN TRÙNG)", and `acceptance/fixtures/telegram/
 * b-response-lost-unknown-operator-decides.json` `expected.ui_requirement_vi`: "Trước khi
 * xác nhận resend, UI PHẢI nói rõ nguy cơ tin trùng". This is that sentence. It is a
 * required warning, not a status label — the system never picks a decision itself
 * (AMD-B03), so the risk has to be stated before the owner can pick one.
 */
export const DUPLICATE_RISK_WARNING_VI = 'Nguy cơ tin trùng: tin nhắn có thể đã được gửi rồi.';

export const UNKNOWN_DECISION_OPTIONS: readonly UnknownDecision[] = UNKNOWN_DECISIONS;

// ---------------------------------------------------------------------------------
// Shapes
// ---------------------------------------------------------------------------------

export interface RunCheckpointView {
  acked_through_ingest_sequence: number | null;
  cursor_state: string | null;
}

export interface RunErrorView {
  /** A code of `contracts/errors.yaml`; never a string this card made up. */
  code: string;
  /** `message_safe` only. Transcript, key and cookie are forbidden (§7). */
  message_safe: string | null;
}

export interface DeliveryPartView {
  id: string;
  part_index: number | null;
  state: DeliveryPartState;
  label: DeliveryStatusLabel;
  /** True only for `unknown`: the one state that needs an owner decision (AMD-B03). */
  needs_decision: boolean;
}

export interface DeliveryStatusView {
  /** Aggregate state as the server reported it, or derived from parts per DP-03. */
  state: DeliveryState | null;
  label: DeliveryStatusLabel | null;
  parts: readonly DeliveryPartView[];
  /** The parts a `delivery.decide_unknown` call may target. */
  undecided_parts: readonly DeliveryPartView[];
  /** Present only when a decision is needed. */
  duplicate_risk_warning_vi: string | null;
}

export interface RunDetailReadModel {
  display_state: ScreenDisplayState;
  id: string | null;
  triple: RunStateTriple | null;
  status: RunStatus | null;
  outcome: RunOutcome | null;
  stop_reason: StopReason | null;
  phase: RunPhase | null;
  status_label: RunStatusLabel | null;
  attention: RunAttention;
  trigger_type: TriggerType | null;
  applied_config: Record<string, unknown> | null;
  items_collected: number | null;
  items_new: number | null;
  checkpoint: RunCheckpointView | null;
  /** B05: `completed` does NOT mean all of X was scanned. */
  coverage_limitation_note: string | null;
  errors: readonly RunErrorView[];
  /** REQ-AC04: exactly 1 for a `needs_user` run. */
  alert_intent_count: number | null;
  delivery: DeliveryStatusView;
  as_of: string | null;
  /** `null` when the body carried no `storage_health` — never silently read as healthy. */
  storage_health: StorageHealth | null;
  storage: StorageNotice;
  actions: readonly ScreenAction[];
  actions_disabled_reason_vi: string | null;
  error_code: string | null;
  error_message_safe: string | null;
  error_redirect_to: 'SCR-login' | 'SCR-not-found' | null;
}

// ---------------------------------------------------------------------------------
// Parsing
// ---------------------------------------------------------------------------------

function parseParts(raw: unknown): DeliveryPartView[] {
  const parts: DeliveryPartView[] = [];
  for (const entry of asArray(raw)) {
    const record = asRecord(entry);
    if (record === null) continue;
    // `delivery_part_id` is what the server sends
    // (`server/app/delivery/service.py::get_status`); `id` is the column name in
    // `entities.yaml ENT-delivery-part`. Both accepted — CR-TC-uiruns-02.
    const id = asString(record['delivery_part_id']) ?? asString(record['id']);
    const state = asDeliveryPartState(record['state']);
    if (id === null || state === null) continue;
    parts.push({
      id,
      part_index: asInteger(record['part_index']),
      state,
      label: deliveryStatusLabel(state),
      needs_decision: state === 'unknown',
    });
  }
  return parts;
}

const NO_DELIVERY: DeliveryStatusView = {
  state: null,
  label: null,
  parts: [],
  undecided_parts: [],
  duplicate_risk_warning_vi: null,
};

export function parseDeliveryStatus(raw: unknown): DeliveryStatusView {
  const record = asRecord(raw);
  if (record === null) return NO_DELIVERY;
  const parts = parseParts(record['parts'] ?? record['delivery_parts']);
  // DP-03: the aggregate is DERIVED from the parts, so when the server reports one it is
  // used, and when it does not the parts decide — never the other way round, and never a
  // default of `sent`.
  const state =
    asDeliveryState(record['state']) ?? aggregateDeliveryState(parts.map((p) => p.state));
  const undecided = parts.filter((part) => part.needs_decision);
  return {
    state,
    label: state === null ? null : deliveryStatusLabel(state),
    parts,
    undecided_parts: undecided,
    duplicate_risk_warning_vi: undecided.length > 0 ? DUPLICATE_RISK_WARNING_VI : null,
  };
}

function parseErrors(raw: unknown): RunErrorView[] {
  const errors: RunErrorView[] = [];
  for (const entry of asArray(raw)) {
    const record = asRecord(entry);
    if (record === null) continue;
    const code = asString(record['code']);
    if (code === null) continue;
    errors.push({ code, message_safe: asString(record['message_safe']) });
  }
  return errors;
}

export interface RunDetailInput {
  /** Body of `run.get`. */
  run?: unknown;
  /** Body of `delivery.get_status`. */
  delivery?: unknown;
  error?: unknown;
  isLoading?: boolean;
}

const EMPTY_ATTENTION: RunAttention = { resume_available: false, unblock_condition_vi: null };

export function buildRunDetailReadModel(input: RunDetailInput): RunDetailReadModel {
  const run = asRecord(input.run);
  const health = asStorageHealth(run?.['storage_health']);
  const asOf = run === null ? null : asString(run['as_of']);
  const storage = storageNotice(health, asOf);
  const delivery = parseDeliveryStatus(input.delivery);

  const status = asRunStatus(run?.['status']);
  const outcome = asRunOutcome(run?.['outcome']);
  const stopReason = asStopReason(run?.['stop_reason']);
  const triple: RunStateTriple | null =
    status === null ? null : { status, outcome, stop_reason: stopReason };
  const attention =
    triple === null
      ? EMPTY_ATTENTION
      : runAttention(triple, asString(run?.['unblock_condition_vi']));

  const checkpointRecord = run === null ? null : asRecord(run['checkpoint']);
  const actions: ScreenAction[] = [];
  if (attention.resume_available) actions.push(SCR_RUN_DETAIL_ACTIONS.resume);
  if (status !== null && !['completed', 'failed', 'cancelled'].includes(status)) {
    actions.push(SCR_RUN_DETAIL_ACTIONS.cancel);
  }
  // `visible_when: delivery.state = unknown`. The decision is taken per PART, because
  // `delivery.decide_unknown` addresses `delivery_part_id` (openapi.yaml) and DP-02
  // forbids moving a part out of `unknown` for any other reason.
  if (delivery.undecided_parts.length > 0) actions.push(SCR_RUN_DETAIL_ACTIONS.decideUnknown);

  const base: Omit<RunDetailReadModel, 'display_state'> = {
    id: run === null ? null : (asString(run['run_id']) ?? asString(run['id'])),
    triple,
    status,
    outcome,
    stop_reason: stopReason,
    phase: asRunPhase(run?.['phase']),
    status_label: triple === null ? null : runStatusLabel(triple),
    attention,
    trigger_type: asTriggerType(run?.['trigger_type']),
    applied_config: run === null ? null : asRecord(run['applied_config']),
    items_collected: asInteger(run?.['items_collected']),
    items_new: asInteger(run?.['items_new']),
    checkpoint:
      checkpointRecord === null
        ? null
        : {
            acked_through_ingest_sequence: asInteger(
              checkpointRecord['acked_through_ingest_sequence'],
            ),
            cursor_state: asString(checkpointRecord['cursor_state']),
          },
    coverage_limitation_note:
      run === null
        ? null
        : (asString(run['coverage_limitation_note']) ?? asString(run['x_coverage_note_vi'])),
    errors: run === null ? [] : parseErrors(run['errors']),
    alert_intent_count: asInteger(run?.['alert_intent_count']),
    delivery,
    as_of: asOf,
    storage_health: health,
    storage,
    actions,
    actions_disabled_reason_vi: storage.reason_vi,
    error_code: null,
    error_message_safe: null,
    error_redirect_to: null,
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
  if (run === null) return { ...base, display_state: 'loading' };
  // `screens.yaml §screens[SCR-run-detail].states`: `empty_vi: "Không áp dụng."` — a run
  // detail always has a run — and `partial_vi` requires naming which diagnostic part is
  // missing, which is exactly "the run answered but its delivery status did not".
  if (input.delivery === undefined) return { ...base, display_state: 'partial' };
  return { ...base, display_state: 'ready' };
}

// ---------------------------------------------------------------------------------
// Query wiring
// ---------------------------------------------------------------------------------

export const runDetailQueryKey = (runId: string) => ['SCR-run-detail', runId] as const;

export async function fetchRunDetail(
  client: ApiClient,
  runId: string,
  deliveryId: string | null,
): Promise<RunDetailInput> {
  const run = await client.get('/v1/runs/{run_id}', { path: { run_id: runId } });
  if (deliveryId === null) return { run };
  const delivery = await client.get('/v1/deliveries/{delivery_id}', {
    path: { delivery_id: deliveryId },
  });
  return { run, delivery };
}

/**
 * `delivery.decide_unknown` on ONE part.
 *
 * AMD-B03: only the operator moves a part out of `unknown`, and the system never picks.
 * There is deliberately no default value for `decision` here — a caller has to name one.
 */
export async function decideUnknownDelivery(
  client: ApiClient,
  deliveryPartId: string,
  decision: UnknownDecision,
): Promise<unknown> {
  return client.mutate('/v1/deliveries/parts/{delivery_part_id}/decide', {
    path: { delivery_part_id: deliveryPartId },
    body: { decision },
  });
}

export function useRunDetailReadModel(
  client: ApiClient,
  runId: string,
  deliveryId: string | null = null,
): RunDetailReadModel {
  const query = useQuery({
    queryKey: runDetailQueryKey(runId),
    queryFn: () => fetchRunDetail(client, runId, deliveryId),
  });
  return buildRunDetailReadModel({
    ...(query.data ?? {}),
    ...(query.error === null ? {} : { error: query.error }),
    isLoading: query.isPending,
  });
}
