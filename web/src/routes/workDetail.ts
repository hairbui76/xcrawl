// Read model for `SCR-work-detail` (contracts/ui/screens.yaml §screens SCR-work-detail).
//
// Card: agent-tasks/TC-ui-reports-detail.md §3 (`web/src/routes/workDetail.ts`), §4
// (`work.get_detail`), §5 (three statement kinds never collapsed, no invented comparator),
// §6 (I04, I07, I13), §8 (AC-11).
//
// Contract gap, carried as CR-TC-UIREPORTS-01: `contracts/http/openapi.yaml`
// `work.get_detail` declares its 200 body as `../schemas/target.schema.json`, i.e. the
// `work | post` tagged union alone. That union cannot carry the eleven fields
// screens.yaml's SCR-work-detail read model names (summary, evidence_level, topic_labels,
// matched_tags, source_posts, paper_refs, work_versions, analysis_history,
// related_reported_items, identity_state, content_state). Rather than hand-write a wire body,
// `WorkDetailSource` below composes the pieces out of contract component types and names its
// fields exactly as screens.yaml does; when the wire schema is fixed, only the adapter in
// `web/src/lib/api.ts` changes.

import type { components } from '../generated/openapi';
import type {
  ComparatorDisplay,
  EvidenceLevel,
  ProvenanceGroup,
  Statement,
  SummaryResult,
} from '../lib/provenance';
import {
  describeComparator,
  evidenceCeilingViolations,
  evidenceLevelLabel,
  EVIDENCE_LEVEL_MEANINGS,
  groupStatementsByKind,
  MISSING_FIELD_LABEL,
} from '../lib/provenance';
import type { AnalysisRevision, MatchedTag, SavedState, TargetRef } from './reportDetail';
import type { ReadContext, ScreenDisplayState, StorageHealth } from './reports';
import { DEFAULT_OWNER_TIMEZONE, formatDateTime, formatDayMonth, readNotice } from './reports';

/** One source post, shaped by contracts/schemas/saved-snapshot.schema.json. */
export type SourcePost = components['schemas']['snapshot_content']['source_posts'][number];
/** Paper identifiers, shaped by the same contract (`work_metadata`). */
export type PaperRefs = NonNullable<components['schemas']['snapshot_content']['work_metadata']>;

/** `work.identity_state` (screens.yaml SCR-work-detail; identity.md §5.3, B15). */
export type IdentityState = 'active' | 'merged' | 'quarantined';
/** Whether the owner has deleted the source data (SC32, REQ-S7.3-05). */
export type ContentState = 'present' | 'redacted_by_owner_deletion';

/** One arXiv/journal version of the work (screens.yaml `work_versions`; REQ-D26). */
export interface WorkVersionRef {
  readonly work_version_id: string;
  readonly version_label: string;
  readonly observed_at?: string;
}

/** One earlier report that already carried this work, with its date (REQ-D29, REQ-D30). */
export interface RelatedReportedItem {
  readonly report_item_id: string;
  readonly report_id: string;
  readonly announced_at: string;
  readonly item_type: 'new_discovery' | 'prior_reference';
}

/** One analysis generation with the summary it produced (screens.yaml `analysis_history`). */
export interface AnalysisHistoryEntry {
  readonly analysis: AnalysisRevision;
  readonly summary?: SummaryResult;
  /** Why this generation was created; absent for the first one (REQ-D26). */
  readonly reason?: string;
  /** Exactly one generation is active at a time (I04). */
  readonly is_active: boolean;
}

/** Field names follow screens.yaml SCR-work-detail read_model.fields one for one. */
export interface WorkDetailSource {
  readonly target: TargetRef;
  readonly display_title: string | null;
  readonly evidence_level: EvidenceLevel | null;
  readonly topic_labels: readonly string[];
  readonly matched_tags: readonly MatchedTag[];
  readonly source_posts: readonly SourcePost[];
  readonly paper_refs: PaperRefs | null;
  readonly work_versions: readonly WorkVersionRef[];
  readonly analysis_history: readonly AnalysisHistoryEntry[];
  readonly related_reported_items: readonly RelatedReportedItem[];
  readonly identity_state: IdentityState;
  readonly content_state: ContentState;
  readonly saved_state?: SavedState;
  /** Server time the source was first accepted (grounding.md §4.5). */
  readonly first_discovered_at?: string;
}

