// Owner-session HTTP client, typed from the generated wire contract.
//
// OWNERSHIP (CR-P0-04, agent-tasks/README.md §5.3): this file is owned by the two UI
// cards. `TC-ui-runs-three-states` writes it first; `TC-ui-reports-detail` EXTENDS it.
// The server half of the owner session (setting `rr_session` / `rr_csrf`, verifying
// `X-CSRF-Token`) belongs to `TC-owner-auth-session` and lives in `server/app/auth/`.
//
// Nothing wire-shaped is hand-written here: every path, method, path parameter, query
// parameter, request header and response body type below is *derived* from
// `src/generated/openapi.d.ts`, which `web/scripts/generate.mjs` produces from
// `contracts/http/openapi.yaml`. Adding an operation means changing the contract and
// regenerating, never editing a literal here.
//
// Security shape (contracts/http/openapi.yaml §components.securitySchemes, and §5 of the
// card): a read takes the HttpOnly cookie `rr_session` alone; a MUTATION takes that cookie
// AND the double-submit header `X-CSRF-Token` inside ONE security requirement — the cookie
// on its own is not enough. `mutate()` therefore refuses to issue a request when the
// non-HttpOnly cookie `rr_csrf` cannot be read, rather than sending a call that the server
// will answer with `CSRF_REJECTED`.

import type { components, paths } from '../generated/openapi';

/** Every path in `contracts/http/openapi.yaml`, as a union of string literals. */
export type ApiPath = keyof paths;

/** The error envelope of SRC-PLAN §5.1, copied into the wire contract. */
export type ErrorEnvelope = components['schemas']['ErrorEnvelope'];

/** The 28 codes of `contracts/errors.yaml`. Code never invents a 29th (card §7). */
export type ErrorCode = ErrorEnvelope['code'];

/**
 * The methods this client speaks.
 *
 * `delete` was added by `TC-ui-reports-detail`: `save.remove` is `DELETE
 * /v1/saved/{target_ref}` in the wire contract, so a client without it cannot reach an
 * operation that card's §4 allows. Widening the union is additive — `GetPath`, `PostPath`,
 * `RequiresCsrf` and `OPERATION_PATHS` all keep their previous meaning.
 */
export type HttpMethod = 'get' | 'post' | 'delete';

/**
 * `X-Schema-Version` is REQUIRED on every request and must not be `latest`
 * (openapi.yaml §components.parameters.SchemaVersionHeader). The value is the wire
 * contract's own `info.version`; `runReadModel.test.ts` asserts the two stay equal.
 */
export const SCHEMA_VERSION = '0.3.0';

/** HttpOnly session cookie (`ownerSessionCookie`). The page cannot read it — only send it. */
export const SESSION_COOKIE_NAME = 'rr_session';

/** Non-HttpOnly half of the double-submit pair; the page reads it to build the header. */
export const CSRF_COOKIE_NAME = 'rr_csrf';

/** `ownerCsrfToken` (openapi.yaml §components.parameters.CsrfTokenHeader). */
export const CSRF_HEADER_NAME = 'X-CSRF-Token';

// ---------------------------------------------------------------------------------
// Type derivation from the generated contract
// ---------------------------------------------------------------------------------

/** The operation object the generator emitted for `P` + `M`, or `never` when absent. */
export type Operation<P extends ApiPath, M extends HttpMethod> = paths[P][M] extends {
  responses: unknown;
}
  ? paths[P][M]
  : never;

/** Paths that expose a `GET` in the contract. */
export type GetPath = {
  [P in ApiPath]: [Operation<P, 'get'>] extends [never] ? never : P;
}[ApiPath];

/** Paths that expose a `POST` in the contract. */
export type PostPath = {
  [P in ApiPath]: [Operation<P, 'post'>] extends [never] ? never : P;
}[ApiPath];

type PathParams<Op> = Op extends { parameters: { path: infer X } } ? Exclude<X, undefined> : never;
type QueryParams<Op> = Op extends { parameters: { query?: infer X } }
  ? Exclude<X, undefined>
  : never;
type JsonBody<Op> = Op extends { requestBody: { content: { 'application/json': infer B } } }
  ? B
  : never;
