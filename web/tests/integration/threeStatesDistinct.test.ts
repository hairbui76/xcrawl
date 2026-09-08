// REQ-AC15 end to end, on fixtures, through the generated client.
//
// "End to end" here means: an `acceptance/fixtures/**` row goes out as a JSON body, comes
// back through `ApiClient` (whose paths, methods and headers are the generated types of
// `contracts/http/openapi.yaml`), through the screen's read model, into a rendered React
// tree — and the assertion is made on the STRINGS that tree contains. No server runs and
// no screenshot is compared, which is exactly what the card asks for: "so sánh chuỗi,
// không so ảnh".
//
// The scheduler that will really answer `run.list` (TC-scheduler-lease-claim) is a sibling
// card landing in the same wave. Nothing here depends on it: the fixture is the backend.

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { render, screen } from '@testing-library/react';
import { createElement } from 'react';
import { describe, expect, it } from 'vitest';

import { ApiClient, ApiError } from '../../src/lib/api';
import { FORBIDDEN_RUN_LABEL_VI, RUN_STATUS_LABELS } from '../../src/lib/runState';
import { buildRunDetailReadModel, decideUnknownDelivery } from '../../src/routes/runDetail';
import { buildRunsReadModel, fetchRuns, runNow } from '../../src/routes/runs';
import RunDetail from '../../src/views/RunDetail';
import RunsList from '../../src/views/RunsList';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, '../../..');

const fixture = <T>(relative: string): T =>
  JSON.parse(readFileSync(resolve(REPO_ROOT, 'acceptance/fixtures', relative), 'utf8')) as T;

interface FixtureM {
  given: { rows: { run: Array<Record<string, unknown>> } };
  expected: {
    ui_labels: Array<{ run_id: string; label_vi: string }>;
    counts: { distinct_labels: number };
    forbidden_string_check: { string_vi: string };
  };
}

const FIXTURE_M = fixture<FixtureM>('telegram/m-three-run-states-distinct-text.json');
const FIXTURE_E = fixture<{ final_state_expected: Record<string, string> }>(
  'collection/e-limit-reached-stop.json',
);
const FIXTURE_D = fixture<{ expected: { display_oracles: string[] } }>(
  'reporting/d-empty-period-coverage-only.json',
);
const FIXTURE_B = fixture<{
  expected: { after_event_3: { rows: { delivery_part: Array<Record<string, unknown>> } } };
}>('telegram/b-response-lost-unknown-operator-decides.json');

// ---------------------------------------------------------------------------------
// A transport that answers from fixtures
// ---------------------------------------------------------------------------------

interface Call {
  url: string;
  init: RequestInit;
}

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  } as unknown as Response;
}

/** Routes by path prefix, so one client answers every operation a screen needs. */
function fixtureClient(routes: Record<string, { status?: number; body: unknown }>) {
  const calls: Call[] = [];
  const client = new ApiClient({
    readCookie: () => 'c'.repeat(32),
    fetch: ((url: string, init: RequestInit) => {
      calls.push({ url, init });
      const key = Object.keys(routes)
        .sort((a, b) => b.length - a.length)
        .find((prefix) => url.startsWith(prefix));
      if (key === undefined) return Promise.resolve(jsonResponse(404, { code: 'NOT_FOUND' }));
      const route = routes[key];
      return Promise.resolve(jsonResponse(route?.status ?? 200, route?.body ?? {}));
    }) as unknown as typeof globalThis.fetch,
  });
  return { client, calls };
}

/**
 * The `run.list` body the scheduler card will eventually produce, built here from the
 * fixture's `given.rows.run` and the field names `screens.yaml §screens[SCR-runs]
 * .read_model` gives — see CR-TC-uiruns-02 for why the shape has to be
 * asserted from those two sources rather than from a JSON Schema.
 */
function runListBody(runs: Array<Record<string, unknown>>): Record<string, unknown> {
  return {
    as_of: '2026-09-07T02:05:00.000Z',
    storage_health: 'healthy',
    runs: runs.map((run) => ({
      id: run['id'],
      status: run['status'],
      outcome: run['outcome'] ?? null,
      stop_reason: run['stop_reason'] ?? null,
      phase: 'reporting',
      trigger_type: 'scheduled',
    })),
  };
}

