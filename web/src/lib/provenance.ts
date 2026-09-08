// Provenance and evidence-level vocabulary for the reading screens.
//
// Card: agent-tasks/TC-ui-reports-detail.md §3 (`web/src/lib/provenance.ts`), §5 denied paths,
// §6 I04/I05/I07/I13, §8 AC-11.
//
// Contract sources, all of them read-only here:
//   * three statement kinds  — contracts/schemas/analysis-result.schema.json $defs.statement_kind
//     (B16 / AMD-B16 / SRC-SPEC §10.3), ceiling table contracts/ai/grounding.md §2/§3;
//   * `comparator`           — analysis-result.schema.json $defs.comparator, grounding.md §4.2;
//   * evidence levels        — contracts/schemas/report.schema.json $defs.analysis_ref.evidence_level
//     (REQ-D21, REQ-AC11);
//   * the D20 display block  — contracts/schemas/saved-snapshot.schema.json $defs.summary_block.
//
// Every wire type below is taken from `src/generated/openapi.d.ts`; this file defines display
// vocabulary and pure projections only. It never fabricates a value: a missing comparator is
// `unknown`, a missing field is an explicit missing label, and a statement is never relabelled.

import type { components } from '../generated/openapi';

/** `author_claim | source_verified | ai_inference` (analysis-result.schema.json). */
export type StatementKind = components['schemas']['statement_kind'];
/** One classified statement with its citations (SV-02/SV-03). */
export type Statement = components['schemas']['statement'];
/** `{kind:'ref', source_ref}` or `{kind:'unknown'}` — B16 forbids inventing a baseline. */
export type Comparator = components['schemas']['comparator'];
/** `post_only | abstract | full_text` (REQ-D21). */
export type EvidenceLevel = components['schemas']['evidence_level'];
/** Task `summary` result shape (REQ-D20). */
export type SummaryResult = components['schemas']['result_summary'];
/** The D20 display block as frozen by a Saved snapshot. */
export type SummaryBlock = components['schemas']['summary_block'];

/**
 * The three kinds, in the order grounding.md §3 tables them. Declared as data so the display
 * layer can iterate; the `satisfies` below fails compilation if the contract ever gains or
 * loses a kind, which is what keeps this list honest rather than merely correct today.
 */
export const STATEMENT_KINDS = ['author_claim', 'source_verified', 'ai_inference'] as const;

/** The three evidence levels, in the ceiling order of grounding.md §2. */
export const EVIDENCE_LEVELS = ['post_only', 'abstract', 'full_text'] as const;

// Compile-time exhaustiveness against the generated unions (both directions).
const _kindsCoverContract = {
  author_claim: true,
  source_verified: true,
  ai_inference: true,
} satisfies Record<StatementKind, true>;
const _levelsCoverContract = {
  post_only: true,
  abstract: true,
  full_text: true,
} satisfies Record<EvidenceLevel, true>;
void _kindsCoverContract;
void _levelsCoverContract;

/**
 * Reader-facing name of each statement kind. Three distinct strings — collapsing any two is
 * the exact failure B16 and REQ-AC11 exist to prevent, so `provenanceLabels.test.ts` asserts
 * distinctness rather than trusting this table.
 *
 * The strings themselves are UI copy, which contracts/ui/screens.yaml §visual_design leaves
 * deliberately unlocked (REQ-S4-10); the *identity* of the three buckets is what is contractual.
 */
export const STATEMENT_KIND_LABELS: Readonly<Record<StatementKind, string>> = {
  author_claim: 'Tác giả tuyên bố',
  source_verified: 'Kiểm được từ nguồn',
  ai_inference: 'Suy luận của AI',
};

/** One line saying what each bucket does and does not warrant (grounding.md §3). */
export const STATEMENT_KIND_MEANINGS: Readonly<Record<StatementKind, string>> = {
  author_claim: 'Tác giả nói như vậy; giá trị đúng/sai chưa được kiểm.',
  source_verified: 'Kiểm được từ nguồn đã cấp cho lần phân tích này.',
  ai_inference: 'Mô hình suy ra; không phải kết luận đã kiểm chứng.',
};

/** Evidence-level labels; values are exactly the enum of report.schema.json (REQ-D21). */
export const EVIDENCE_LEVEL_LABELS: Readonly<Record<EvidenceLevel, string>> = {
  post_only: 'Chỉ đọc post',
  abstract: 'Đã đọc abstract',
  full_text: 'Đã đọc toàn văn',
};

/** What each level licenses the analysis to say (grounding.md §2). */
export const EVIDENCE_LEVEL_MEANINGS: Readonly<Record<EvidenceLevel, string>> = {
  post_only: 'Nguồn duy nhất là post trên X; không có phát biểu nào kiểm được từ paper.',
  abstract: 'Có abstract; phát biểu kiểm được giới hạn trong abstract.',
  full_text: 'Đã đọc toàn văn.',
};

/**
 * Statement kinds a given evidence level may carry (grounding.md §2, check SV-03).
 * `post_only` may never carry `source_verified`.
 */
export const ALLOWED_STATEMENT_KINDS: Readonly<Record<EvidenceLevel, readonly StatementKind[]>> = {
  post_only: ['author_claim', 'ai_inference'],
  abstract: ['author_claim', 'source_verified', 'ai_inference'],
  full_text: ['author_claim', 'source_verified', 'ai_inference'],
};

/** Label for a comparator that has no source (B16, grounding.md §4.2). Never a baseline. */
export const COMPARATOR_UNKNOWN_LABEL = 'Không có nguồn so sánh (comparator: unknown)';

