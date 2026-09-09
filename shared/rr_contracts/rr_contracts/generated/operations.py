# GENERATED — do not edit; source sha256 contracts/ports.yaml=c7c7734001b98f25…
# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.
# Editing this file by hand makes code and contract drift apart silently; the rule is
# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the
# contract, regenerate, and mark the affected task cards STALE per INV-06.
#   contracts/ports.yaml  sha256:c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412

"""Operation ids from contracts/ports.yaml.

contracts/ports.yaml is the naming authority for operations (coordination baseline
§3). Referring to an operation by a string literal instead of a member of this enum
is how a near-miss name (`worker.grab_assignment`) gets into code without failing a
build.

``OWNER_MODULE``, ``TRANSPORT`` and ``MUTATION`` restate the three fields the
default-deny boundary check needs (contracts/modules.yaml): who owns the operation,
how it is reached, and whether it changes state.
"""

from __future__ import annotations

from enum import Enum


class OperationId(str, Enum):
    """Every operation in contracts/ports.yaml, in contract order."""

    #: Đăng nhập tài khoản duy nhất
    AUTH_LOGIN = "auth.login"
    #: Kết thúc session hiện tại
    AUTH_LOGOUT = "auth.logout"
    #: Đọc trạng thái session
    AUTH_GET_SESSION = "auth.get_session"
    #: Đọc cấu hình (lịch, giới hạn, provider/model theo tác vụ, embedding, liên kết Telegram)
    SETTINGS_GET_CONFIG = "settings.get_config"
    #: Sửa cấu hình
    SETTINGS_UPDATE_CONFIG = "settings.update_config"
    #: Thử một provider AI đã cấu hình (đường API key, phía server)
    SETTINGS_TEST_PROVIDER = "settings.test_provider"
    #: Danh sách tag, từ đồng nghĩa, tag loại trừ
    TAG_LIST = "tag.list"
    #: Thêm tag (kèm alias và exclusion)
    TAG_CREATE = "tag.create"
    #: Sửa tag/alias/exclusion
    TAG_UPDATE = "tag.update"
    #: Xóa tag
    TAG_DELETE = "tag.delete"
    #: Xem nhãn chủ đề đang khớp một tag (Topics)
    TAG_PREVIEW_MATCHES = "tag.preview_matches"
    #: Quét lại kho theo tag ("quét lại kho", D28)
    TAG_RESCAN_CORPUS = "tag.rescan_corpus"
    #: Đọc phiên bản cấu hình tag đang hoạt động (nội bộ)
    TAG_GET_ACTIVE_CONFIG_VERSION = "tag.get_active_config_version"
    #: Đóng băng phiên bản tag vào transaction publish report (B01)
    TAG_FREEZE_CONFIG_VERSION = "tag.freeze_config_version"
    #: Danh sách run + trạng thái collector online/offline
    RUN_LIST = "run.list"
    #: Chi tiết một run (Run detail)
    RUN_GET = "run.get"
    #: Chạy ngay (thủ công)
    RUN_RUN_NOW = "run.run_now"
    #: Tiếp tục run đang `needs_user` (hành động riêng trong app, B10)
    RUN_RESUME = "run.resume"
    #: Hủy một run chưa kết thúc
    RUN_CANCEL = "run.cancel"
    #: Quét lịch tới hạn (tick nội bộ)
    SCHEDULER_EVALUATE_DUE = "scheduler.evaluate_due"
    #: Tạo run theo lịch
    JOB_ENQUEUE_SCHEDULED_RUN = "job.enqueue_scheduled_run"
    #: Gộp nhiều đợt quá hạn thành một (D15)
    JOB_COALESCE_OVERDUE = "job.coalesce_overdue"
    #: Đăng ký readiness/capability của worker trên máy cá nhân
    WORKER_REGISTER_CAPABILITIES = "worker.register_capabilities"
    #: Collector kéo việc khi online (D11)
    WORKER_CLAIM_ASSIGNMENT = "worker.claim_assignment"
    #: Gia hạn lease và báo tiến độ
    WORKER_HEARTBEAT = "worker.heartbeat"
    #: Báo điểm dừng của đợt (challenge / limit / blocked / hết phiên)
    WORKER_REPORT_STOP = "worker.report_stop"
    #: Trả lại assignment (kết thúc bình thường hoặc worker tắt)
    WORKER_RELEASE_ASSIGNMENT = "worker.release_assignment"
    #: Đọc trạng thái worker (online/offline, last run) cho màn hình Runs
    WORKER_GET_STATUS = "worker.get_status"
    #: Nộp một lô post đã thu thập (collector → server, D08)
    INGEST_SUBMIT_BATCH = "ingest.submit_batch"
    #: Đẩy con trỏ checkpoint khi **không có** item mới (cursor-only advance)
    INGEST_COMMIT_CHECKPOINT = "ingest.commit_checkpoint"
    #: Đọc trạng thái checkpoint của một run (port nội bộ, chỉ đọc)
    INGEST_GET_CHECKPOINT = "ingest.get_checkpoint"
    #: Tra receipt sau khi mất ACK (trước khi retry mutation)
    INGEST_GET_RECEIPT = "ingest.get_receipt"
    #: Lấy metadata/abstract paper qua API arXiv/OpenAlex (từ server, D32)
    RESEARCH_FETCH_WORK_METADATA = "research.fetch_work_metadata"
    #: Trạng thái connector nguồn nghiên cứu (nhịp gọi, lỗi gần đây)
    RESEARCH_GET_CONNECTOR_HEALTH = "research.get_connector_health"
    #: Phân giải target (`work` | `post`) theo canonical identity
    IDENTITY_RESOLVE_TARGET = "identity.resolve_target"
    #: Ghi alias identity (không merge đoán)
    IDENTITY_RECORD_ALIAS = "identity.record_alias"
    #: Đưa xung đột identity vào cách ly
    IDENTITY_QUARANTINE_CONFLICT = "identity.quarantine_conflict"
    #: Gộp hai work đã tồn tại khi phát hiện chúng là cùng một công trình
    IDENTITY_MERGE_WORKS = "identity.merge_works"
    #: Owner giải quyết một xung đột identity đang cách ly
    IDENTITY_RESOLVE_CONFLICT = "identity.resolve_conflict"
    #: Work detail (summary, nhãn, tag khớp, post dẫn, lịch sử phân tích, mục liên quan)
    WORK_GET_DETAIL = "work.get_detail"
    #: Xếp hàng task phân tích cho các target đã commit
    ANALYSIS_ENQUEUE_TASKS = "analysis.enqueue_tasks"
    #: Analysis worker nhận task từ server
    ANALYSIS_CLAIM_TASK = "analysis.claim_task"
    #: Lấy input đã commit của task (đường dữ liệu duy nhất cho worker)
    ANALYSIS_GET_TASK_INPUT = "analysis.get_task_input"
    #: Gia hạn lease của task phân tích
    ANALYSIS_HEARTBEAT = "analysis.heartbeat"
    #: Nộp kết quả phân tích đúng schema
    ANALYSIS_SUBMIT_RESULT = "analysis.submit_result"
    #: Báo lần thử không rõ kết quả (worker chết sau khi model đã chạy)
    ANALYSIS_REPORT_ATTEMPT_UNKNOWN = "analysis.report_attempt_unknown"
    #: Owner bấm phân tích lại một mục (D26)
    ANALYSIS_REQUEST_REANALYSIS = "analysis.request_reanalysis"
    #: Chạy inference cho một task qua adapter (trên máy cá nhân)
    AI_RUN_INFERENCE_TASK = "ai.run_inference_task"
    #: Dò khả năng dùng được của provider trên máy cá nhân (đặc biệt CLI/ACP)
    AI_PROBE_PROVIDER_CAPABILITY = "ai.probe_provider_capability"
    #: Lưu API key vào secret store phía server
    SECRET_STORE_PROVIDER_KEY = "secret.store_provider_key"
    #: Cấp credential ngắn hạn theo từng task cho analysis worker (B13)
    SECRET_ISSUE_TASK_CREDENTIAL = "secret.issue_task_credential"
    #: Thu hồi credential của task khi task kết thúc hoặc lease mất
    SECRET_REVOKE_TASK_CREDENTIAL = "secret.revoke_task_credential"
    #: Sinh vector cho nhãn và tag bằng model local ở server (D50)
    EMBEDDING_GENERATE_VECTORS = "embedding.generate_vectors"
    #: Đọc embedding generation đang active
    EMBEDDING_GET_ACTIVE_GENERATION = "embedding.get_active_generation"
    #: Bắt đầu dựng generation mới khi đổi model embedding
    EMBEDDING_START_GENERATION_REBUILD = "embedding.start_generation_rebuild"
    #: Chuyển active generation một cách nguyên tử sau khi kiểm đủ vector
    EMBEDDING_ACTIVATE_GENERATION = "embedding.activate_generation"
    #: Dựng một kỳ báo cáo (chọn mục, tính hướng đang nổi)
    REPORT_BUILD = "report.build"
    #: Publish một kỳ báo cáo (transaction CAS, điểm đóng băng tag theo B01)
    REPORT_PUBLISH = "report.publish"
    #: Danh sách báo cáo theo kỳ (màn hình mặc định)
    REPORT_LIST = "report.list"
    #: Chi tiết một kỳ báo cáo
    REPORT_GET = "report.get"
    #: Save một mục (app hoặc Telegram) kèm snapshot
    SAVE_CREATE = "save.create"
    #: Bỏ lưu (khác xóa dữ liệu gốc)
    SAVE_REMOVE = "save.remove"
    #: Xóa dữ liệu gốc của **một** target (thao tác thứ hai của SRC-SPEC §7.3)
    DATA_DELETE_TARGET = "data.delete_target"
    #: Xóa toàn bộ dữ liệu (thao tác thứ ba của SRC-SPEC §7.3, đòi xác nhận gõ tay)
    DATA_PURGE_ALL = "data.purge_all"
    #: Kho đã lưu (Saved)
    SAVE_LIST = "save.list"
    #: Export Saved
    SAVE_EXPORT = "save.export"
    #: Nhận update từ Telegram (ingress webhook)
    TELEGRAM_RECEIVE_UPDATE = "telegram.receive_update"
    #: Thực thi một trong ba lệnh được phép (Save / chạy ngay / xem trạng thái)
    TELEGRAM_EXECUTE_COMMAND = "telegram.execute_command"
    #: Sinh mã liên kết một lần có hạn (trong app)
    TELEGRAM_ISSUE_LINK_CODE = "telegram.issue_link_code"
    #: Dùng mã liên kết (ngoại lệ hẹp cho chat chưa liên kết, B09)
    TELEGRAM_CONSUME_LINK_CODE = "telegram.consume_link_code"
    #: Hủy liên kết Telegram (hành động trong app)
    TELEGRAM_UNLINK = "telegram.unlink"
    #: Gửi một payload đã đóng tới recipient đã liên kết
    TELEGRAM_SEND_PAYLOAD = "telegram.send_payload"
    #: Tạo delivery intent trong transaction đã commit (outbox)
    DELIVERY_CREATE_INTENT = "delivery.create_intent"
    #: Dispatcher lấy intent kế tiếp và gửi (outbox dispatch)
    DELIVERY_DISPATCH_NEXT = "delivery.dispatch_next"
    #: Ghi receipt sau khi gửi thành công
    DELIVERY_RECORD_RECEIPT = "delivery.record_receipt"
    #: Đánh dấu part không rõ đã gửi hay chưa (B03)
    DELIVERY_MARK_UNKNOWN = "delivery.mark_unknown"
    #: Đọc trạng thái gửi của một report/alert
    DELIVERY_GET_STATUS = "delivery.get_status"
    #: Owner quyết định với một part `unknown` (B03)
    DELIVERY_DECIDE_UNKNOWN = "delivery.decide_unknown"
    #: Tạo snapshot nhất quán của SQLite (Online Backup API hoặc VACUUM INTO)
    BACKUP_CREATE_SNAPSHOT = "backup.create_snapshot"
    #: Kiểm tra tính toàn vẹn của một snapshot
    BACKUP_VERIFY_SNAPSHOT = "backup.verify_snapshot"
    #: Khôi phục từ snapshot vào môi trường có khóa side effect
    BACKUP_RESTORE_SNAPSHOT = "backup.restore_snapshot"
    #: Đối soát sau restore rồi mới mở lại side effect
    BACKUP_RECONCILE_AFTER_RESTORE = "backup.reconcile_after_restore"
    #: Liveness tối thiểu (kênh độc lập DB)
    HEALTH_GET_LIVENESS = "health.get_liveness"
    #: Readiness chi tiết theo module
    HEALTH_GET_READINESS = "health.get_readiness"
    #: Trạng thái ghi được của data store
    STORAGE_GET_HEALTH = "storage.get_health"