type OkBody<Op> = Op extends { responses: { 200: { content: { 'application/json': infer R } } } }
  ? R
  : never;

/**
 * `contracts/http/openapi.yaml` types most owner bodies as `GenericObject` — an explicit
 * placeholder ("hình dạng chi tiết thuộc một gói khác và CHƯA tồn tại"), which the
 * generator renders as `Record<string, never>`, i.e. an object that may hold nothing.
 * Taken literally that type makes the placeholder unusable: no field could be sent or
 * read. So a placeholder body is widened to an open record here, and only here, with the
 * gap reported as CR-TC-uiruns-02. Every operation whose body IS closed in
 * the contract keeps its exact generated type.
 */
type OpenIfPlaceholder<B> = [B] extends [Record<string, never>] ? Record<string, unknown> : B;

/**
 * The request headers the contract declares REQUIRED for `P` + `M`.
 *
 * This is the structural home of the CSRF obligation: for a mutation the generated type
 * lists `X-CSRF-Token`, for a read it does not. `runReadModel.test.ts` asserts exactly
 * that at compile time, so an operation that silently loses its CSRF requirement in the
 * contract fails the build rather than the field.
 */
export type RequiredHeaders<P extends ApiPath, M extends HttpMethod> =
  Operation<P, M> extends { parameters: { header: infer H } } ? Exclude<H, undefined> : never;

type Empty = Record<string, never>;
type OrEmpty<T> = [T] extends [never] ? Empty : T;

/** Options of a read: path parameters when the operation has any, query when it has any. */
export type GetOptions<P extends GetPath> = {
  path?: OrEmpty<PathParams<Operation<P, 'get'>>>;
  query?: OrEmpty<QueryParams<Operation<P, 'get'>>>;
  signal?: AbortSignal;
};

/** Options of a mutation. `body` is the contract's request body; headers are automatic. */
export type MutateOptions<P extends PostPath> = {
  path?: OrEmpty<PathParams<Operation<P, 'post'>>>;
  body?: OrEmpty<OpenIfPlaceholder<JsonBody<Operation<P, 'post'>>>>;
  /** Overrides the generated key; pass the SAME key to replay a mutation (SRC-PLAN §5.1). */
  idempotencyKey?: string;
  signal?: AbortSignal;
};

/** Response body of a `GET` on `P` with status 200, straight from the contract. */
export type GetResponse<P extends GetPath> = OpenIfPlaceholder<OkBody<Operation<P, 'get'>>>;

/** Response body of a `POST` on `P` with status 200, straight from the contract. */
export type PostResponse<P extends PostPath> = OpenIfPlaceholder<OkBody<Operation<P, 'post'>>>;

// ---------------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------------

/**
 * A non-2xx answer, carrying the parsed envelope when the server sent one.
 *
 * `message` is built from `code` and `correlation_id` only. The envelope itself is
 * forbidden to contain a transcript, key or cookie (openapi.yaml §ErrorEnvelope), and
 * this class adds nothing to it, so an error surfaced to the user cannot leak one.
 */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly path: string,
    readonly envelope: ErrorEnvelope | null,
  ) {
    super(
      envelope === null
        ? `${path} → HTTP ${status}`
        : `${path} → HTTP ${status} ${envelope.code} (correlation_id ${envelope.correlation_id})`,
    );
    this.name = 'ApiError';
  }

  /** The contract code, or `null` when the response carried no envelope at all. */
  get code(): ErrorCode | null {
    return this.envelope === null ? null : this.envelope.code;
  }
}

/**
 * Raised instead of sending a mutation whose CSRF token could not be read.
 *
 * Sending it anyway would produce a `CSRF_REJECTED` round trip that looks like a server
 * fault; the real condition is a browser state (cookie missing or expired) the user has
 * to be told about.
 */
export class MissingCsrfTokenError extends Error {
  constructor() {
    super(`Cookie ${CSRF_COOKIE_NAME} is not readable; refusing to send an owner mutation.`);
    this.name = 'MissingCsrfTokenError';
  }
}

