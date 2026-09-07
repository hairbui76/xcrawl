// -----------------------------------------------------------------------------------
// OWNERSHIP NOTICE — this file is not owned by the Phase 0 skeleton packet.
//
// `web/src/lib/api.ts` is written by the card that owns the browser half of the owner
// session: `agent-tasks/TC-owner-auth-session.md` (server half) together with the two UI
// cards that consume it, `TC-ui-runs-three-states` and `TC-ui-reports-detail`
// (agent-tasks/README.md §5.3: "Card nào chạy trước tạo file; card sau MỞ RỘNG, không
// viết lại").
//
// Phase 0 therefore ships ONLY a typed fetch stub so the shell compiles and the generated
// wire types have a consumer. In particular this file DELIBERATELY CONTAINS NO CSRF
// LOGIC: reading the non-HttpOnly cookie `rr_csrf` and attaching `X-CSRF-Token` to every
// owner mutation is the owning card's obligation, and half-implementing it here would
// leave a security behaviour that looks done and is not.
// -----------------------------------------------------------------------------------

import type { paths } from '../generated/openapi';

/** Every path in `contracts/http/openapi.yaml`, as a union of string literals. */
export type ApiPath = keyof paths;

/** Response body type of a `GET` on `P` with status 200, straight from the contract. */
export type GetResponse<P extends ApiPath> = paths[P] extends {
  get: { responses: { 200: { content: { 'application/json': infer T } } } };
}
  ? T
  : never;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly path: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * The API origin. Empty string means "same origin as the app", which is the deployment
 * shape in `contracts/ops/deployment.md` (web and api behind one server). It is read at
 * runtime rather than baked in at build time so one build can be deployed anywhere.
 */
export function apiBaseUrl(): string {
  return '';
}

/**
 * Minimal typed GET. `credentials: 'include'` sends the HttpOnly session cookie
 * `rr_session`, which is the read-only half of the owner scheme; read-only routes take
 * the cookie alone (`ownerSessionCookie` in contracts/http/openapi.yaml).
 *
 * There is no mutation helper here on purpose — see the ownership notice above.
 */
export async function apiGet<P extends ApiPath>(path: P): Promise<GetResponse<P>> {
  const response = await fetch(`${apiBaseUrl()}${String(path)}`, {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    throw new ApiError(response.status, String(path), `GET ${String(path)} → ${response.status}`);
  }
  return (await response.json()) as GetResponse<P>;
}