#: Operation id -> `owner_module` of contracts/ports.yaml.
OWNER_MODULE: dict[OperationId, str] = {
    OperationId.AUTH_LOGIN: "MOD-auth-service",
    OperationId.AUTH_LOGOUT: "MOD-auth-service",
    OperationId.AUTH_GET_SESSION: "MOD-auth-service",
    OperationId.SETTINGS_GET_CONFIG: "MOD-settings-service",
    OperationId.SETTINGS_UPDATE_CONFIG: "MOD-settings-service",
    OperationId.SETTINGS_TEST_PROVIDER: "MOD-settings-service",
    OperationId.TAG_LIST: "MOD-tag-service",
    OperationId.TAG_CREATE: "MOD-tag-service",
    OperationId.TAG_UPDATE: "MOD-tag-service",
    OperationId.TAG_DELETE: "MOD-tag-service",
    OperationId.TAG_PREVIEW_MATCHES: "MOD-tag-service",
    OperationId.TAG_RESCAN_CORPUS: "MOD-tag-service",
    OperationId.TAG_GET_ACTIVE_CONFIG_VERSION: "MOD-tag-service",
    OperationId.TAG_FREEZE_CONFIG_VERSION: "MOD-tag-service",
    OperationId.RUN_LIST: "MOD-job-service",
    OperationId.RUN_GET: "MOD-job-service",
    OperationId.RUN_RUN_NOW: "MOD-job-service",
    OperationId.RUN_RESUME: "MOD-job-service",
    OperationId.RUN_CANCEL: "MOD-job-service",
    OperationId.SCHEDULER_EVALUATE_DUE: "MOD-scheduler",
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN: "MOD-job-service",
    OperationId.JOB_COALESCE_OVERDUE: "MOD-job-service",
    OperationId.WORKER_REGISTER_CAPABILITIES: "MOD-job-service",
    OperationId.WORKER_CLAIM_ASSIGNMENT: "MOD-job-service",
    OperationId.WORKER_HEARTBEAT: "MOD-job-service",
    OperationId.WORKER_REPORT_STOP: "MOD-job-service",
    OperationId.WORKER_RELEASE_ASSIGNMENT: "MOD-job-service",
    OperationId.WORKER_GET_STATUS: "MOD-job-service",
    OperationId.INGEST_SUBMIT_BATCH: "MOD-ingest-service",
    OperationId.INGEST_COMMIT_CHECKPOINT: "MOD-ingest-service",
    OperationId.INGEST_GET_CHECKPOINT: "MOD-ingest-service",
    OperationId.INGEST_GET_RECEIPT: "MOD-ingest-service",
    OperationId.RESEARCH_FETCH_WORK_METADATA: "MOD-research-connector",
    OperationId.RESEARCH_GET_CONNECTOR_HEALTH: "MOD-research-connector",
    OperationId.IDENTITY_RESOLVE_TARGET: "MOD-identity-service",
    OperationId.IDENTITY_RECORD_ALIAS: "MOD-identity-service",
    OperationId.IDENTITY_QUARANTINE_CONFLICT: "MOD-identity-service",
    OperationId.IDENTITY_MERGE_WORKS: "MOD-identity-service",
    OperationId.IDENTITY_RESOLVE_CONFLICT: "MOD-identity-service",
    OperationId.WORK_GET_DETAIL: "MOD-identity-service",
    OperationId.ANALYSIS_ENQUEUE_TASKS: "MOD-analysis-service",
    OperationId.ANALYSIS_CLAIM_TASK: "MOD-analysis-service",
    OperationId.ANALYSIS_GET_TASK_INPUT: "MOD-analysis-service",
    OperationId.ANALYSIS_HEARTBEAT: "MOD-analysis-service",
    OperationId.ANALYSIS_SUBMIT_RESULT: "MOD-analysis-service",
    OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN: "MOD-analysis-service",
    OperationId.ANALYSIS_REQUEST_REANALYSIS: "MOD-analysis-service",
    OperationId.AI_RUN_INFERENCE_TASK: "MOD-ai-adapter",
    OperationId.AI_PROBE_PROVIDER_CAPABILITY: "MOD-ai-adapter",
    OperationId.SECRET_STORE_PROVIDER_KEY: "MOD-secret-service",
    OperationId.SECRET_ISSUE_TASK_CREDENTIAL: "MOD-secret-service",
    OperationId.SECRET_REVOKE_TASK_CREDENTIAL: "MOD-secret-service",
    OperationId.EMBEDDING_GENERATE_VECTORS: "MOD-embedding-service",
    OperationId.EMBEDDING_GET_ACTIVE_GENERATION: "MOD-embedding-service",
    OperationId.EMBEDDING_START_GENERATION_REBUILD: "MOD-embedding-service",
    OperationId.EMBEDDING_ACTIVATE_GENERATION: "MOD-embedding-service",
    OperationId.REPORT_BUILD: "MOD-report-service",
    OperationId.REPORT_PUBLISH: "MOD-report-service",
    OperationId.REPORT_LIST: "MOD-report-service",
    OperationId.REPORT_GET: "MOD-report-service",
    OperationId.SAVE_CREATE: "MOD-saved-service",
    OperationId.SAVE_REMOVE: "MOD-saved-service",
    OperationId.DATA_DELETE_TARGET: "MOD-data-admin-service",
    OperationId.DATA_PURGE_ALL: "MOD-data-admin-service",
    OperationId.SAVE_LIST: "MOD-saved-service",
    OperationId.SAVE_EXPORT: "MOD-saved-service",
    OperationId.TELEGRAM_RECEIVE_UPDATE: "MOD-telegram-adapter",
    OperationId.TELEGRAM_EXECUTE_COMMAND: "MOD-telegram-adapter",
    OperationId.TELEGRAM_ISSUE_LINK_CODE: "MOD-telegram-adapter",
    OperationId.TELEGRAM_CONSUME_LINK_CODE: "MOD-telegram-adapter",
    OperationId.TELEGRAM_UNLINK: "MOD-telegram-adapter",
    OperationId.TELEGRAM_SEND_PAYLOAD: "MOD-telegram-adapter",
    OperationId.DELIVERY_CREATE_INTENT: "MOD-delivery-service",
    OperationId.DELIVERY_DISPATCH_NEXT: "MOD-delivery-service",
    OperationId.DELIVERY_RECORD_RECEIPT: "MOD-delivery-service",
    OperationId.DELIVERY_MARK_UNKNOWN: "MOD-delivery-service",
    OperationId.DELIVERY_GET_STATUS: "MOD-delivery-service",
    OperationId.DELIVERY_DECIDE_UNKNOWN: "MOD-delivery-service",
    OperationId.BACKUP_CREATE_SNAPSHOT: "MOD-backup-service",
    OperationId.BACKUP_VERIFY_SNAPSHOT: "MOD-backup-service",
    OperationId.BACKUP_RESTORE_SNAPSHOT: "MOD-backup-service",
    OperationId.BACKUP_RECONCILE_AFTER_RESTORE: "MOD-backup-service",
    OperationId.HEALTH_GET_LIVENESS: "MOD-health-service",
    OperationId.HEALTH_GET_READINESS: "MOD-health-service",
    OperationId.STORAGE_GET_HEALTH: "MOD-data-store",
}