// ---------------------------------------------------------------------------------
// Identifiers
// ---------------------------------------------------------------------------------

/** Crockford base32, i.e. exactly the alphabet of `Ulid` in the wire contract. */
const CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

function randomBytes(count: number): Uint8Array {
  const out = new Uint8Array(count);
  const webCrypto = globalThis.crypto as Crypto | undefined;
  if (webCrypto !== undefined && typeof webCrypto.getRandomValues === 'function') {
    webCrypto.getRandomValues(out);
    return out;
  }
  // `X-Request-Id` and `Idempotency-Key` are correlation values, not secrets; a weaker
  // source is a degraded log, not a vulnerability. Kept so the client works in a runtime
  // without WebCrypto rather than failing a read.
  for (let i = 0; i < out.length; i += 1) out[i] = Math.floor(Math.random() * 256);
  return out;
}

/**
 * A ULID matching `components.schemas.Ulid` (`^[0-9A-HJKMNP-TV-Z]{26}$`): 48 bits of
 * millisecond timestamp then 80 bits of randomness, Crockford base32.
 */
export function newUlid(now: number = Date.now()): string {
  let time = '';
  let remaining = now;
  for (let i = 0; i < 10; i += 1) {
    time = CROCKFORD[remaining % 32] + time;
    remaining = Math.floor(remaining / 32);
  }
  const bytes = randomBytes(16);
  let random = '';
  for (let i = 0; i < 16; i += 1) random += CROCKFORD[(bytes[i] ?? 0) % 32];
  return time + random;
}

/** Reads a non-HttpOnly cookie from `document.cookie`; `null` when absent. */
export function readCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  for (const part of document.cookie.split(';')) {
    const separator = part.indexOf('=');
    if (separator < 0) continue;
    if (part.slice(0, separator).trim() !== name) continue;
    return decodeURIComponent(part.slice(separator + 1).trim());
  }
  return null;
}

// ---------------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------------

export interface ApiClientOptions {
  /**
   * Transport. Tests pass a function that answers from `acceptance/fixtures/**`, which is
   * why this card needs no running server: the fixture travels through the same generated
   * types and the same header construction as production traffic.
   */
  fetch?: typeof globalThis.fetch;
  /** Empty string means same origin, the deployment shape of contracts/ops/deployment.md. */
  baseUrl?: string;
  readCookie?: (name: string) => string | null;
  newRequestId?: () => string;
  newIdempotencyKey?: () => string;
}

/**
 * The API origin. Empty string means "same origin as the app". Read at runtime rather
 * than baked in at build time so one build can be deployed anywhere — and so the page can
 * never be configured to talk to a third party (card §5 forbidden edges FE-03/FE-04).
 */
export function apiBaseUrl(): string {
  return '';
}

function fillPath(template: string, params: Record<string, unknown>): string {
  return template.replace(/\{([^}]+)\}/g, (_match, name: string) => {
    const value = params[name];
    if (value === undefined || value === null) {
      throw new TypeError(`Missing path parameter '${name}' for ${template}`);
    }
    return encodeURIComponent(String(value));
  });
}

function buildQuery(params: Record<string, unknown> | undefined): string {
  if (params === undefined) return '';
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue;
    search.set(key, String(value));
  }
  const rendered = search.toString();
  return rendered === '' ? '' : `?${rendered}`;
}

async function readEnvelope(response: Response): Promise<ErrorEnvelope | null> {
  try {
    const parsed: unknown = await response.json();
    if (typeof parsed !== 'object' || parsed === null) return null;
    const record = parsed as Record<string, unknown>;
    if (typeof record['code'] !== 'string' || typeof record['correlation_id'] !== 'string') {
      return null;
    }
    return record as unknown as ErrorEnvelope;
  } catch {
    return null;
  }
}

export class ApiClient {
  private readonly transport: typeof globalThis.fetch;
  private readonly baseUrl: string;
  private readonly cookieReader: (name: string) => string | null;
  private readonly requestId: () => string;
  private readonly idempotencyKey: () => string;

