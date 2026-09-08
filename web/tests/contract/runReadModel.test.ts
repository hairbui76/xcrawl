// Contract test for the Runs read model: state → view.
//
// Every assertion here reads a contract file from `contracts/` (or a fixture from
// `acceptance/fixtures/`) at run time and compares it with what `src/lib/runState.ts`,
// `src/lib/api.ts` and `src/routes/*.ts` believe. Nothing is compared against a literal
// this test wrote down, because a literal copied twice drifts silently; a file read twice
// cannot. The wire contract is YAML rather than JSON Schema for these bodies, so the
// contract's own text is the oracle and the parsing below is deliberately narrow — a
// contract change that breaks the parse fails the test rather than passing it.

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import type { ApiPath, RequiredHeaders } from '../../src/lib/api';
import {
  ApiClient,
  MissingCsrfTokenError,
  OPERATION_PATHS,
  SCHEMA_VERSION,
  newUlid,
} from '../../src/lib/api';
import {
  COLLECTOR_ONLINE_STATES,
  DELIVERY_PART_STATES,
  DELIVERY_STATES,
  DELIVERY_STATUS_LABELS,
  DISPLAY_STATES,
  ERROR_OBLIGATIONS,
  FORBIDDEN_RUN_LABEL_VI,
  RUN_OUTCOMES,
  RUN_PHASES,
  RUN_STATUSES,
  RUN_STATUS_LABELS,
  STOP_REASONS,
  STORAGE_HEALTHS,
  TERMINAL_RUN_STATUSES,
  TRIGGER_TYPES,
  UNKNOWN_DECISIONS,
  aggregateDeliveryState,
  deliveryStatusLabel,
  runAttention,
  runStatusLabel,
  storageNotice,
} from '../../src/lib/runState';
import { SCR_RUNS_ACTIONS, buildRunsReadModel } from '../../src/routes/runs';
import { SCR_RUN_DETAIL_ACTIONS, buildRunDetailReadModel } from '../../src/routes/runDetail';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(HERE, '../..');
const REPO_ROOT = resolve(WEB_ROOT, '..');

const read = (relative: string): string => readFileSync(resolve(REPO_ROOT, relative), 'utf8');

const RUN_YAML = read('contracts/state/run.yaml');
const DELIVERY_YAML = read('contracts/state/delivery.yaml');
const STORAGE_YAML = read('contracts/state/storage.yaml');
const SCREENS_YAML = read('contracts/ui/screens.yaml');
const ENTITIES_YAML = read('contracts/data/entities.yaml');
const OPENAPI_YAML = read('contracts/http/openapi.yaml');
const FIXTURE_M = JSON.parse(
  read('acceptance/fixtures/telegram/m-three-run-states-distinct-text.json'),
) as {
  given: { rows: { run: Array<Record<string, unknown>> } };
  expected: {
    ui_labels: Array<{ run_id: string; label_vi: string }>;
    counts: { distinct_labels: number };
    forbidden_string_check: { string_vi: string; expected_occurrences: number };
  };
};

// ---------------------------------------------------------------------------------
// Narrow readers for the contract files
// ---------------------------------------------------------------------------------

/** `values: [a, b, c]` under `enums:` → `['a','b','c']`. */
function enumValues(yaml: string, name: string): string[] {
  const block = /\nenums:\n([\s\S]*?)\n[a-z_]+:/.exec(yaml);
  expect(block, `enums block of the contract`).not.toBeNull();
  const pattern = new RegExp(`\\n  ${name}:\\n(?:[^\\n]*\\n)*?    values: \\[([^\\]]*)\\]`);
  const found = pattern.exec(`\n${block?.[1] ?? ''}`);
  expect(found, `enums.${name}`).not.toBeNull();
  return (found?.[1] ?? '').split(',').map((value) => value.trim());
}