const WORKER_BODY = { collector_online_state: 'unknown', last_run_at: null };

// ---------------------------------------------------------------------------------
// 1. The three states of REQ-AC15
// ---------------------------------------------------------------------------------

describe('three run states give three different display strings', () => {
  it('fixture m, through the generated client and the rendered screen', async () => {
    const { client, calls } = fixtureClient({
      '/v1/runs': { body: runListBody(FIXTURE_M.given.rows.run) },
      '/v1/workers/status': { body: WORKER_BODY },
    });

    const model = buildRunsReadModel(await fetchRuns(client));
    render(createElement(RunsList, { model }));

    const rendered = FIXTURE_M.expected.ui_labels.map(
      (entry) => screen.getByTestId(`run-status-label-${entry.run_id}`).textContent,
    );

    // (a) each run shows the label the fixture demands…
    expect(rendered).toEqual(FIXTURE_M.expected.ui_labels.map((entry) => entry.label_vi));
    // (b) …and the three strings are different from one another.
    expect(new Set(rendered).size).toBe(FIXTURE_M.expected.counts.distinct_labels);
    // (c) the request really went through the contract's path.
    expect(calls.map((call) => call.url).sort()).toEqual(['/v1/runs', '/v1/workers/status']);
  });

  it('the forbidden phrase appears nowhere on the screen', async () => {
    const { client } = fixtureClient({
      '/v1/runs': { body: runListBody(FIXTURE_M.given.rows.run) },
      '/v1/workers/status': { body: WORKER_BODY },
    });
    const { container } = render(
      createElement(RunsList, { model: buildRunsReadModel(await fetchRuns(client)) }),
    );
    expect(container.textContent ?? '').not.toContain(FORBIDDEN_RUN_LABEL_VI);
    expect(FORBIDDEN_RUN_LABEL_VI).toBe(FIXTURE_M.expected.forbidden_string_check.string_vi);
  });

  it('an empty list is "chưa có đợt nào", not the forbidden phrase', async () => {
    const { client } = fixtureClient({
      '/v1/runs': { body: { as_of: 'T', storage_health: 'healthy', runs: [] } },
      '/v1/workers/status': { body: WORKER_BODY },
    });
    const model = buildRunsReadModel(await fetchRuns(client));
    const { container } = render(createElement(RunsList, { model }));
    expect(model.display_state).toBe('empty');
    expect(screen.getByTestId('runs-empty').textContent).toBe('Chưa có đợt nào.');
    expect(container.textContent ?? '').not.toContain(FORBIDDEN_RUN_LABEL_VI);
  });

  it('the limit-reached triple of fixture e is "đợt dừng sớm", never a failure', () => {
    // `final_state_expected`: status completed, outcome "partial hoặc complete",
    // stop_reason limit_reached — and the fixture's forbidden_effects forbid `failed`.
    expect(FIXTURE_E.final_state_expected['status']).toBe('completed');
    expect(FIXTURE_E.final_state_expected['stop_reason']).toBe('limit_reached');
    for (const outcome of ['partial', 'complete'] as const) {
      const model = buildRunsReadModel({
        runList: {
          as_of: 'T',
          storage_health: 'healthy',
          runs: [{ id: 'R', status: 'completed', outcome, stop_reason: 'limit_reached' }],
        },
        workerStatus: WORKER_BODY,
      });
      expect(model.runs[0]?.status_label?.label_vi).toBe(RUN_STATUS_LABELS.stopped_early.label_vi);
      expect(model.runs[0]?.status_label?.label_vi).not.toBe(RUN_STATUS_LABELS.run_failed.label_vi);
    }
  });

  it('the empty period of fixture d shows "không có nội dung phù hợp"', () => {
    expect(FIXTURE_D.expected.display_oracles.join(' ')).toContain('không có nội dung phù hợp');
    const model = buildRunsReadModel({
      runList: {
        as_of: 'T',
        storage_health: 'healthy',
        runs: [
          {
            id: 'R',
            status: 'completed',
            outcome: 'empty',
            stop_reason: null,
            empty_period_note: 'Kỳ rỗng: có coverage record, không có report (REQ-D57).',
          },
        ],
      },
      workerStatus: WORKER_BODY,
    });
    render(createElement(RunsList, { model }));
    expect(screen.getByTestId('run-status-label-R').textContent).toBe(
      RUN_STATUS_LABELS.no_matching_content.label_vi,
    );
    // The coverage record is visible even though the period produced no report.
    expect(screen.getByTestId('run-note-R').textContent).toContain('REQ-D57');
  });
});

