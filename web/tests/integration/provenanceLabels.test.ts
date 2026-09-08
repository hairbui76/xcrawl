// E1 integration test: the reader can tell an AI inference from a checked fact.
//
// Card: agent-tasks/TC-ui-reports-detail.md §8 (AC-11), §5 (never show `ai_inference` as
// `source_verified`; a missing comparator is `unknown`, never an invented baseline), §12
// (reviewer question: "người đọc có phân biệt được suy luận của AI với dữ kiện đã kiểm chứng
// không"). Oracles are string comparisons on rendered output, not screenshots.
//
// Fixtures: `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` (the payload a
// post-only item legitimately produces) and `.../d-schema-valid-but-uncited.json`
// (`semantic_variant`: a payload that claims `source_verified` under `post_only` — rejected
// before commit, and if one ever reached the screen it must be flagged, not relabelled).

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { createElement } from 'react';

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import {
  EVIDENCE_LEVELS,
  EVIDENCE_LEVEL_LABELS,
  STATEMENT_KINDS,
  STATEMENT_KIND_LABELS,
  describeComparator,
  evidenceCeilingViolations,
  groupStatementsByKind,
  type EvidenceLevel,
  type Statement,
  type SummaryResult,
} from '../../src/lib/provenance';
import { FORBIDDEN_RUN_LABEL_VI } from '../../src/lib/runState';
import {
  buildReportDetailReadModel,
  type AnalysisRevision,
  type ReportItemPayload,
  type SummaryIndex,
} from '../../src/routes/reportDetail';
import type { ReportPayload } from '../../src/routes/reports';
import { buildWorkDetailReadModel } from '../../src/routes/workDetail';
import ReportDetail from '../../src/views/ReportDetail';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '../../..');

/**
 * The §2 fixtures this file exercises, by their full repository path — see the same note in
 * `tests/contract/reportReadModel.test.ts`. Read straight from `acceptance/`, never copied.
 */
const FIXTURES = {
  aiA: 'acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json',
  aiD: 'acceptance/fixtures/ai/d-schema-valid-but-uncited.json',
  collectionH: 'acceptance/fixtures/collection/h-metadata-unavailable-post-only.json',
} as const;

function fixture(repoPath: string): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(REPO_ROOT, repoPath), 'utf8'));
}

interface AnalysisResultPayload {
  evidence_level: EvidenceLevel;
  result: SummaryResult;
}

const FX_A = fixture(FIXTURES.aiA);
const POST_ONLY_RESULT = (FX_A.expected as { analysis_result: AnalysisResultPayload })
  .analysis_result;

const FX_D = fixture(FIXTURES.aiD);
const UNSUPPORTED_CLAIM = (
  FX_D.expected as { semantic_variant: { rejected_payload: AnalysisResultPayload } }
).semantic_variant.rejected_payload;