/** Every `label_vi` inside one named block of `screens.yaml §global_rules`. */
function labelBlock(name: string): string[] {
  const pattern = new RegExp(`\\n  ${name}:\\n([\\s\\S]*?)\\n  [a-z_]+:`);
  const block = pattern.exec(SCREENS_YAML);
  expect(block, `global_rules.${name}`).not.toBeNull();
  // `(?<![a-z_])` so `forbidden_label_vi` — the phrase each label must NOT be — is not
  // mistaken for the label itself.
  return [...(block?.[1] ?? '').matchAll(/(?<![a-z_])label_vi: "([^"]+)"/g)].map(
    (match) => match[1] ?? '',
  );
}

/** `id: ACT-…` + `operation_id: …` pairs inside one screen's `actions:` block. */
function screenActions(screenId: string): Array<{ id: string; operation_id: string }> {
  const screen = new RegExp(
    `\\n  - id: ${screenId}\\n([\\s\\S]*?)(?=\\n  - id: SCR-|\\ncoverage_matrix:)`,
  );
  const body = screen.exec(SCREENS_YAML);
  expect(body, `screen ${screenId}`).not.toBeNull();
  const actions = /\n {4}actions:\n([\s\S]*?)(?=\n {4}[a-z_]+:)/.exec(body?.[1] ?? '');
  expect(actions, `${screenId}.actions`).not.toBeNull();
  const text = actions?.[1] ?? '';
  const ids = [...text.matchAll(/\bid: (ACT-[A-Za-z0-9-]+)/g)].map((match) => match[1] ?? '');
  const operations = [...text.matchAll(/operation_id: ([A-Za-z_]+\.[A-Za-z_]+)/g)].map(
    (match) => match[1] ?? '',
  );
  expect(ids.length, `${screenId} action ids vs operation_ids`).toBe(operations.length);
  return ids.map((id, index) => ({ id, operation_id: operations[index] ?? '' }));
}

/** path → method → operationId, straight out of the wire contract. */
function openapiOperations(): Map<string, string> {
  const table = new Map<string, string>();
  let path: string | null = null;
  let method: string | null = null;
  for (const line of OPENAPI_YAML.split('\n')) {
    const pathMatch = /^ {2}(\/[^:]*):\s*$/.exec(line);
    if (pathMatch) {
      path = pathMatch[1] ?? null;
      method = null;
      continue;
    }
    const methodMatch = /^ {4}(get|post|put|patch|delete):\s*$/.exec(line);
    if (methodMatch) {
      method = methodMatch[1] ?? null;
      continue;
    }
    const operationMatch = /^ {6}operationId: (\S+)\s*$/.exec(line);
    if (operationMatch && path !== null && method !== null) {
      table.set(operationMatch[1] ?? '', `${method} ${path}`);
    }
  }
  return table;
}

function sourceFiles(directory: string): string[] {
  const out: string[] = [];
  const walk = (current: string): void => {
    for (const entry of readdirSync(current)) {
      const full = join(current, entry);
      if (statSync(full).isDirectory()) {
        if (entry !== 'generated' && entry !== 'node_modules') walk(full);
      } else if (/\.(ts|tsx)$/.test(entry)) {
        out.push(full);
      }
    }
  };
  walk(resolve(WEB_ROOT, directory));
  return out;
}

// ---------------------------------------------------------------------------------
// 1. Enum parity — the unions in runState.ts are the contract's enums
// ---------------------------------------------------------------------------------