// ---------------------------------------------------------------------------------
// 2. needs_user vs blocked
// ---------------------------------------------------------------------------------

describe('needs_user and blocked are told apart', () => {
  const runs = [
    { id: 'RNEEDS', status: 'needs_user', outcome: null, stop_reason: 'captcha' },
    {
      id: 'RBLOCK',
      status: 'blocked',
      outcome: null,
      stop_reason: 'source_blocked',
      unblock_condition_vi: 'Nguồn X mở lại truy cập cho phiên này.',
    },
  ];

  it('on the Runs list: resume appears on needs_user only', () => {
    const model = buildRunsReadModel({
      runList: { as_of: 'T', storage_health: 'healthy', runs },
      workerStatus: WORKER_BODY,
    });
    render(createElement(RunsList, { model }));
    expect(screen.getByTestId('action-ACT-resume-run-RNEEDS')).toBeInTheDocument();
    expect(screen.queryByTestId('action-ACT-resume-run-RBLOCK')).toBeNull();
    // Same label, different rows — so the distinguishing string has to be elsewhere.
    expect(screen.getByTestId('run-status-label-RNEEDS').textContent).toBe(
      screen.getByTestId('run-status-label-RBLOCK').textContent,
    );
    expect(screen.getByTestId('run-note-RBLOCK').textContent).toBe(
      'Nguồn X mở lại truy cập cho phiên này.',
    );
    expect(screen.getByTestId('run-note-RNEEDS').textContent).toBe('—');
  });

  it('on Run detail: blocked shows its unblock condition and no resume', () => {
    const blocked = buildRunDetailReadModel({ run: runs[1], delivery: {} });
    const { container } = render(createElement(RunDetail, { model: blocked }));
    expect(screen.queryByTestId('action-ACT-resume-run-detail')).toBeNull();
    expect(screen.getByTestId('unblock-condition').textContent).toBe(
      'Nguồn X mở lại truy cập cho phiên này.',
    );
    const blockedText = container.textContent ?? '';

    const needsUser = buildRunDetailReadModel({ run: runs[0], delivery: {} });
    const second = render(createElement(RunDetail, { model: needsUser }));
    expect(second.container.textContent ?? '').not.toBe(blockedText);
  });
});

// ---------------------------------------------------------------------------------
// 3. Delivery unknown is its own thing (I09, I13, AMD-B03)
// ---------------------------------------------------------------------------------