  constructor(options: ApiClientOptions = {}) {
    this.transport = options.fetch ?? globalThis.fetch.bind(globalThis);
    this.baseUrl = options.baseUrl ?? apiBaseUrl();
    this.cookieReader = options.readCookie ?? readCookie;
    this.requestId = options.newRequestId ?? (() => newUlid());
    this.idempotencyKey = options.newIdempotencyKey ?? (() => newUlid());
  }

  /** The double-submit token the page can read, or `null`. */
  csrfToken(): string | null {
    return this.cookieReader(CSRF_COOKIE_NAME);
  }

  /**
   * A read. Sends the session cookie alone: CSRF protects state changes, not reads
   * (openapi.yaml §ownerSessionCookie).
   */
  async get<P extends GetPath>(path: P, options: GetOptions<P> = {}): Promise<GetResponse<P>> {
    const url = fillPath(String(path), (options.path ?? {}) as Record<string, unknown>);
    return this.send<GetResponse<P>>(
      'GET',
      `${url}${buildQuery(options.query as Record<string, unknown> | undefined)}`,
      String(path),
      {
        'X-Schema-Version': SCHEMA_VERSION,
        'X-Request-Id': this.requestId(),
      },
      undefined,
      options.signal,
    );
  }

  /**
   * A mutation. Sends session cookie AND `X-CSRF-Token` AND `Idempotency-Key`, which is
   * the header set the contract marks required for every `x-mutation: true` operation the
   * card is allowed to call (§4).
   */
  async mutate<P extends PostPath>(
    path: P,
    options: MutateOptions<P> = {},
  ): Promise<PostResponse<P>> {
    const token = this.csrfToken();
    if (token === null || token === '') throw new MissingCsrfTokenError();
    const url = fillPath(String(path), (options.path ?? {}) as Record<string, unknown>);
    return this.send<PostResponse<P>>(
      'POST',
      url,
      String(path),
      {
        'X-Schema-Version': SCHEMA_VERSION,
        'X-Request-Id': this.requestId(),
        'Idempotency-Key': options.idempotencyKey ?? this.idempotencyKey(),
        [CSRF_HEADER_NAME]: token,
        'Content-Type': 'application/json',
      },
      JSON.stringify(options.body ?? {}),
      options.signal,
    );
  }

  // >>> TC-ui-reports-detail >>>
  /**
   * A deleting mutation. Same obligations as `mutate`: session cookie AND `X-CSRF-Token` AND
   * `Idempotency-Key`, which is exactly the header set the contract marks required on
   * `save.remove` (`DELETE /v1/saved/{target_ref}`, `x-mutation: true`). Added by
   * `TC-ui-reports-detail`; a DELETE carries no request body.
   */
  async remove<P extends DeletePath>(
    path: P,
    options: DeleteOptions<P> = {},
  ): Promise<DeleteResponse<P>> {
    const token = this.csrfToken();
    if (token === null || token === '') throw new MissingCsrfTokenError();
    const url = fillPath(String(path), (options.path ?? {}) as Record<string, unknown>);
    return this.send<DeleteResponse<P>>(
      'DELETE',
      url,
      String(path),
      {
        'X-Schema-Version': SCHEMA_VERSION,
        'X-Request-Id': this.requestId(),
        'Idempotency-Key': options.idempotencyKey ?? this.idempotencyKey(),
        [CSRF_HEADER_NAME]: token,
      },
      undefined,
      options.signal,
    );
  }
  // <<< TC-ui-reports-detail <<<

  private async send<R>(
    method: 'GET' | 'POST' | 'DELETE',
    url: string,
    templatePath: string,
    headers: Record<string, string>,
    body: string | undefined,
    signal: AbortSignal | undefined,
  ): Promise<R> {
    const init: RequestInit = {
      method,
      // Sends `rr_session`; the page never reads it (HttpOnly).
      credentials: 'include',
      headers: { Accept: 'application/json', ...headers },
    };
    if (body !== undefined) init.body = body;
    if (signal !== undefined) init.signal = signal;
    const response = await this.transport(`${this.baseUrl}${url}`, init);
    if (!response.ok) {
      throw new ApiError(
        response.status,
        `${method} ${templatePath}`,
        await readEnvelope(response),
      );
    }
    return (await response.json()) as R;
  }
}