describe('enums match contracts/state/*.yaml', () => {
  it.each([
    ['status', RUN_STATUSES],
    ['phase', RUN_PHASES],
    ['outcome', RUN_OUTCOMES],
    ['stop_reason', STOP_REASONS],
    ['trigger_type', TRIGGER_TYPES],
  ])('run.yaml enums.%s', (name, values) => {
    expect([...values]).toEqual(enumValues(RUN_YAML, name));
  });

  it('run.yaml terminal_states', () => {
    const found = /\nterminal_states: \[([^\]]*)\]/.exec(RUN_YAML);
    expect(found).not.toBeNull();
    expect([...TERMINAL_RUN_STATUSES]).toEqual(
      (found?.[1] ?? '').split(',').map((value) => value.trim()),
    );
  });

  it.each([
    ['delivery_state', DELIVERY_STATES],
    ['delivery_part_state', DELIVERY_PART_STATES],
    ['unknown_decision', UNKNOWN_DECISIONS],
  ])('delivery.yaml enums.%s', (name, values) => {
    expect([...values]).toEqual(enumValues(DELIVERY_YAML, name));
  });

  it('storage.yaml enums.storage_health', () => {
    expect([...STORAGE_HEALTHS]).toEqual(enumValues(STORAGE_YAML, 'storage_health'));
  });

  it('entities.yaml ENT-worker-registration.online_state', () => {
    const found = /\{name: online_state,[^}]*constraints: "([^"]*)"/.exec(ENTITIES_YAML);
    expect(found).not.toBeNull();
    for (const value of COLLECTOR_ONLINE_STATES) {
      expect(found?.[1] ?? '', value).toContain(`\`${value}\``);
    }
  });

  it('screens.yaml five_display_states are exactly the five this app models', () => {
    const block = /\n {2}five_display_states:\n([\s\S]*?)\n {2}[a-z_]+:/.exec(SCREENS_YAML);
    const ids = [...(block?.[1] ?? '').matchAll(/\{id: ([a-z_]+),/g)].map((match) => match[1]);
    expect(ids).toEqual([...DISPLAY_STATES]);
  });
});

// ---------------------------------------------------------------------------------
// 2. Label parity — every display string is the contract's, character for character
// ---------------------------------------------------------------------------------

describe('display strings come from contracts/ui/screens.yaml', () => {
  it('run_status_labels', () => {
    expect(labelBlock('run_status_labels')).toEqual([
      RUN_STATUS_LABELS.no_matching_content.label_vi,
      RUN_STATUS_LABELS.stopped_early.label_vi,
      RUN_STATUS_LABELS.run_failed.label_vi,
    ]);
  });

  it('delivery_status_labels', () => {
    expect(labelBlock('delivery_status_labels')).toEqual([
      DELIVERY_STATUS_LABELS.delivery_sent.label_vi,
      DELIVERY_STATUS_LABELS.delivery_pending.label_vi,
      DELIVERY_STATUS_LABELS.delivery_unknown.label_vi,
      DELIVERY_STATUS_LABELS.delivery_failed.label_vi,
      DELIVERY_STATUS_LABELS.delivery_cancelled.label_vi,
    ]);
  });

  it('the phrase SRC-SPEC §8.3 forbids is the one the app refuses to use', () => {
    expect(SCREENS_YAML).toContain(`phrase_vi: "${FORBIDDEN_RUN_LABEL_VI}"`);
    expect(FORBIDDEN_RUN_LABEL_VI).toBe(FIXTURE_M.expected.forbidden_string_check.string_vi);
    expect(FIXTURE_M.expected.forbidden_string_check.expected_occurrences).toBe(0);
  });

  it('no view or read model contains the forbidden phrase', () => {
    for (const file of [...sourceFiles('src/views'), ...sourceFiles('src/routes')]) {
      expect(readFileSync(file, 'utf8'), file).not.toContain(FORBIDDEN_RUN_LABEL_VI);
    }
  });
});

// ---------------------------------------------------------------------------------
// 3. The state triple decides the label (I13, REQ-AC15)
// ---------------------------------------------------------------------------------

