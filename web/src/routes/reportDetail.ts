// Read model for `SCR-report-detail` (contracts/ui/screens.yaml §screens SCR-report-detail).
//
// Card: agent-tasks/TC-ui-reports-detail.md §3 (`web/src/routes/reportDetail.ts`), §4
// (`report.get`), §6 (I04, I05, I07, I13), §8 (AC-10, AC-11, fixtures `reporting/h`, `i`,
// `ui/sc10-…`).
//
// The load-bearing rule of this module: the *analysis revision* an item shows is the one the
// published report froze (`report_item.analysis`), never a newer generation that appeared after
// publish (I05). The Telegram digest reads the same frozen reference
// (contracts/telegram/delivery.md §3.1), which is why `ac10ChannelPayload` below is a single
// projection both channels can be compared against field by field (AC-10).

import type {
  Ac10Completeness,
  ComparatorDisplay,
  EvidenceLevel,
  ProvenanceGroup,
  Statement,
  SummaryResult,
} from '../lib/provenance';
import {
  assessAc10Completeness,
  describeComparator,
  evidenceCeilingViolations,
  evidenceLevelLabel,
  EVIDENCE_LEVEL_MEANINGS,
  groupStatementsByKind,
  MISSING_FIELD_LABEL,
  SUMMARY_PENDING_LABEL,
} from '../lib/provenance';
import type {
  AnalysisRevision,
  ScreenDisplayState,
  EmergingDirection,
  MatchedTag,
  ReadContext,
  ReportItemPayload,
  ReportPayload,
  StorageHealth,
  TargetRef,
} from './reports';
import { DEFAULT_OWNER_TIMEZONE, formatDateTime, formatDayMonth, readNotice } from './reports';

// Re-exported so a caller working on this screen imports its types from this module.
export type {
  AnalysisRevision,
  EmergingDirection,
  MatchedTag,
  ReportItemPayload,
  ReportPayload,
  TargetRef,
};

/** `saved_item.state` as SCR-report-detail reads it (screens.yaml `items[].saved_state`). */
export type SavedState = 'active' | 'not_saved';

/**
 * Summary payloads keyed by `analysis_id`.
 *
 * report.schema.json carries only an `analysis_ref` — a pointer with a hash, not the summary
 * text (its own words: "Nội dung summary do PC06 định nghĩa; schema này không mô tả các trường
 * bên trong payload"). The five REQ-AC10 parts therefore cannot be read off a `report.get`
 * response alone; see CR-TC-UIREPORTS-03. Until that is resolved the read model takes
 * the summaries as a separate, contract-shaped input and reports any it did not get as missing
 * rather than inventing them.
 */
export type SummaryIndex = ReadonlyMap<string, SummaryResult>;

export interface ReportDetailInput {
  readonly load: 'loading' | 'loaded' | 'error';
  readonly report: ReportPayload | null;
  readonly summaries?: SummaryIndex;
  readonly savedStates?: Readonly<Record<string, SavedState>>;
  readonly context: ReadContext;
}

/** The five REQ-AC10 parts, in the shape both channels are compared on (fixture `ui/sc10-…`). */
export interface Ac10ChannelPayload {
  readonly analysis_id: string;
  readonly generation_number: number;
  readonly content: string | null;
  readonly difference_from_prior: string | null;
  readonly limitation_vi: string | null;
  readonly evidence_level: EvidenceLevel;
  readonly matched_tags: readonly { readonly tag_text: string; readonly similarity: number }[];
}

