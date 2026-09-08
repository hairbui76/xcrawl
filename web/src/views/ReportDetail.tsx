// `SCR-report-detail` view: evidence-level and provenance labels.
//
// Card: agent-tasks/TC-ui-reports-detail.md §3 (`web/src/views/ReportDetail.tsx`), §5 (never
// show `ai_inference` as `source_verified`; never invent a comparator), §8 (AC-11).
//
// Everything displayed comes from `buildReportDetailReadModel`; this component adds no
// business rule of its own. Source content (paper titles, post text, AI output) is rendered as
// React children, i.e. escaped, and never as HTML — SRC-SPEC §11.4 / I11 make that a security
// property, not a style choice.

import type { ReportDetailItem, ReportDetailReadModel } from '../routes/reportDetail';
import type { ProvenanceGroup } from '../lib/provenance';
import { MISSING_FIELD_LABEL } from '../lib/provenance';

function ProvenanceBlock({ groups }: { groups: readonly ProvenanceGroup[] }) {
  return (
    <section aria-label="Phân loại phát biểu">
      {groups.map((group) => (
        <div key={group.kind} data-provenance-kind={group.kind}>
          <h4>{group.label}</h4>
          <p>{group.meaning}</p>
          {group.statements.length === 0 ? (
            <p data-empty-group={group.kind}>Không có phát biểu loại này.</p>
          ) : (
            <ul>
              {group.statements.map((statement, index) => (
                <li key={`${group.kind}-${index}`}>
                  <span>{statement.text}</span>
                  <span>
                    {statement.citation_refs.length === 0
                      ? ' (không trích nguồn)'
                      : ` (nguồn: ${statement.citation_refs.join(', ')})`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </section>
  );
}

function ItemCard({
  item,
  mutationsEnabled,
  mutationsDisabledReason,
  onSaveToggle,
}: {
  item: ReportDetailItem;
  mutationsEnabled: boolean;
  mutationsDisabledReason: string | null;
  onSaveToggle?: (item: ReportDetailItem) => void;
}) {
  // ACT-save-item / ACT-unsave-item map to `save.create` / `save.remove` (screens.yaml). The
  // call itself lives in `web/src/lib/api.ts`; the view raises the intent and never issues a
  // request of its own. With no handler mounted the button is disabled and says why, rather
  // than looking live and doing nothing (UI-03's "no silent failure", applied to the shell).
  const saveEnabled = mutationsEnabled && onSaveToggle !== undefined;
  const saveDisabledReason =
    mutationsDisabledReason ?? (onSaveToggle === undefined ? 'Thao tác lưu chưa được nối.' : null);
  return (
    <article id={`item-${item.report_item_id}`} data-item-type={item.item_type}>
      <h3>{item.target_key}</h3>

      {/* REQ-D29 / REQ-AC09 / I07: a prior reference carries its date and is not a new find. */}
      <p data-role="item-type-label">{item.item_type_label}</p>
      {item.late_discovery_label !== null && <p>{item.late_discovery_label}</p>}

      {/* REQ-D21 / REQ-AC11: reading-depth label. */}
      <p data-role="evidence-level" data-evidence-level={item.evidence_level ?? 'missing'}>
        {item.evidence_level_label}
        {item.evidence_level_meaning !== '' && ` — ${item.evidence_level_meaning}`}
      </p>

      {/* grounding.md §4.5: analysis date and discovery date, both. */}
      <p data-role="analyzed-at">{item.analyzed_at_label}</p>
      <p data-role="discovered-at">{item.discovered_at_label}</p>

      {item.summary_state_label !== null && (
        <p data-role="summary-state">{item.summary_state_label}</p>
      )}

      <dl>
        <dt>Nội dung</dt>
        <dd data-role="content">{item.content ?? MISSING_FIELD_LABEL}</dd>
        <dt>Điểm khác với cái đã có</dt>
        <dd data-role="difference">{item.difference_from_prior ?? MISSING_FIELD_LABEL}</dd>
        <dt>Hạn chế</dt>
        <dd data-role="limitation">{item.limitation_vi ?? MISSING_FIELD_LABEL}</dd>
      </dl>

      {/* B16: a missing comparator is stated, never replaced by an invented baseline. */}
      <p data-role="comparator" data-comparator-kind={item.comparator.kind}>
        {item.comparator.kind === 'unknown'
          ? item.comparator.label
          : `${item.comparator.label} ${item.comparator.sourceRef}`}
        {item.comparator.note !== undefined && ` — ${item.comparator.note}`}
      </p>

      <p data-role="matched-tags">{item.matched_tags_label}</p>

      <ProvenanceBlock groups={item.provenance} />

      {item.ceiling_violations.length > 0 && (
        <p data-role="ceiling-violation">
          Dữ liệu lỗi: {item.ceiling_violations.length} phát biểu vượt mức bằng chứng cho phép; nhãn
          gốc được giữ nguyên, không tự hạ hay nâng loại.
        </p>
      )}

      {item.identity_warning !== null && (
        <p data-role="identity-warning">{item.identity_warning}</p>
      )}

      {item.incomplete_label !== null && <p data-role="incomplete">{item.incomplete_label}</p>}

      <p>
        <button
          type="button"
          data-action={item.saved_state === 'active' ? 'ACT-unsave-item' : 'ACT-save-item'}
          disabled={!saveEnabled}
          aria-describedby={saveEnabled ? undefined : 'mutations-disabled-reason'}
          onClick={onSaveToggle === undefined ? undefined : () => onSaveToggle(item)}
        >
          {item.saved_state === 'active' ? 'Bỏ lưu' : 'Save'}
        </button>
      </p>
      {!saveEnabled && saveDisabledReason !== null && (
        <p id="mutations-disabled-reason">{saveDisabledReason}</p>
      )}
    </article>
  );
}

export default function ReportDetail({
  model,
  onSaveToggle,
}: {
  model: ReportDetailReadModel;
  onSaveToggle?: (item: ReportDetailItem) => void;
}) {
  if (model.state === 'loading') {
    return <p role="status">Đang tải kỳ báo cáo…</p>;
  }

  return (
    <section aria-labelledby="report-detail-heading" data-display-state={model.state}>
      <h1 id="report-detail-heading">{model.published_at_label}</h1>
      <p>{model.coverage_label}</p>
      {model.coverage_note_vi !== '' && <p>{model.coverage_note_vi}</p>}
      <p>{model.tag_config_version_label}</p>

      {model.error_notice !== null && <p role="alert">{model.error_notice}</p>}
      {model.stale_notice !== null && <p role="status">{model.stale_notice}</p>}
      {model.partial_notice !== null && <p>{model.partial_notice}</p>}

      {/* REQ-D53: the emerging-directions block is at the top of the page. */}
      <section aria-label="Hướng đang nổi">
        {model.emerging_directions.map((direction) => (
          <div key={direction.direction_id} data-evidence-state={direction.evidence_state}>
            {/* REQ-D54: this string is a contract constant. */}
            <h2>{direction.label}</h2>
            <p>{direction.state_label}</p>
            {direction.insufficient_reason !== null && (
              <p>Lý do: {direction.insufficient_reason}</p>
            )}
          </div>
        ))}
      </section>

      <section aria-label="Danh sách mục">
        {model.items.map((item) => (
          <ItemCard
            key={item.report_item_id}
            item={item}
            mutationsEnabled={model.mutations_enabled}
            mutationsDisabledReason={model.mutations_disabled_reason}
            onSaveToggle={onSaveToggle}
          />
        ))}
      </section>
    </section>
  );
}
