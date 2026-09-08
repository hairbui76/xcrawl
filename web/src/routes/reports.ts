// Read model for `SCR-reports` (contracts/ui/screens.yaml §screens SCR-reports).
//
// Card: agent-tasks/TC-ui-reports-detail.md §3 (`web/src/routes/reports.ts`), §4 (`report.list`),
// §5 (no direct database access, no fabricated labels), §6 (I05, I13), §7 (error obligations).
//
// The name of the database engine is deliberately not written anywhere under `web/src/`:
// `runReadModel.test.ts` sweeps these directories for it as the browser-side half of
// forbidden edge FE-01 (MOD-web-ui → MOD-data-store), and a mention in a comment is
// indistinguishable from one in code to a grep. Same rule for absolute URLs (FE-03/FE-04).
//
// Pure projection: it takes what `report.list` returned plus the ambient read context, and
// returns display strings. It performs no I/O — `web/src/lib/api.ts` does that — so every rule
// below is testable by comparing strings.

import type { components } from '../generated/openapi';
import { MISSING_FIELD_LABEL } from '../lib/provenance';
import type {
  DeliveryState,
  ScreenDisplayState,
  StorageHealth,
  StorageNotice,
} from '../lib/runState';
import { deliveryStatusLabel, storageNotice } from '../lib/runState';

// The delivery, storage-health and display-state vocabularies are NOT redefined here.
// `TC-ui-runs-three-states` derived them from contracts/state/{delivery,storage}.yaml and
// contracts/ui/screens.yaml in `web/src/lib/runState.ts`; a second copy on this side would be a
// second place for `unknown` to drift into `sent` (I13, AMD-B03). This module imports them.
export type { DeliveryState, ScreenDisplayState, StorageHealth, StorageNotice };

// ---------------------------------------------------------------------------------------
// Wire types shared by the three reading screens.
//
// All of them come from `src/generated/openapi.d.ts`; nothing wire-shaped is hand-written.
// Two adjustments are made, each of them a defect in the generated copy rather than in the
// contract, and each carried as a change request:
//
//   * CR-TC-UIREPORTS-04 — `openapi-typescript` lifts a referenced schema's JSON-Schema
//     `$defs` block into a *required* property of the wire type. No response body carries it,
//     so it is omitted here. Omitting it removes no field the contract defines.
//   * CR-TC-UIREPORTS-05 — the generated constant for
//     `analysis_ref.analysis_result_schema_id` is the bare filename
//     `"analysis-result.schema.json"`, while contracts/schemas/report.schema.json declares the
//     full `$id` URL and every fixture carries the URL. The field is widened to `string` so the
//     read model follows the contract rather than the generator's copy of it.
// ---------------------------------------------------------------------------------------

/** Tagged union `work | post` (contracts/schemas/target.schema.json). */
export type TargetRef = components['schemas']['target'];
/** One surviving tag match (contracts/reporting/selection.md §4.3). */
export type MatchedTag = components['schemas']['matched_tag'];
/** The frozen pointer to the analysis revision an item was published with. */
export type AnalysisRevision = Omit<
  components['schemas']['analysis_ref'],
  'analysis_result_schema_id'
> & { analysis_result_schema_id: string };
/** One item of a published report (report.schema.json `$defs/report_item`). */
export type ReportItemPayload = Omit<
  components['schemas']['report_item'],
  'target' | 'analysis'
> & { target: TargetRef; analysis?: AnalysisRevision };
export type EmergingDirection = components['schemas']['emerging_direction'];

/** One published report as the contract shapes it (contracts/schemas/report.schema.json). */
export type ReportPayload = Omit<components['schemas']['report.schema'], '$defs' | 'items'> & {
  items: readonly ReportItemPayload[];
};

/**
 * Shown when nobody has read the delivery state.
 *
 * Delivery is NOT an operation this card may call (card §4): the state arrives as ambient
 * context from whoever owns the delivery read. "Not read" is not one of the delivery states and
 * must not be rendered as one — telling the two apart is exactly I13.
 */
export const DELIVERY_STATUS_UNREAD_LABEL = 'Chưa đọc trạng thái gửi';

/** Quality labels (screens.yaml SCR-reports `quality`; AMD-B17). */
export const QUALITY_LABELS: Readonly<Record<ReportPayload['quality'], string>> = {
  complete: 'Đầy đủ',
  partial: 'Một phần',
};