function reportWith(
  analysisId: string,
  evidenceLevel: EvidenceLevel,
  summary: SummaryResult,
): { report: ReportPayload; summaries: SummaryIndex } {
  const analysis: AnalysisRevision = {
    analysis_id: analysisId,
    task_type: 'summary',
    generation_number: 1,
    payload_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
    evidence_level: evidenceLevel,
    analyzed_at: '2026-09-06T18:00:00.000Z',
    analysis_result_schema_id: 'https://research-radar.local/schemas/analysis-result.schema.json',
  };
  const item: ReportItemPayload = {
    report_item_id: '01JRTEMA000000000000000000',
    target: {
      kind: 'work',
      work_id: '01JWRKA1000000000000000000',
      target_key: 'work:01JWRKA1000000000000000000',
    },
    target_key: 'work:01JWRKA1000000000000000000',
    item_type: 'new_discovery',
    matched_tags: [
      {
        tag_id: '01JTAGPFD00000000000000000',
        tag_text: 'protein folding',
        matched_via: 'tag',
        score: 0.87,
        threshold_applied: 0.8,
      },
    ],
    late_discovery: false,
    selected_via_backfill: false,
    identity_state: 'active',
    summary_state: 'present',
    analysis,
    discovered_at: '2026-09-05T10:00:00.000Z',
  };
  const report = {
    schema_version: '0.1.0',
    report_id: '01JRPTA1000000000000000000',
    report_build_id: 'e3d50998-9139-47cc-be74-c42aba0e42f3',
    owner_id: '01JW0WNER00000000000000000',
    status: 'published',
    quality: 'complete',
    coverage: {
      coverage_window_id: '01JCWNH2000000000000000000',
      sequence: 1,
      coverage_from: '2026-08-30T13:00:00.000Z',
      coverage_to: '2026-09-06T13:00:00.000Z',
      ingest_sequence_from: 1,
      ingest_sequence_to: 10,
      predecessor_window_id: null,
    },
    tag_config_version: {
      tag_config_version_id: '01JTCVH0000000000000000000',
      sequence: 1,
      content_hash: 'sha256:469a86f67168250cdcc6a52782eb81a409d35a3586a8018136f4c10a2cc92b88',
      frozen_at: '2026-09-06T13:00:00.000Z',
    },
    selection_version: '0.1.0',
    embedding_generation: {
      embedding_generation_id: '01JEMBGEN10000000000000000',
      model_name: 'multilingual-e5-small',
      model_version: '1.0.0',
      dimension: 4,
      normalization: 'l2',
    },
    items: [item],
    emerging_directions: [],
    pending_items: [],
    coverage_note: {
      observed_data_only: true,
      empty_period: false,
      threshold_calibration_state: 'uncalibrated',
      run_stop_reason: null,
      source_coverage_limits_note: null,
    },
    built_at: '2026-09-06T13:00:00.000Z',
    published_at: '2026-09-06T13:00:00.000Z',
    content_hash: 'sha256:4a79a555cd91ef33a113d896fcd8d77683e4099628b5d9f53e9be77fccc6978e',
    evidence_refs: [],
  } as unknown as ReportPayload;

  return { report, summaries: new Map([[analysisId, summary]]) };
}

const CONTEXT = { asOf: '2026-09-06T20:10:00.000Z', storageHealth: 'healthy' } as const;

describe('provenance vocabulary (B16 / REQ-AC11)', () => {
  it('gives the three statement kinds three different display strings', () => {
    const labels = STATEMENT_KINDS.map((kind) => STATEMENT_KIND_LABELS[kind]);
    expect(new Set(labels).size).toBe(STATEMENT_KINDS.length);
    expect(STATEMENT_KIND_LABELS.ai_inference).not.toBe(STATEMENT_KIND_LABELS.source_verified);
  });

  it('gives the three evidence levels three different display strings', () => {
    const labels = EVIDENCE_LEVELS.map((level) => EVIDENCE_LEVEL_LABELS[level]);
    expect(new Set(labels).size).toBe(EVIDENCE_LEVELS.length);
    expect(Object.keys(EVIDENCE_LEVEL_LABELS).sort()).toEqual([...EVIDENCE_LEVELS].sort());
  });

  it('keeps all three buckets even when one of them is empty (I13)', () => {
    const groups = groupStatementsByKind(POST_ONLY_RESULT.result.statements);
    expect(groups.map((group) => group.kind)).toEqual([...STATEMENT_KINDS]);
    const verified = groups.find((group) => group.kind === 'source_verified');
    expect(verified?.statements).toHaveLength(0);
  });

  it('reports a missing comparator as unknown and carries no baseline (B16)', () => {
    const comparator = describeComparator(
      POST_ONLY_RESULT.result.difference_from_existing.comparator,
    );
    expect(comparator.kind).toBe('unknown');
    expect(comparator.label).toContain('comparator: unknown');
    expect(describeComparator(undefined).kind).toBe('unknown');
    expect(describeComparator(null).kind).toBe('unknown');
  });

  it('flags a statement that exceeds its evidence ceiling instead of relabelling it (SV-03)', () => {
    const violations = evidenceCeilingViolations(
      UNSUPPORTED_CLAIM.evidence_level,
      UNSUPPORTED_CLAIM.result.statements,
    );
    expect(UNSUPPORTED_CLAIM.evidence_level).toBe('post_only');
    expect(violations).toHaveLength(1);
    expect((violations[0] as Statement).kind).toBe('source_verified');
    // The statement keeps the kind the payload declared; nothing is rewritten.
    expect(
      groupStatementsByKind(UNSUPPORTED_CLAIM.result.statements).find(
        (group) => group.kind === 'ai_inference',
      )?.statements,
    ).toHaveLength(0);
  });
});