export interface WorkDetailInput {
  readonly load: 'loading' | 'loaded' | 'error';
  readonly source: WorkDetailSource | null;
  readonly context: ReadContext;
}

export interface WorkDetailHistoryRow {
  readonly analysis_id: string;
  readonly generation_number: number;
  readonly analyzed_at: string;
  readonly analyzed_at_label: string;
  readonly evidence_level: EvidenceLevel;
  readonly evidence_level_label: string;
  readonly is_active: boolean;
  readonly reason: string | null;
}

export interface WorkDetailReadModel {
  readonly screen: 'SCR-work-detail';
  readonly state: ScreenDisplayState;
  readonly target: TargetRef | null;
  readonly display_title: string;
  /** Active generation's summary; older generations are kept, not overwritten (I04, REQ-D26). */
  readonly content: string | null;
  readonly difference_from_prior: string | null;
  readonly limitation_vi: string | null;
  readonly comparator: ComparatorDisplay;
  /** All three buckets, always present and never merged (B16, REQ-AC11). */
  readonly provenance: readonly ProvenanceGroup[];
  readonly ceiling_violations: readonly Statement[];
  /**
   * Under `post_only`, every novelty statement reads as inference, not conclusion (REQ-AC11).
   * Null at other levels.
   */
  readonly novelty_is_inference_notice: string | null;
  readonly evidence_level: EvidenceLevel | null;
  readonly evidence_level_label: string;
  readonly evidence_level_meaning: string;
  readonly topic_labels: readonly string[];
  readonly matched_tags_label: string;
  readonly source_posts: readonly SourcePost[];
  /** X engagement is never evidence (SRC-SPEC §10.3); this read model carries no such counter. */
  readonly source_posts_note: string;
  readonly paper_refs: PaperRefs | null;
  readonly paper_metadata_notice: string | null;
  readonly work_versions: readonly WorkVersionRef[];
  readonly analysis_history: readonly WorkDetailHistoryRow[];
  readonly analyzed_at_label: string;
  readonly discovered_at_label: string;
  readonly related_reported_items: readonly (RelatedReportedItem & {
    readonly announced_label: string;
  })[];
  readonly identity_state: IdentityState | null;
  readonly identity_warning: string | null;
  readonly content_state: ContentState | null;
  readonly content_state_notice: string | null;
  readonly saved_state: SavedState;
  readonly as_of: string | null;
  readonly storage_health: StorageHealth | null;
  readonly mutations_enabled: boolean;
  readonly mutations_disabled_reason: string | null;
  readonly stale_notice: string | null;
  readonly error_notice: string | null;
}

/** The active generation, or the highest generation number when none is flagged (I04). */
export function activeGeneration(
  history: readonly AnalysisHistoryEntry[],
): AnalysisHistoryEntry | null {
  const flagged = history.find((entry) => entry.is_active);
  if (flagged !== undefined) return flagged;
  return history.reduce<AnalysisHistoryEntry | null>(
    (best, entry) =>
      best === null || entry.analysis.generation_number > best.analysis.generation_number
        ? entry
        : best,
    null,
  );
}

