// `SCR-run-detail` — diagnosing one run.
//
// Three things this screen must keep apart, and the reason each one is here:
//   * `needs_user` offers "Tiếp tục" (resume). `blocked` does NOT — it shows the server's
//     `unblock_condition_vi` instead (B10/AMD-B10, `screens.yaml` `visible_when`).
//   * delivery `unknown` reads "Chưa xác định — có thể đã gửi", never "Đã gửi Telegram"
//     and never "Không gửi được" (I13, AMD-B03), and it offers `delivery.decide_unknown`.
//   * a Telegram problem is shown next to the run, not inside its status (I09).

import type { UnknownDecision } from '../lib/runState';
import type { ScreenAction } from '../routes/runs';
import type { DeliveryPartView, RunDetailReadModel } from '../routes/runDetail';

export interface RunDetailProps {
  model: RunDetailReadModel;
  onAction?: (action: ScreenAction) => void;
  /** Called with the part and the decision the owner picked. Never called automatically. */
  onDecideUnknown?: (part: DeliveryPartView, decision: UnknownDecision) => void;
}

function Delivery({ model, onDecideUnknown }: RunDetailProps) {
  const { delivery } = model;
  return (
    <section aria-labelledby="delivery-heading" data-testid="delivery-status">
      <h2 id="delivery-heading">Delivery</h2>
      <p data-testid="delivery-label">{delivery.label === null ? '—' : delivery.label.label_vi}</p>
      <ul data-testid="delivery-parts">
        {delivery.parts.map((part) => (
          <li key={part.id} data-testid={`delivery-part-${part.id}`}>
            <span data-testid={`delivery-part-label-${part.id}`}>{part.label.label_vi}</span>
            {part.needs_decision ? (
              <span data-testid={`delivery-part-decision-${part.id}`}>
                {/* The risk has to be stated BEFORE a resend can be chosen. */}
                <span data-testid={`duplicate-risk-${part.id}`}>
                  {delivery.duplicate_risk_warning_vi}
                </span>
                {(
                  ['resend_accepting_duplicate_risk', 'mark_not_delivered', 'abandon'] as const
                ).map((decision) => (
                  <button
                    key={decision}
                    type="button"
                    data-testid={`decide-${decision}-${part.id}`}
                    data-operation-id="delivery.decide_unknown"
                    disabled={model.actions_disabled_reason_vi !== null}
                    title={model.actions_disabled_reason_vi ?? undefined}
                    onClick={() => onDecideUnknown?.(part, decision)}
                  >
                    {decision}
                  </button>
                ))}
              </span>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function RunDetail({ model, onAction, onDecideUnknown }: RunDetailProps) {
  return (
    <section aria-labelledby="run-detail-heading" data-testid="scr-run-detail">
      <h1 id="run-detail-heading">Run detail</h1>

      <p data-testid="as-of">
        as_of: <span data-testid="as-of-value">{model.as_of ?? '—'}</span> · storage_health:{' '}
        <span data-testid="storage-health-value">{model.storage_health ?? '—'}</span>
      </p>
      {model.storage.reason_vi === null ? null : (
        <p role="status" data-testid="storage-notice">
          {model.storage.reason_vi}
        </p>
      )}

      {model.display_state === 'error' ? (
        <p role="alert" data-testid="run-detail-error">
          {model.error_message_safe ?? model.error_code ?? '—'}
        </p>
      ) : null}

      <p data-testid="run-status-label">
        {model.status_label === null ? (model.status ?? '—') : model.status_label.label_vi}
      </p>
      <p data-testid="run-stop-reason">{model.stop_reason ?? '—'}</p>
      <p data-testid="run-trigger-type">{model.trigger_type ?? '—'}</p>
      <p data-testid="run-items-collected">{model.items_collected ?? '—'}</p>
      <p data-testid="run-items-new">{model.items_new ?? '—'}</p>
      <p data-testid="run-checkpoint">
        {model.checkpoint === null ? '—' : (model.checkpoint.acked_through_ingest_sequence ?? '—')}
      </p>
      {/* B05: "completed" is not a claim that all of X was scanned. */}
      <p data-testid="coverage-limitation-note">{model.coverage_limitation_note ?? '—'}</p>
      <p data-testid="alert-intent-count">{model.alert_intent_count ?? '—'}</p>

      {/* Only a `blocked` run has one; a `needs_user` run gets the resume button instead. */}
      <p data-testid="unblock-condition">{model.attention.unblock_condition_vi ?? '—'}</p>

      <ul data-testid="run-errors">
        {model.errors.map((error) => (
          <li key={error.code} data-testid={`run-error-${error.code}`}>
            {error.code}: {error.message_safe ?? '—'}
          </li>
        ))}
      </ul>

      <div data-testid="run-actions">
        {model.actions.map((action) => (
          <button
            key={action.id}
            type="button"
            data-testid={`action-${action.id}`}
            data-operation-id={action.operation_id}
            disabled={model.actions_disabled_reason_vi !== null}
            title={model.actions_disabled_reason_vi ?? undefined}
            onClick={() => onAction?.(action)}
          >
            {action.label_vi}
          </button>
        ))}
      </div>

      <Delivery model={model} onDecideUnknown={onDecideUnknown} />
    </section>
  );
}