describe('state triple → label', () => {
  it('the three REQ-AC15 triples give the three fixture labels', () => {
    const labels = FIXTURE_M.given.rows.run.map((row) =>
      runStatusLabel({
        status: row['status'] as never,
        outcome: (row['outcome'] ?? null) as never,
        stop_reason: (row['stop_reason'] ?? null) as never,
      }),
    );
    expect(labels.map((label) => label?.label_vi ?? null)).toEqual(
      FIXTURE_M.expected.ui_labels.map((entry) => entry.label_vi),
    );
    expect(new Set(labels.map((label) => label?.label_vi)).size).toBe(
      FIXTURE_M.expected.counts.distinct_labels,
    );
  });

  it('the triples run.yaml §I13 names as distinct produce distinct labels', () => {
    // `contracts/state/run.yaml §invariants_owned I13.positive_oracle_vi`.
    const labels = [
      runStatusLabel({ status: 'completed', outcome: 'empty', stop_reason: null }),
      runStatusLabel({ status: 'completed', outcome: 'partial', stop_reason: 'limit_reached' }),
      runStatusLabel({ status: 'completed', outcome: 'complete', stop_reason: 'limit_reached' }),
      runStatusLabel({ status: 'failed', outcome: 'failed', stop_reason: 'source_blocked' }),
    ].map((label) => label?.label_vi);
    expect(labels[0]).toBe(RUN_STATUS_LABELS.no_matching_content.label_vi);
    expect(labels[1]).toBe(RUN_STATUS_LABELS.stopped_early.label_vi);
    expect(labels[2]).toBe(RUN_STATUS_LABELS.stopped_early.label_vi);
    expect(labels[3]).toBe(RUN_STATUS_LABELS.run_failed.label_vi);
    expect(new Set(labels).size).toBe(3);
  });

  it('needs_user and blocked share the label but never the affordances', () => {
    const needsUser = runAttention(
      { status: 'needs_user', outcome: null, stop_reason: 'captcha' },
      null,
    );
    const blocked = runAttention(
      { status: 'blocked', outcome: null, stop_reason: 'source_blocked' },
      'Đăng nhập lại nguồn X.',
    );
    expect(needsUser.resume_available).toBe(true);
    expect(needsUser.unblock_condition_vi).toBeNull();
    expect(blocked.resume_available).toBe(false);
    expect(blocked.unblock_condition_vi).toBe('Đăng nhập lại nguồn X.');
  });

  it('a state screens.yaml names no label for falls back to the machine value, not a phrase', () => {
    // CR-TC-uiruns-01: the table covers none of these.
    for (const status of ['queued', 'running', 'waiting_retry', 'cancelled'] as const) {
      expect(runStatusLabel({ status, outcome: null, stop_reason: null })).toBeNull();
    }
    expect(
      runStatusLabel({ status: 'completed', outcome: 'complete', stop_reason: null }),
    ).toBeNull();
  });
});

// ---------------------------------------------------------------------------------
// 4. Delivery is a separate dimension (I09, I13, DP-03)
// ---------------------------------------------------------------------------------

describe('delivery labels', () => {
  it('unknown is never sent and never failed', () => {
    const unknown = deliveryStatusLabel('unknown').label_vi;
    expect(unknown).toBe(DELIVERY_STATUS_LABELS.delivery_unknown.label_vi);
    expect(unknown).not.toBe(DELIVERY_STATUS_LABELS.delivery_sent.label_vi);
    expect(unknown).not.toBe(DELIVERY_STATUS_LABELS.delivery_failed.label_vi);
  });

  it('every delivery state has its own label and all five labels are distinct', () => {
    const labels = DELIVERY_STATES.map((state) => deliveryStatusLabel(state).label_vi);
    expect(new Set(labels).size).toBe(Object.keys(DELIVERY_STATUS_LABELS).length);
  });

  it('DP-03: one unknown part outranks any number of sent parts', () => {
    expect(aggregateDeliveryState(['sent', 'sent', 'unknown'])).toBe('unknown');
    expect(aggregateDeliveryState(['sent', 'failed'])).toBe('failed');
    expect(aggregateDeliveryState(['sent', 'sent'])).toBe('sent');
    expect(aggregateDeliveryState([])).toBeNull();
  });

  it('DP-03 precedence is the contract sentence, in order', () => {
    const found = /precedence_vi: "([a-z_ >]+)/.exec(DELIVERY_YAML);
    expect(found).not.toBeNull();
    const contractOrder = (found?.[1] ?? '').split('>').map((value) => value.trim());
    const ours = DELIVERY_STATES.map((state) => state).filter((state) =>
      contractOrder.includes(state),
    );
    const ranked = [...ours].sort((a, b) => contractOrder.indexOf(a) - contractOrder.indexOf(b));
    expect(ranked).toEqual(contractOrder);
  });
});