/** Label for a field the payload does not carry. Shown instead of pretending completeness. */
export const MISSING_FIELD_LABEL = 'chưa có';

/** Label for an item whose summary has not been produced yet (AMD-B17). */
export const SUMMARY_PENDING_LABEL = 'chưa có summary';

// The globally forbidden phrase (contracts/ui/screens.yaml §run_status_labels
// forbidden_globally, SRC-SPEC §8.3) is NOT restated here: `web/src/lib/runState.ts` already
// exports it as `FORBIDDEN_RUN_LABEL_VI`, and a second literal is a second thing to forget to
// update. The display tests sweep rendered output against that one.

export function statementKindLabel(kind: StatementKind): string {
  return STATEMENT_KIND_LABELS[kind];
}

export function evidenceLevelLabel(level: EvidenceLevel): string {
  return EVIDENCE_LEVEL_LABELS[level];
}

/** A comparator ready to display: either a citation, or an explicit absence. */
export type ComparatorDisplay =
  | {
      readonly kind: 'ref';
      readonly label: string;
      readonly sourceRef: string;
      readonly note?: string;
    }
  | { readonly kind: 'unknown'; readonly label: string; readonly note?: string };

/**
 * Project a comparator for display. Absent input is `unknown`, not an omission and never an
 * invented baseline (B16). Accepts both contract spellings: the object form of
 * analysis-result.schema.json and the `known | unknown` enum a Saved snapshot freezes.
 */
export function describeComparator(
  comparator: Comparator | SummaryBlock['comparator'] | undefined | null,
): ComparatorDisplay {
  if (comparator === undefined || comparator === null || comparator === 'unknown') {
    return { kind: 'unknown', label: COMPARATOR_UNKNOWN_LABEL };
  }
  if (comparator === 'known') {
    // The snapshot records that a comparator existed but not which source it was; saying which
    // would be inventing one, so the reference is reported as not carried by this payload.
    return {
      kind: 'unknown',
      label: COMPARATOR_UNKNOWN_LABEL,
      note: 'Nguồn so sánh không nằm trong payload này.',
    };
  }
  if (comparator.kind === 'unknown') {
    return comparator.note === undefined
      ? { kind: 'unknown', label: COMPARATOR_UNKNOWN_LABEL }
      : { kind: 'unknown', label: COMPARATOR_UNKNOWN_LABEL, note: comparator.note };
  }
  return comparator.note === undefined
    ? { kind: 'ref', label: 'So với', sourceRef: comparator.source_ref }
    : { kind: 'ref', label: 'So với', sourceRef: comparator.source_ref, note: comparator.note };
}

/** One provenance bucket, kept separate from the other two even when it is empty. */
export interface ProvenanceGroup {
  readonly kind: StatementKind;
  readonly label: string;
  readonly meaning: string;
  readonly statements: readonly Statement[];
}

/**
 * Split statements into the three buckets, in contract order, keeping empty buckets.
 *
 * Empty buckets are kept on purpose: "no verified statement" and "verified statements not
 * shown" must not look the same to a reader (I13), and a UI that drops the empty bucket makes
 * the two indistinguishable.
 */
export function groupStatementsByKind(
  statements: readonly Statement[],
): readonly ProvenanceGroup[] {
  return STATEMENT_KINDS.map((kind) => ({
    kind,
    label: STATEMENT_KIND_LABELS[kind],
    meaning: STATEMENT_KIND_MEANINGS[kind],
    statements: statements.filter((statement) => statement.kind === kind),
  }));
}

/**
 * Statements whose kind exceeds what the evidence level licenses (grounding.md §2, SV-03).
 *
 * Such a payload should never have been committed (fixture `ai/d` expects zero analysis rows),
 * so a non-empty result here is a data defect. The UI surfaces it; it never repairs it by
 * relabelling the statement, which would be exactly the fabrication B16 forbids.
 */
export function evidenceCeilingViolations(
  level: EvidenceLevel,
  statements: readonly Statement[],
): readonly Statement[] {
  const allowed = ALLOWED_STATEMENT_KINDS[level];
  return statements.filter((statement) => !allowed.includes(statement.kind));
}

/**
 * The five parts REQ-AC10 requires of every item (screens.yaml SCR-report-detail
 * §ac10_completeness; contracts/telegram/delivery.md §3.1 lists the same five for the digest).
 * Field ids follow acceptance/fixtures/ui/sc10-…json `channel_payloads.*.fields_present`.
 */
export const AC10_FIELDS = [
  'content',
  'difference_from_prior',
  'limitation_vi',
  'evidence_level',
  'matched_tags',
] as const;

export type Ac10Field = (typeof AC10_FIELDS)[number];

/** Which of the five parts a projected item actually carries. */
export interface Ac10Completeness {
  readonly complete: boolean;
  readonly present: readonly Ac10Field[];
  readonly missing: readonly Ac10Field[];
}

export function assessAc10Completeness(
  carried: Readonly<Partial<Record<Ac10Field, unknown>>>,
): Ac10Completeness {
  const present = AC10_FIELDS.filter((field) => {
    const value = carried[field];
    if (value === undefined || value === null) return false;
    if (typeof value === 'string') return value.length > 0;
    if (Array.isArray(value)) return value.length > 0;
    return true;
  });
  const missing = AC10_FIELDS.filter((field) => !present.includes(field));
  return { complete: missing.length === 0, present, missing };
}
