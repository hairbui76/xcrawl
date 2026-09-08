// E1 contract test: the reading screens show the analysis revision the report froze — the same
// one the Telegram digest carries — and a work already announced shows as a dated reference.
//
// Card: agent-tasks/TC-ui-reports-detail.md §8 (AC-10, fixtures `ui/sc10-…`, `reporting/h`,
// `reporting/i`), §6 (I05, I07), oracle "so sánh trường-với-trường, không so văn bản".
//
// The fixtures are the oracle and are read from disk, never restated here.

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import {
  ac10ChannelPayload,
  buildReportDetailReadModel,
  type AnalysisRevision,
  type MatchedTag,
  type ReportItemPayload,
  type SummaryIndex,
} from '../../src/routes/reportDetail';
import type { ReportPayload } from '../../src/routes/reports';
import { buildReportsReadModel, formatDayMonth } from '../../src/routes/reports';
import { FORBIDDEN_RUN_LABEL_VI } from '../../src/lib/runState';
import type { SummaryResult } from '../../src/lib/provenance';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '../../..');

/**
 * The §2 fixtures this file exercises, by their full repository path.
 *
 * Spelled out rather than assembled from fragments so that a grep for
 * `acceptance/fixtures/...` finds every fixture a test actually reads — the accounting
 * `evidence/tools/e0_check.py` §E0-20 exists to force. The JSON is read from
 * `acceptance/` directly; no fixture is ever copied into `web/`.
 */
const FIXTURES = {
  sc10: 'acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json',
  reportingH: 'acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json',
  reportingI: 'acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json',
  boundaryA: 'acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json',
} as const;

function fixture(repoPath: string): Record<string, unknown> {
  return JSON.parse(readFileSync(resolve(REPO_ROOT, repoPath), 'utf8'));
}

const HEALTHY = { asOf: '2026-09-06T20:10:00.000Z', storageHealth: 'healthy' } as const;

describe('SCR-report-detail read model — fixture reporting/h (REQ-D29, REQ-AC09, I07)', () => {
  const fx = fixture(FIXTURES.reportingH);
  const report = (fx.expected as { report: unknown }).report as ReportPayload;
  const model = buildReportDetailReadModel({ load: 'loaded', report, context: HEALTHY });

  it('shows the already-announced work as a dated reference, not as a new discovery', () => {
    const item = model.items[0];
    expect(item).toBeDefined();
    expect(item?.item_type).toBe('prior_reference');
    // display_oracles: "Mục hiển thị 'đã báo cáo 12/03' — ngày lấy từ first_announced_at".
    const announcedAt = report.items[0]?.first_announced?.first_announced_at;
    expect(announcedAt).toBeDefined();
    expect(item?.item_type_label).toBe(`Đã báo cáo ${formatDayMonth(announcedAt as string)}`);
    expect(item?.item_type_label).toContain('12/03');
  });

  it('counts zero new discoveries, matching the fixture count', () => {
    const expectedCounts = (fx.expected as { counts: Record<string, number> }).counts;
    const expectedNewDiscoveries =
      expectedCounts["report_item[report_id=HRP2 AND item_type='new_discovery']"];
    expect(expectedNewDiscoveries).toBeDefined();
    const newDiscoveries = model.items.filter((item) => item.item_type === 'new_discovery');
    expect(newDiscoveries).toHaveLength(expectedNewDiscoveries as number);
  });

  it('shows the analysis date and the discovery date, and they differ (grounding.md §4.5)', () => {
    const item = model.items[0];
    expect(item?.analyzed_at).toBe(report.items[0]?.analysis?.analyzed_at);
    expect(item?.discovered_at).toBe(report.items[0]?.discovered_at);
    expect(item?.analyzed_at_label).not.toContain('chưa có');
    expect(item?.discovered_at_label).not.toContain('chưa có');
    expect(item?.analyzed_at_label).not.toBe(item?.discovered_at_label);
  });

  it('keeps the contract label of the emerging-directions block (REQ-D54, B14)', () => {
    const direction = model.emerging_directions[0];
    expect(direction?.label).toBe('ứng viên để đọc sâu');
    expect(direction?.evidence_state).toBe('insufficient_evidence');
    expect(direction?.state_label).toContain('Chưa đủ bằng chứng');
    expect(direction?.state_label).not.toContain('đang nổi —');
  });
});

