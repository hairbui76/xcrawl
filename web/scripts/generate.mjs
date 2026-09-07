// Generate web/src/generated/openapi.d.ts from contracts/http/openapi.yaml.
//
// Rule (ADR-0011; agent-tasks/README.md §5.3; docs/master-plan.md §2.3): the TypeScript
// wire types are GENERATED from the contract and never hand-written. This script is the
// TypeScript half of the same discipline shared/rr_contracts/generate.py enforces on the
// Python side, and it is paired with web/tests/contract/generatedClient.test.ts, which
// fails when the contract's hash drifts from the record or when regenerating produces a
// diff.
//
// Determinism: openapi-typescript is run through its Node API with no timestamp and no
// version string in the output; the only variable input is the contract file's bytes.
//
// Usage:
//   node scripts/generate.mjs           write src/generated/
//   node scripts/generate.mjs --check   regenerate in memory and diff; exit 1 on any diff

import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import openapiTS, { astToString } from 'openapi-typescript';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(HERE, '..');
const REPO_ROOT = resolve(WEB_ROOT, '..');
const SOURCE_REL = 'contracts/http/openapi.yaml';
const SOURCE = resolve(REPO_ROOT, SOURCE_REL);
const OUT_DIR = resolve(WEB_ROOT, 'src/generated');
const OUT_TYPES = resolve(OUT_DIR, 'openapi.d.ts');
const OUT_MANIFEST = resolve(OUT_DIR, 'GENERATED_FROM.json');

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function banner(hash) {
  return [
    `// GENERATED — do not edit; source sha256 ${hash}`,
    `// Produced by web/scripts/generate.mjs from ${SOURCE_REL}.`,
    '// Editing this file by hand makes code and contract drift apart silently; the rule is',
    '// ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change the wire types: change',
    '// the contract, regenerate, and mark the affected task cards STALE per INV-06.',
    '',
    '',
  ].join('\n');
}

const SCHEMAS_DIR = resolve(REPO_ROOT, 'contracts/schemas');

/**
 * Materialise a bundle of contracts/http/openapi.yaml whose $refs all resolve offline.
 *
 * contracts/schemas/report.schema.json refers to target.schema.json by its $id URL
 * (https://research-radar.local/...). That is correct JSON Schema, but the bundler inside
 * openapi-typescript tries to FETCH the URL, which fails — and would be worse if it ever
 * succeeded, since generation must never depend on the network. Hand-fixing the generated
 * .d.ts is the one thing this file forbids, so the reference is resolved before generation:
 * the contract tree is copied into a temporary directory with its layout preserved
 * (http/openapi.yaml keeps working ../schemas/... refs) and every $id URL is rewritten to
 * the sibling file name. Nothing under contracts/ is written.
 *
 * The transform is textual and depends only on the source bytes, so the bundle — and the
 * output — is deterministic.
 */
function materialiseBundle() {
  const root = mkdtempSync(join(tmpdir(), 'rr-openapi-'));
  mkdirSync(join(root, 'schemas'));
  mkdirSync(join(root, 'http'));

  const byId = new Map();
  const schemaFiles = readdirSync(SCHEMAS_DIR)
    .filter((name) => name.endsWith('.schema.json'))
    .sort();
  for (const name of schemaFiles) {
    const doc = JSON.parse(readFileSync(join(SCHEMAS_DIR, name), 'utf8'));
    if (doc.$id) byId.set(doc.$id, name);
  }

  const rewrite = (text) => {
    let out = text;
    for (const [id, name] of [...byId.entries()].sort()) {
      out = out.split(id).join(name);
    }
    return out;
  };

  for (const name of schemaFiles) {
    writeFileSync(
      join(root, 'schemas', name),
      rewrite(readFileSync(join(SCHEMAS_DIR, name), 'utf8')),
      'utf8',
    );
  }
  writeFileSync(
    join(root, 'http', basename(SOURCE)),
    rewrite(readFileSync(SOURCE, 'utf8')),
    'utf8',
  );
  return { root, entry: join(root, 'http', basename(SOURCE)) };
}

async function render() {
  const hash = sha256(SOURCE);
  const bundle = materialiseBundle();
  let ast;
  try {
    ast = await openapiTS(pathToFileURL(bundle.entry), {
      alphabetize: true,
      excludeDeprecated: false,
    });
  } finally {
    rmSync(bundle.root, { recursive: true, force: true });
  }
  const types = banner(hash) + astToString(ast);
  const manifest =
    JSON.stringify(
      {
        generator: 'web/scripts/generate.mjs',
        rule: 'Generated code must match the contract it was generated from. A mismatch means either the contract changed without regeneration, or a generated file was hand-edited. Both are defects (ADR-0011; agent-tasks/README.md §5.3).',
        sources: [{ path: SOURCE_REL, sha256: hash, bytes: readFileSync(SOURCE).length }],
        outputs: ['openapi.d.ts'],
      },
      null,
      2,
    ) + '\n';
  return { types, manifest, hash };
}

const check = process.argv.includes('--check');
const { types, manifest } = await render();

if (!check) {
  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(OUT_TYPES, types, 'utf8');
  writeFileSync(OUT_MANIFEST, manifest, 'utf8');
  console.log(`generated ${OUT_TYPES} (${types.length} bytes)`);
  process.exit(0);
}

const differences = [];
for (const [path, expected] of [
  [OUT_TYPES, types],
  [OUT_MANIFEST, manifest],
]) {
  if (!existsSync(path)) {
    differences.push(`missing: ${path}`);
  } else if (readFileSync(path, 'utf8') !== expected) {
    differences.push(`content differs: ${path}`);
  }
}
if (differences.length > 0) {
  console.error('REGENERATION DIFF:');
  for (const line of differences) console.error('  ' + line);
  process.exit(1);
}
console.log('generated client matches a fresh run of the generator');