describe('delivery unknown', () => {
  const part = FIXTURE_B.expected.after_event_3.rows.delivery_part[0] ?? {};

  it('reads as "chưa xác định", never as sent or failed', async () => {
    const { client } = fixtureClient({
      '/v1/runs/': { body: { id: 'R', status: 'completed', outcome: 'complete' } },
      '/v1/deliveries/': {
        body: {
          state: 'unknown',
          parts: [{ id: part['id'], part_index: 0, state: part['state'] }],
        },
      },
    });
    const run = await client.get('/v1/runs/{run_id}', { path: { run_id: 'R' } });
    const delivery = await client.get('/v1/deliveries/{delivery_id}', {
      path: { delivery_id: 'D' },
    });
    const model = buildRunDetailReadModel({ run, delivery });
    const { container } = render(createElement(RunDetail, { model }));

    expect(screen.getByTestId('delivery-label').textContent).toBe('Chưa xác định — có thể đã gửi');
    expect(container.textContent ?? '').not.toContain('Đã gửi Telegram');
    expect(container.textContent ?? '').not.toContain('Không gửi được');
    // I09: the run stays complete; a Telegram problem is not a collection failure.
    expect(screen.getByTestId('run-status-label').textContent).toBe('completed');
  });

  it('offers the three decisions and states the duplicate risk first', () => {
    const model = buildRunDetailReadModel({
      run: { id: 'R', status: 'completed', outcome: 'complete' },
      delivery: { state: 'unknown', parts: [{ id: 'P1', part_index: 0, state: 'unknown' }] },
    });
    render(createElement(RunDetail, { model }));
    expect(screen.getByTestId('action-ACT-decide-unknown-delivery')).toBeInTheDocument();
    for (const decision of ['resend_accepting_duplicate_risk', 'mark_not_delivered', 'abandon']) {
      expect(screen.getByTestId(`decide-${decision}-P1`)).toBeInTheDocument();
    }
    expect(screen.getByTestId('duplicate-risk-P1').textContent ?? '').toContain('trùng');
  });

  it('the decision travels as an owner mutation with CSRF', async () => {
    const { client, calls } = fixtureClient({ '/v1/deliveries/': { body: {} } });
    await decideUnknownDelivery(client, '01JDPART000000000000000000', 'mark_not_delivered');
    expect(calls[0]?.url).toBe('/v1/deliveries/parts/01JDPART000000000000000000/decide');
    const headers = (calls[0]?.init.headers ?? {}) as Record<string, string>;
    expect(headers['X-CSRF-Token']).toBe('c'.repeat(32));
    expect(JSON.parse(String(calls[0]?.init.body))).toEqual({
      decision: 'mark_not_delivered',
    });
  });

  it('sent parts plus one unknown part still read as unknown (DP-03)', () => {
    const model = buildRunDetailReadModel({
      run: { id: 'R', status: 'completed', outcome: 'complete' },
      delivery: {
        parts: [
          { id: 'P0', part_index: 0, state: 'sent' },
          { id: 'P1', part_index: 1, state: 'unknown' },
        ],
      },
    });
    expect(model.delivery.state).toBe('unknown');
    expect(model.delivery.label?.label_vi).toBe('Chưa xác định — có thể đã gửi');
  });
});

// ---------------------------------------------------------------------------------
// 4. Mutations from the screen, and the two failure modes the card names
// ---------------------------------------------------------------------------------