describe('SCR-report-detail read model — fixture reporting/i (identity merge, I07)', () => {
  const fx = fixture(FIXTURES.reportingI);
  const report = (fx.expected as { report: unknown }).report as ReportPayload;
  const model = buildReportDetailReadModel({ load: 'loaded', report, context: HEALTHY });

  it('shows the inherited first-announcement date, still as one reference', () => {
    const item = model.items[0];
    const announcedAt = report.items[0]?.first_announced?.first_announced_at;
    expect(item?.item_type).toBe('prior_reference');
    expect(item?.item_type_label).toBe(`Đã báo cáo ${formatDayMonth(announcedAt as string)}`);
    expect(item?.first_announced_at).toBe(announcedAt);
    expect(model.items.filter((each) => each.item_type === 'new_discovery')).toHaveLength(0);
  });
});

describe('SCR-reports read model — list projection', () => {
  const fx = fixture(FIXTURES.reportingH);
  const report = (fx.expected as { report: unknown }).report as ReportPayload;

  it('derives the counts screens.yaml declares and names the half-open window', () => {
    const model = buildReportsReadModel({ load: 'loaded', reports: [report], context: HEALTHY });
    const row = model.rows[0];
    expect(row?.item_count).toBe(report.items.length);
    expect(row?.emerging_direction_count).toBe(report.emerging_directions.length);
    expect(row?.coverage_label).toContain('nửa mở [from, to)');
  });

  it('says the delivery state was not read instead of guessing one (I13)', () => {
    const model = buildReportsReadModel({ load: 'loaded', reports: [report], context: HEALTHY });
    expect(model.rows[0]?.delivery_status_label).toBe('Chưa đọc trạng thái gửi');
    expect(model.rows[0]?.delivery_status_label).not.toBe('Đã gửi Telegram');
  });

  it('never emits the globally forbidden phrase in its empty state (SRC-SPEC §8.3)', () => {
    const model = buildReportsReadModel({ load: 'loaded', reports: [], context: HEALTHY });
    expect(model.state).toBe('empty');
    expect(model.empty_copy).toBe('Chưa có kỳ nào, bấm chạy ngay');
    expect(JSON.stringify(model)).not.toContain(FORBIDDEN_RUN_LABEL_VI);
  });
});

// ---------------------------------------------------------------------------------------
// AC-10: the app and the Telegram digest read the same frozen analysis revision.
// ---------------------------------------------------------------------------------------

interface Sc10Fixture {
  given: {
    rows: {
      report: { id: string; published_at: string }[];
      report_item: {
        id: string;
        report_id: string;
        target_key: string;
        item_type: string;
        analysis_id: string;
      }[];
      analysis: {
        id: string;
        generation_number: number;
        evidence_level: string;
        analyzed_at: string;
      }[];
    };
  };
  expected: {
    channel_payloads: {
      app_report_detail: Record<string, unknown>;
      telegram_digest: Record<string, unknown>;
    };
    counts: Record<string, number>;
    oracles: { assert: string }[];
  };
}