/** Empty-state copy, verbatim from SRC-SPEC §4 via screens.yaml SCR-reports.states.empty. */
export const REPORTS_EMPTY_COPY = 'Chưa có kỳ nào, bấm chạy ngay';

/** Owner display timezone (B08 / AMD-B08, ACCEPTED OD-20260907-01). Labels only, never maths. */
export const DEFAULT_OWNER_TIMEZONE = 'Asia/Ho_Chi_Minh';

/** Ambient read context shared by every business screen (UI-01…UI-03). */
export interface ReadContext {
  /** UTC ms timestamp of the last successful DB read, or `null` when never read (UI-01). */
  readonly asOf: string | null;
  /** `null` when health has not been read; that is not the same as `healthy` (I13). */
  readonly storageHealth: StorageHealth | null;
  /** IANA zone used for date labels only (time-and-tags.md §2). */
  readonly ownerTimezone?: string;
}

export interface ReportsInput {
  /** `loading` before the first response; `error` when the read failed (cached rows kept). */
  readonly load: 'loading' | 'loaded' | 'error';
  /** Reports carried by the response, or the last known ones when `load` is `error`. */
  readonly reports: readonly ReportPayload[];
  readonly context: ReadContext;
  /** Delivery state per `report_id`, from whoever read it. Absent ⇒ not read. */
  readonly deliveryStates?: Readonly<Record<string, DeliveryState>>;
}

export interface ReportsRow {
  readonly report_id: string;
  readonly published_at: string;
  /** `dd/MM` in the owner's zone (time-and-tags.md §2 item 1). */
  readonly published_at_label: string;
  readonly coverage_from: string;
  readonly coverage_to: string;
  /** Says the right boundary is exclusive, in words (screens.yaml `coverage_to` note). */
  readonly coverage_label: string;
  readonly item_count: number;
  readonly emerging_direction_count: number;
  readonly quality: ReportPayload['quality'];
  readonly quality_label: string;
  /** Number of items still missing a summary; drives the `partial` label (AMD-B17). */
  readonly pending_item_count: number;
  readonly delivery_status_label: string;
}

export interface ReportsReadModel {
  readonly screen: 'SCR-reports';
  readonly state: ScreenDisplayState;
  readonly rows: readonly ReportsRow[];
  /** Non-null only in the `empty` state; the copy says why it is empty (SRC-SPEC §4). */
  readonly empty_copy: string | null;
  readonly as_of: string | null;
  readonly as_of_label: string;
  readonly storage_health: StorageHealth | null;
  /** UI-03: mutations disabled with a stated reason whenever health is not `healthy`. */
  readonly mutations_enabled: boolean;
  readonly mutations_disabled_reason: string | null;
  /** UI-02: shown data is last-known, explicitly labelled. */
  readonly stale_notice: string | null;
  /** Set in the `error` state: kept data is old and says so (screens.yaml SCR-reports.error_vi). */
  readonly error_notice: string | null;
}

/**
 * Calendar parts of an instant in a given zone.
 *
 * The parts are assembled by hand rather than taken from a locale's own pattern: the separator
 * a locale picks varies with the ICU data a runtime happens to ship, and the fixture oracles
 * quote an exact string ("đã báo cáo 12/03", reporting/h display_oracles). Only the zone
 * conversion is delegated to `Intl`.
 */
function zonedParts(
  timestampUtc: string,
  timezone: string,
  options: Intl.DateTimeFormatOptions,
): Partial<Record<Intl.DateTimeFormatPartTypes, string>> {
  const parts: Partial<Record<Intl.DateTimeFormatPartTypes, string>> = {};
  for (const part of new Intl.DateTimeFormat('en-GB', {
    timeZone: timezone,
    ...options,
  }).formatToParts(new Date(timestampUtc))) {
    parts[part.type] = part.value;
  }
  return parts;
}

/** `dd/MM` in the owner's zone. Display only — never used to compute a boundary (§2 O-2). */
export function formatDayMonth(timestampUtc: string, timezone = DEFAULT_OWNER_TIMEZONE): string {
  const parts = zonedParts(timestampUtc, timezone, { day: '2-digit', month: '2-digit' });
  return `${parts.day ?? '??'}/${parts.month ?? '??'}`;
}