describe('actions and failures', () => {
  it('"Chạy ngay" sends the CSRF header the contract requires', async () => {
    const { client, calls } = fixtureClient({ '/v1/runs/run-now': { body: {} } });
    const model = buildRunsReadModel({
      runList: {
        as_of: 'T',
        storage_health: 'healthy',
        runs: [{ id: 'R', status: 'running', outcome: null, stop_reason: null }],
      },
      workerStatus: WORKER_BODY,
    });
    render(
      createElement(RunsList, {
        model,
        onAction: (action) => {
          if (action.operation_id === 'run.run_now') void runNow(client);
        },
      }),
    );
    const button = screen.getByTestId('action-ACT-run-now-from-runs-R');
    expect(button).toBeEnabled();
    button.click();
    await Promise.resolve();
    const headers = (calls[0]?.init.headers ?? {}) as Record<string, string>;
    expect(headers['X-CSRF-Token']).toBe('c'.repeat(32));
  });

  it('write_blocked disables every action with a readable reason (UI-03)', () => {
    const model = buildRunsReadModel({
      runList: {
        as_of: '2026-09-07T02:00:00.000Z',
        storage_health: 'write_blocked',
        runs: [{ id: 'R', status: 'running', outcome: null, stop_reason: null }],
      },
      workerStatus: WORKER_BODY,
    });
    render(createElement(RunsList, { model }));
    const button = screen.getByTestId('action-ACT-run-now-from-runs-R');
    expect(button).toBeDisabled();
    expect(button.getAttribute('title') ?? '').toContain('write_blocked');
    expect(screen.getByTestId('storage-notice').textContent ?? '').toContain(
      '2026-09-07T02:00:00.000Z',
    );
  });

  it('UNAUTHORIZED sends the user to the login screen; CSRF_REJECTED does not', () => {
    const unauthorized = buildRunsReadModel({
      error: new ApiError(401, 'GET /v1/runs', {
        code: 'UNAUTHORIZED',
        scope: 'request',
        retry_class: 'none',
        message_safe: 'Phiên không hợp lệ.',
        correlation_id: '01JERR00000000000000000000',
      }),
    });
    expect(unauthorized.display_state).toBe('error');
    expect(unauthorized.error_redirect_to).toBe('SCR-login');

    const csrf = buildRunsReadModel({
      error: new ApiError(403, 'POST /v1/runs/run-now', {
        code: 'CSRF_REJECTED',
        scope: 'request',
        retry_class: 'none',
        message_safe: 'Yêu cầu không hợp lệ.',
        correlation_id: '01JERR00000000000000000001',
      }),
    });
    expect(csrf.error_redirect_to).toBeNull();
    render(createElement(RunsList, { model: csrf }));
    expect(screen.getByTestId('runs-error').textContent).toBe('Yêu cầu không hợp lệ.');
  });

  it('a failed read keeps the cached list and labels it with as_of', () => {
    const model = buildRunsReadModel({
      runList: {
        as_of: '2026-09-07T02:00:00.000Z',
        storage_health: 'healthy',
        runs: [{ id: 'R', status: 'completed', outcome: 'empty', stop_reason: null }],
      },
      error: new ApiError(500, 'GET /v1/runs', null),
    });
    expect(model.display_state).toBe('error');
    expect(model.runs).toHaveLength(1);
    render(createElement(RunsList, { model }));
    expect(screen.getByTestId('as-of-value').textContent).toBe('2026-09-07T02:00:00.000Z');
  });
});

// ---------------------------------------------------------------------------------
// 5. Recorded responses from the real backends (CR-TC-uiruns-02)
// ---------------------------------------------------------------------------------
//
// `contracts/http/openapi.yaml` types these four bodies as `GenericObject`, so no schema
// says what their keys are and the read model above was written against the FIELD NAMES of
// `contracts/ui/screens.yaml §read_model`. The bodies below are not invented: they were
// recorded by driving the servers W6A and W5C actually wrote —
// `server/app/jobs/router.py` (sha256 285da7b65243e730…) and
// `server/app/delivery/router.py` (sha256 37482f0689eba2b8…) — through
// `fastapi.testclient.TestClient` over a throwaway migrated SQLite file, logged in as the
// owner, on 2026-09-07. The capture script lives in the worker's scratch directory and
// wrote nothing under `server/`; it is quoted in the handoff.
//
// Recording them found four real disagreements, all now absorbed by the read model:
//   1. a run row is keyed `run_id`, not `id`;
//   2. `run.list` / `run.get` send NEITHER `as_of` NOR `storage_health`, which UI-01
//      requires of every business screen;
//   3. `worker.get_status` answers `{"workers": [...]}` with per-row `online_state` /
//      `last_run_at`, not the two flat fields `screens.yaml` names;
//   4. a delivery part is keyed `delivery_part_id`, not `id`.
// Fields 2 is reported, not papered over: the model shows "—" rather than "healthy".