describe('AC-10 — fixture ui/sc10: one revision, two channels', () => {
  const fx = fixture(FIXTURES.sc10) as unknown as Sc10Fixture;
  const rows = fx.given.rows;
  const digest = fx.expected.channel_payloads.telegram_digest;
  const appExpected = fx.expected.channel_payloads.app_report_detail;

  // The report_item points at exactly one analysis revision; the newer generation that appeared
  // after publish must not be reachable from either channel (I05).
  const itemRow = rows.report_item[0];
  const frozenAnalysis = rows.analysis.find((row) => row.id === itemRow?.analysis_id);
  const newerAnalysis = rows.analysis.find((row) => row.id !== itemRow?.analysis_id);

  const analysisRef: AnalysisRevision = {
    analysis_id: frozenAnalysis?.id as string,
    task_type: 'summary',
    generation_number: frozenAnalysis?.generation_number as number,
    payload_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
    evidence_level: frozenAnalysis?.evidence_level as AnalysisRevision['evidence_level'],
    analyzed_at: frozenAnalysis?.analyzed_at as string,
    analysis_result_schema_id: 'https://research-radar.local/schemas/analysis-result.schema.json',
  };

  const matchedTags = (digest.matched_tags as { tag_text: string; similarity: number }[]).map(
    (tag): MatchedTag => ({
      tag_id: '01JTAGPFD00000000000000000',
      tag_text: tag.tag_text,
      matched_via: 'tag',
      score: tag.similarity,
      threshold_applied: 0.8,
    }),
  );

  // The five REQ-AC10 parts the digest carries, as the analysis produced them.
  const summary: SummaryResult = {
    content: digest.content as string,
    difference_from_existing: {
      text: digest.difference_from_prior as string,
      comparator: { kind: 'unknown' },
    },
    limitation_line: digest.limitation_vi as string,
    statements: [
      {
        kind: 'author_claim',
        text: 'Tác giả nói vậy.',
        citation_refs: ['post:01JPSTA1000000000000000000'],
      },
      { kind: 'ai_inference', text: 'Mức độ mới chưa xác định được.', citation_refs: [] },
    ],
  };

  const item: ReportItemPayload = {
    report_item_id: itemRow?.id as string,
    target: {
      kind: 'work',
      work_id: '01JW0RKV100000000000000000',
      target_key: itemRow?.target_key as string,
    },
    target_key: itemRow?.target_key as string,
    item_type: 'new_discovery',
    matched_tags: matchedTags,
    late_discovery: false,
    selected_via_backfill: false,
    identity_state: 'active',
    summary_state: 'present',
    analysis: analysisRef,
    discovered_at: '2026-09-05T10:00:00.000Z',
  };

  const summaries: SummaryIndex = new Map([[analysisRef.analysis_id, summary]]);

  const report = {
    schema_version: '0.1.0',
    report_id: rows.report[0]?.id as string,
    report_build_id: 'e3d50998-9139-47cc-be74-c42aba0e42f3',
    owner_id: '01J0WNER100000000000000000',
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
      frozen_at: rows.report[0]?.published_at as string,
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
    built_at: rows.report[0]?.published_at as string,
    published_at: rows.report[0]?.published_at as string,
    content_hash: 'sha256:4a79a555cd91ef33a113d896fcd8d77683e4099628b5d9f53e9be77fccc6978e',
    evidence_refs: [],
  } as unknown as ReportPayload;

  const model = buildReportDetailReadModel({ load: 'loaded', report, summaries, context: HEALTHY });

  it('carries the analysis_id and generation the report froze', () => {
    const projected = model.items[0]?.channel_payload;
    expect(projected?.analysis_id).toBe(digest.analysis_id);
    expect(projected?.analysis_id).toBe(appExpected.analysis_id);
    expect(projected?.generation_number).toBe(digest.generation_number);
  });

  it('matches the Telegram payload field by field on the five REQ-AC10 parts', () => {
    const projected = model.items[0]?.channel_payload;
    expect(projected).toBeDefined();
    for (const field of digest.fields_present as string[]) {
      expect((projected as unknown as Record<string, unknown>)[field], `field ${field}`).toEqual(
        digest[field],
      );
    }
  });

  it('reports the five parts as complete, so nothing is shown as full when it is not', () => {
    expect(model.items[0]?.completeness.complete).toBe(true);
    expect(model.items[0]?.incomplete_label).toBeNull();
  });

  it('never reaches the newer generation that appeared after publish (I05)', () => {
    expect(newerAnalysis?.id).toBeDefined();
    expect(JSON.stringify(model)).not.toContain(newerAnalysis?.id as string);
  });

  it('projects exactly one distinct analysis id across the two channels', () => {
    const projected = model.items[0]?.channel_payload;
    const distinct = new Set([projected?.analysis_id, digest.analysis_id]);
    expect(distinct.size).toBe(fx.expected.counts.distinct_analysis_id_across_channels);
  });

  it('projects the same object for a channel given the same frozen reference', () => {
    const again = ac10ChannelPayload(analysisRef, summary, matchedTags);
    expect(again).toEqual(model.items[0]?.channel_payload);
  });
});

// ---------------------------------------------------------------------------------------
// SG-DENY / SC49: the browser half of every forbidden edge that starts at MOD-web-ui.
//
// The edge list is NOT written out here — it is read from
// `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, which is the oracle
// `contracts/modules.yaml` and SC49 share. Selecting `actor === 'MOD-web-ui'` from the sweep
// yields FE-01 (→ MOD-data-store), FE-02 (→ MOD-secret-service), FE-03 (→ EXT-ai-provider-api)
// and FE-04 (→ EXT-telegram-api). If the contract ever adds a fifth edge out of the web UI,
// this test starts checking it without anyone remembering to edit a list.
//
// The server half of each edge is enforced elsewhere. What is checkable in this card's own
// bytes is `ENF-import-rule`: these modules reach nothing but the generated client, so there
// is no code path from a reading screen to a database, a secret, a provider endpoint or the
// Bot API. The oracle is a count over source text, not a judgement.
// ---------------------------------------------------------------------------------------

interface SweepEvent {
  forbidden_edge_ref: string;
  actor: string;
  callee: string;
  operation: string | null;
  edge_assertion: string;
  expected_error_code: string;
}