/** `dd/MM/yyyy HH:mm` in the owner's zone, for `as_of` and analysis/discovery stamps. */
export function formatDateTime(timestampUtc: string, timezone = DEFAULT_OWNER_TIMEZONE): string {
  const parts = zonedParts(timestampUtc, timezone, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
  return `${parts.day ?? '??'}/${parts.month ?? '??'}/${parts.year ?? '????'} ${parts.hour ?? '??'}:${parts.minute ?? '??'}`;
}

/**
 * UI-02 / UI-03 for one screen: is the data last-known, and why are mutations disabled.
 *
 * `storageNotice` from `runState.ts` answers both for a health value the screen has actually
 * read. The one case it does not cover is `null` — health not read at all — which is neither
 * `healthy` nor any unhealthy value, and which must disable mutations rather than default to
 * "fine" (I13).
 */
export function readNotice(health: StorageHealth | null, asOf: string | null): StorageNotice {
  if (health !== null) return storageNotice(health, asOf);
  return {
    last_known: true,
    reason_vi: 'Chưa đọc được tình trạng lưu trữ; các thay đổi mới chưa chắc lưu được.',
  };
}

/** The delivery label for one report; "not read" is its own string, never a state (I13). */
export function reportDeliveryLabel(state: DeliveryState | undefined): string {
  return state === undefined ? DELIVERY_STATUS_UNREAD_LABEL : deliveryStatusLabel(state).label_vi;
}

function coverageLabel(from: string, to: string, timezone: string): string {
  return `Bao trùm ${formatDayMonth(from, timezone)} đến trước ${formatDayMonth(to, timezone)} (nửa mở [from, to))`;
}

/**
 * Project one published report into a Reports row.
 *
 * Only `status = 'published'` reports reach here (screens.yaml derived_rules_vi); an empty
 * period has a coverage window and no report, and shows up on Runs instead (REQ-D57, AMD-B04).
 */
export function toReportsRow(
  report: ReportPayload,
  timezone: string,
  deliveryState: DeliveryState | undefined,
): ReportsRow {
  return {
    report_id: report.report_id,
    published_at: report.published_at,
    published_at_label: formatDayMonth(report.published_at, timezone),
    coverage_from: report.coverage.coverage_from,
    coverage_to: report.coverage.coverage_to,
    coverage_label: coverageLabel(
      report.coverage.coverage_from,
      report.coverage.coverage_to,
      timezone,
    ),
    item_count: report.items.length,
    emerging_direction_count: report.emerging_directions.length,
    quality: report.quality,
    quality_label: QUALITY_LABELS[report.quality],
    pending_item_count: report.pending_items.length,
    delivery_status_label: reportDeliveryLabel(deliveryState),
  };
}

export function buildReportsReadModel(input: ReportsInput): ReportsReadModel {
  const timezone = input.context.ownerTimezone ?? DEFAULT_OWNER_TIMEZONE;
  const health = input.context.storageHealth;
  const notice = readNotice(health, input.context.asOf);
  const rows = input.reports
    .filter((report) => report.status === 'published')
    .map((report) => toReportsRow(report, timezone, input.deliveryStates?.[report.report_id]));

  const state: ScreenDisplayState = (() => {
    if (input.load === 'loading') return 'loading';
    if (input.load === 'error') return 'error';
    if (health !== null && health !== 'healthy') return 'stale_last_known';
    if (rows.length === 0) return 'empty';
    return rows.some((row) => row.quality === 'partial') ? 'partial' : 'ready';
  })();

  return {
    screen: 'SCR-reports',
    state,
    rows,
    empty_copy: state === 'empty' ? REPORTS_EMPTY_COPY : null,
    as_of: input.context.asOf,
    as_of_label:
      input.context.asOf === null
        ? `Thời điểm đọc: ${MISSING_FIELD_LABEL}`
        : `Số liệu tính đến ${formatDateTime(input.context.asOf, timezone)}`,
    storage_health: health,
    mutations_enabled: notice.reason_vi === null,
    mutations_disabled_reason: notice.reason_vi,
    stale_notice: notice.last_known ? notice.reason_vi : null,
    error_notice:
      input.load === 'error'
        ? 'Không tải được danh sách kỳ; nội dung dưới đây là dữ liệu cũ đã tải trước đó.'
        : null,
  };
}