export function buildWorkDetailReadModel(input: WorkDetailInput): WorkDetailReadModel {
  const timezone = input.context.ownerTimezone ?? DEFAULT_OWNER_TIMEZONE;
  const health = input.context.storageHealth;
  const notice = readNotice(health, input.context.asOf);
  const source = input.source;
  const active = source === null ? null : activeGeneration(source.analysis_history);
  const summary = active?.summary;
  const statements: readonly Statement[] = summary?.statements ?? [];
  const evidenceLevel = source?.evidence_level ?? active?.analysis.evidence_level ?? null;

  const state: ScreenDisplayState = (() => {
    if (input.load === 'loading') return 'loading';
    if (input.load === 'error' || source === null) return 'error';
    if (health !== null && health !== 'healthy') return 'stale_last_known';
    // "Thiếu metadata paper ⇒ hiện 'chỉ có post'" (screens.yaml partial_vi, REQ-D33).
    if (source.paper_refs === null || summary === undefined) return 'partial';
    return 'ready';
  })();

  return {
    screen: 'SCR-work-detail',
    state,
    target: source?.target ?? null,
    display_title: source?.display_title ?? MISSING_FIELD_LABEL,
    content: summary?.content ?? null,
    difference_from_prior: summary?.difference_from_existing.text ?? null,
    limitation_vi: summary?.limitation_line ?? null,
    comparator: describeComparator(summary?.difference_from_existing.comparator),
    provenance: groupStatementsByKind(statements),
    ceiling_violations:
      evidenceLevel === null ? [] : evidenceCeilingViolations(evidenceLevel, statements),
    novelty_is_inference_notice:
      evidenceLevel === 'post_only'
        ? 'Chỉ có post làm nguồn: mọi phát biểu về tính mới ở đây là suy luận, không phải kết luận.'
        : null,
    evidence_level: evidenceLevel,
    evidence_level_label:
      evidenceLevel === null
        ? `Mức độ đọc: ${MISSING_FIELD_LABEL}`
        : evidenceLevelLabel(evidenceLevel),
    evidence_level_meaning: evidenceLevel === null ? '' : EVIDENCE_LEVEL_MEANINGS[evidenceLevel],
    topic_labels: source?.topic_labels ?? [],
    matched_tags_label:
      source === null || source.matched_tags.length === 0
        ? `Khớp tag: ${MISSING_FIELD_LABEL}`
        : `Khớp tag: ${source.matched_tags.map((tag) => tag.tag_text).join(', ')}`,
    source_posts: source?.source_posts ?? [],
    source_posts_note:
      'Các post dẫn tới công trình này. Lượt thích và lượt đăng lại không phải bằng chứng khoa học.',
    paper_refs: source?.paper_refs ?? null,
    paper_metadata_notice:
      source !== null && source.paper_refs === null
        ? 'Chỉ có post: chưa có metadata paper (DOI, arXiv, abstract) cho mục này.'
        : null,
    work_versions: source?.work_versions ?? [],
    analysis_history:
      source === null
        ? []
        : source.analysis_history.map((entry) => ({
            analysis_id: entry.analysis.analysis_id,
            generation_number: entry.analysis.generation_number,
            analyzed_at: entry.analysis.analyzed_at,
            analyzed_at_label: formatDateTime(entry.analysis.analyzed_at, timezone),
            evidence_level: entry.analysis.evidence_level,
            evidence_level_label: evidenceLevelLabel(entry.analysis.evidence_level),
            is_active: entry.is_active,
            reason: entry.reason ?? null,
          })),
    analyzed_at_label:
      active === null
        ? `Ngày phân tích: ${MISSING_FIELD_LABEL}`
        : `Ngày phân tích: ${formatDateTime(active.analysis.analyzed_at, timezone)}`,
    discovered_at_label:
      source?.first_discovered_at === undefined
        ? `Ngày phát hiện: ${MISSING_FIELD_LABEL}`
        : `Ngày phát hiện: ${formatDateTime(source.first_discovered_at, timezone)}`,
    related_reported_items:
      source === null
        ? []
        : source.related_reported_items.map((related) => ({
            ...related,
            announced_label: `Đã báo cáo ${formatDayMonth(related.announced_at, timezone)}`,
          })),
    identity_state: source?.identity_state ?? null,
    identity_warning:
      source?.identity_state === 'quarantined'
        ? 'Đang có xung đột định danh; hai bản ghi chưa được xác nhận là hai công trình độc lập.'
        : null,
    content_state: source?.content_state ?? null,
    content_state_notice:
      source?.content_state === 'redacted_by_owner_deletion'
        ? 'Dữ liệu gốc của mục này đã được xóa theo yêu cầu; bản Saved vẫn đọc được từ snapshot.'
        : null,
    saved_state: source?.saved_state ?? 'not_saved',
    as_of: input.context.asOf,
    storage_health: health,
    mutations_enabled: notice.reason_vi === null,
    mutations_disabled_reason: notice.reason_vi,
    stale_notice: notice.last_known ? notice.reason_vi : null,
    error_notice:
      input.load === 'error'
        ? 'Không tải được chi tiết công trình; phần đã tải vẫn hiển thị và được ghi rõ là thiếu.'
        : null,
  };
}