describe('SG-DENY — the reading screens can reach nothing but the owner API', () => {
  const OWNED_FILES = [
    'web/src/lib/provenance.ts',
    'web/src/routes/reports.ts',
    'web/src/routes/reportDetail.ts',
    'web/src/routes/workDetail.ts',
    'web/src/views/ReportDetail.tsx',
  ] as const;

  const sweep = fixture(FIXTURES.boundaryA) as unknown as { events: SweepEvent[] };
  const webUiEdges = sweep.events.filter((event) => event.actor === 'MOD-web-ui');

  /**
   * Tokens that would realise one of those edges from inside a browser module, keyed by the
   * callee the fixture names. A module that contains none of them cannot reach that callee.
   */
  const TOKENS_BY_CALLEE: Readonly<Record<string, readonly string[]>> = {
    'MOD-data-store': ['better-sqlite3', 'node:sqlite', 'indexedDB', 'openDatabase'],
    'MOD-secret-service': ['secret.issue_task_credential', 'secret.get', 'Authorization'],
    'EXT-ai-provider-api': ['api.anthropic.com', 'api.openai.com', 'x-api-key'],
    'EXT-telegram-api': ['api.telegram.org', 'sendMessage', 'bot_token'],
  };

  /** Escape hatches that would defeat the "source content is data" rule (I11) whatever the edge. */
  const ESCAPE_HATCHES = [
    'dangerouslySetInnerHTML',
    'XMLHttpRequest',
    'WebSocket',
    'eval(',
  ] as const;

  /** Comments name the forbidden edges on purpose; the oracle is about code, so strip them. */
  function code(text: string): string {
    return text.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');
  }

  const sources = OWNED_FILES.map((path) => {
    const text = readFileSync(resolve(REPO_ROOT, path), 'utf8');
    return { path, text, code: code(text) };
  });

  it('covers exactly the MOD-web-ui edges the sweep fixture declares', () => {
    expect(webUiEdges.length).toBeGreaterThan(0);
    for (const edge of webUiEdges) {
      expect(edge.edge_assertion, edge.forbidden_edge_ref).toBe('forbidden');
      // Every callee the fixture names must have a token set here, or the sweep would pass
      // by not looking (the FE-03 row carries `operation: null` and is still an edge).
      expect(
        Object.keys(TOKENS_BY_CALLEE),
        `${edge.forbidden_edge_ref} → ${edge.callee} has no token set`,
      ).toContain(edge.callee);
      // R5-01 boundary table: a capability the browser lacks, or a principal class refusal.
      expect(['CAPABILITY_DENIED', 'UNAUTHORIZED'], edge.forbidden_edge_ref).toContain(
        edge.expected_error_code,
      );
    }
  });

  it('contains no token that would realise a forbidden edge, per callee', () => {
    for (const source of sources) {
      for (const edge of webUiEdges) {
        for (const token of TOKENS_BY_CALLEE[edge.callee] ?? []) {
          expect(
            source.code.toLowerCase(),
            `${source.path} / ${edge.forbidden_edge_ref} → ${edge.callee} / ${token}`,
          ).not.toContain(token.toLowerCase());
        }
        if (edge.operation !== null) {
          expect(source.code, `${source.path} / ${edge.operation}`).not.toContain(edge.operation);
        }
      }
    }
  });

  it('uses no escape hatch that would render source content as code (I11)', () => {
    for (const source of sources) {
      for (const token of ESCAPE_HATCHES) {
        expect(source.code.toLowerCase(), `${source.path} / ${token}`).not.toContain(
          token.toLowerCase(),
        );
      }
    }
  });

  it('imports nothing but its own siblings and the generated client (ENF-import-rule)', () => {
    for (const source of sources) {
      const specifiers = [...source.code.matchAll(/from\s+'([^']+)'/g)].map((match) => match[1]);
      expect(specifiers.length, source.path).toBeGreaterThan(0);
      for (const specifier of specifiers) {
        expect(specifier, `${source.path} imports ${specifier}`).toMatch(/^\.\.?\//);
      }
    }
  });

  it('opens no socket of its own: no fetch in any read model or view', () => {
    for (const source of sources) {
      expect(source.code, source.path).not.toMatch(/\bfetch\s*\(/);
    }
  });

  it('carries no absolute URL except the schema $id the contract itself names', () => {
    for (const source of sources) {
      const urls = source.code.match(/https?:\/\/[^\s'"`)]+/g) ?? [];
      for (const url of urls) {
        expect(url, `${source.path} → ${url}`).toContain('research-radar.local/schemas/');
      }
    }
  });
});
