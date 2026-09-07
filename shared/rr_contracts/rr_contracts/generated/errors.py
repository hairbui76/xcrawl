# GENERATED — do not edit; source sha256 contracts/errors.yaml=640991c91ad046eb…
# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.
# Editing this file by hand makes code and contract drift apart silently; the rule is
# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the
# contract, regenerate, and mark the affected task cards STALE per INV-06.
#   contracts/errors.yaml  sha256:640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f

"""Error codes registered in contracts/errors.yaml.

The registry is the single source of truth for the wire vocabulary: an error code
that is not in this enum does not exist (contracts/errors.yaml). ``SCOPE`` and
``RETRY_CLASS`` carry the two fields a caller must branch on and are kept beside the
enum so a handler cannot invent a retry policy the contract did not grant.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """Every code in contracts/errors.yaml, in contract order."""

    #: X đòi xác minh hoặc phiên đã hết hạn
    X_CHALLENGE_REQUIRED = "X_CHALLENGE_REQUIRED"
    #: X chặn truy cập hoặc thiếu capability bắt buộc
    X_ACCESS_BLOCKED = "X_ACCESS_BLOCKED"
    #: Lease của assignment đã hết hạn; worker cũ bị thu hồi quyền
    WORKER_LEASE_EXPIRED = "WORKER_LEASE_EXPIRED"
    #: Lời gọi mang lease_epoch cũ hơn epoch hiện hành
    STALE_LEASE = "STALE_LEASE"
    #: Client không nhận được ACK; server có thể đã commit hoặc chưa
    INGEST_ACK_LOST = "INGEST_ACK_LOST"
    #: Cùng idempotency key nhưng payload khác
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    #: arXiv/OpenAlex không trả metadata cho một target
    SOURCE_METADATA_UNAVAILABLE = "SOURCE_METADATA_UNAVAILABLE"
    #: Hai định danh canonical mâu thuẫn cho cùng một công trình
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    #: Output của model sai schema hoặc thiếu trường bắt buộc
    AI_OUTPUT_INVALID = "AI_OUTPUT_INVALID"
    #: Provider AI không dùng được (mạng, CLI lỗi khởi động, quota)
    AI_PROVIDER_UNAVAILABLE = "AI_PROVIDER_UNAVAILABLE"
    #: Worker chết sau khi model đã chạy; không biết đã phát sinh chi phí hay chưa
    AI_ATTEMPT_UNCERTAIN = "AI_ATTEMPT_UNCERTAIN"
    #: Vector khác model/generation/dimension bị đem so sánh
    EMBEDDING_GENERATION_MISMATCH = "EMBEDDING_GENERATION_MISMATCH"
    #: tag_config_version đổi giữa lúc build và lúc CAS commit
    TAG_VERSION_STALE = "TAG_VERSION_STALE"
    #: Thua CAS trên một tài nguyên có predecessor (coverage window, generation active)
    CONFLICT = "CONFLICT"
    #: Timeout / mất kết nối / crash sau điểm có thể đã gửi
    TELEGRAM_SEND_UNCERTAIN = "TELEGRAM_SEND_UNCERTAIN"
    #: Recipient không hợp lệ / bị thu hồi / lỗi vĩnh viễn
    TELEGRAM_PERMANENT_FAILURE = "TELEGRAM_PERMANENT_FAILURE"
    #: Update Telegram từ chat chưa liên kết hoặc lệnh ngoài allowlist
    UNAUTHORIZED_COMMAND = "UNAUTHORIZED_COMMAND"
    #: Data store không ghi được (hết ổ, I/O lỗi, DB unavailable)
    STORAGE_WRITE_FAILED = "STORAGE_WRITE_FAILED"
    #: Vừa restore, chưa đối soát; side effect bị khóa
    RESTORE_UNVERIFIED = "RESTORE_UNVERIFIED"
    #: Bố cục nguồn đổi tới mức parser không bóc được trường bắt buộc
    SOURCE_LAYOUT_CHANGED = "SOURCE_LAYOUT_CHANGED"
    #: Thiếu hoặc sai CSRF token trên một mutation dùng phiên owner
    CSRF_REJECTED = "CSRF_REJECTED"
    #: Thiếu hoặc sai xác thực ở mức API cho operation được gọi
    UNAUTHORIZED = "UNAUTHORIZED"
    #: Tiến trình/mạng/tool capability bị từ chối ở mức nền tảng, không phải ở mức API
    CAPABILITY_DENIED = "CAPABILITY_DENIED"
    #: Cạnh caller→callee không có trong contracts/modules.yaml
    FORBIDDEN_EDGE = "FORBIDDEN_EDGE"
    #: Request sai schema, sai enum, vượt giới hạn kích thước
    VALIDATION_ERROR = "VALIDATION_ERROR"
    #: Tài nguyên không tồn tại trong phạm vi owner
    NOT_FOUND = "NOT_FOUND"
    #: Bị giới hạn nhịp gọi (nguồn ngoài hoặc chính API nội bộ)
    RATE_LIMITED = "RATE_LIMITED"
    #: Lỗi không phân loại được ở phía server
    INTERNAL = "INTERNAL"


#: Error code -> `scope` field of contracts/errors.yaml.
SCOPE: dict[ErrorCode, str] = {
    ErrorCode.X_CHALLENGE_REQUIRED: "run",
    ErrorCode.X_ACCESS_BLOCKED: "run",
    ErrorCode.WORKER_LEASE_EXPIRED: "request",
    ErrorCode.STALE_LEASE: "request",
    ErrorCode.INGEST_ACK_LOST: "request",
    ErrorCode.IDEMPOTENCY_CONFLICT: "request",
    ErrorCode.SOURCE_METADATA_UNAVAILABLE: "item",
    ErrorCode.IDENTITY_CONFLICT: "item",
    ErrorCode.AI_OUTPUT_INVALID: "item",
    ErrorCode.AI_PROVIDER_UNAVAILABLE: "item",
    ErrorCode.AI_ATTEMPT_UNCERTAIN: "item",
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: "request",
    ErrorCode.TAG_VERSION_STALE: "request",
    ErrorCode.CONFLICT: "request",
    ErrorCode.TELEGRAM_SEND_UNCERTAIN: "delivery",
    ErrorCode.TELEGRAM_PERMANENT_FAILURE: "delivery",
    ErrorCode.UNAUTHORIZED_COMMAND: "request",
    ErrorCode.STORAGE_WRITE_FAILED: "storage",
    ErrorCode.RESTORE_UNVERIFIED: "storage",
    ErrorCode.SOURCE_LAYOUT_CHANGED: "run",
    ErrorCode.CSRF_REJECTED: "request",
    ErrorCode.UNAUTHORIZED: "request",
    ErrorCode.CAPABILITY_DENIED: "request",
    ErrorCode.FORBIDDEN_EDGE: "request",
    ErrorCode.VALIDATION_ERROR: "request",
    ErrorCode.NOT_FOUND: "request",
    ErrorCode.RATE_LIMITED: "request",
    ErrorCode.INTERNAL: "request",
}

#: Error code -> `retry_class` field of contracts/errors.yaml.
RETRY_CLASS: dict[ErrorCode, str] = {
    ErrorCode.X_CHALLENGE_REQUIRED: "needs_user",
    ErrorCode.X_ACCESS_BLOCKED: "none",
    ErrorCode.WORKER_LEASE_EXPIRED: "none",
    ErrorCode.STALE_LEASE: "none",
    ErrorCode.INGEST_ACK_LOST: "retryable_with_budget",
    ErrorCode.IDEMPOTENCY_CONFLICT: "none",
    ErrorCode.SOURCE_METADATA_UNAVAILABLE: "retryable_with_budget",
    ErrorCode.IDENTITY_CONFLICT: "operator_decision",
    ErrorCode.AI_OUTPUT_INVALID: "retryable_with_budget",
    ErrorCode.AI_PROVIDER_UNAVAILABLE: "retryable_with_budget",
    ErrorCode.AI_ATTEMPT_UNCERTAIN: "unknown_outcome",
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: "none",
    ErrorCode.TAG_VERSION_STALE: "retryable_with_budget",
    ErrorCode.CONFLICT: "retryable_with_budget",
    ErrorCode.TELEGRAM_SEND_UNCERTAIN: "unknown_outcome",
    ErrorCode.TELEGRAM_PERMANENT_FAILURE: "none",
    ErrorCode.UNAUTHORIZED_COMMAND: "none",
    ErrorCode.STORAGE_WRITE_FAILED: "retryable_with_budget",
    ErrorCode.RESTORE_UNVERIFIED: "operator_decision",
    ErrorCode.SOURCE_LAYOUT_CHANGED: "none",
    ErrorCode.CSRF_REJECTED: "none",
    ErrorCode.UNAUTHORIZED: "none",
    ErrorCode.CAPABILITY_DENIED: "none",
    ErrorCode.FORBIDDEN_EDGE: "none",
    ErrorCode.VALIDATION_ERROR: "none",
    ErrorCode.NOT_FOUND: "none",
    ErrorCode.RATE_LIMITED: "retryable_with_budget",
    ErrorCode.INTERNAL: "unknown_outcome",
}
