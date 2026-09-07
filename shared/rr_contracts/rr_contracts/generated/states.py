# GENERATED — do not edit; source sha256 contracts/state/analysis.yaml=06b18de42c3bbfff…, contracts/state/delivery.yaml=318789179ec79a4e…, contracts/state/report.yaml=77969cb473c84a7d…, contracts/state/run.yaml=479125cb0d927c69…, contracts/state/storage.yaml=a77803f1690ee774…
# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.
# Editing this file by hand makes code and contract drift apart silently; the rule is
# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the
# contract, regenerate, and mark the affected task cards STALE per INV-06.
#   contracts/state/analysis.yaml  sha256:06b18de42c3bbffff9a74b2e990025361cf2b179736f1994a5558f5eef3618ce
#   contracts/state/delivery.yaml  sha256:318789179ec79a4e21939a82d4fb78bfb3cd257ed7c3af4c519bf2ab631ee807
#   contracts/state/report.yaml  sha256:77969cb473c84a7df90e6b784ad1afa637313e813ccbb59d99b1ea329241245f
#   contracts/state/run.yaml  sha256:479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27
#   contracts/state/storage.yaml  sha256:a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849

"""State enums from contracts/state/*.yaml.

Each enum is CLOSED: E0-09 proves the contract lists every reachable state, so a
value absent here is a value the state machine does not have. Notably
``StorageHealth`` has no ``unknown`` member -- code that cannot determine storage
health must say so some other way rather than widening the enum.
"""

from __future__ import annotations

from enum import Enum


class AnalysisItemState(str, Enum):
    """`item_state` of contracts/state/analysis.yaml.

    """

    PENDING = "pending"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    VALID = "valid"
    FAILED = "failed"
    UNKNOWN_ATTEMPT = "unknown_attempt"


class AnalysisAttemptOutcome(str, Enum):
    """`attempt_outcome` of contracts/state/analysis.yaml.

    """

    ACCEPTED = "accepted"
    SCHEMA_INVALID = "schema_invalid"
    PROVIDER_ERROR = "provider_error"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    TIMEOUT_UNKNOWN = "timeout_unknown"
    CANCELLED_STALE_LEASE = "cancelled_stale_lease"


class AnalysisTaskType(str, Enum):
    """`task_type` of contracts/state/analysis.yaml.

    `contracts/ports.yaml analysis.enqueue_tasks` viết ba giá trị là `open_labeling` | `summary` | `emerging_direction_phrasing`. Tên có thẩm quyền là của entities.yaml (ruling R-03): `label` | `summary` | `direction_phrasing`. Xem CR-PC03-05.
    """

    LABEL = "label"
    SUMMARY = "summary"
    DIRECTION_PHRASING = "direction_phrasing"


class DeliveryState(str, Enum):
    """`delivery_state` of contracts/state/delivery.yaml.

    """

    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    RETRY_WAIT = "retry_wait"
    UNKNOWN = "unknown"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliveryPartState(str, Enum):
    """`delivery_part_state` of contracts/state/delivery.yaml.

    entities.yaml khai bốn giá trị `pending | sent | unknown | failed`. PC03 thêm `sending` để trạng thái "đã ghi attempt, chưa có kết quả" quan sát được — đó chính là trạng thái mà crash biến thành `unknown`. Bổ sung additive; xem CR-PC03-07.
    """

    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    UNKNOWN = "unknown"
    FAILED = "failed"


class DeliveryIntentKind(str, Enum):
    """`intent_kind` of contracts/state/delivery.yaml.

    """

    REPORT_DIGEST = "report_digest"
    RUN_ALERT = "run_alert"


class DeliveryUnknownDecision(str, Enum):
    """`unknown_decision` of contracts/state/delivery.yaml.

    """

    RESEND_ACCEPTING_DUPLICATE_RISK = "resend_accepting_duplicate_risk"
    MARK_NOT_DELIVERED = "mark_not_delivered"
    ABANDON = "abandon"


class ReportStatus(str, Enum):
    """`status` of contracts/state/report.yaml.

    """

    BUILDING = "building"
    PUBLISHED = "published"
    ABORTED = "aborted"


class ReportAbortReason(str, Enum):
    """`abort_reason` of contracts/state/report.yaml.

    """

    EMPTY_PERIOD = "empty_period"
    TAG_VERSION_STALE = "tag_version_stale"
    EMBEDDING_GENERATION_MISMATCH = "embedding_generation_mismatch"
    CAS_CONFLICT = "cas_conflict"
    BUILDER_FAILURE = "builder_failure"
    CANCELLED = "cancelled"


class ReportQuality(str, Enum):
    """`quality` of contracts/state/report.yaml.

    `quality` là TRƯỜNG RIÊNG với `status` (SRC-PLAN §8.2). Một report có thể `published` + `partial`. Không bao giờ nhồi chất lượng vào enum trạng thái — đó chính là lỗi `stopped_limit` mà B02 phải gỡ.
    """

    COMPLETE = "complete"
    PARTIAL = "partial"


class RunPhase(str, Enum):
    """`phase` of contracts/state/run.yaml.

    `phase` chỉ có nghĩa khi `status ∈ {running, waiting_retry, needs_user, blocked}`; ở trạng thái terminal nó là phase cuối cùng đã đạt (chỉ để hiển thị).
    """

    COLLECTING = "collecting"
    ENRICHING = "enriching"
    ANALYZING = "analyzing"
    REPORTING = "reporting"


class RunStatus(str, Enum):
    """`status` of contracts/state/run.yaml.

    """

    QUEUED = "queued"
    RUNNING = "running"
    WAITING_RETRY = "waiting_retry"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunOutcome(str, Enum):
    """`outcome` of contracts/state/run.yaml.

    NULL khi run chưa kết thúc (ENT-run.outcome nullable). NOT NULL với mọi trạng thái terminal.
    """

    COMPLETE = "complete"
    PARTIAL = "partial"
    EMPTY = "empty"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunStopReason(str, Enum):
    """`stop_reason` of contracts/state/run.yaml.

    Nullable. `stop_reason` là LÝ DO DỪNG, độc lập với `status` và `outcome` (AMD-B02): `completed` + `limit_reached` là tổ hợp hợp lệ và phổ biến (AC-03 đọc lại).
    """

    LIMIT_REACHED = "limit_reached"
    CAPTCHA = "captcha"
    SESSION_EXPIRED = "session_expired"
    SOURCE_BLOCKED = "source_blocked"
    STORAGE_UNAVAILABLE = "storage_unavailable"
    WORKER_LOST = "worker_lost"
    SOURCE_LAYOUT_CHANGED = "source_layout_changed"
    RATE_LIMITED = "rate_limited"


class RunTriggerType(str, Enum):
    """`trigger_type` of contracts/state/run.yaml.

    """

    SCHEDULED = "scheduled"
    MANUAL = "manual"


class StorageHealth(str, Enum):
    """`storage_health` of contracts/state/storage.yaml.

    """

    HEALTHY = "healthy"
    WRITE_BLOCKED = "write_blocked"
    MAINTENANCE = "maintenance"
    RECOVERY_REQUIRED = "recovery_required"