// ---------------------------------------------------------------------------------
// 5. Actions exist in the contract's action map (card §8, §5 default deny)
// ---------------------------------------------------------------------------------

describe('action map', () => {
  it('SCR-runs exposes exactly the contract actions', () => {
    const contract = screenActions('SCR-runs');
    expect(
      Object.values(SCR_RUNS_ACTIONS)
        .map((action) => action.id)
        .sort(),
    ).toEqual(contract.map((action) => action.id).sort());
    for (const action of Object.values(SCR_RUNS_ACTIONS)) {
      expect(contract, action.id).toContainEqual({
        id: action.id,
        operation_id: action.operation_id,
      });
    }
  });

  it('SCR-run-detail exposes exactly the contract actions', () => {
    const contract = screenActions('SCR-run-detail');
    expect(
      Object.values(SCR_RUN_DETAIL_ACTIONS)
        .map((action) => action.id)
        .sort(),
    ).toEqual(contract.map((action) => action.id).sort());
    for (const action of Object.values(SCR_RUN_DETAIL_ACTIONS)) {
      expect(contract, action.id).toContainEqual({
        id: action.id,
        operation_id: action.operation_id,
      });
    }
  });

  it('every operation the client can reach is one of the nine the card may consume', () => {
    // Card §4 "Consumes", verbatim and exhaustive.
    expect(Object.keys(OPERATION_PATHS).sort()).toEqual(
      [
        'delivery.decide_unknown',
        'delivery.get_status',
        'health.get_readiness',
        'run.cancel',
        'run.get',
        'run.list',
        'run.resume',
        'run.run_now',
        'worker.get_status',
      ].sort(),
    );
  });

  it('each operation sits at the path and method the wire contract gives it', () => {
    const contract = openapiOperations();
    for (const [operationId, entry] of Object.entries(OPERATION_PATHS)) {
      expect(contract.get(operationId), operationId).toBe(`${entry.method} ${entry.path}`);
    }
  });
});

// ---------------------------------------------------------------------------------
// 6. Session and CSRF (card §5, §7)
// ---------------------------------------------------------------------------------

/** Compile-time: the wire contract requires `X-CSRF-Token` on a mutation and not on a read. */
type Expect<T extends true> = T;
type RequiresCsrf<
  P extends ApiPath,
  M extends 'get' | 'post',
> = 'X-CSRF-Token' extends keyof RequiredHeaders<P, M> ? true : false;

export type AssertRunNowCsrf = Expect<RequiresCsrf<'/v1/runs/run-now', 'post'>>;
export type AssertResumeCsrf = Expect<RequiresCsrf<'/v1/runs/{run_id}/resume', 'post'>>;
export type AssertCancelCsrf = Expect<RequiresCsrf<'/v1/runs/{run_id}/cancel', 'post'>>;
export type AssertDecideCsrf = Expect<
  RequiresCsrf<'/v1/deliveries/parts/{delivery_part_id}/decide', 'post'>
>;
export type AssertRunListHasNoCsrf = Expect<
  RequiresCsrf<'/v1/runs', 'get'> extends false ? true : false
>;

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

function recordingClient(status = 200, body: unknown = {}, csrf: string | null = 'x'.repeat(32)) {
  const calls: Call[] = [];
  const client = new ApiClient({
    fetch: ((url: string, init: RequestInit) => {
      calls.push({ url, init });
      return Promise.resolve(jsonResponse(status, body));
    }) as unknown as typeof globalThis.fetch,
    readCookie: () => csrf,
  });
  return { client, calls };
}

