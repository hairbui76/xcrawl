// `SCR-runs` — the Runs screen.
//
// The component holds no logic: `routes/runs.ts` has already decided every label, every
// visible action and the display state, so what a test asserts about this file is only
// that it puts the read model's strings on the screen and adds none of its own. That is
// what makes REQ-AC15 checkable by comparing strings.
//
// Visual design is deliberately unfixed (`screens.yaml §global_rules.visual_design`,
// REQ-S4-10: "thiếu design token KHÔNG phải blocker"), so there is no styling here.

import type { RunsReadModel, RunRow, ScreenAction } from '../routes/runs';

export interface RunsListProps {
  model: RunsReadModel;
  /** Invoked with the contract action and the row it belongs to. */
  onAction?: (action: ScreenAction, runId: string | null) => void;
}

function StorageBanner({ model }: { model: RunsReadModel }) {
  if (model.storage.reason_vi === null) return null;
  return (
    <p role="status" data-testid="storage-notice">
      {model.storage.reason_vi}
    </p>
  );
}

function AsOf({ model }: { model: RunsReadModel }) {
  // UI-01: every business screen carries `as_of` and `storage_health`.
  return (
    <p data-testid="as-of">
      as_of: <span data-testid="as-of-value">{model.as_of ?? '—'}</span> · storage_health:{' '}
      <span data-testid="storage-health-value">{model.storage_health ?? '—'}</span>
    </p>
  );
}

function Collector({ model }: { model: RunsReadModel }) {
  // `unknown` is rendered as `unknown`; turning it into `offline` is the I13 violation the
  // contract calls out by name.
  return (
    <p data-testid="collector">
      collector:{' '}
      <span data-testid="collector-online-state">{model.collector_online_state ?? '—'}</span> ·
      last_run_at: <span data-testid="last-run-at">{model.last_run_at ?? '—'}</span>
    </p>
  );
}

function Actions({ row, onAction }: { row: RunRow; onAction: RunsListProps['onAction'] }) {
  return (
    <>
      {row.actions.map((action) => (
        <button
          key={action.id}
          type="button"
          data-testid={`action-${action.id}-${row.id}`}
          data-operation-id={action.operation_id}
          // UI-03: disabled WITH a reason, never silently inert.
          disabled={row.actions_disabled_reason_vi !== null}
          title={row.actions_disabled_reason_vi ?? undefined}
          onClick={() => onAction?.(action, row.id)}
        >
          {action.label_vi}
        </button>
      ))}
    </>
  );
}

function Row({ row, onAction }: { row: RunRow; onAction: RunsListProps['onAction'] }) {
  return (
    <tr data-testid={`run-row-${row.id}`}>
      <td data-testid={`run-status-label-${row.id}`}>
        {/*
          The label of `screens.yaml §run_status_labels` when the contract names one. When
          it does not (queued/running/waiting_retry/cancelled/plain completed — see
          CR-TC-uiruns-01), the machine value of `status` is shown rather
          than a Vietnamese sentence this card invented.
        */}
        {row.status_label === null ? row.status : row.status_label.label_vi}
      </td>
      <td data-testid={`run-stop-reason-${row.id}`}>{row.stop_reason ?? '—'}</td>
      <td data-testid={`run-outcome-${row.id}`}>{row.outcome ?? '—'}</td>
      <td data-testid={`run-phase-${row.id}`}>{row.phase ?? '—'}</td>
      <td data-testid={`run-trigger-${row.id}`}>{row.trigger_type ?? '—'}</td>
      <td data-testid={`run-progress-${row.id}`}>
        {row.progress === null ? '—' : (row.progress.acked_through_ingest_sequence ?? '—')}
      </td>
      {/* I09: delivery state lives in its OWN column and is never folded into the run label. */}
      <td data-testid={`run-delivery-${row.id}`}>{row.delivery_state ?? '—'}</td>
      <td data-testid={`run-note-${row.id}`}>
        {row.empty_period_note ?? row.unblock_condition_vi ?? '—'}
      </td>
      <td>
        <Actions row={row} onAction={onAction} />
      </td>
    </tr>
  );
}

export default function RunsList({ model, onAction }: RunsListProps) {
  return (
    <section aria-labelledby="runs-heading" data-testid="scr-runs">
      <h1 id="runs-heading">Runs</h1>
      <AsOf model={model} />
      <Collector model={model} />
      <StorageBanner model={model} />

      {model.display_state === 'loading' ? (
        <p role="status" data-testid="runs-loading">
          Đang tải…
        </p>
      ) : null}

      {model.display_state === 'error' ? (
        <p role="alert" data-testid="runs-error">
          {/* `message_safe` from the server; the UI adds nothing that could leak (§7). */}
          {model.error_message_safe ?? model.error_code ?? '—'}
        </p>
      ) : null}

      {model.display_state === 'empty' ? (
        // `screens.yaml §screens[SCR-runs].states.empty_vi`, verbatim.
        <p data-testid="runs-empty">Chưa có đợt nào.</p>
      ) : (
        <table data-testid="runs-table">
          <thead>
            <tr>
              <th scope="col">status_label</th>
              <th scope="col">stop_reason</th>
              <th scope="col">outcome</th>
              <th scope="col">phase</th>
              <th scope="col">trigger_type</th>
              <th scope="col">progress</th>
              <th scope="col">delivery</th>
              <th scope="col">note</th>
              <th scope="col">actions</th>
            </tr>
          </thead>
          <tbody>
            {model.runs.map((row) => (
              <Row key={row.id} row={row} onAction={onAction} />
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