/**
 * `operation_id` → the path+method that carries it, for the operations this card is
 * allowed to call (card §4 "Consumes"). `contracts/ports.yaml` is the naming authority for
 * `operation_id` and the wire contract keeps it as `operationId`, so this table is
 * checkable: `runReadModel.test.ts` reads `contracts/http/openapi.yaml` and asserts every
 * entry names the operation the contract puts at that path and method, and that no entry
 * exists outside the card's §4 list. Later UI cards append their own operations here.
 */
export const OPERATION_PATHS = {
  'run.list': { path: '/v1/runs', method: 'get' },
  'run.get': { path: '/v1/runs/{run_id}', method: 'get' },
  'run.run_now': { path: '/v1/runs/run-now', method: 'post' },
  'run.resume': { path: '/v1/runs/{run_id}/resume', method: 'post' },
  'run.cancel': { path: '/v1/runs/{run_id}/cancel', method: 'post' },
  'worker.get_status': { path: '/v1/workers/status', method: 'get' },
  'delivery.get_status': { path: '/v1/deliveries/{delivery_id}', method: 'get' },
  'delivery.decide_unknown': {
    path: '/v1/deliveries/parts/{delivery_part_id}/decide',
    method: 'post',
  },
  'health.get_readiness': { path: '/v1/health/readiness', method: 'get' },
} as const satisfies Readonly<Record<string, { path: ApiPath; method: HttpMethod }>>;

export type OperationId = keyof typeof OPERATION_PATHS;

/** The client the app uses. Tests construct their own with a fixture transport. */
export const apiClient = new ApiClient();

/** Kept from the Phase 0 skeleton so existing call sites keep compiling. */
export async function apiGet<P extends GetPath>(path: P): Promise<GetResponse<P>> {
  return apiClient.get(path);
}

// ===================================================================================
// >>> TC-ui-reports-detail >>>
//
// The reading path: Reports, Report detail, Work detail, Save.
//
// `TC-ui-runs-three-states` wrote everything above; this block EXTENDS it and rewrites
// none of it (agent-tasks/README.md §5.3). It adds the DELETE-shaped half of the client
// (`save.remove`), the operation table for this card, and one wrapper per operation.
//
// Card `agent-tasks/TC-ui-reports-detail.md` §4 allows exactly seven operations and no
// others: `report.list`, `report.get`, `work.get_detail`, `save.create`, `save.remove`,
// `save.list`, `analysis.request_reanalysis`. Every path below is a key of the generated
// `paths` type, so a path the contract does not declare does not compile, and
// `reportReadModel.test.ts` re-reads `contracts/http/openapi.yaml` to assert that each
// entry sits at the operation the contract puts there.
// ===================================================================================

/** Paths that expose a `DELETE` in the contract. */
export type DeletePath = {
  [P in ApiPath]: [Operation<P, 'delete'>] extends [never] ? never : P;
}[ApiPath];

/** Options of a deleting mutation. A DELETE carries no request body in this contract. */
export type DeleteOptions<P extends DeletePath> = {
  path?: OrEmpty<PathParams<Operation<P, 'delete'>>>;
  /** Overrides the generated key; pass the SAME key to replay (SRC-PLAN §5.1). */
  idempotencyKey?: string;
  signal?: AbortSignal;
};

/** Response body of a `DELETE` on `P` with status 200, straight from the contract. */
export type DeleteResponse<P extends DeletePath> = OpenIfPlaceholder<
  OkBody<Operation<P, 'delete'>>
>;

/**
 * Response body of a `POST` on `P` with status **201**.
 *
 * `PostResponse` above reads status 200, which is right for the run operations. `save.create`
 * answers `201`, so its body needs its own reader rather than a cast at the call site.
 */
export type CreatedResponse<P extends PostPath> =
  Operation<P, 'post'> extends { responses: { 201: { content: { 'application/json': infer R } } } }
    ? R
    : never;