describe('SCR-report-detail rendering — fixture ai/a (post-only item)', () => {
  const { report, summaries } = reportWith(
    '01JANAA1000000000000000000',
    POST_ONLY_RESULT.evidence_level,
    POST_ONLY_RESULT.result,
  );
  const model = buildReportDetailReadModel({ load: 'loaded', report, summaries, context: CONTEXT });

  it('labels the reading depth exactly as the contract enum names it', () => {
    render(createElement(ReportDetail, { model }));
    const level = document.querySelector('[data-role="evidence-level"]');
    expect(level?.getAttribute('data-evidence-level')).toBe('post_only');
    expect(level?.textContent).toContain(EVIDENCE_LEVEL_LABELS.post_only);
  });

  it('renders each statement under its own kind, never under another', () => {
    render(createElement(ReportDetail, { model }));
    const inference = document.querySelector('[data-provenance-kind="ai_inference"]');
    const verified = document.querySelector('[data-provenance-kind="source_verified"]');
    const authored = document.querySelector('[data-provenance-kind="author_claim"]');
    expect(inference).not.toBeNull();
    expect(verified).not.toBeNull();
    expect(authored).not.toBeNull();

    for (const statement of POST_ONLY_RESULT.result.statements) {
      const host = document.querySelector(`[data-provenance-kind="${statement.kind}"]`);
      expect(host?.textContent, statement.text).toContain(statement.text);
      for (const other of STATEMENT_KINDS.filter((kind) => kind !== statement.kind)) {
        expect(
          document.querySelector(`[data-provenance-kind="${other}"]`)?.textContent,
          `${statement.kind} leaked into ${other}`,
        ).not.toContain(statement.text);
      }
    }
  });

  it('shows the empty verified bucket as empty rather than dropping it', () => {
    render(createElement(ReportDetail, { model }));
    const verified = document.querySelector('[data-provenance-kind="source_verified"]');
    expect(verified?.textContent).toContain('Không có phát biểu loại này.');
  });

  it('shows the three provenance headings as three distinct strings on screen', () => {
    render(createElement(ReportDetail, { model }));
    const headings = STATEMENT_KINDS.map((kind) => STATEMENT_KIND_LABELS[kind]);
    for (const heading of headings) {
      expect(screen.getByText(heading)).toBeInTheDocument();
    }
    expect(new Set(headings).size).toBe(3);
  });

  it('states the missing comparator instead of inventing a baseline', () => {
    render(createElement(ReportDetail, { model }));
    const comparator = document.querySelector('[data-role="comparator"]');
    expect(comparator?.getAttribute('data-comparator-kind')).toBe('unknown');
    expect(comparator?.textContent).toContain('comparator: unknown');
  });

  it('shows the analysis date and the discovery date together (grounding.md §4.5)', () => {
    render(createElement(ReportDetail, { model }));
    expect(document.querySelector('[data-role="analyzed-at"]')?.textContent).toContain(
      'Ngày phân tích',
    );
    expect(document.querySelector('[data-role="discovered-at"]')?.textContent).toContain(
      'Ngày phát hiện',
    );
  });

  it('offers no "edit report" control and fails no button silently (UC-03, UI-03)', () => {
    const { container } = render(createElement(ReportDetail, { model }));
    expect(container.textContent).not.toContain('Sửa báo cáo');
    const buttons = [...container.querySelectorAll('button')];
    expect(buttons.map((button) => button.textContent)).toEqual(['Save']);
    // No save handler is mounted here, so the control is disabled and says why.
    expect(buttons[0]?.disabled).toBe(true);
    expect(container.querySelector('#mutations-disabled-reason')?.textContent).toContain(
      'chưa được nối',
    );
  });

  it('never renders a globally forbidden phrase (SRC-SPEC §8.3)', () => {
    const { container } = render(createElement(ReportDetail, { model }));
    expect(container.textContent).not.toContain(FORBIDDEN_RUN_LABEL_VI);
  });
});