#: Operation id -> `transport` of contracts/ports.yaml.
TRANSPORT: dict[OperationId, str] = {
    OperationId.AUTH_LOGIN: "http",
    OperationId.AUTH_LOGOUT: "http",
    OperationId.AUTH_GET_SESSION: "http",
    OperationId.SETTINGS_GET_CONFIG: "http",
    OperationId.SETTINGS_UPDATE_CONFIG: "http",
    OperationId.SETTINGS_TEST_PROVIDER: "http",
    OperationId.TAG_LIST: "http",
    OperationId.TAG_CREATE: "http",
    OperationId.TAG_UPDATE: "http",
    OperationId.TAG_DELETE: "http",
    OperationId.TAG_PREVIEW_MATCHES: "http",
    OperationId.TAG_RESCAN_CORPUS: "http",
    OperationId.TAG_GET_ACTIVE_CONFIG_VERSION: "internal",
    OperationId.TAG_FREEZE_CONFIG_VERSION: "internal",
    OperationId.RUN_LIST: "http",
    OperationId.RUN_GET: "http",
    OperationId.RUN_RUN_NOW: "http",
    OperationId.RUN_RESUME: "http",
    OperationId.RUN_CANCEL: "http",
    OperationId.SCHEDULER_EVALUATE_DUE: "internal",
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN: "internal",
    OperationId.JOB_COALESCE_OVERDUE: "internal",
    OperationId.WORKER_REGISTER_CAPABILITIES: "http",
    OperationId.WORKER_CLAIM_ASSIGNMENT: "http",
    OperationId.WORKER_HEARTBEAT: "http",
    OperationId.WORKER_REPORT_STOP: "http",
    OperationId.WORKER_RELEASE_ASSIGNMENT: "http",
    OperationId.WORKER_GET_STATUS: "http",
    OperationId.INGEST_SUBMIT_BATCH: "http",
    OperationId.INGEST_COMMIT_CHECKPOINT: "http",
    OperationId.INGEST_GET_CHECKPOINT: "internal",
    OperationId.INGEST_GET_RECEIPT: "http",
    OperationId.RESEARCH_FETCH_WORK_METADATA: "internal",
    OperationId.RESEARCH_GET_CONNECTOR_HEALTH: "internal",
    OperationId.IDENTITY_RESOLVE_TARGET: "internal",
    OperationId.IDENTITY_RECORD_ALIAS: "internal",
    OperationId.IDENTITY_QUARANTINE_CONFLICT: "internal",
    OperationId.IDENTITY_MERGE_WORKS: "internal",
    OperationId.IDENTITY_RESOLVE_CONFLICT: "http",
    OperationId.WORK_GET_DETAIL: "http",
    OperationId.ANALYSIS_ENQUEUE_TASKS: "internal",
    OperationId.ANALYSIS_CLAIM_TASK: "http",
    OperationId.ANALYSIS_GET_TASK_INPUT: "http",
    OperationId.ANALYSIS_HEARTBEAT: "http",
    OperationId.ANALYSIS_SUBMIT_RESULT: "http",
    OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN: "http",
    OperationId.ANALYSIS_REQUEST_REANALYSIS: "http",
    OperationId.AI_RUN_INFERENCE_TASK: "internal",
    OperationId.AI_PROBE_PROVIDER_CAPABILITY: "internal",
    OperationId.SECRET_STORE_PROVIDER_KEY: "internal",
    OperationId.SECRET_ISSUE_TASK_CREDENTIAL: "http",
    OperationId.SECRET_REVOKE_TASK_CREDENTIAL: "internal",
    OperationId.EMBEDDING_GENERATE_VECTORS: "internal",
    OperationId.EMBEDDING_GET_ACTIVE_GENERATION: "internal",
    OperationId.EMBEDDING_START_GENERATION_REBUILD: "internal",
    OperationId.EMBEDDING_ACTIVATE_GENERATION: "internal",
    OperationId.REPORT_BUILD: "internal",
    OperationId.REPORT_PUBLISH: "internal",
    OperationId.REPORT_LIST: "http",
    OperationId.REPORT_GET: "http",
    OperationId.SAVE_CREATE: "http",
    OperationId.SAVE_REMOVE: "http",
    OperationId.DATA_DELETE_TARGET: "http",
    OperationId.DATA_PURGE_ALL: "http",
    OperationId.SAVE_LIST: "http",
    OperationId.SAVE_EXPORT: "http",
    OperationId.TELEGRAM_RECEIVE_UPDATE: "http",
    OperationId.TELEGRAM_EXECUTE_COMMAND: "internal",
    OperationId.TELEGRAM_ISSUE_LINK_CODE: "http",
    OperationId.TELEGRAM_CONSUME_LINK_CODE: "internal",
    OperationId.TELEGRAM_UNLINK: "http",
    OperationId.TELEGRAM_SEND_PAYLOAD: "internal",
    OperationId.DELIVERY_CREATE_INTENT: "internal",
    OperationId.DELIVERY_DISPATCH_NEXT: "internal",
    OperationId.DELIVERY_RECORD_RECEIPT: "internal",
    OperationId.DELIVERY_MARK_UNKNOWN: "internal",
    OperationId.DELIVERY_GET_STATUS: "http",
    OperationId.DELIVERY_DECIDE_UNKNOWN: "http",
    OperationId.BACKUP_CREATE_SNAPSHOT: "http",
    OperationId.BACKUP_VERIFY_SNAPSHOT: "http",
    OperationId.BACKUP_RESTORE_SNAPSHOT: "http",
    OperationId.BACKUP_RECONCILE_AFTER_RESTORE: "http",
    OperationId.HEALTH_GET_LIVENESS: "http",
    OperationId.HEALTH_GET_READINESS: "http",
    OperationId.STORAGE_GET_HEALTH: "internal",
}