/**
 * `operation_id` → path+method for the seven operations of this card's §4.
 *
 * Kept separate from `OPERATION_PATHS` rather than appended to it: that table is asserted
 * *exhaustive* against `TC-ui-runs-three-states`'s own §4 list in its contract test, so adding
 * entries there would fail a sibling card's oracle. Two tables, one per card, keep both
 * assertions honest — see the handoff for the note to the Coordinator.
 */
export const REPORTS_OPERATION_PATHS = {
  'report.list': { path: '/v1/reports', method: 'get' },
  'report.get': { path: '/v1/reports/{report_id}', method: 'get' },
  'work.get_detail': { path: '/v1/works/{work_id}', method: 'get' },
  'save.list': { path: '/v1/saved', method: 'get' },
  'save.create': { path: '/v1/saved', method: 'post' },
  'save.remove': { path: '/v1/saved/{target_ref}', method: 'delete' },
  'analysis.request_reanalysis': { path: '/v1/analysis/reanalysis', method: 'post' },
} as const satisfies Readonly<Record<string, { path: ApiPath; method: HttpMethod }>>;

export type ReportsOperationId = keyof typeof REPORTS_OPERATION_PATHS;

/** `report.list` — the Reports screen. */
export async function fetchReportList(
  options: { limit?: number; cursor?: string } = {},
  client: ApiClient = apiClient,
): Promise<GetResponse<'/v1/reports'>> {
  return client.get('/v1/reports', { query: options });
}

/** `report.get` — one published period. Its content is immutable after publish (I05). */
export async function fetchReport(
  reportId: string,
  client: ApiClient = apiClient,
): Promise<GetResponse<'/v1/reports/{report_id}'>> {
  return client.get('/v1/reports/{report_id}', { path: { report_id: reportId } });
}

/** `work.get_detail` — the deep read of one work. */
export async function fetchWorkDetail(
  workId: string,
  client: ApiClient = apiClient,
): Promise<GetResponse<'/v1/works/{work_id}'>> {
  return client.get('/v1/works/{work_id}', { path: { work_id: workId } });
}

/** `save.list` — the Saved shelf. */
export async function fetchSavedList(
  options: { limit?: number; cursor?: string; q?: string } = {},
  client: ApiClient = apiClient,
): Promise<GetResponse<'/v1/saved'>> {
  return client.get('/v1/saved', { query: options });
}

/**
 * `save.create` — Save the item being read.
 *
 * `idempotencyKey` is the caller's on purpose: five presses of Save with the same key are one
 * row (REQ-D38, REQ-AC13), and a retry after a lost ACK must REUSE it rather than mint a new
 * one. `source_report_item_id` in the body is what makes the snapshot capture the analysis
 * revision on screen rather than a newer one (screens.yaml ACT-save-item, REQ-D55).
 */
export async function saveItem(
  body: Record<string, unknown>,
  idempotencyKey: string,
  client: ApiClient = apiClient,
): Promise<CreatedResponse<'/v1/saved'>> {
  const created = await client.mutate('/v1/saved', { body, idempotencyKey });
  return created as unknown as CreatedResponse<'/v1/saved'>;
}

/**
 * `save.remove` — un-save.
 *
 * Un-saving is not deleting the source data and does not drop the snapshot (REQ-S7.3-05,
 * REQ-D55); it removes the `saved_item` row only.
 */
export async function unsaveItem(
  targetRef: string,
  idempotencyKey: string,
  client: ApiClient = apiClient,
): Promise<DeleteResponse<'/v1/saved/{target_ref}'>> {
  return client.remove('/v1/saved/{target_ref}', {
    path: { target_ref: targetRef },
    idempotencyKey,
  });
}

/**
 * `analysis.request_reanalysis` — ask for a new generation.
 *
 * A new generation is created and the old one is KEPT (REQ-D26). A published report does not
 * change because of it (UC-03, I05): the report holds a frozen `analysis_ref`.
 */
export async function requestReanalysis(
  body: Record<string, unknown>,
  idempotencyKey: string,
  client: ApiClient = apiClient,
): Promise<PostResponse<'/v1/analysis/reanalysis'>> {
  return client.mutate('/v1/analysis/reanalysis', { body, idempotencyKey });
}
// <<< TC-ui-reports-detail <<<