describe('SCR-report-detail rendering — a payload that oversteps its evidence ceiling', () => {
  const { report, summaries } = reportWith(
    '01JANAD1000000000000000000',
    UNSUPPORTED_CLAIM.evidence_level,
    UNSUPPORTED_CLAIM.result,
  );
  const model = buildReportDetailReadModel({ load: 'loaded', report, summaries, context: CONTEXT });

  it('surfaces the defect and leaves the declared kind untouched', () => {
    render(createElement(ReportDetail, { model }));
    expect(document.querySelector('[data-role="ceiling-violation"]')?.textContent).toContain(
      'vượt mức bằng chứng cho phép',
    );
    const verified = document.querySelector('[data-provenance-kind="source_verified"]');
    const statement = UNSUPPORTED_CLAIM.result.statements[0] as Statement;
    expect(verified?.textContent).toContain(statement.text);
    expect(
      document.querySelector('[data-provenance-kind="ai_inference"]')?.textContent,
    ).not.toContain(statement.text);
  });
});

describe('SCR-report-detail rendering — an item whose summary is not there', () => {
  const { report } = reportWith('01JANAE1000000000000000000', 'post_only', {
    content: '',
    difference_from_existing: { text: '', comparator: { kind: 'unknown' } },
    limitation_line: '',
    statements: [],
  });
  const model = buildReportDetailReadModel({ load: 'loaded', report, context: CONTEXT });

  it('marks the item incomplete rather than showing it as full (REQ-AC10, AMD-B17)', () => {
    render(createElement(ReportDetail, { model }));
    expect(model.items[0]?.completeness.complete).toBe(false);
    expect(document.querySelector('[data-role="incomplete"]')?.textContent).toContain('còn thiếu');
    expect(document.querySelector('[data-role="content"]')?.textContent).toBe('chưa có');
  });
});

describe('SCR-work-detail read model — grounding rules (REQ-AC11, screens.yaml §grounding_rules)', () => {
  const analysis: AnalysisRevision = {
    analysis_id: '01JANAA1000000000000000000',
    task_type: 'summary',
    generation_number: 1,
    payload_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
    evidence_level: POST_ONLY_RESULT.evidence_level,
    analyzed_at: '2026-09-06T18:00:00.000Z',
    analysis_result_schema_id: 'https://research-radar.local/schemas/analysis-result.schema.json',
  };
  const model = buildWorkDetailReadModel({
    load: 'loaded',
    source: {
      target: { kind: 'work', work_id: '01JWRKA1000000000000000000' },
      display_title: 'Một công trình',
      evidence_level: POST_ONLY_RESULT.evidence_level,
      topic_labels: ['protein folding'],
      matched_tags: [],
      source_posts: [],
      paper_refs: null,
      work_versions: [],
      analysis_history: [{ analysis, summary: POST_ONLY_RESULT.result, is_active: true }],
      related_reported_items: [],
      identity_state: 'active',
      content_state: 'present',
      first_discovered_at: '2026-09-05T10:00:00.000Z',
    },
    context: CONTEXT,
  });

  it('keeps the three statement kinds apart on the deep-read screen too', () => {
    expect(model.provenance.map((group) => group.kind)).toEqual([...STATEMENT_KINDS]);
    expect(new Set(model.provenance.map((group) => group.label)).size).toBe(3);
    expect(
      model.provenance.find((group) => group.kind === 'source_verified')?.statements,
    ).toHaveLength(0);
  });

  it('says every novelty statement is inference when the only source is a post', () => {
    expect(model.evidence_level).toBe('post_only');
    expect(model.novelty_is_inference_notice).toContain('suy luận');
    expect(model.novelty_is_inference_notice).toContain('không phải kết luận');
  });

  it('shows the missing comparator and the missing paper metadata as missing', () => {
    expect(model.comparator.kind).toBe('unknown');
    expect(model.paper_metadata_notice).toContain('Chỉ có post');
    expect(model.state).toBe('partial');
  });

  it('shows the analysis date next to the discovery date (SRC-SPEC §10.3)', () => {
    expect(model.analyzed_at_label).not.toContain('chưa có');
    expect(model.discovered_at_label).not.toContain('chưa có');
    expect(model.analyzed_at_label).not.toBe(model.discovered_at_label);
  });

  it('does not present X engagement as evidence', () => {
    expect(model.source_posts_note).toContain('không phải bằng chứng khoa học');
    expect(JSON.stringify(model)).not.toContain('like_count');
  });
});