function headerOf(call: Call | undefined, name: string): string | undefined {
  const headers = (call?.init.headers ?? {}) as Record<string, string>;
  return headers[name];
}

describe('owner session transport', () => {
  it('sends the schema version the wire contract declares', () => {
    const info = /\ninfo:\n(?:[^\n]*\n)*? {2}version: (\S+)/.exec(OPENAPI_YAML);
    expect(info).not.toBeNull();
    expect(SCHEMA_VERSION).toBe(info?.[1]);
  });

  it('a read sends the session cookie and no CSRF header', async () => {
    const { client, calls } = recordingClient();
    await client.get('/v1/runs');
    expect(calls[0]?.init.credentials).toBe('include');
    expect(headerOf(calls[0], 'X-CSRF-Token')).toBeUndefined();
    expect(headerOf(calls[0], 'X-Schema-Version')).toBe(SCHEMA_VERSION);
    expect(headerOf(calls[0], 'X-Request-Id')).toMatch(/^[0-9A-HJKMNP-TV-Z]{26}$/);
  });

  function expectOwnerMutation(call: Call | undefined, url: string): void {
    expect(call?.url).toBe(url);
    expect(headerOf(call, 'X-CSRF-Token')).toBe('x'.repeat(32));
    expect(headerOf(call, 'Idempotency-Key')).toMatch(/^[A-Za-z0-9_.:-]{16,128}$/);
    expect(headerOf(call, 'X-Schema-Version')).toBe(SCHEMA_VERSION);
    expect(call?.init.credentials).toBe('include');
  }

  it('run.run_now carries X-CSRF-Token and Idempotency-Key', async () => {
    const { client, calls } = recordingClient();
    await client.mutate('/v1/runs/run-now', { body: {} });
    expectOwnerMutation(calls[0], '/v1/runs/run-now');
  });

  it('run.resume carries X-CSRF-Token and Idempotency-Key', async () => {
    const { client, calls } = recordingClient();
    await client.mutate('/v1/runs/{run_id}/resume', {
      path: { run_id: '01JRVNA0000000000000000000' },
      body: {},
    });
    expectOwnerMutation(calls[0], '/v1/runs/01JRVNA0000000000000000000/resume');
  });

  it('run.cancel carries X-CSRF-Token and Idempotency-Key', async () => {
    const { client, calls } = recordingClient();
    await client.mutate('/v1/runs/{run_id}/cancel', {
      path: { run_id: '01JRVNA0000000000000000000' },
      body: {},
    });
    expectOwnerMutation(calls[0], '/v1/runs/01JRVNA0000000000000000000/cancel');
  });

  it('delivery.decide_unknown carries X-CSRF-Token and Idempotency-Key', async () => {
    const { client, calls } = recordingClient();
    await client.mutate('/v1/deliveries/parts/{delivery_part_id}/decide', {
      path: { delivery_part_id: '01JDPART000000000000000000' },
      body: { decision: 'abandon' },
    });
    expectOwnerMutation(calls[0], '/v1/deliveries/parts/01JDPART000000000000000000/decide');
  });

  it('refuses to send a mutation when the CSRF cookie is unreadable', async () => {
    const { client, calls } = recordingClient(200, {}, null);
    await expect(client.mutate('/v1/runs/run-now', { body: {} })).rejects.toBeInstanceOf(
      MissingCsrfTokenError,
    );
    expect(calls).toHaveLength(0);
  });

  it('newUlid matches components.schemas.Ulid', () => {
    const pattern = /\n {4}Ulid:\n {6}type: string\n {6}pattern: (\S+)/.exec(OPENAPI_YAML);
    expect(pattern).not.toBeNull();
    const contractPattern = new RegExp(pattern?.[1] ?? '');
    for (let i = 0; i < 50; i += 1) expect(newUlid()).toMatch(contractPattern);
  });

  it('surfaces the envelope without inventing a code, and leaks nothing into the message', async () => {
    const envelope = {
      code: 'CSRF_REJECTED',
      scope: 'request',
      retry_class: 'none',
      message_safe: 'Yêu cầu không hợp lệ.',
      correlation_id: '01JERR00000000000000000000',
      details_safe: { cookie: 'super-secret-value' },
    };
    const { client } = recordingClient(403, envelope);
    await client.mutate('/v1/runs/run-now', { body: {} }).then(
      () => expect.unreachable('403 must reject'),
      (error: unknown) => {
        const apiError = error as { code: string; message: string };
        expect(apiError.code).toBe('CSRF_REJECTED');
        expect(apiError.message).not.toContain('super-secret-value');
        expect(apiError.message).toContain('01JERR00000000000000000000');
      },
    );
  });
});