const RECORDED = {
  runList: {
    runs: [
      {
        run_id: '01JRVNE0000000000000000000',
        trigger_type: 'scheduled',
        phase: 'collecting',
        status: 'blocked',
        outcome: null,
        stop_reason: 'source_blocked',
        created_at: '2026-09-07T04:00:00.000Z',
        attempt_count: 1,
        schedule_occurrence_ids: [],
        catch_up_window: null,
        posts_observed_total: 200,
        posts_ingested_new: 187,
        limit_hit: false,
        limit_kind: null,
        cursor_invalidated: false,
        x_coverage_note_vi: null,
        unblock_condition_vi: 'Nguồn X mở lại truy cập cho phiên này.',
        last_error_code: null,
      },
      {
        run_id: '01JRVND0000000000000000000',
        trigger_type: 'scheduled',
        phase: 'collecting',
        status: 'needs_user',
        outcome: null,
        stop_reason: 'captcha',
        created_at: '2026-09-07T03:00:00.000Z',
        attempt_count: 1,
        schedule_occurrence_ids: [],
        catch_up_window: null,
        posts_observed_total: 200,
        posts_ingested_new: 187,
        limit_hit: false,
        limit_kind: null,
        cursor_invalidated: false,
        x_coverage_note_vi: null,
        unblock_condition_vi: null,
        last_error_code: null,
      },
      {
        run_id: '01JRVNC0000000000000000000',
        trigger_type: 'scheduled',
        phase: 'collecting',
        status: 'failed',
        outcome: 'failed',
        stop_reason: 'source_blocked',
        created_at: '2026-09-07T02:00:00.000Z',
        attempt_count: 1,
        schedule_occurrence_ids: [],
        catch_up_window: null,
        posts_observed_total: 200,
        posts_ingested_new: 187,
        limit_hit: false,
        limit_kind: null,
        cursor_invalidated: false,
        x_coverage_note_vi: null,
        unblock_condition_vi: null,
        last_error_code: null,
      },
      {
        run_id: '01JRVNB0000000000000000000',
        trigger_type: 'scheduled',
        phase: 'reporting',
        status: 'completed',
        outcome: 'partial',
        stop_reason: 'limit_reached',
        created_at: '2026-09-07T01:00:00.000Z',
        attempt_count: 1,
        schedule_occurrence_ids: [],
        catch_up_window: null,
        posts_observed_total: 200,
        posts_ingested_new: 187,
        limit_hit: true,
        limit_kind: 'posts',
        cursor_invalidated: false,
        x_coverage_note_vi: 'Đạt giới hạn 200 bài; phần feed sau mốc đó KHÔNG được quan sát.',
        unblock_condition_vi: null,
        last_error_code: null,
      },
      {
        run_id: '01JRVNA0000000000000000000',
        trigger_type: 'scheduled',
        phase: 'reporting',
        status: 'completed',
        outcome: 'empty',
        stop_reason: null,
        created_at: '2026-09-07T00:00:00.000Z',
        attempt_count: 1,
        schedule_occurrence_ids: [],
        catch_up_window: null,
        posts_observed_total: 0,
        posts_ingested_new: 0,
        limit_hit: false,
        limit_kind: null,
        cursor_invalidated: false,
        x_coverage_note_vi: null,
        unblock_condition_vi: null,
        last_error_code: null,
      },
    ],
  } as const,
  runGet: {
    run_id: '01JRVNB0000000000000000000',
    trigger_type: 'scheduled',
    phase: 'reporting',
    status: 'completed',
    outcome: 'partial',
    stop_reason: 'limit_reached',
    created_at: '2026-09-07T01:00:00.000Z',
    attempt_count: 1,
    schedule_occurrence_ids: [],
    catch_up_window: null,
    posts_observed_total: 200,
    posts_ingested_new: 187,
    limit_hit: true,
    limit_kind: 'posts',
    cursor_invalidated: false,
    x_coverage_note_vi: 'Đạt giới hạn 200 bài; phần feed sau mốc đó KHÔNG được quan sát.',
    unblock_condition_vi: null,
    last_error_code: null,
    applied_config: {},
  } as const,
  workerStatus: {
    workers: [],
  } as const,
  deliveryGetStatus: {
    delivery_id: '01JDE11V100000000000000000',
    report_id: '01JREP0RT10000000000000000',
    channel: 'telegram',
    state: 'unknown',
    status_label: 'unknown',
    attempt_count: 1,
    telegram_link_generation: 3,
    created_at: '2026-09-07T02:00:00.000Z',
    updated_at: '2026-09-07T02:10:31.500Z',
    parts: [
      {
        delivery_part_id: '01JDPART0SENT0000000000000',
        part_index: 0,
        state: 'sent',
        payload_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
        provider_message_id: '9001',
        updated_at: '2026-09-07T02:10:31.500Z',
      },
      {
        delivery_part_id: '01JDPART000000000000000000',
        part_index: 1,
        state: 'unknown',
        payload_hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
        provider_message_id: null,
        updated_at: '2026-09-07T02:10:31.500Z',
      },
    ],
  } as const,
};