export interface ReportDetailItem {
  readonly report_item_id: string;
  readonly target: TargetRef;
  readonly target_key: string;
  readonly item_type: ReportItemPayload['item_type'];
  /**
   * `new_discovery` ⇒ "Phát hiện mới"; `prior_reference` ⇒ "Đã báo cáo <dd/MM>" with the date
   * from `first_announced.first_announced_at` (REQ-D29, REQ-AC09, fixture `reporting/h`
   * display_oracles). A prior reference is never labelled as a new discovery (I07).
   */
  readonly item_type_label: string;
  readonly first_announced_at: string | null;
  readonly reference_reason: ReportItemPayload['reference_reason'] | null;
  /** Display-only flag; it does not change `item_type` (time-and-tags.md §5.3). */
  readonly late_discovery_label: string | null;
  readonly analysis: AnalysisRevision | null;
  /** The frozen revision, for the AC-10 comparison. `null` when the item has no summary yet. */
  readonly analysis_revision_id: string | null;
  readonly generation_number: number | null;
  readonly analyzed_at: string | null;
  /** Analysis date and discovery date are both shown (grounding.md §4.5, CR-PC06-05). */
  readonly analyzed_at_label: string;
  readonly discovered_at: string | null;
  readonly discovered_at_label: string;
  readonly evidence_level: EvidenceLevel | null;
  readonly evidence_level_label: string;
  readonly evidence_level_meaning: string;
  readonly summary_state: NonNullable<ReportItemPayload['summary_state']>;
  readonly summary_state_label: string | null;
  readonly content: string | null;
  readonly difference_from_prior: string | null;
  readonly limitation_vi: string | null;
  readonly comparator: ComparatorDisplay;
  /** All three buckets, always, empty ones included (B16). */
  readonly provenance: readonly ProvenanceGroup[];
  /** Statements whose kind exceeds the evidence ceiling — a data defect, surfaced not repaired. */
  readonly ceiling_violations: readonly Statement[];
  readonly matched_tags: readonly MatchedTag[];
  readonly matched_tags_label: string;
  readonly identity_warning: string | null;
  readonly saved_state: SavedState;
  readonly completeness: Ac10Completeness;
  /** Non-null when at least one of the five REQ-AC10 parts is missing. */
  readonly incomplete_label: string | null;
  readonly channel_payload: Ac10ChannelPayload | null;
}

export interface ReportDetailDirection {
  readonly direction_id: string;
  /** Contract constant "ứng viên để đọc sâu" (REQ-D54). */
  readonly label: EmergingDirection['label'];
  readonly evidence_state: EmergingDirection['evidence_state'];
  /** `insufficient_evidence` reads as missing evidence, never as an emerging direction (B14). */
  readonly state_label: string;
  readonly insufficient_reason: string | null;
  readonly member_target_keys: readonly string[];
}

export interface ReportDetailReadModel {
  readonly screen: 'SCR-report-detail';
  readonly state: ScreenDisplayState;
  readonly report_id: string | null;
  readonly published_at_label: string;
  readonly coverage_label: string;
  readonly coverage_note_vi: string;
  readonly tag_config_version_label: string;
  readonly quality: ReportPayload['quality'] | null;
  readonly pending_item_count: number;
  readonly partial_notice: string | null;
  /** Emerging directions block, rendered at the top of the page (REQ-D53). */
  readonly emerging_directions: readonly ReportDetailDirection[];
  readonly items: readonly ReportDetailItem[];
  readonly as_of: string | null;
  readonly storage_health: StorageHealth | null;
  readonly mutations_enabled: boolean;
  readonly mutations_disabled_reason: string | null;
  readonly stale_notice: string | null;
  readonly error_notice: string | null;
}

const DIRECTION_STATE_LABELS: Readonly<Record<EmergingDirection['evidence_state'], string>> = {
  sufficient: 'Đủ bằng chứng cho nhóm này',
  insufficient_evidence: 'Chưa đủ bằng chứng — chưa kết luận là hướng đang nổi',
};

const INSUFFICIENT_REASON_LABELS: Readonly<Record<string, string>> = {
  below_min_sample: 'số thành viên dưới ngưỡng tối thiểu',
  cold_start_insufficient_history: 'chưa đủ số kỳ trước để so sánh',
  delta_below_threshold: 'mức tăng dưới ngưỡng',
  generation_reset: 'generation embedding vừa đổi',
};

/** "khớp tag nào" line (REQ-D20, REQ-AC10). Empty is impossible per schema (`minItems: 1`). */
export function matchedTagsLabel(tags: readonly MatchedTag[]): string {
  if (tags.length === 0) return `Khớp tag: ${MISSING_FIELD_LABEL}`;
  return `Khớp tag: ${tags.map((tag) => tag.tag_text).join(', ')}`;
}