// ---------------------------------------------------------------------------------
// 7. Error obligations (card §7)
// ---------------------------------------------------------------------------------

describe('error obligations', () => {
  it('UNAUTHORIZED goes to the login screen; CSRF_REJECTED does not end the session', () => {
    expect(ERROR_OBLIGATIONS['UNAUTHORIZED']).toEqual({
      redirect_to: 'SCR-login',
      end_session: true,
      banner_vi: null,
    });
    expect(ERROR_OBLIGATIONS['CSRF_REJECTED']?.end_session).toBe(false);
    expect(ERROR_OBLIGATIONS['CSRF_REJECTED']?.redirect_to).toBeNull();
    expect(ERROR_OBLIGATIONS['NOT_FOUND']?.redirect_to).toBe('SCR-not-found');
    expect(ERROR_OBLIGATIONS['STORAGE_WRITE_FAILED']?.banner_vi).toBe('Chưa lưu được');
  });

  it('every code named in the card is a code of contracts/errors.yaml', () => {
    const errors = read('contracts/errors.yaml');
    for (const code of Object.keys(ERROR_OBLIGATIONS)) {
      expect(errors, code).toContain(`- code: ${code}`);
    }
  });
});

// ---------------------------------------------------------------------------------
// 8. Storage health is the fifth dimension (UI-01..UI-04)
// ---------------------------------------------------------------------------------

describe('storage health', () => {
  it('healthy adds no banner; anything else labels the data last-known with as_of', () => {
    expect(storageNotice('healthy', '2026-09-07T02:00:00.000Z')).toEqual({
      last_known: false,
      reason_vi: null,
    });
    for (const health of ['write_blocked', 'maintenance', 'recovery_required'] as const) {
      const notice = storageNotice(health, '2026-09-07T02:00:00.000Z');
      expect(notice.last_known).toBe(true);
      expect(notice.reason_vi).toContain('2026-09-07T02:00:00.000Z');
      expect(notice.reason_vi).toContain(health);
    }
  });

  it('UI-04: a completed/empty run read during write_blocked is still empty', () => {
    const model = buildRunsReadModel({
      runList: {
        as_of: '2026-09-07T02:00:00.000Z',
        storage_health: 'write_blocked',
        runs: [{ id: 'R1', status: 'completed', outcome: 'empty', stop_reason: null }],
      },
      workerStatus: { collector_online_state: 'unknown', last_run_at: null },
    });
    expect(model.display_state).toBe('stale_last_known');
    expect(model.runs[0]?.outcome).toBe('empty');
    expect(model.runs[0]?.status_label?.label_vi).toBe(
      RUN_STATUS_LABELS.no_matching_content.label_vi,
    );
    // UI-03: disabled, with a readable reason — not silently inert.
    expect(model.runs[0]?.actions_disabled_reason_vi).toBe(model.storage.reason_vi);
  });

  it('UI-01: as_of and storage_health are always in the read model', () => {
    const model = buildRunsReadModel({});
    expect(model).toHaveProperty('as_of');
    expect(model).toHaveProperty('storage_health');
    expect(model.display_state).toBe('loading');
  });
});