/** The keys the read model actually reads. A rename of any of these breaks the screens. */
const RELIED_ON = {
  run: [
    'run_id',
    'status',
    'outcome',
    'stop_reason',
    'phase',
    'trigger_type',
    'posts_observed_total',
    'posts_ingested_new',
    'unblock_condition_vi',
    'x_coverage_note_vi',
  ],
  runDetailOnly: ['applied_config'],
  workerStatus: ['workers'],
  worker: ['online_state', 'last_run_at'],
  delivery: ['state', 'parts'],
  deliveryPart: ['delivery_part_id', 'part_index', 'state'],
};

describe('recorded backend responses', () => {
  it('every field the read model relies on is present in the recorded bodies', () => {
    const row = RECORDED.runList.runs[0] as Record<string, unknown>;
    for (const key of RELIED_ON.run) expect(Object.keys(row), key).toContain(key);
    const detail = RECORDED.runGet as Record<string, unknown>;
    for (const key of [...RELIED_ON.run, ...RELIED_ON.runDetailOnly]) {
      expect(Object.keys(detail), key).toContain(key);
    }
    for (const key of RELIED_ON.workerStatus) {
      expect(Object.keys(RECORDED.workerStatus), key).toContain(key);
    }
    const del = RECORDED.deliveryGetStatus as Record<string, unknown>;
    for (const key of RELIED_ON.delivery) expect(Object.keys(del), key).toContain(key);
    const part = RECORDED.deliveryGetStatus.parts[0] as Record<string, unknown>;
    for (const key of RELIED_ON.deliveryPart) expect(Object.keys(part), key).toContain(key);
  });

  it('the three REQ-AC15 labels come out of the REAL run.list body', () => {
    const model = buildRunsReadModel({
      runList: RECORDED.runList,
      workerStatus: RECORDED.workerStatus,
    });
    expect(model.runs).toHaveLength(RECORDED.runList.runs.length);
    const byId = new Map(model.runs.map((run) => [run.id, run.status_label?.label_vi ?? null]));
    expect(byId.get('01JRVNA0000000000000000000')).toBe(
      RUN_STATUS_LABELS.no_matching_content.label_vi,
    );
    expect(byId.get('01JRVNB0000000000000000000')).toBe(RUN_STATUS_LABELS.stopped_early.label_vi);
    expect(byId.get('01JRVNC0000000000000000000')).toBe(RUN_STATUS_LABELS.run_failed.label_vi);
    expect(
      new Set([
        byId.get('01JRVNA0000000000000000000'),
        byId.get('01JRVNB0000000000000000000'),
        byId.get('01JRVNC0000000000000000000'),
      ]).size,
    ).toBe(3);
  });

  it('needs_user and blocked survive the real body with their affordances intact', () => {
    const model = buildRunsReadModel({
      runList: RECORDED.runList,
      workerStatus: RECORDED.workerStatus,
    });
    const needsUser = model.runs.find((run) => run.status === 'needs_user');
    const blocked = model.runs.find((run) => run.status === 'blocked');
    expect(needsUser?.attention.resume_available).toBe(true);
    expect(blocked?.attention.resume_available).toBe(false);
    expect(blocked?.unblock_condition_vi).toBe('Nguồn X mở lại truy cập cho phiên này.');
    expect(model.runs.map((run) => run.id)).not.toContain(null);
  });

  it('the real body carries no as_of and no storage_health, and the screen says so', () => {
    expect(Object.keys(RECORDED.runList)).not.toContain('as_of');
    expect(Object.keys(RECORDED.runList)).not.toContain('storage_health');
    const model = buildRunsReadModel({
      runList: RECORDED.runList,
      workerStatus: RECORDED.workerStatus,
    });
    // UI-01 is unmet by the backend. The UI reports the gap rather than inventing "healthy":
    expect(model.as_of).toBeNull();
    expect(model.storage_health).toBeNull();
    expect(model.storage.last_known).toBe(false);
    render(createElement(RunsList, { model }));
    expect(screen.getByTestId('storage-health-value').textContent).toBe('—');
    expect(screen.getByTestId('as-of-value').textContent).toBe('—');
  });

  it('an empty workers[] is rendered as "—", never as offline (I13)', () => {
    const model = buildRunsReadModel({
      runList: RECORDED.runList,
      workerStatus: RECORDED.workerStatus,
    });
    expect(model.collector_online_state).toBeNull();
    render(createElement(RunsList, { model }));
    expect(screen.getByTestId('collector-online-state').textContent).toBe('—');
    expect(screen.getByTestId('collector-online-state').textContent).not.toBe('offline');
  });

  it('a worker row is read from workers[] when one is registered', () => {
    const model = buildRunsReadModel({
      runList: RECORDED.runList,
      workerStatus: {
        workers: [
          {
            worker_identity: 'W',
            worker_kind: 'collector',
            online_state: 'unknown',
            last_run_at: '2026-09-07T01:00:00.000Z',
          },
        ],
      },
    });
    expect(model.collector_online_state).toBe('unknown');
    expect(model.last_run_at).toBe('2026-09-07T01:00:00.000Z');
  });

  it('the REAL run.get and delivery.get_status drive the Run detail screen', () => {
    const model = buildRunDetailReadModel({
      run: RECORDED.runGet,
      delivery: RECORDED.deliveryGetStatus,
    });
    expect(model.id).toBe('01JRVNB0000000000000000000');
    expect(model.status_label?.label_vi).toBe(RUN_STATUS_LABELS.stopped_early.label_vi);
    // `coverage_limitation_note` is not a key the server sends; `x_coverage_note_vi` is.
    expect(model.coverage_limitation_note).toBe(RECORDED.runGet.x_coverage_note_vi);
    // DP-03 through the real parts: one `sent` and one `unknown` aggregate to `unknown`.
    expect(model.delivery.state).toBe('unknown');
    expect(model.delivery.label?.label_vi).toBe('Chưa xác định — có thể đã gửi');
    expect(model.delivery.undecided_parts.map((part) => part.id)).toEqual([
      '01JDPART000000000000000000',
    ]);
    expect(model.actions.map((action) => action.operation_id)).toContain('delivery.decide_unknown');
    const { container } = render(createElement(RunDetail, { model }));
    // The AGGREGATE must not read as sent (I13). The part that really was sent still says
    // so — DP-01 gives every part its own receipt, and hiding that would be the opposite
    // error: two parts, two truths, shown separately.
    expect(screen.getByTestId('delivery-label').textContent).toBe('Chưa xác định — có thể đã gửi');
    expect(screen.getByTestId('delivery-part-label-01JDPART0SENT0000000000000').textContent).toBe(
      'Đã gửi Telegram',
    );
    expect(screen.getByTestId('delivery-part-label-01JDPART000000000000000000').textContent).toBe(
      'Chưa xác định — có thể đã gửi',
    );
    expect(container.textContent ?? '').not.toContain(FORBIDDEN_RUN_LABEL_VI);
  });

  it('run.get sends none of the other SCR-run-detail diagnostic fields', () => {
    // Reported as CR-TC-uiruns-07 rather than defaulted to a number that would read as
    // "zero items collected" when the truth is "the server did not say".
    for (const key of [
      'items_collected',
      'items_new',
      'checkpoint',
      'errors',
      'alert_intent_count',
      'delivery_status',
    ]) {
      expect(Object.keys(RECORDED.runGet), key).not.toContain(key);
    }
    const model = buildRunDetailReadModel({ run: RECORDED.runGet, delivery: {} });
    expect(model.items_collected).toBeNull();
    expect(model.items_new).toBeNull();
    expect(model.checkpoint).toBeNull();
    expect(model.alert_intent_count).toBeNull();
    expect(model.errors).toEqual([]);
  });
});