/**
 * The item-type line. For a prior reference the date is mandatory: fixture
 * `reporting/h` display_oracles requires "đã báo cáo 12/03", rendered in the owner's zone.
 */
export function itemTypeLabel(item: ReportItemPayload, timezone: string): string {
  if (item.item_type === 'prior_reference') {
    const announcedAt = item.first_announced?.first_announced_at;
    return announcedAt === undefined
      ? `Đã báo cáo (ngày công bố: ${MISSING_FIELD_LABEL})`
      : `Đã báo cáo ${formatDayMonth(announcedAt, timezone)}`;
  }
  return 'Phát hiện mới';
}

/**
 * Project the five REQ-AC10 parts of an item.
 *
 * Both channels project from the same frozen `analysis_ref`, so equality of this object's
 * `analysis_id`/`generation_number` with the digest's is the AC-10 oracle, and equality of the
 * remaining fields is the "field by field, not text" comparison the card's §8 asks for.
 */
export function ac10ChannelPayload(
  analysis: AnalysisRevision,
  summary: SummaryResult | undefined,
  matchedTags: readonly MatchedTag[],
): Ac10ChannelPayload {
  return {
    analysis_id: analysis.analysis_id,
    generation_number: analysis.generation_number,
    content: summary?.content ?? null,
    difference_from_prior: summary?.difference_from_existing.text ?? null,
    limitation_vi: summary?.limitation_line ?? null,
    evidence_level: analysis.evidence_level,
    matched_tags: matchedTags.map((tag) => ({ tag_text: tag.tag_text, similarity: tag.score })),
  };
}

function toItem(
  item: ReportItemPayload,
  summaries: SummaryIndex,
  savedStates: Readonly<Record<string, SavedState>>,
  timezone: string,
): ReportDetailItem {
  const analysis = item.analysis ?? null;
  const summary = analysis === null ? undefined : summaries.get(analysis.analysis_id);
  const statements: readonly Statement[] = summary?.statements ?? [];
  const summaryState = item.summary_state ?? 'pending';
  const evidenceLevel = analysis?.evidence_level ?? null;
  const matchedTags = item.matched_tags;

  const completeness = assessAc10Completeness({
    content: summary?.content,
    difference_from_prior: summary?.difference_from_existing.text,
    limitation_vi: summary?.limitation_line,
    evidence_level: evidenceLevel,
    matched_tags: matchedTags,
  });

  return {
    report_item_id: item.report_item_id,
    target: item.target,
    target_key: item.target_key,
    item_type: item.item_type,
    item_type_label: itemTypeLabel(item, timezone),
    first_announced_at: item.first_announced?.first_announced_at ?? null,
    reference_reason: item.reference_reason ?? null,
    late_discovery_label: item.late_discovery ? 'Phát hiện muộn' : null,
    analysis,
    analysis_revision_id: analysis?.analysis_id ?? null,
    generation_number: analysis?.generation_number ?? null,
    analyzed_at: analysis?.analyzed_at ?? null,
    analyzed_at_label:
      analysis === undefined || analysis === null
        ? `Ngày phân tích: ${MISSING_FIELD_LABEL}`
        : `Ngày phân tích: ${formatDateTime(analysis.analyzed_at, timezone)}`,
    discovered_at: item.discovered_at ?? null,
    discovered_at_label:
      item.discovered_at === undefined
        ? `Ngày phát hiện: ${MISSING_FIELD_LABEL}`
        : `Ngày phát hiện: ${formatDateTime(item.discovered_at, timezone)}`,
    evidence_level: evidenceLevel,
    evidence_level_label:
      evidenceLevel === null
        ? `Mức độ đọc: ${MISSING_FIELD_LABEL}`
        : evidenceLevelLabel(evidenceLevel),
    evidence_level_meaning: evidenceLevel === null ? '' : EVIDENCE_LEVEL_MEANINGS[evidenceLevel],
    summary_state: summaryState,
    summary_state_label: summaryState === 'pending' ? SUMMARY_PENDING_LABEL : null,
    content: summary?.content ?? null,
    difference_from_prior: summary?.difference_from_existing.text ?? null,
    limitation_vi: summary?.limitation_line ?? null,
    comparator: describeComparator(summary?.difference_from_existing.comparator),
    provenance: groupStatementsByKind(statements),
    ceiling_violations:
      evidenceLevel === null ? [] : evidenceCeilingViolations(evidenceLevel, statements),
    matched_tags: matchedTags,
    matched_tags_label: matchedTagsLabel(matchedTags),
    identity_warning:
      item.identity_state === 'quarantined'
        ? 'Đang có xung đột định danh; mục này chưa được xác nhận là một công trình riêng.'
        : null,
    saved_state: savedStates[item.report_item_id] ?? 'not_saved',
    completeness,
    incomplete_label: completeness.complete
      ? null
      : `Mục còn thiếu: ${completeness.missing.join(', ')}`,
    channel_payload: analysis === null ? null : ac10ChannelPayload(analysis, summary, matchedTags),
  };
}