// ---------------------------------------------------------------------------------------
// §2 fixture `collection/h-metadata-unavailable-post-only.json`.
//
// The academic source returned nothing, the batch still committed, and the receipt carries a
// `SOURCE_METADATA_UNAVAILABLE` warning whose `message_safe` states the display consequence:
// the item shows at the "chỉ có post" level. That sentence is the ingest side of the same rule
// `contracts/ui/screens.yaml` SCR-work-detail states as `partial_vi` (REQ-D33), so the phrase
// the reader sees is taken FROM the fixture rather than restated here.
//
// The fixture also forbids, in its own words, raising `evidence_level` to `abstract` or
// `full_text` when the corresponding source does not exist — checked below from the read
// model's side.
// ---------------------------------------------------------------------------------------

interface IngestWarning {
  code: string;
  message_safe: string;
}

describe('SCR-work-detail — a target whose paper metadata never arrived (REQ-D33)', () => {
  const fx = fixture(FIXTURES.collectionH) as unknown as {
    events: { response_body: { receipt: { warnings: IngestWarning[] } } }[];
    forbidden_effects: string[];
  };
  const warning = fx.events[0]?.response_body.receipt.warnings[0] as IngestWarning;

  /** The phrase the fixture's own user-facing sentence puts in quotes: "chỉ có post". */
  const quotedLevel = /[“"']([^”"']+)[”"']/.exec(warning.message_safe)?.[1] as string;

  const model = buildWorkDetailReadModel({
    load: 'loaded',
    source: {
      target: { kind: 'post', post_id: '01JPSTA1000000000000000000' },
      display_title: 'Một post giới thiệu paper',
      evidence_level: 'post_only',
      topic_labels: [],
      matched_tags: [],
      source_posts: [],
      // The whole point of the fixture: no DOI, no arXiv id, no abstract.
      paper_refs: null,
      work_versions: [],
      analysis_history: [],
      related_reported_items: [],
      identity_state: 'active',
      content_state: 'present',
      first_discovered_at: '2026-09-07T08:01:12.480Z',
    },
    context: CONTEXT,
  });

  it('carries the warning the fixture pins, with a code from contracts/errors.yaml', () => {
    expect(warning.code).toBe('SOURCE_METADATA_UNAVAILABLE');
    expect(quotedLevel).toBeTruthy();
  });

  it('says what is missing, in the words the fixture uses, and reads as partial not complete', () => {
    expect(model.paper_metadata_notice).not.toBeNull();
    expect(model.paper_metadata_notice?.toLowerCase()).toContain(quotedLevel.toLowerCase());
    expect(model.state).toBe('partial');
  });

  it('never raises the evidence level above what the sources support', () => {
    expect(model.evidence_level).toBe('post_only');
    expect(model.evidence_level_label).toBe(EVIDENCE_LEVEL_LABELS.post_only);
    expect(model.novelty_is_inference_notice).not.toBeNull();
    // The fixture forbids the upgrade in its own words; a `source_verified` statement at this
    // level is reported as a ceiling violation rather than silently accepted.
    expect(fx.forbidden_effects.join(' ')).toContain('evidence_level');
    expect(
      evidenceCeilingViolations('post_only', [
        {
          kind: 'source_verified',
          text: 'Paper đạt 92%.',
          citation_refs: ['post:01JPSTA1000000000000000000'],
        },
      ]),
    ).toHaveLength(1);
  });

  it('shows no summary it does not have, and says the analysis date is missing', () => {
    expect(model.content).toBeNull();
    expect(model.comparator.kind).toBe('unknown');
    expect(model.analyzed_at_label).toContain('chưa có');
    expect(model.discovered_at_label).not.toContain('chưa có');
  });
});
