// The generate-don't-hand-edit rule for the TypeScript side, made checkable.
//
// Mirrors shared/rr_contracts/tests/test_generated_matches_contracts.py:
//   * the contract's sha256 must still match what GENERATED_FROM.json recorded
//     (contract moved, code did not);
//   * regenerating must produce no diff (code moved, contract did not — i.e. a hand edit).

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(HERE, '../..');
const REPO_ROOT = resolve(WEB_ROOT, '..');
const MANIFEST = JSON.parse(
  readFileSync(resolve(WEB_ROOT, 'src/generated/GENERATED_FROM.json'), 'utf8'),
) as { sources: Array<{ path: string; sha256: string; bytes: number }> };

describe('generated OpenAPI client', () => {
  it('records exactly one source: the HTTP wire contract', () => {
    expect(MANIFEST.sources.map((s) => s.path)).toEqual(['contracts/http/openapi.yaml']);
  });

  it('was generated from the contract that is on disk now', () => {
    for (const source of MANIFEST.sources) {
      const bytes = readFileSync(resolve(REPO_ROOT, source.path));
      expect(createHash('sha256').update(bytes).digest('hex'), source.path).toBe(source.sha256);
      expect(bytes.length, source.path).toBe(source.bytes);
    }
  });

  it('carries the do-not-edit banner', () => {
    const types = readFileSync(resolve(WEB_ROOT, 'src/generated/openapi.d.ts'), 'utf8');
    expect(types.startsWith('// GENERATED — do not edit;')).toBe(true);
  });

  it('regenerating produces no diff', () => {
    // Throws (and fails the test) on a non-zero exit, printing the differing files.
    execFileSync('node', ['scripts/generate.mjs', '--check'], {
      cwd: WEB_ROOT,
      stdio: 'pipe',
      encoding: 'utf8',
    });
  });
}, 120_000);