#: Operation id -> `mutation` of contracts/ports.yaml.
MUTATION: dict[OperationId, bool] = {
    OperationId.AUTH_LOGIN: True,
    OperationId.AUTH_LOGOUT: True,
    OperationId.AUTH_GET_SESSION: False,
    OperationId.SETTINGS_GET_CONFIG: False,
    OperationId.SETTINGS_UPDATE_CONFIG: True,
    OperationId.SETTINGS_TEST_PROVIDER: True,
    OperationId.TAG_LIST: False,
    OperationId.TAG_CREATE: True,
    OperationId.TAG_UPDATE: True,
    OperationId.TAG_DELETE: True,
    OperationId.TAG_PREVIEW_MATCHES: False,
    OperationId.TAG_RESCAN_CORPUS: True,
    OperationId.TAG_GET_ACTIVE_CONFIG_VERSION: False,
    OperationId.TAG_FREEZE_CONFIG_VERSION: True,
    OperationId.RUN_LIST: False,
    OperationId.RUN_GET: False,
    OperationId.RUN_RUN_NOW: True,
    OperationId.RUN_RESUME: True,
    OperationId.RUN_CANCEL: True,
    OperationId.SCHEDULER_EVALUATE_DUE: False,
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN: True,
    OperationId.JOB_COALESCE_OVERDUE: True,
    OperationId.WORKER_REGISTER_CAPABILITIES: True,
    OperationId.WORKER_CLAIM_ASSIGNMENT: True,
    OperationId.WORKER_HEARTBEAT: True,
    OperationId.WORKER_REPORT_STOP: True,
    OperationId.WORKER_RELEASE_ASSIGNMENT: True,
    OperationId.WORKER_GET_STATUS: False,
    OperationId.INGEST_SUBMIT_BATCH: True,
    OperationId.INGEST_COMMIT_CHECKPOINT: True,
    OperationId.INGEST_GET_CHECKPOINT: False,
    OperationId.INGEST_GET_RECEIPT: False,
    OperationId.RESEARCH_FETCH_WORK_METADATA: False,
    OperationId.RESEARCH_GET_CONNECTOR_HEALTH: False,
    OperationId.IDENTITY_RESOLVE_TARGET: False,
    OperationId.IDENTITY_RECORD_ALIAS: True,
    OperationId.IDENTITY_QUARANTINE_CONFLICT: True,
    OperationId.IDENTITY_MERGE_WORKS: True,
    OperationId.IDENTITY_RESOLVE_CONFLICT: True,
    OperationId.WORK_GET_DETAIL: False,
    OperationId.ANALYSIS_ENQUEUE_TASKS: True,
    OperationId.ANALYSIS_CLAIM_TASK: True,
    OperationId.ANALYSIS_GET_TASK_INPUT: False,
    OperationId.ANALYSIS_HEARTBEAT: True,
    OperationId.ANALYSIS_SUBMIT_RESULT: True,
    OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN: True,
    OperationId.ANALYSIS_REQUEST_REANALYSIS: True,
    OperationId.AI_RUN_INFERENCE_TASK: False,
    OperationId.AI_PROBE_PROVIDER_CAPABILITY: False,
    OperationId.SECRET_STORE_PROVIDER_KEY: True,
    OperationId.SECRET_ISSUE_TASK_CREDENTIAL: True,
    OperationId.SECRET_REVOKE_TASK_CREDENTIAL: True,
    OperationId.EMBEDDING_GENERATE_VECTORS: True,
    OperationId.EMBEDDING_GET_ACTIVE_GENERATION: False,
    OperationId.EMBEDDING_START_GENERATION_REBUILD: True,
    OperationId.EMBEDDING_ACTIVATE_GENERATION: True,
    OperationId.REPORT_BUILD: True,
    OperationId.REPORT_PUBLISH: True,
    OperationId.REPORT_LIST: False,
    OperationId.REPORT_GET: False,
    OperationId.SAVE_CREATE: True,
    OperationId.SAVE_REMOVE: True,
    OperationId.DATA_DELETE_TARGET: True,
    OperationId.DATA_PURGE_ALL: True,
    OperationId.SAVE_LIST: False,
    OperationId.SAVE_EXPORT: False,
    OperationId.TELEGRAM_RECEIVE_UPDATE: True,
    OperationId.TELEGRAM_EXECUTE_COMMAND: True,
    OperationId.TELEGRAM_ISSUE_LINK_CODE: True,
    OperationId.TELEGRAM_CONSUME_LINK_CODE: True,
    OperationId.TELEGRAM_UNLINK: True,
    OperationId.TELEGRAM_SEND_PAYLOAD: True,
    OperationId.DELIVERY_CREATE_INTENT: True,
    OperationId.DELIVERY_DISPATCH_NEXT: True,
    OperationId.DELIVERY_RECORD_RECEIPT: True,
    OperationId.DELIVERY_MARK_UNKNOWN: True,
    OperationId.DELIVERY_GET_STATUS: False,
    OperationId.DELIVERY_DECIDE_UNKNOWN: True,
    OperationId.BACKUP_CREATE_SNAPSHOT: True,
    OperationId.BACKUP_VERIFY_SNAPSHOT: True,
    OperationId.BACKUP_RESTORE_SNAPSHOT: True,
    OperationId.BACKUP_RECONCILE_AFTER_RESTORE: True,
    OperationId.HEALTH_GET_LIVENESS: False,
    OperationId.HEALTH_GET_READINESS: False,
    OperationId.STORAGE_GET_HEALTH: False,
}