// ---------------------------------------------------------------------------------
// 9. Run detail read model
// ---------------------------------------------------------------------------------

describe('run detail read model', () => {
  it('needs_user offers resume, blocked offers the unblock condition instead', () => {
    const needsUser = buildRunDetailReadModel({
      run: { id: 'R1', status: 'needs_user', outcome: null, stop_reason: 'captcha' },
      delivery: {},
    });
    expect(needsUser.actions.map((action) => action.operation_id)).toContain('run.resume');
    expect(needsUser.attention.unblock_condition_vi).toBeNull();

    const blocked = buildRunDetailReadModel({
      run: {
        id: 'R2',
        status: 'blocked',
        outcome: null,
        stop_reason: 'source_blocked',
        unblock_condition_vi: 'Nguồn X mở lại truy cập.',
      },
      delivery: {},
    });
    expect(blocked.actions.map((action) => action.operation_id)).not.toContain('run.resume');
    expect(blocked.attention.unblock_condition_vi).toBe('Nguồn X mở lại truy cập.');
  });

  it('a terminal run offers no cancel', () => {
    const model = buildRunDetailReadModel({
      run: { id: 'R3', status: 'completed', outcome: 'complete', stop_reason: null },
      delivery: {},
    });
    expect(model.actions).toHaveLength(0);
  });

  it('delivery unknown offers decide_unknown and states the duplicate risk', () => {
    const model = buildRunDetailReadModel({
      run: { id: 'R4', status: 'completed', outcome: 'complete', stop_reason: null },
      delivery: {
        state: 'unknown',
        parts: [{ id: 'P1', part_index: 0, state: 'unknown' }],
      },
    });
    expect(model.delivery.label?.label_vi).toBe(DELIVERY_STATUS_LABELS.delivery_unknown.label_vi);
    expect(model.actions.map((action) => action.operation_id)).toContain('delivery.decide_unknown');
    expect(model.delivery.undecided_parts.map((part) => part.id)).toEqual(['P1']);
    expect(model.delivery.duplicate_risk_warning_vi).not.toBeNull();
    // I09: the run itself is untouched by the delivery problem.
    expect(model.status_label).toBeNull();
    expect(model.outcome).toBe('complete');
  });
});

// ---------------------------------------------------------------------------------
// 10. Default deny for MOD-web-ui (SG-DENY, SC49, FE-01…FE-04)
// ---------------------------------------------------------------------------------

describe('forbidden edges of MOD-web-ui', () => {
  const files = [
    ...sourceFiles('src/lib'),
    ...sourceFiles('src/routes'),
    ...sourceFiles('src/views'),
  ];

  it('the app opens no connection outside its own origin (FE-03, FE-04)', () => {
    for (const file of files) {
      expect(readFileSync(file, 'utf8'), file).not.toMatch(/https?:\/\//);
    }
  });

  it('the app names no database, no secret operation and no provider (FE-01, FE-02)', () => {
    for (const file of files) {
      const text = readFileSync(file, 'utf8');
      expect(text, file).not.toContain('secret.issue_task_credential');
      expect(text, file).not.toContain('api.telegram.org');
      expect(text, file).not.toMatch(/\bsqlite\b/i);
    }
  });

  it('the client can only address the nine operations of card §4', () => {
    const contract = openapiOperations();
    const allowed = new Set(Object.keys(OPERATION_PATHS));
    for (const operationId of contract.keys()) {
      if (allowed.has(operationId)) continue;
      const entry = contract.get(operationId) ?? '';
      const path = entry.slice(entry.indexOf(' ') + 1);
      for (const value of Object.values(OPERATION_PATHS)) {
        expect(value.path, `${operationId} must not be reachable`).not.toBe(path);
      }
    }
  });
});