function toDirection(direction: EmergingDirection): ReportDetailDirection {
  const reason = direction.insufficient_reason ?? null;
  return {
    direction_id: direction.direction_id,
    label: direction.label,
    evidence_state: direction.evidence_state,
    state_label: DIRECTION_STATE_LABELS[direction.evidence_state],
    insufficient_reason: reason === null ? null : (INSUFFICIENT_REASON_LABELS[reason] ?? reason),
    member_target_keys: direction.member_target_keys,
  };
}

export function buildReportDetailReadModel(input: ReportDetailInput): ReportDetailReadModel {
  const timezone = input.context.ownerTimezone ?? DEFAULT_OWNER_TIMEZONE;
  const health = input.context.storageHealth;
  const notice = readNotice(health, input.context.asOf);
  const report = input.report;
  const summaries: SummaryIndex = input.summaries ?? new Map();
  const savedStates = input.savedStates ?? {};

  const items =
    report === null
      ? []
      : report.items.map((item) => toItem(item, summaries, savedStates, timezone));

  const state: ScreenDisplayState = (() => {
    if (input.load === 'loading') return 'loading';
    if (input.load === 'error' || report === null) return 'error';
    if (health !== null && health !== 'healthy') return 'stale_last_known';
    if (report.quality === 'partial' || items.some((item) => !item.completeness.complete)) {
      return 'partial';
    }
    return 'ready';
  })();

  return {
    screen: 'SCR-report-detail',
    state,
    report_id: report?.report_id ?? null,
    published_at_label:
      report === null ? '' : `Kỳ ${formatDayMonth(report.published_at, timezone)}`,
    coverage_label:
      report === null
        ? ''
        : `Bao trùm ${formatDayMonth(report.coverage.coverage_from, timezone)} đến trước ${formatDayMonth(report.coverage.coverage_to, timezone)} (nửa mở [from, to))`,
    coverage_note_vi:
      report === null
        ? ''
        : report.coverage_note.observed_data_only
          ? 'Chỉ nêu phạm vi dữ liệu đã quan sát được; không khẳng định bao phủ toàn bộ X.'
          : '',
    tag_config_version_label:
      report === null ? '' : `Phiên bản tag đã dùng: #${report.tag_config_version.sequence}`,
    quality: report?.quality ?? null,
    pending_item_count: report?.pending_items.length ?? 0,
    partial_notice:
      report !== null && report.quality === 'partial'
        ? `Kỳ này còn ${report.pending_items.length} mục chưa có summary.`
        : null,
    emerging_directions: report === null ? [] : report.emerging_directions.map(toDirection),
    items,
    as_of: input.context.asOf,
    storage_health: health,
    mutations_enabled: notice.reason_vi === null,
    mutations_disabled_reason: notice.reason_vi,
    stale_notice: notice.last_known ? notice.reason_vi : null,
    error_notice:
      input.load === 'error'
        ? 'Không tải được kỳ báo cáo; phần đã tải vẫn hiển thị và được ghi rõ là thiếu.'
        : null,
  };
}
