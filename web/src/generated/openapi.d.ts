// GENERATED — do not edit; source sha256 28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92
// Produced by web/scripts/generate.mjs from contracts/http/openapi.yaml.
// Editing this file by hand makes code and contract drift apart silently; the rule is
// ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change the wire types: change
// the contract, regenerate, and mark the affected task cards STALE per INV-06.

export interface paths {
    "/healthz": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Liveness tối thiểu (kênh độc lập DB)
         * @description Không. Kênh này phải trả lời được **kể cả khi DB không ghi được** (SRC-PLAN §8.4).
         *
         *     Phải trả lời được KỂ CẢ KHI DB không ghi được (SRC-PLAN §8.4). CHỈ `up` + phiên bản schema; KHÔNG lộ cấu hình, tên provider, chat ID hay dữ liệu nghiệp vụ.
         */
        get: operations["health.get_liveness"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/reanalysis": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Owner bấm phân tích lại một mục (D26)
         * @description target reference + lý do (`manual` | `new_paper_version`).
         *
         *     Tạo generation mới, **giữ bản cũ** (D26). Đổi tag không kích hoạt operation này (AC-06: 0 lần gọi AI).
         *
         *     Tạo GENERATION MỚI, giữ bản cũ (REQ-D26). Đổi tag KHÔNG kích hoạt operation này (REQ-AC06: 0 lần gọi AI).
         */
        post: operations["analysis.request_reanalysis"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/tasks/{task_id}/attempt-unknown": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Báo lần thử không rõ kết quả (worker chết sau khi model đã chạy)
         * @description task_id, attempt_id, thời điểm, lý do mất kết quả.
         *
         *     analysis → `unknown_attempt`. **Không** cam kết chưa phát sinh chi phí; chạy lại ghi attempt mới (SRC-PLAN §10 AI_ATTEMPT_UNCERTAIN).
         *
         *     KHÔNG cam kết chưa phát sinh phí; chạy lại ghi attempt MỚI (SRC-PLAN §10 AI_ATTEMPT_UNCERTAIN).
         */
        post: operations["analysis.report_attempt_unknown"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/tasks/{task_id}/heartbeat": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Gia hạn lease của task phân tích
         * @description lease_id, lease_epoch, tiến độ.
         *
         *     Cập nhật hạn lease; không ghi kết quả.
         */
        post: operations["analysis.heartbeat"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/tasks/{task_id}/input": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Lấy input đã commit của task (đường dữ liệu duy nhất cho worker)
         * @description task_id + lease_id/epoch.
         *
         *     Không. Worker **không** nhận dữ liệu chưa commit trực tiếp từ collector (B12).
         *
         *     Nội dung nguồn là DỮ LIỆU, KHÔNG phải lệnh (SRC-SPEC §11.4, I11).
         */
        get: operations["analysis.get_task_input"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/tasks/{task_id}/result": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Nộp kết quả phân tích đúng schema
         * @description task_id, lease_id/epoch, JSON đúng schema với `author_claim` / `source_verified` / `ai_inference` tách riêng, citation target, evidence level, usage (`unknown` được phép).
         *
         *     analysis `running` → `valid` khi schema hợp lệ; sai schema → AI_OUTPUT_INVALID, không commit. Usage không biết ghi `unknown`, **không** ghi 0 (I14). Comparator thiếu ghi `comparator: unknown` (B16).
         *
         *     `valid` chỉ đạt sau CẢ HAI cửa: schema validation VÀ semantic validation của PC06 (contracts/state/analysis.yaml T-AN-03). Usage không biết ghi `unknown`, KHÔNG ghi 0 (I14).
         */
        post: operations["analysis.submit_result"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/analysis/tasks/claim": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Analysis worker nhận task từ server
         * @description worker_instance_id, capability provider hiện có, số task muốn nhận.
         *
         *     analysis `pending` → `running`; cấp lease/epoch.
         *
         *     Task CHỈ được tạo cho dữ liệu ĐÃ COMMIT ở server (B12/AMD-B12); worker không nhận dữ liệu trực tiếp từ collector. Schema chi tiết thuộc PC06 (`contracts/ai/tasks.yaml`).
         */
        post: operations["analysis.claim_task"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Đăng nhập tài khoản duy nhất
         * @description Thông tin đăng nhập của owner; không có trang signup (D05).
         *
         *     Tạo một session của owner; ghi audit đăng nhập đã che secrets.
         *
         *     Một tài khoản duy nhất, KHÔNG có trang signup và KHÔNG có quên-mật-khẩu tự động (REQ-D05).
         */
        post: operations["auth.login"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Kết thúc session hiện tại
         * @description Không có body; định danh lấy từ session.
         *
         *     Thu hồi session; không đụng dữ liệu nghiệp vụ.
         */
        post: operations["auth.logout"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/auth/session": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Đọc trạng thái session */
        get: operations["auth.get_session"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/backup/restores": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Khôi phục từ snapshot vào môi trường có khóa side effect
         * @description snapshot_id + môi trường đích + xác nhận gõ tay.
         *
         *     Sau restore, `storage.health = recovery_required`: dispatcher và worker claim **bị dừng**, outbox **không** replay, `first_announced` **không** bị reset cho tới khi reconcile xong (I15).
         *
         *     Sau restore: dispatcher và worker claim BỊ DỪNG, outbox cũ KHÔNG replay, `first_announced` KHÔNG bị reset cho tới khi reconcile xong (I15, NC-10). Cần xác nhận gõ tay.
         */
        post: operations["backup.restore_snapshot"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/backup/restores/{restore_id}/reconcile": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Đối soát sau restore rồi mới mở lại side effect
         * @description restore_id + quyết định với outbox cũ và lease cũ.
         *
         *     Thu hồi stale lease, quyết định outbox cũ **có chủ đích**, rồi mới chuyển `storage.health` về `healthy`. Không có đường tự động resume dispatcher (negative case NC-10).
         *
         *     CỔNG DUY NHẤT mở lại side effect. Thu hồi stale lease, quyết định outbox cũ CÓ CHỦ ĐÍCH, rồi mới chuyển `storage.health` về `healthy`. KHÔNG có đường tự động (NC-10).
         */
        post: operations["backup.reconcile_after_restore"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/backup/snapshots": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Tạo snapshot nhất quán của SQLite (Online Backup API hoặc VACUUM INTO)
         * @description Nhãn snapshot + đích lưu.
         *
         *     **Không** copy file DB đang hoạt động làm bằng chứng đủ; WAL là một phần trạng thái bền (SRC-PLAN §3.1). Profile Chrome trên máy cá nhân **không** nằm trong backup của server (SRC-SPEC §11.2).
         *
         *     SQLite Online Backup API hoặc `VACUUM INTO` — an toàn với WAL (AMD-B11/ADR-0005). KHÔNG copy riêng file DB.
         */
        post: operations["backup.create_snapshot"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/backup/snapshots/{snapshot_id}/verify": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Kiểm tra tính toàn vẹn của một snapshot
         * @description snapshot_id.
         *
         *     Ghi kết quả verify; không đổi dữ liệu sản xuất.
         */
        post: operations["backup.verify_snapshot"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/data/purge": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Xóa toàn bộ dữ liệu (thao tác thứ ba của SRC-SPEC §7.3, đòi xác nhận gõ tay)
         * @description `phase`, `purge_challenge_id` (phase execute), `confirmation_phrase` (phase execute).
         *
         *     Xem transaction_vi và exclusions_vi. Ba tập bảng (37 xóa / 21 giữ / 2 không bao giờ xóa) theo ruling CR-PC05-06 + CR-PC05-07; CR-PC01-05 khép lại.
         *
         *     Xóa dữ liệu nghiên cứu. Phạm vi ĐÃ ĐƯỢC OWNER CHỐT — `ACCEPTED (OD-20260907-01 mục 24)`; nó KHÔNG còn `OWNER_DECISION_REQUIRED`, và `PROV-PC00-01` / `PROV-PC01-03` chỉ còn giá trị LỊCH SỬ. Ba tập bảng dưới đây lấy nguyên văn từ ruling `PURGE-LIST-ruling.md` (2026-09-07T05:55Z), bản đã sửa lỗi CR-PC05-06.
         *
         *     XÓA (37 bảng): post, post_work, work, work_version, identity_alias, identity_conflict, identity_merge_audit, work_label, analysis, analysis_generation, analysis_attempt, analysis_task, embedding_generation, tag_vector, report, report_item, emerging_direction, coverage_window, pending_item_ledger, backfill_ledger, first_announced_ledger, rescan_ledger, saved_item, saved_snapshot, delivery, delivery_part, delivery_attempt, delivery_receipt, outbox_intent, run, assignment, assignment_lease, checkpoint, ingest_receipt, source_fetch_log, telegram_update_log, telegram_link_attempt (bộ đếm rate limit, giữ 30 ngày — dữ liệu VẬN HÀNH, không phải cấu hình).
         *
         *     GIỮ LẠI (21 bảng): `owner`, `session`, `secret_ref`, `task_credential`, `secret_audit`, `telegram_link`, `telegram_link_code`, `provider_config`, `provider_test_result`, `settings`, `schedule_occurrence`, `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version`, `source_connection`, `backup_snapshot`, `backup_manifest`, `restore_record`, `purge_challenge`, `worker_registration` (đăng ký/token của collector là CẤU HÌNH, không chứa dữ liệu nghiên cứu; xóa nó buộc phải đăng ký lại collector).
         *
         *     KHÔNG BAO GIỜ XÓA (2 bảng): `schema_migration` (mô tả cấu trúc kho) và `data_deletion_audit` (bản ghi xóa được giữ VĨNH VIỄN theo tham số PC08 đã phê chuẩn; chính thao tác purge ghi một hàng audit vào đây).
         *
         *     LÝ DO GIỮ: xóa credential đăng nhập sẽ khóa chính chủ nhà ra ngoài app (REQ-D05 cấm signup và cấm quên-mật-khẩu tự động), và xóa cấu hình biến 'xóa dữ liệu' thành 'gỡ cài đặt' — hai ý định khác nhau. Sau purge, hệ thống vẫn đăng nhập được, vẫn giữ lịch và tag, và vẫn đủ cấu hình để chạy đợt mới từ đầu.
         *
         *     BACKUP KHÔNG BỊ ĐỤNG TỚI: artifact backup trên hệ thống tệp và các bảng `backup_*` đều được giữ. Hộp thoại xác nhận PHẢI nói thẳng rằng **dữ liệu vừa xóa vẫn còn trong các bản backup**; xóa khỏi backup là một thao tác vận hành RIÊNG (contracts/ops/backup-restore.md). Không được để người dùng tin rằng purge đã xóa mọi dấu vết — đây là điểm Owner được cảnh báo là có hậu quả lớn nhất.
         *
         *     HAI PHA (một operation_id, hai `phase`): (1) `request_challenge` — server sinh `purge_challenge` có hạn và trả về cụm từ xác nhận để người dùng gõ lại; KHÔNG xóa gì. (2) `execute` — đòi `purge_challenge_id` + `confirmation_phrase` khớp CHÍNH XÁC cụm từ server đã phát; sai hoặc hết hạn ⇒ 422 `VALIDATION_ERROR`, challenge bị hủy và phải xin lại. Một challenge dùng đúng một lần.
         *
         *     TIỀN ĐIỀU KIỆN: chỉ chạy được khi `storage.health = maintenance`; ở `healthy`, `write_blocked` hay `recovery_required` ⇒ 409 `CONFLICT`. Thu hồi mọi `assignment_lease`, dừng scheduler và delivery dispatcher TRƯỚC khi xóa (I10). Sau khi xong, `storage.health` VẪN ở `maintenance` cho tới khi owner mở lại — không tự động resume dispatcher (cùng nguyên tắc NC-10).
         */
        post: operations["data.purge_all"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/data/targets/{target_ref}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Xóa dữ liệu gốc của **một** target (thao tác thứ hai của SRC-SPEC §7.3)
         * @description `target_ref` (tagged union `work` | `post`), `confirmation.acknowledged: true` (cờ xác nhận **bắt buộc**; thiếu hoặc `false` ⇒ `VALIDATION_ERROR`), và lý do tùy chọn.
         *
         *     Quy tắc cascade và referential integrity chi tiết thuộc PC02 (`contracts/data/entities.yaml`, `contracts/data/invariants.md`) — PC01 chốt **ai sở hữu mutation, phạm vi giữ lại và cờ xác nhận**, không chốt danh sách bảng cuối cùng (CR-PC01-05).
         *
         *     Xóa dữ liệu gốc của MỘT target; GIỮ `saved_snapshot` (REQ-D55) và các ledger. Cần cờ xác nhận tường minh trong body. Khác `data.purge_all` ở phạm vi: thao tác này nhắm một target, không đụng tới cấu hình hay dữ liệu nghiên cứu khác, và cũng KHÔNG đụng tới backup — dữ liệu đã xóa vẫn còn trong các bản backup (OD-20260907-01 mục 24, cùng quy tắc với `data.purge_all`).
         */
        delete: operations["data.delete_target"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/deliveries/{delivery_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Đọc trạng thái gửi của một report/alert
         * @description report_id hoặc delivery_id.
         *
         *     Trả trạng thái aggregate VÀ từng part. Bốn trạng thái incomplete/empty/failed/unknown hiển thị RIÊNG (I13).
         */
        get: operations["delivery.get_status"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/deliveries/parts/{delivery_part_id}/decide": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Owner quyết định với một part `unknown` (B03)
         * @description delivery_part_id + quyết định ∈ {`resend_accepting_duplicate_risk`, `mark_not_delivered`, `abandon`} + xác nhận rằng nguy cơ trùng đã được chấp nhận.
         *
         *     Chỉ **operator** mới đưa part `unknown` ra khỏi trạng thái đó; hệ thống không tự quyết định (AMD-B03).
         *
         *     CHỈ Operator mới đưa một part ra khỏi `unknown`; hệ thống KHÔNG tự quyết định (AMD-B03). Ba lựa chọn: `resend_accepting_duplicate_risk` | `mark_not_delivered` | `abandon`, kèm xác nhận đã chấp nhận nguy cơ trùng.
         */
        post: operations["delivery.decide_unknown"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/health/readiness": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Readiness chi tiết theo module
         * @description Trạng thái từng module từ BỘ NHỚ tiến trình; đây là fallback bắt buộc của quy tắc EPR-01 (contracts/errors.yaml).
         */
        get: operations["health.get_readiness"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/identity/conflicts/{conflict_id}/resolve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Owner giải quyết một xung đột identity đang cách ly
         * @description conflict_id + quyết định (`merge` | `keep_separate`) + lý do.
         *
         *     Quyết định `merge` thực thi bằng cách gọi identity.merge_works (port nội bộ) — đó là đường merge **duy nhất**; quyết định `keep_separate` đóng conflict và giữ hai canonical id. Giữ audit trail; snapshot lịch sử **không** bị sửa (PC02 chốt chi tiết).
         *
         *     KHÔNG merge đoán (B15, I03). Merge vượt `identity_merge_max_moved_rows` (100000, PROVISIONAL) bị từ chối và ở lại `identity_conflict`.
         */
        post: operations["identity.resolve_conflict"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/ingest/batches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Nộp một lô post đã thu thập (collector → server, D08)
         * @description request_id, schema_version, idempotency_key, payload_hash, job_id, lease_id, lease_epoch, danh sách post (x_post_id, tác giả, nội dung, URL, published_at, provenance), link paper phát hiện được. Quan sát "nguồn đã bị xóa trên X" là **một trường của item** trong lô — `source_deleted_observed_at` (RFC 3339 UTC, nullable) — chứ **không** phải một operation riêng: collector chỉ báo cáo cái nó quan sát được ở thời điểm thu thập, còn việc diễn giải và ghi nhận là của server (ruling của Coordinator trong PKT-PC01-FIX1). Trường này không xóa dữ liệu và không đụng tới Saved: snapshot đã lưu vẫn đọc được kể cả khi bài gốc bị xóa trên X (D55, AC-12).
         *
         *     **Đường chính để checkpoint trở nên bền.** Commit post + receipt dedup + `client_checkpoint_proposal` của lô trong **cùng một** transaction (PC02 `TXN-ingest-batch`, I02). Dedup theo `x_post_id`; cam kết là **không ingest trùng**, không phải "không bao giờ đọc lại" (B05/AMD-B05). ACK chỉ sau commit. Không có đường nào ghi checkpoint ở transaction riêng **trước** commit của lô (ruling R-01); ingest.commit_checkpoint chỉ dùng khi lô rỗng.
         *
         *     Giới hạn tầng transport: tối đa 200 item và 8 MiB body (`x-transport-limits`); vượt ⇒ 422 `VALIDATION_ERROR`, KHÔNG cắt cụt âm thầm. Item hỏng ở mức nghiệp vụ đi vào `counts.rejected` của receipt chứ không làm hỏng cả lô.
         */
        post: operations["ingest.submit_batch"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/ingest/checkpoints": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Đẩy con trỏ checkpoint khi **không có** item mới (cursor-only advance)
         * @description lease_id/epoch, `proposed_cursor`, `proposed_acked_through_ingest_sequence`, `reason` ∈ {`empty_page`, `end_of_feed`, `segment_close`}, và `item_count: 0` (bắt buộc bằng 0).
         *
         *     Checkpoint **không đi trước dữ liệu bền** (I02). Dữ liệu đã tải nhưng chưa ingest không được coi là checkpoint bền (SRC-PLAN §8.1). Entity là `checkpoint`, **do MOD-ingest-service sở hữu duy nhất**; MOD-job-service chỉ **đọc** trạng thái này qua ingest.get_checkpoint hoặc qua payload của worker.claim_assignment, không sở hữu và không ghi (ruling R-01; token `run_checkpoint_pointer` đã bị gỡ).
         *
         *     RULING R-01: đường này chỉ TIẾN CON TRỎ, KHÔNG kèm item mới (trang rỗng / hết feed / đóng segment). GUARD: `proposed_acked_through_ingest_sequence` chỉ được <= `acked_through_ingest_sequence` đã commit của run; vượt quá ⇒ 422 VALIDATION_ERROR và KHÔNG có write một phần. Oracle: `checkpoint.acked_through_ingest_sequence <= max(committed ingest_receipt.max_ingest_sequence)`.
         */
        post: operations["ingest.commit_checkpoint"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/ingest/receipts/{idempotency_key}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Tra receipt sau khi mất ACK (trước khi retry mutation)
         * @description assignment_id + batch_idempotency_key.
         *
         *     ĐƯỜNG TRA CỨU BẮT BUỘC trước mọi retry mutation (SRC-PLAN §5.1). Read-only.
         */
        get: operations["ingest.get_receipt"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/reports": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Danh sách báo cáo theo kỳ (màn hình mặc định)
         * @description Phân trang.
         *
         *     Response mang `report_build_id` (UUIDv4, `UNIQUE(owner_id, report_build_id)` — khóa idempotency của `report.publish`, F-A1R2-01) và `abort_reason` (enum `empty_period | tag_version_stale | embedding_generation_mismatch | cas_conflict | builder_failure | cancelled`, NOT NULL khi và chỉ khi `status='aborted'`). Hai cột do PC02 FIX3 khai trên ENT-report theo bảng field-level của ruling FIX3; hình dạng chi tiết ở `contracts/schemas/report.schema.json` (PC04). `abort_reason='empty_period'` là một kỳ RỖNG HỢP LỆ, KHÔNG phải lỗi — UI không được gộp nó với `builder_failure` (I13).
         */
        get: operations["report.list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/reports/{report_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Chi tiết một kỳ báo cáo
         * @description report_id.
         *
         *     Nội dung report đã publish là BẤT BIẾN (I05); delivery không đổi nó (B01). Response mang `report_build_id` (UUIDv4, `UNIQUE(owner_id, report_build_id)` — khóa idempotency của `report.publish`, F-A1R2-01) và `abort_reason` (enum `empty_period | tag_version_stale | embedding_generation_mismatch | cas_conflict | builder_failure | cancelled`, NOT NULL khi và chỉ khi `status='aborted'`). Hai cột do PC02 FIX3 khai trên ENT-report theo bảng field-level của ruling FIX3; hình dạng chi tiết ở `contracts/schemas/report.schema.json` (PC04). `abort_reason='empty_period'` là một kỳ RỖNG HỢP LỆ, KHÔNG phải lỗi — UI không được gộp nó với `builder_failure` (I13).
         */
        get: operations["report.get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Danh sách run + trạng thái collector online/offline
         * @description Bộ lọc phân trang; với caller Telegram chỉ lấy N run gần nhất.
         *
         *     Không. Lệnh status **không** mutation (B10).
         *
         *     Lệnh Telegram `status` là READ-ONLY và đi qua đây (B10/AMD-B10). Mỗi run trả bộ ba `(status, outcome, stop_reason)` để ba trạng thái của REQ-AC15 phân biệt được (I13).
         */
        get: operations["run.list"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/runs/{run_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Chi tiết một run (Run detail)
         * @description run_id.
         *
         *     Log trả về ĐÃ CHE SECRETS (SRC-SPEC §11.2).
         */
        get: operations["run.get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/runs/{run_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Hủy một run chưa kết thúc
         * @description run_id.
         *
         *     Thu hồi lease, chặn publish mới; dữ liệu đã commit không bị xóa (SRC-PLAN §8.1).
         *
         *     Thu hồi lease, chặn publish mới; dữ liệu ĐÃ COMMIT không bị xóa.
         */
        post: operations["run.cancel"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/runs/{run_id}/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Tiếp tục run đang `needs_user` (hành động riêng trong app, B10)
         * @description `run_id`, `request_id`, và tùy trạng thái nguồn: từ `needs_user` cần xác nhận owner đã xử lý challenge; từ `blocked` cần `unblock_reason` (bắt buộc, chuỗi tự do đã che secrets) — owner tuyên bố điều kiện chặn đã hết.
         *
         *     → `queued`, giữ checkpoint đã ACK, **cấp lease mới khi claim**, không tiếp tục bằng lease cũ (SRC-PLAN §8.1). Không có lệnh Telegram tương ứng (B10): resume chỉ là hành động trong app.
         *
         *     Hành động RIÊNG trong app; KHÔNG có lệnh Telegram tương ứng (AMD-B10). `needs_user` → `queued`, giữ checkpoint đã ACK, cấp LEASE MỚI khi claim (I10). Phiên còn challenge ⇒ 409 X_CHALLENGE_REQUIRED và run ở nguyên `needs_user`.
         */
        post: operations["run.resume"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/runs/run-now": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Chạy ngay (thủ công)
         * @description Không có tham số nghiệp vụ ngoài request_id.
         *
         *     Tạo run `trigger_type = manual` ở `queued`. **Không** vượt qua run đang `needs_user` hay `blocked` (B10): trả run hiện tại kèm lý do, không tự resume.
         *
         *     KHÔNG vượt qua run đang `needs_user` hay `blocked`: trả run hiện tại kèm lý do, KHÔNG tự resume (B10/AMD-B10, contracts/state/run.yaml T-RUN-21).
         */
        post: operations["run.run_now"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/saved": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Kho đã lưu (Saved)
         * @description Phân trang + từ khóa tìm kiếm.
         */
        get: operations["save.list"];
        put?: never;
        /**
         * Save một mục (app hoặc Telegram) kèm snapshot
         * @description target reference + nguồn Save (`app` | `telegram`) + analysis revision đang đọc.
         *
         *     Ghi snapshot bất biến lấy từ **revision đang đọc**, không lấy bản analysis mới hơn vừa xuất hiện (PC07). Bỏ tag hay xóa bài gốc trên X không làm mất snapshot (D55/AC-12).
         *
         *     Idempotency theo `(owner_id, target_ref)`: bấm Save nhiều lần vẫn MỘT bản ghi (REQ-D38, REQ-AC13). Save là snapshot BẤT BIẾN (I08).
         */
        post: operations["save.create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/saved/{target_ref}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Bỏ lưu (khác xóa dữ liệu gốc)
         * @description saved_item_id hoặc target reference.
         *
         *     Đây là **thao tác thứ nhất** trong ba thao tác riêng biệt của SRC-SPEC §7.3 (REQ-S7.3-05): bỏ lưu ≠ xóa dữ liệu gốc (`data.delete_target`) ≠ xóa toàn bộ dữ liệu (`data.purge_all`). Bỏ lưu chỉ gỡ `saved_item`; **không** xóa post/work gốc và **không** xóa snapshot của các bản Saved khác.
         *
         *     Bỏ Save KHÁC xóa dữ liệu gốc (`data.delete_target`) và KHÁC xóa toàn bộ (`data.purge_all`). Snapshot lịch sử vẫn đọc được (REQ-D55).
         */
        delete: operations["save.remove"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/saved/export": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Export Saved
         * @description Định dạng export mong muốn.
         *
         *     Export Saved là mục HOÃN sang P1 theo baseline §5 (REQ-OQ10, PROVISIONAL); operation giữ chỗ trong hợp đồng để PC07 quyết định bật hay không.
         */
        get: operations["save.export"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/secrets/task-credentials": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Cấp credential ngắn hạn theo từng task cho analysis worker (B13)
         * @description task_id + lease_id/epoch.
         *
         *     Ghi audit cấp phát đã che secrets; hạn dùng do PC08 chốt.
         *
         *     Credential có PHẠM VI ĐÚNG MỘT TASK và thời hạn ngắn (B13/ADR-0010). KHÔNG bao giờ cấp toàn bộ secrets. Giá trị credential KHÔNG được ghi log. Hình dạng chi tiết thuộc PC08.
         */
        post: operations["secret.issue_task_credential"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/settings": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Đọc cấu hình (lịch, giới hạn, provider/model theo tác vụ, embedding, liên kết Telegram)
         * @description CHỈ trả THAM CHIẾU tới secret, không bao giờ giá trị key (denied case NC-03).
         */
        get: operations["settings.get_config"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * Sửa cấu hình
         * @description Delta cấu hình: lịch, timezone IANA, giới hạn mỗi đợt, N ngày với ngược, provider/model theo tác vụ, key mới (chỉ ghi vào secret service), model embedding.
         *
         *     Ghi bản cấu hình mới; đổi model embedding kích hoạt embedding.start_generation_rebuild (không tự chuyển active generation); key mới đi qua secret.store_provider_key.
         */
        patch: operations["settings.update_config"];
        trace?: never;
    };
    "/v1/settings/providers/{provider_name}/test": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Thử một provider AI đã cấu hình (đường API key, phía server)
         * @description Provider ID cần thử; không nhận key trực tiếp từ frontend.
         *
         *     Ghi provider_test_result mới nhất; không đổi cấu hình.
         *
         *     Kết quả `usable | unusable | unknown` + reason_code; `unknown` KHÔNG được ghi thành 0 hay thành `unusable` (I14).
         */
        post: operations["settings.test_provider"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tags": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Danh sách tag, từ đồng nghĩa, tag loại trừ */
        get: operations["tag.list"];
        put?: never;
        /**
         * Thêm tag (kèm alias và exclusion)
         * @description Chữ người dùng gõ, alias, exclusion, ngưỡng riêng nếu có.
         *
         *     Tạo tag, sinh vector qua embedding.generate_vectors, tạo tag_config_version mới, mở một backfill activation N ngày dùng đúng một lần (D28; ledger do PC04 định nghĩa).
         */
        post: operations["tag.create"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tags/{tag_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Xóa tag
         * @description Tag ID.
         *
         *     Tạo tag_config_version mới. **Không** xóa post/work/analysis/Saved đã có (SRC-SPEC §7.3, §8.2 ví dụ 2 và 7).
         *
         *     Bỏ tag KHÔNG xóa dữ liệu và KHÔNG xóa Saved snapshot (REQ-D55, I08).
         */
        delete: operations["tag.delete"];
        options?: never;
        head?: never;
        /**
         * Sửa tag/alias/exclusion
         * @description Delta của một tag.
         *
         *     Tạo tag_config_version mới; không sửa report đã publish (I05).
         */
        patch: operations["tag.update"];
        trace?: never;
    };
    "/v1/tags/preview-matches": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Xem nhãn chủ đề đang khớp một tag (Topics)
         * @description Tag ID hoặc chữ nháp; tùy chọn ngưỡng thử.
         *
         *     Không ghi dữ liệu authoritative; có thể sinh vector tạm cho chữ nháp.
         *
         *     POST vì cần request body, nhưng KHÔNG đổi domain state (`x-mutation: false`); an toàn để gọi lại.
         */
        post: operations["tag.preview_matches"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tags/rescan-corpus": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Quét lại kho theo tag ("quét lại kho", D28)
         * @description Tag ID và phạm vi thời gian yêu cầu.
         *
         *     Tạo bản ghi rescan có ledger **riêng**; không reset first-announcement, không tiêu thụ backfill activation, không đẩy con trỏ coverage chính (SRC-PLAN §9.2).
         */
        post: operations["tag.rescan_corpus"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/telegram/link": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Hủy liên kết Telegram (hành động trong app)
         * @description Xác nhận của owner.
         *
         *     Tăng link generation; delivery đang `pending`/`retry_wait` cho recipient cũ chuyển `cancelled`, **không** chuyển payload cũ sang recipient mới (SRC-PLAN §8.3).
         *
         *     Hủy liên kết là hành động TRONG APP, không phải lệnh Telegram thứ tư (AMD-B10). Delivery đang `pending`/`retry_wait` chuyển `cancelled` (contracts/state/delivery.yaml T-DL-08).
         */
        delete: operations["telegram.unlink"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/telegram/link-codes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Sinh mã liên kết một lần có hạn (trong app)
         * @description Không có tham số nghiệp vụ ngoài request_id.
         *
         *     Tạo mã chưa dùng, có hạn (SRC-SPEC §11.2). Mã không được tái sử dụng.
         *
         *     Mã DÙNG MỘT LẦN, có hạn (SRC-SPEC §11.2). Liên kết mới vô hiệu hóa liên kết cũ (REQ-D37).
         */
        post: operations["telegram.issue_link_code"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/telegram/webhook": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Nhận update từ Telegram (ingress webhook)
         * @description Update của Telegram (message hoặc callback query).
         *
         *     Không đổi domain state khi update không hợp lệ. Chỉ update từ chat đã liên kết (hoặc mã liên kết hợp lệ) mới đi tiếp sang telegram.execute_command.
         *
         *     CHÍNH SÁCH IM LẶNG (REQ-S11.3-02): update từ chat CHƯA LIÊN KẾT bị bỏ im lặng và server vẫn trả 204, vì một mã lỗi phân biệt được sẽ tự xác nhận bot tồn tại. Ngoại lệ hẹp B09/AMD-B09: chuỗi khớp ĐÚNG định dạng mã liên kết được đối chiếu với mã chưa hết hạn chưa dùng; mã sai/hết hạn/đã dùng CŨNG im lặng. `UNAUTHORIZED_COMMAND` được GHI AUDIT, KHÔNG gửi ra ngoài. Ngữ nghĩa lệnh thuộc PC07 (`contracts/telegram/commands.yaml`).
         */
        post: operations["telegram.receive_update"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/assignments/{assignment_id}/heartbeat": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Gia hạn lease và báo tiến độ
         * @description lease_id, lease_epoch, tiến độ quan sát được, trạng thái phiên X.
         *
         *     Cập nhật hạn lease và mốc heartbeat (đầu vào cho "collector online"); không đổi dữ liệu nghiên cứu.
         *
         *     Gia hạn lease và báo tiến độ quan sát được; KHÔNG đổi dữ liệu nghiên cứu. Response mang `directive` để truyền lệnh dừng khi Owner đã cancel.
         */
        post: operations["worker.heartbeat"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/assignments/{assignment_id}/release": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Trả lại assignment (kết thúc bình thường hoặc worker tắt)
         * @description lease_id, lease_epoch, lý do trả.
         *
         *     Thu hồi lease, tăng epoch; phần chưa ACK không được coi là đã lưu.
         */
        post: operations["worker.release_assignment"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/assignments/{assignment_id}/stop": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Báo điểm dừng của đợt (challenge / limit / blocked / hết phiên)
         * @description lease_id/epoch + `stop_reason` ∈ {`challenge_required`, `limit_reached`, `session_expired`, `source_blocked`, `source_layout_changed`, `rate_limited`, `worker_shutdown`, `local_storage_unavailable`} + checkpoint đã ACK cuối cùng.
         *
         *     `challenge_required`/`session_expired` → run `needs_user`, tạo **tối đa một** alert intent cho mỗi run, không tự thử lại. `limit_reached` → đóng collection segment, giữ checkpoint, chuyển phase tiếp theo. `source_blocked` → run `blocked`, ghi điều kiện gỡ chặn, **không** luân chuyển account/proxy. `rate_limited` → đóng collection segment với `RATE_LIMITED`, run kết thúc `outcome: partial`, **không** retry trong cùng run; đợt theo lịch kế tiếp chạy bình thường. Đây **khác** `source_blocked`: rate limit nghĩa là X **vẫn cho vào** nhưng bảo chờ, còn `source_blocked` nghĩa là X **không cho vào**. Ba cách hiểu gộp làm một sẽ cho ba hành vi UI khác nhau ở AC-15 (SRC-SPEC §9.3 "dừng đợt, ghi lý do, không luân chuyển gì để lách"; ruling CR-PC10-02; PC03 thêm hàng transition trong run.yaml). Giữ checkpoint đã ACK; **không** luân chuyển account/proxy và **không** dò lại để tìm giới hạn. `source_layout_changed` → run `blocked` với `SOURCE_LAYOUT_CHANGED`: nguồn đổi bố cục nên parser không đọc được, **khác hẳn** bị chặn — cách gỡ là sửa parser, không phải chờ hết hạn chế, và **không** được tự thử lại để dò (ruling CR-PC05-01; PC03 đăng ký mã trong contracts/errors.yaml). Dữ liệu đã ACK giữ nguyên; không đoán nội dung từ bố cục lạ.
         *
         *     `challenge_required`/`session_expired` ⇒ run `needs_user` + TỐI ĐA MỘT alert intent mỗi run (REQ-AC04). `limit_reached` ⇒ đóng segment, giữ checkpoint, sang phase kế. `source_blocked` ⇒ run `blocked`, KHÔNG luân chuyển account/proxy.
         */
        post: operations["worker.report_stop"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/assignments/claim": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Collector kéo việc khi online (D11)
         * @description worker_instance_id, capability đang có, số việc muốn nhận.
         *
         *     run `queued` → `running/collecting`; cấp lease/epoch; ghi owner của assignment. Phần checkpoint trong payload được **đọc** từ MOD-ingest-service qua ingest.get_checkpoint; MOD-job-service không sở hữu entity `checkpoint` (ruling R-01).
         *
         *     `storage.health != healthy` ⇒ 503; `recovery_required` ⇒ 409 RESTORE_UNVERIFIED (I15, NC-10). Timeout của claim là KHÔNG BIẾT KẾT QUẢ: gọi lại với CÙNG `claim_request_id`, không sinh key mới.
         */
        post: operations["worker.claim_assignment"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/registrations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Đăng ký readiness/capability của worker trên máy cá nhân
         * @description worker_instance_id, worker_kind (`collector` | `analysis`), phiên bản, danh sách capability: `collector_online`, `chrome_profile_ready`, `x_session_state` (`ok|challenge|expired|unknown`), `ai_providers[]` với `usable | unusable | unknown` + `reason_code`, `embedding_supported: false`.
         *
         *     Cập nhật bản ghi readiness của worker; server chỉ giao assignment mà worker khai đủ capability. Worker **không bao giờ** khai `embedding` (D50/B12).
         *
         *     Đăng ký KHÔNG cấp lease — lease chỉ đến từ claim (contracts/ops/deployment.md §7 bước 6, I10). Khai `embedding_supported: true` ⇒ 422 VALIDATION_ERROR (guard D50/B12).
         */
        post: operations["worker.register_capabilities"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/workers/status": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Đọc trạng thái worker (online/offline, last run) cho màn hình Runs
         * @description online/offline theo ngưỡng heartbeat của contracts/ops/deployment.md. `last_run` CHỈ để xem, KHÔNG dùng làm mốc lọc dữ liệu (REQ-D12).
         */
        get: operations["worker.get_status"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/works/{work_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Work detail (summary, nhãn, tag khớp, post dẫn, lịch sử phân tích, mục liên quan)
         * @description target reference (`work` hoặc `post`).
         */
        get: operations["work.get_detail"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        "$defs-target_key": string;
        "$defs-timestamp_utc_ms": string;
        /** @description ULID 26 ký tự Crockford base32 chữ hoa. ID luôn truyền dưới dạng string (SRC-PLAN §5.1). */
        "$defs-ulid": string;
        accepted_item: {
            /** @description GIỜ SERVER chấp nhận LẦN ĐẦU, không tin clock worker (SRC-PLAN §9.1). Với `deduplicated`, đây là giá trị CŨ, không phải giờ của lần gửi lại. */
            discovered_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
            /** @description Tie-break thứ tự cho các mục cùng mili giây (AMD-B08). */
            ingest_sequence: number;
            /** @enum {string} */
            outcome: "inserted" | "deduplicated" | "quarantined" | "rejected";
            /** @description ID nội bộ của hàng `post`. */
            post_id: components["schemas"]["ulid"];
            /**
             * @description NOT NULL khi `outcome ∈ {rejected, quarantined}`. Lý do đọc được, KHÔNG kèm nội dung post (redaction — contracts/errors.yaml VALIDATION_ERROR).
             * @enum {string|null}
             */
            rejection_reason?: "text_too_large" | "too_many_media_refs" | "too_many_links" | "thread_context_too_long" | "malformed_x_post_id" | "identity_conflict" | null;
            /** @description Target đã resolve, nếu có. Tagged union `work | post` (B06/ADR-0009). null khi chưa resolve được — KHÔNG đoán (REQ-D33). */
            target_ref?: {
                key: string;
                /** @enum {string} */
                kind: "work" | "post";
            } | null;
            x_post_id: components["schemas"]["x_post_id"];
        };
        /** @description Bảy thành phần của analysis key, nguyên văn entities.yaml ENT-analysis.analysis_key.components và ADR-0008. KHÔNG chứa tag/tag_config_version (đổi tag không gọi AI lại — REQ-AC06, I04) và KHÔNG chứa provider/model (đổi provider không tự invalidate — ADR-0008 §6). */
        analysis_key: {
            generation_number: number;
            owner_id: components["schemas"]["analysis-result.schema_$defs-ulid"];
            prompt_version: components["schemas"]["semver"];
            schema_version: components["schemas"]["semver"];
            /** @description sha256 của JCS đầu vào đã dùng: {work_version.content_fingerprint?, post.source_snapshot_hash[]} (entities.yaml). Đổi nội dung nguồn ⇒ đổi key. */
            source_fingerprint: components["schemas"]["sha256"];
            target_key: components["schemas"]["target_key"];
            task_type: components["schemas"]["task_type"];
        };
        analysis_ref: {
            analysis_id: components["schemas"]["report.schema_$defs-ulid"];
            /**
             * @description CHỈ tham chiếu. Nội dung summary do PC06 định nghĩa; schema này không mô tả các trường bên trong payload.
             * @constant
             */
            analysis_result_schema_id: "analysis-result.schema.json";
            analyzed_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            /**
             * @description Nhãn mức độ đọc (REQ-D21, REQ-AC11).
             * @enum {string}
             */
            evidence_level: "post_only" | "abstract" | "full_text";
            generation_number: number;
            payload_hash: components["schemas"]["sha256"];
            /** @constant */
            task_type: "summary";
        };
        /**
         * Analysis result (label | summary | direction_phrasing)
         * @description Kết quả MỘT lần phân tích đã được chấp nhận, nộp qua analysis.submit_result và lưu vào analysis.payload. Envelope chung + `oneOf` phân biệt bằng `task_type`. Đây KHÔNG phải hàng analysis_attempt: attempt không bao giờ là kết quả (I16).
         */
        "analysis-result.schema": {
            analysis_key: components["schemas"]["analysis_key"];
            /** @description FK → analysis_attempt.id. Kết quả luôn truy được về đúng attempt đã tạo ra nó (entities.yaml `accepted_from_attempt_id`). */
            attempt_id: components["schemas"]["analysis-result.schema_$defs-ulid"];
            /** @description Mức độ đọc THỰC TẾ của nguồn đã cấp cho lần chạy này (REQ-D21). Cấm nâng mức khi nguồn tương ứng không tồn tại — kiểm ngữ nghĩa SV-04. */
            evidence_level: components["schemas"]["evidence_level"];
            /** @description Tập source id đã được CẤP cho lần chạy này. Mọi citation_refs / evidence_refs phải là tập con của tập này (kiểm ngữ nghĩa SV-02). */
            input_source_ids?: components["schemas"]["source_id"][];
            produced_at: components["schemas"]["analysis-result.schema_$defs-timestamp_utc_ms"];
            provider: components["schemas"]["provider_ref"];
            /** @description Nội dung theo từng task. Được chọn bằng `task_type` ở khối allOf/if-then bên dưới. */
            result: Record<string, never>;
            /**
             * @description Semver của chính schema này. PHẢI bằng analysis_key.schema_version (kiểm ngữ nghĩa SV-07).
             * @constant
             */
            schema_version: "0.1.0";
            /** @description Discriminator của `oneOf` bên dưới. */
            task_type: components["schemas"]["task_type"];
            usage: components["schemas"]["usage"];
            $defs: {
                /** @description ULID 26 ký tự Crockford base32 chữ hoa; ID luôn là string (SRC-PLAN §5.1). */
                ulid: string;
                /** @description Khóa union của target (contracts/schemas/target.schema.json). */
                target_key: string;
                /** @description Định danh của MỘT nguồn cụ thể đã được cấp trong input: một hàng `post` hoặc một hàng `work_version`. Citation chỉ được trỏ tới đây — không trỏ tới URL tự do, không trỏ tới tên tác giả, không trỏ tới văn bản tự do. */
                source_id: string;
                /** @description RFC 3339 UTC, hậu tố Z, đúng ba chữ số mili giây (AMD-B08). */
                timestamp_utc_ms: string;
                sha256: string;
                semver: string;
                /**
                 * @description Nguyên văn contracts/data/entities.yaml ENT-analysis.task_type (ruling R-03). `embedding` KHÔNG có ở đây: embedding chạy local ở server, không qua AI adapter (REQ-D48, SRC-SPEC §10.1).
                 * @enum {string}
                 */
                task_type: "label" | "summary" | "direction_phrasing";
                /**
                 * @description REQ-D21 / REQ-AC11. Thứ tự tăng dần: post_only < abstract < full_text.
                 * @enum {string}
                 */
                evidence_level: "post_only" | "abstract" | "full_text";
                /** @description Bảy thành phần của analysis key, nguyên văn entities.yaml ENT-analysis.analysis_key.components và ADR-0008. KHÔNG chứa tag/tag_config_version (đổi tag không gọi AI lại — REQ-AC06, I04) và KHÔNG chứa provider/model (đổi provider không tự invalidate — ADR-0008 §6). */
                analysis_key: {
                    generation_number: number;
                    owner_id: components["schemas"]["analysis-result.schema_$defs-ulid"];
                    prompt_version: components["schemas"]["semver"];
                    schema_version: components["schemas"]["semver"];
                    /** @description sha256 của JCS đầu vào đã dùng: {work_version.content_fingerprint?, post.source_snapshot_hash[]} (entities.yaml). Đổi nội dung nguồn ⇒ đổi key. */
                    source_fingerprint: components["schemas"]["sha256"];
                    target_key: components["schemas"]["target_key"];
                    task_type: components["schemas"]["task_type"];
                };
                /** @description Metadata truy vết. KHÔNG thuộc analysis key (ADR-0008 §6): đổi provider/model không tự invalidate kết quả cũ. */
                provider_ref: {
                    /**
                     * @description Hai họ provider của REQ-D41. Nguyên văn entities.yaml ENT-provider-config.auth_family.
                     * @enum {string}
                     */
                    auth_family: "api_key" | "cli_acp";
                    /** @description Không dùng `latest` (entities.yaml). */
                    model_name: string;
                    provider_config_id?: components["schemas"]["analysis-result.schema_$defs-ulid"];
                    provider_name: string;
                };
                /** @description REQ-D44 + I14: 'không rõ' là giá trị hợp lệ và CẤM ghi thành 0. Cấu trúc ép điều đó ở mức schema. */
                usage: {
                    /** @description Micro-USD nguyên để tránh số thực. null khi không biết. */
                    cost_micro_usd: number | null;
                    tokens_in: number | null;
                    tokens_out: number | null;
                    /** @description true = adapter không báo được usage (điển hình đường CLI/ACP, REQ-D44). */
                    unknown: boolean;
                } & (unknown & unknown);
                /**
                 * @description B16 / AMD-B16 / SRC-SPEC §10.3: tách ba loại phát biểu. `source_verified` chỉ dùng khi nội dung kiểm được từ nguồn ĐÃ CẤP; mọi phát biểu về tính mới là `ai_inference` (REQ-AC11).
                 * @enum {string}
                 */
                statement_kind: "author_claim" | "source_verified" | "ai_inference";
                statement: {
                    /** @description Phải là tập con của input_source_ids (SV-02). `ai_inference` được phép rỗng — suy luận không cần nguồn, nhưng PHẢI mang nhãn ai_inference (SV-03). */
                    citation_refs: components["schemas"]["source_id"][];
                    kind: components["schemas"]["statement_kind"];
                    text: string;
                } & unknown;
                /** @description B16: thiếu nguồn so sánh thì ghi thiếu, KHÔNG bịa baseline. */
                comparator: {
                    /** @constant */
                    kind: "ref";
                    note?: string;
                    source_ref: components["schemas"]["source_id"];
                } | {
                    /** @constant */
                    kind: "unknown";
                    /** @description Vì sao không có comparator. KHÔNG được chứa một baseline được bịa ra. */
                    note?: string;
                };
                /** @description Task `label` — gắn nhãn chủ đề MỞ (REQ-D22): 'bài này thuộc chủ đề gì', KHÔNG hỏi 'có khớp tag hiện tại không'. */
                result_label: {
                    labels: {
                        /**
                         * @description Ba mức RỜI RẠC, không phải điểm xác suất — cùng lý do với identity.md §7: MVP không có cách hiệu chỉnh một thang liên tục, nên không giả vờ có.
                         * @enum {string}
                         */
                        confidence: "low" | "medium" | "high";
                        evidence_refs: components["schemas"]["source_id"][];
                        /** @description Khớp giới hạn của entities.yaml ENT-work-label.label_text (1..120). */
                        label: string;
                    }[];
                };
                /** @description Task `summary` — hình dạng D20: nội dung + điểm khác với cái đã có + MỘT dòng hạn chế. Dòng 'khớp tag nào' KHÔNG nằm ở đây: nó là dữ liệu tra từ report_item.selection_reason (PC04), không phải do AI sinh (REQ-D20, SRC-SPEC §10.1). */
                result_summary: {
                    content: string;
                    difference_from_existing: {
                        comparator: components["schemas"]["comparator"];
                        text: string;
                    };
                    /** @description MỘT dòng hạn chế (D20). Không được rỗng: 'không có hạn chế nào' là một phát biểu phải viết ra, không phải một trường bỏ trống. */
                    limitation_line: string;
                    /**
                     * @description SRC-SPEC §10.3: nguồn chưa peer review phải có nhãn tương ứng. `unknown` hợp lệ; cấm đoán `peer_reviewed`.
                     * @enum {string}
                     */
                    peer_review_status?: "preprint_not_peer_reviewed" | "peer_reviewed" | "unknown";
                    /** @description Mọi phát biểu đáng kể đã tách theo kind (B16). */
                    statements: components["schemas"]["statement"][];
                };
                /** @description Task `direction_phrasing` — AI CHỈ diễn đạt lại một kết quả ĐÃ TÍNH bởi contracts/reporting/selection.md §8. AI không chọn thành viên, không tính mật độ, không đổi nhãn (CR-PC04-05). */
                result_direction_phrasing: {
                    /** @description FK → emerging_direction.id đã tính ở PC04. */
                    direction_ref: components["schemas"]["analysis-result.schema_$defs-ulid"];
                    /**
                     * @description Hằng số hợp đồng (REQ-D54), giống contracts/schemas/report.schema.json. 'phát hiện mới' bị cấm.
                     * @constant
                     */
                    label?: "ứng viên để đọc sâu";
                    /** @description PHẢI bằng đúng emerging_direction.member_target_keys — không thêm, không bớt (SV-05). Đây là hàng rào chống việc AI 'chọn lại' thành viên. */
                    member_refs: components["schemas"]["target_key"][];
                    /** @description Câu chữ mô tả. Kiểm ngữ nghĩa SV-06 cấm các cụm khẳng định tính mới khoa học. */
                    text: string;
                };
            };
        } & (unknown & unknown & unknown);
        /** @description RFC 3339 UTC, hậu tố Z, đúng ba chữ số mili giây (AMD-B08). */
        "analysis-result.schema_$defs-timestamp_utc_ms": string;
        /** @description ULID 26 ký tự Crockford base32 chữ hoa; ID luôn là string (SRC-PLAN §5.1). */
        "analysis-result.schema_$defs-ulid": string;
        /** @description arXiv base ID đã chuẩn hóa theo identity.md §2.2, KHÔNG kèm hậu tố phiên bản. Kiểu mới `YYMM.NNNNN` hoặc kiểu cũ `archive[.CC]/YYMMNNN`. */
        arxiv_base_canonical: string;
        /** @description Nhãn phiên bản arXiv; sống ở work_version, không thuộc canonical id. */
        arxiv_version_label: string;
        assignment: {
            assignment_id: components["schemas"]["ulid"];
            capability_requirements: {
                /** @constant */
                requires_chrome_profile: true;
                /**
                 * @description Server chỉ giao khi worker khai `x_session_state = ok`. `challenge`/`expired`/`unknown` ⇒ không giao (contracts/state/run.yaml T-RUN-01 guard).
                 * @constant
                 */
                requires_x_session_ok: true;
            };
            /** @description NOT NULL khi run này gộp nhiều occurrence quá hạn (REQ-D15). Chỉ để hiển thị và để ghi khoảng bao trùm; KHÔNG phải bộ lọc dữ liệu (REQ-D12). */
            catch_up_window?: {
                from: components["schemas"]["timestamp_utc_ms"];
                occurrence_count: number;
                to: components["schemas"]["timestamp_utc_ms"];
            } | null;
            checkpoint: components["schemas"]["server_checkpoint"];
            /** @description true khi assignment này đến sau `run.resume` (needs_user → queued). Lease LUÔN mới; không có đường tiếp tục bằng lease cũ (contracts/state/run.yaml §LM-07, I10). */
            is_resume: boolean;
            lease: components["schemas"]["lease"];
            /**
             * @description Phase cần làm tiếp. Collector chỉ nhận assignment ở `collecting`.
             * @enum {string}
             */
            phase: "collecting" | "enriching" | "analyzing" | "reporting";
            /** @description FK → run.id (contracts/data/entities.yaml ENT-run). */
            run_id: components["schemas"]["ulid"];
            search_config: components["schemas"]["search_config"];
            stop_conditions: components["schemas"]["stop_conditions"];
            /**
             * @description REQ-D14.
             * @enum {string}
             */
            trigger_type: "scheduled" | "manual";
            /** @description Câu ghi rõ giới hạn bao phủ X cho đợt này. BẮT BUỘC không rỗng: `completed` không có nghĩa đã quét đủ toàn bộ X (AMD-B05). Collector chép lại nguyên văn vào metadata run khi báo dừng. */
            x_coverage_note_vi: string;
        };
        author: {
            display_name?: string;
            /** @description Không kèm ký tự @. */
            handle: string;
            /** @description Dùng để xác định thread do chính tác giả viết (REQ-D31). */
            x_user_id?: string;
        };
        /** @description Định danh canonical đã biết của một work. Vắng mặt hoàn toàn là hợp lệ: work có thể tồn tại trước khi metadata về (metadata_state = 'none'). */
        canonical_identifiers: {
            arxiv_base?: components["schemas"]["arxiv_base_canonical"];
            doi?: components["schemas"]["doi_canonical"];
        };
        /** @description Checkpoint được commit TRONG CÙNG transaction với post + receipt (TXN-ingest-batch, I02). Checkpoint KHÔNG BAO GIỜ đi trước dữ liệu bền. */
        checkpoint_ack: {
            /** @description BẤT BIẾN R-01: giá trị này KHÔNG BAO GIỜ vượt `max(committed ingest_receipt.max_ingest_sequence)` của run. */
            acked_through_ingest_sequence: number;
            checkpoint_id: components["schemas"]["ulid"];
            /** @description Append-only, đơn điệu tăng trong một run; seq lùi bị từ chối. */
            checkpoint_sequence: number;
            /**
             * @description `invalidated` ⇒ recovery policy cho phép đọc lại; dedup vẫn ở ingest (AMD-B05).
             * @enum {string}
             */
            cursor_state: "valid" | "invalidated";
            /** @description Con trỏ ĐÃ LƯU (server chỉ lưu SAU khi dữ liệu kèm theo đã commit). null khi cursor mất hiệu lực. */
            cursor_token: string | null;
            items_ingested_total: number;
        };
        /** @description Request của `ingest.commit_checkpoint` (ruling R-01): TIẾN CON TRỎ THUẦN TÚY, KHÔNG có item. */
        checkpoint_only_request: {
            assignment_id: components["schemas"]["ulid"];
            /** @description Idempotency key cùng với assignment_id. Seq lùi bị từ chối; cùng seq + cùng payload trả bản đã ghi. */
            checkpoint_seq: number;
            /** @enum {string} */
            cursor_state: "valid" | "invalidated";
            cursor_token: string | null;
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /** @description GUARD (R-01): server CHẤP NHẬN chỉ khi giá trị này <= `acked_through_ingest_sequence` đã commit cho run đó. Vượt quá ⇒ `VALIDATION_ERROR` (422) và KHÔNG có write một phần. Đây chính là counterexample 2 của I02 được biến thành một guard kiểm được. */
            proposed_acked_through_ingest_sequence: number;
            /**
             * @description Ba tình huống duy nhất được phép dùng đường này. Nộp item PHẢI đi qua `ingest.submit_batch`.
             * @enum {string}
             */
            reason: "empty_page" | "end_of_feed" | "segment_close";
            request_id: components["schemas"]["ulid"];
            schema_version: components["schemas"]["semver"];
        };
        checkpoint_proposal: {
            /** @enum {string} */
            cursor_state: "valid" | "invalidated";
            /** @description null hợp lệ khi cursor mất hiệu lực; khi đó cursor_state = 'invalidated' và recovery policy cho phép đọc lại, dedup ở ingest (AMD-B05). */
            cursor_token?: string | null;
            items_collected_in_run?: number;
            /** @enum {string} */
            phase: "collecting" | "enriching" | "analyzing" | "reporting";
            /**
             * @description GỢI Ý; trạng thái run do server quyết (PC03). Collector không tự đặt run sang needs_user.
             * @enum {string}
             */
            stop_hint?: "none" | "limit_reached" | "captcha" | "session_expired" | "source_blocked";
        };
        claim_request: {
            capabilities: components["schemas"]["collector_capabilities"];
            /** @description Idempotency key của claim (contracts/ports.yaml: 'Cùng claim_request_id trả cùng assignment; không cấp hai lease'). Timeout của claim là KHÔNG BIẾT KẾT QUẢ (SRC-PLAN §5.1): worker phải gọi lại với CÙNG key, không sinh key mới. */
            claim_request_id: string;
            /** @description Cố định 1: MVP một người dùng, một collector, một run đang chạy (contracts/state/run.yaml T-RUN-21 coalesce). */
            max_assignments: number;
            /** @description ID của lần gọi này. Retry sinh request_id mới nhưng GIỮ NGUYÊN claim_request_id. */
            request_id: components["schemas"]["ulid"];
            schema_version: components["schemas"]["semver"];
            worker_instance_id: components["schemas"]["ulid"];
            /**
             * @description `worker.claim_assignment` chỉ dành cho collector. Analysis worker dùng `analysis.claim_task` (PC06).
             * @enum {string}
             */
            worker_kind: "collector";
        };
        collector_capabilities: {
            /** @description Chrome thật với PROFILE RIÊNG CỦA DỰ ÁN (REQ-D09), không phải profile mặc định. false ⇒ server không giao việc. */
            chrome_profile_ready: boolean;
            collector_online: boolean;
            collector_version?: components["schemas"]["semver"];
            /**
             * @description LUÔN false. Server TỪ CHỐI bản đăng ký khai true bằng VALIDATION_ERROR — guard cho D50/B12: embedding không bao giờ chạy trên máy cá nhân.
             * @constant
             */
            embedding_supported: false;
            /**
             * @description `unknown` được đối xử như KHÔNG dùng được khi quyết định giao việc, nhưng hiển thị khác `unusable` (contracts/ops/deployment.md §7).
             * @enum {string}
             */
            x_session_state: "ok" | "challenge" | "expired" | "unknown";
        };
        /** @description B16: thiếu nguồn so sánh thì ghi thiếu, KHÔNG bịa baseline. */
        comparator: {
            /** @constant */
            kind: "ref";
            note?: string;
            source_ref: components["schemas"]["source_id"];
        } | {
            /** @constant */
            kind: "unknown";
            /** @description Vì sao không có comparator. KHÔNG được chứa một baseline được bịa ra. */
            note?: string;
        };
        /** @description Bất biến số học: received = inserted + deduplicated + quarantined + rejected (contracts/data/entities.yaml ENT-ingest-receipt CHECK). */
        counts: {
            /** @description Số item trùng `x_post_id` đã có. Cam kết là KHÔNG INGEST TRÙNG, không phải 'không bao giờ đọc lại' (AMD-B05). */
            deduplicated: number;
            /** @description Số hàng `post` MỚI. Đây là oracle của AMD-B05: sau replay, tổng số này không tăng. */
            inserted: number;
            /** @description Sequence lớn nhất đã cấp trong lô. Là MỐC ACK. */
            max_ingest_sequence: number;
            /** @description Item bị giữ lại vì `IDENTITY_CONFLICT`; nguồn của cả hai phía được giữ, KHÔNG merge đoán (B15, I03). */
            quarantined: number;
            /** @description Số item trong lô. 0 hợp lệ CHỈ khi `receipt_kind = checkpoint_only`. */
            received: number;
            /** @description Item không hợp lệ ở mức nghiệp vụ (đã qua schema). Vượt giới hạn kích thước ⇒ vào đây, KHÔNG cắt cụt âm thầm. */
            rejected: number;
            /** @description Số cạnh `post_work` mới. */
            works_linked: number;
        };
        coverage: {
            /** @description Inclusive. */
            coverage_from: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            /** @description EXCLUSIVE — khoảng nửa mở [from, to) (SRC-PLAN §9.2). */
            coverage_to: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            coverage_window_id: components["schemas"]["report.schema_$defs-ulid"];
            /** @description Inclusive. Vị từ thành viên thật sự (time-and-tags.md §4.3). */
            ingest_sequence_from: number;
            /** @description EXCLUSIVE. */
            ingest_sequence_to: number;
            /** @description NULL chỉ cho cửa sổ đầu tiên. Guard CAS: coverage_from = predecessor.coverage_to (I06). */
            predecessor_window_id: components["schemas"]["report.schema_$defs-ulid"] | null;
            sequence: number;
        };
        coverage_note: {
            /** @description Các tag đã dùng entitlement backfill trong kỳ này (REQ-D28). */
            backfill_applied_tag_ids?: components["schemas"]["report.schema_$defs-ulid"][];
            /** @description Luôn false trong một read model đã publish: kỳ rỗng không tạo report hiển thị (REQ-D57). Trường tồn tại để consumer khẳng định được điều đó. */
            empty_period: boolean;
            /** @description true = coverage nêu phạm vi dữ liệu ĐÃ QUAN SÁT, không hứa bao phủ toàn bộ thời gian trên X (SRC-PLAN §9.2, B05). */
            observed_data_only: boolean;
            /** @description Ví dụ limit_reached, captcha, session_expired (SRC-PLAN §8.1). Null khi run kết thúc bình thường. */
            run_stop_reason?: string | null;
            /** @description Câu chữ về giới hạn bao phủ nguồn X (AMD-B05). */
            source_coverage_limits_note?: string | null;
            /**
             * @description REQ-A2 / REQ-OQ08. 'uncalibrated' → UI phải nói rõ ngưỡng chưa hiệu chỉnh; cấm tuyên bố chỉ tiêu chất lượng §1.4.
             * @enum {string}
             */
            threshold_calibration_state: "uncalibrated" | "calibrated";
        };
        density_measure: {
            comparison_windows_used: {
                coverage_window_sequence: number;
                members_in_radius: number;
            }[];
            density_delta: number;
            /** @description Số target_key riêng biệt trong nhóm ở kỳ này. */
            density_now: number;
            /** @description Trung bình cộng trên các kỳ trước TỒN TẠI; không đệm 0 cho kỳ không tồn tại. */
            density_prior: number;
            density_ratio: number;
        };
        density_parameters: {
            comparison_window_k: number;
            /** @constant */
            metric: "cosine";
            min_delta: number;
            min_members: number;
            min_prior_windows: number;
            /**
             * @description REQ-A4 chưa chạy → không bao giờ là 'CALIBRATED' ở giai đoạn Pre-code.
             * @enum {string}
             */
            parameters_status?: "PROVISIONAL" | "PROVISIONAL_BOOTSTRAP" | "CALIBRATED";
            prior_floor: number;
            radius: components["schemas"]["score"];
            /** @constant */
            rounding_decimals: 4;
        };
        /** @description DOI đã chuẩn hóa theo contracts/data/identity.md §2.1: chữ thường, không tiền tố URL, không dấu câu cuối. */
        doi_canonical: string;
        embedding_generation_ref: {
            dimension: number;
            embedding_generation_id: components["schemas"]["report.schema_$defs-ulid"];
            model_name: string;
            /** @description Không dùng 'latest' (entities.yaml). */
            model_version: string;
            /** @enum {string} */
            normalization: "l2" | "none";
        };
        emerging_direction: {
            /** @description Vector centroid đã chuẩn hóa L2, độ dài bằng embedding_generation.dimension. Ghi bất biến để kỳ sau so lại được. */
            centroid?: number[];
            density?: components["schemas"]["density_measure"];
            direction_id: components["schemas"]["report.schema_$defs-ulid"];
            embedding_generation_id: components["schemas"]["report.schema_$defs-ulid"];
            /**
             * @description B14: thiếu dữ liệu KHÔNG được gọi là 'đang nổi'.
             * @enum {string}
             */
            evidence_state: "sufficient" | "insufficient_evidence";
            /** @description Target bị loại khỏi phép đếm vì đang có identity_conflict mở (B15). */
            excluded_quarantined_target_keys: components["schemas"]["$defs-target_key"][];
            insufficient_reason?: ("below_min_sample" | "cold_start_insufficient_history" | "delta_below_threshold" | "generation_reset") | null;
            /**
             * @description REQ-D54. Chuỗi này là hằng số hợp đồng; 'phát hiện mới' bị cấm.
             * @constant
             */
            label: "ứng viên để đọc sâu";
            member_target_keys: components["schemas"]["$defs-target_key"][];
            parameters: components["schemas"]["density_parameters"];
            /** @description analysis của task direction_phrasing (PC06). NULL hợp lệ: khối tồn tại được khi không có AI. */
            phrasing_analysis_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
        } & (unknown & unknown);
        /**
         * @description Envelope lỗi chung (SRC-PLAN §5.1). Hình dạng này là BẢN SAO của `error_envelope` trong contracts/errors.yaml;
         *     nếu hai bên lệch nhau thì contracts/errors.yaml THẮNG và file này phải sửa.
         *
         *     `correlation_id` LUÔN có mặt, kể cả khi `storage.health != healthy`: nó sinh trong bộ nhớ tiến trình, không cần
         *     một hàng DB. Không mã lỗi nào đòi hỏi ghi được vào DB mới coi là đã báo (contracts/errors.yaml §EPR-01).
         *
         *     Envelope KHÔNG BAO GIỜ chứa: transcript của model, prompt gốc, nội dung post nguyên văn, API key, bot token,
         *     cookie, header Authorization, chat ID, đường dẫn file tuyệt đối, stack trace, câu SQL, tên bảng/cột nội bộ.
         */
        ErrorEnvelope: {
            /**
             * @description Phải là một mã đã khai trong contracts/errors.yaml. Không có mã ngoài danh mục.
             * @enum {string}
             */
            code: "X_CHALLENGE_REQUIRED" | "X_ACCESS_BLOCKED" | "WORKER_LEASE_EXPIRED" | "STALE_LEASE" | "INGEST_ACK_LOST" | "IDEMPOTENCY_CONFLICT" | "SOURCE_METADATA_UNAVAILABLE" | "IDENTITY_CONFLICT" | "AI_OUTPUT_INVALID" | "AI_PROVIDER_UNAVAILABLE" | "AI_ATTEMPT_UNCERTAIN" | "EMBEDDING_GENERATION_MISMATCH" | "TAG_VERSION_STALE" | "CONFLICT" | "TELEGRAM_SEND_UNCERTAIN" | "TELEGRAM_PERMANENT_FAILURE" | "UNAUTHORIZED_COMMAND" | "STORAGE_WRITE_FAILED" | "RESTORE_UNVERIFIED" | "SOURCE_LAYOUT_CHANGED" | "CSRF_REJECTED" | "UNAUTHORIZED" | "CAPABILITY_DENIED" | "FORBIDDEN_EDGE" | "VALIDATION_ERROR" | "NOT_FOUND" | "RATE_LIMITED" | "INTERNAL";
            correlation_id: components["schemas"]["Ulid"];
            /** @description Chỉ chứa các khóa liệt kê ở `details_safe_keys` của mã trong contracts/errors.yaml. Khóa lạ ⇒ producer tự từ chối, không gửi ra. */
            details_safe?: Record<string, never> | null;
            /** @description Tiếng Việt, render từ `message_safe_template` của mã. KHÔNG chèn giá trị ngoài `details_safe_keys`. */
            message_safe: string;
            /** @description Chỉ có mặt khi `retry_class = retryable_with_budget` hoặc mã `RATE_LIMITED`. null nghĩa là KHÔNG có gợi ý, KHÔNG phải 'retry ngay'. */
            retry_after_ms?: number | null;
            /**
             * @description Bằng đúng `retry_class` của mã. `unknown_outcome` nghĩa là KHÔNG BIẾT side effect đã xảy ra hay chưa — client KHÔNG được coi là rollback.
             * @enum {string}
             */
            retry_class: "none" | "retryable_with_budget" | "needs_user" | "operator_decision" | "unknown_outcome";
            /**
             * @description Bằng đúng `scope` của mã trong contracts/errors.yaml.
             * @enum {string}
             */
            scope: "run" | "item" | "delivery" | "storage" | "request";
        };
        /**
         * @description REQ-D21 / REQ-AC11. Thứ tự tăng dần: post_only < abstract < full_text.
         * @enum {string}
         */
        evidence_level: "post_only" | "abstract" | "full_text";
        excluded_by: {
            /** @enum {string} */
            exclusion_scope: "global" | "tag_scoped";
            scoped_tag_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
            score: components["schemas"]["score"];
            tag_exclusion_id: components["schemas"]["report.schema_$defs-ulid"];
            threshold_applied: components["schemas"]["score"];
        };
        /** @description Ánh xạ tới first_announced_ledger (entities.yaml): first_announced_report_id = ledger.first_report_id; first_announced_at = ledger.first_announced_at; merge_audit_id = ledger.merge_audit_id. first_announced_window_sequence và target_key_at_announcement là giá trị DẪN XUẤT ở read model (join coverage_window trên report_id, và report_item của kỳ công bố lần đầu) — không phải cột của sổ. */
        first_announced_ref: {
            first_announced_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            first_announced_report_id: components["schemas"]["report.schema_$defs-ulid"];
            first_announced_window_sequence: number;
            /** @description first_announced_ledger.merge_audit_id: NOT NULL khi ngày công bố được kế thừa từ work bị hợp nhất (time-and-tags.md §8.3). */
            merge_audit_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
            target_key_at_announcement?: components["schemas"]["$defs-target_key"];
        };
        /**
         * @description Chỗ giữ có chủ đích: hình dạng chi tiết thuộc một gói khác và CHƯA tồn tại tại thời điểm viết file này.
         *     Xem `$ref` trong `x-response-schema-planned` của ports.yaml cho từng operation. Đây KHÔNG phải giấy phép chấp
         *     nhận trường tùy ý: gói sở hữu phải thay bằng schema đóng với `additionalProperties: false` trước G3.
         */
        GenericObject: Record<string, never>;
        heartbeat_request: {
            assignment_id: components["schemas"]["ulid"];
            /** @description Epoch cũ ⇒ STALE_LEASE và KHÔNG đổi dữ liệu (contracts/ports.yaml worker.heartbeat). */
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /** @description QUAN SÁT của collector, KHÔNG phải dữ liệu authoritative. Server không ghi các số này vào bảng nghiên cứu. */
            observed_progress: {
                elapsed_s: number;
                posts_seen_in_run: number;
                posts_submitted_in_run: number;
            };
            request_id: components["schemas"]["ulid"];
            schema_version: components["schemas"]["semver"];
            /** @enum {string} */
            x_session_state: "ok" | "challenge" | "expired" | "unknown";
        };
        heartbeat_response: {
            /**
             * @description `stop_cancelled`: Owner đã gọi `run.cancel` (contracts/state/run.yaml T-RUN-17b) — collector dừng ngay, không commit thêm. `stop_storage_unavailable`: xem contracts/state/storage.yaml.
             * @enum {string}
             */
            directive: "continue" | "stop_cancelled" | "stop_storage_unavailable" | "stop_lease_revoked";
            /** @description Hạn mới sau khi gia hạn. Vắng mặt khi `lease_valid = false`. */
            lease_expires_at?: components["schemas"]["timestamp_utc_ms"];
            lease_valid: boolean;
            /** @enum {string} */
            storage_health?: "healthy" | "write_blocked" | "maintenance" | "recovery_required";
        };
        https_url: string;
        IdempotencyKey: string;
        ingest_item: {
            author: components["schemas"]["author"];
            /** @description Đồng hồ WORKER — KHÔNG TIN CẬY. Server lưu để chẩn đoán và không bao giờ dùng làm mốc nghiệp vụ; discovered_at là giờ server (SRC-PLAN §9.1). */
            collected_at: components["schemas"]["$defs-timestamp_utc_ms"];
            /** @description BCP 47 nếu nguồn cung cấp. Không tự đoán. */
            lang?: string;
            /** @description Mảng rỗng hợp lệ. Ảnh chụp paper KHÔNG được dùng để đoán ID (REQ-D33). */
            media_refs: components["schemas"]["media_ref"][];
            /** @description Ngày đăng do X cung cấp. Được phép vắng mặt; KHÔNG suy ra từ collected_at. */
            published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
            /** @description Đầu vào cho identity resolution, không phải kết luận. Server tự chuẩn hóa theo identity.md §2. */
            referenced_links: components["schemas"]["referenced_link"][];
            /** @description Thời điểm collector QUAN SÁT thấy post này đã bị xóa trên X. Không có operation riêng cho việc đánh dấu xóa nguồn: quan sát đi qua chính `ingest.submit_batch` dưới dạng trường này (ruling Coordinator PKT-PC02-FIX1). Server ghi vào post.source_deleted_observed_at theo quy tắc ĐƠN ĐIỆU: chỉ ghi khi giá trị hiện tại là NULL. Giá trị null hoặc vắng mặt nghĩa là 'không có quan sát', KHÔNG phải 'post còn sống'. Là mốc quan sát của server sau khi nhận (đồng hồ worker vẫn không tin cậy; server có quyền thay bằng committed_at nếu lệch quá ngưỡng của PC05). */
            source_deleted_observed_at?: components["schemas"]["$defs-timestamp_utc_ms"] | null;
            source_provenance?: components["schemas"]["source_provenance"];
            /** @description Nội dung post. Là DỮ LIỆU, không phải lệnh (SRC-SPEC §11.4). maxLength đếm ký tự; giới hạn byte UTF-8 ép ở tầng transport. */
            text: string;
            thread_context?: components["schemas"]["thread_context"];
            url: components["schemas"]["https_url"];
            /** @description ID post trên X, dạng string (SRC-PLAN §5.1). Là khóa dedup ingest (AMD-B05). */
            x_post_id: string;
        };
        /**
         * Ingest batch request (collector → backend)
         * @description Payload của mutation `ingest.submit_batch`. Tuân thủ wire rules SRC-PLAN §5.1: request_id, schema_version, idempotency_key, payload_hash, và vì mutation này đang giữ job nên có thêm job_id, lease_id, lease_epoch.
         */
        "ingest-batch.schema": {
            /** @description ĐỀ XUẤT của collector. Server chỉ lưu sau khi dữ liệu kèm theo đã commit (I02); server không bao giờ tin con trỏ này là bằng chứng dữ liệu đã bền. */
            client_checkpoint_proposal: components["schemas"]["checkpoint_proposal"];
            /** @description Phiên bản collector, để chẩn đoán khi layout X đổi. Không ảnh hưởng nghiệp vụ. */
            collector_build?: string;
            /** @description Khóa chống trùng do client cấp. Cùng key + cùng payload_hash → trả receipt đã commit; cùng key + payload_hash khác → IDEMPOTENCY_CONFLICT, không ghi đè (SRC-PLAN §5.1). */
            idempotency_key: string;
            /** @description Mảng post đã thu được. minItems = 1: batch rỗng là lỗi hợp đồng, không phải trạng thái hợp lệ — kết thúc đợt dùng operation stop, không dùng batch rỗng. */
            items: components["schemas"]["ingest_item"][];
            job_id: components["schemas"]["ulid"];
            /** @description Epoch của lease đang giữ. Epoch cũ → STALE_LEASE, không dữ liệu authoritative nào đổi (I10). */
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /** @description Xem x-contract.payload_hash_definition. */
            payload_hash: components["schemas"]["sha256"];
            /** @description ID của lần gọi này. Retry sinh request_id mới nhưng giữ nguyên idempotency_key. */
            request_id: components["schemas"]["ulid"];
            /** @description Run mà assignment này thuộc về. Server vẫn tự xác định từ job_id; trường này chỉ để đối chiếu. */
            run_id?: components["schemas"]["ulid"];
            /** @description Phiên bản wire schema này. Không dùng 'latest' (SRC-PLAN §5). */
            schema_version: components["schemas"]["semver"];
            $defs: {
                ulid: string;
                semver: string;
                sha256: string;
                timestamp_utc_ms: string;
                https_url: string;
                ingest_item: {
                    author: components["schemas"]["author"];
                    /** @description Đồng hồ WORKER — KHÔNG TIN CẬY. Server lưu để chẩn đoán và không bao giờ dùng làm mốc nghiệp vụ; discovered_at là giờ server (SRC-PLAN §9.1). */
                    collected_at: components["schemas"]["$defs-timestamp_utc_ms"];
                    /** @description BCP 47 nếu nguồn cung cấp. Không tự đoán. */
                    lang?: string;
                    /** @description Mảng rỗng hợp lệ. Ảnh chụp paper KHÔNG được dùng để đoán ID (REQ-D33). */
                    media_refs: components["schemas"]["media_ref"][];
                    /** @description Ngày đăng do X cung cấp. Được phép vắng mặt; KHÔNG suy ra từ collected_at. */
                    published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                    /** @description Đầu vào cho identity resolution, không phải kết luận. Server tự chuẩn hóa theo identity.md §2. */
                    referenced_links: components["schemas"]["referenced_link"][];
                    /** @description Thời điểm collector QUAN SÁT thấy post này đã bị xóa trên X. Không có operation riêng cho việc đánh dấu xóa nguồn: quan sát đi qua chính `ingest.submit_batch` dưới dạng trường này (ruling Coordinator PKT-PC02-FIX1). Server ghi vào post.source_deleted_observed_at theo quy tắc ĐƠN ĐIỆU: chỉ ghi khi giá trị hiện tại là NULL. Giá trị null hoặc vắng mặt nghĩa là 'không có quan sát', KHÔNG phải 'post còn sống'. Là mốc quan sát của server sau khi nhận (đồng hồ worker vẫn không tin cậy; server có quyền thay bằng committed_at nếu lệch quá ngưỡng của PC05). */
                    source_deleted_observed_at?: components["schemas"]["$defs-timestamp_utc_ms"] | null;
                    source_provenance?: components["schemas"]["source_provenance"];
                    /** @description Nội dung post. Là DỮ LIỆU, không phải lệnh (SRC-SPEC §11.4). maxLength đếm ký tự; giới hạn byte UTF-8 ép ở tầng transport. */
                    text: string;
                    thread_context?: components["schemas"]["thread_context"];
                    url: components["schemas"]["https_url"];
                    /** @description ID post trên X, dạng string (SRC-PLAN §5.1). Là khóa dedup ingest (AMD-B05). */
                    x_post_id: string;
                };
                author: {
                    display_name?: string;
                    /** @description Không kèm ký tự @. */
                    handle: string;
                    /** @description Dùng để xác định thread do chính tác giả viết (REQ-D31). */
                    x_user_id?: string;
                };
                media_ref: {
                    alt_text?: string;
                    /** @enum {string} */
                    media_type: "photo" | "video" | "animated_gif" | "unknown";
                    url: components["schemas"]["https_url"];
                };
                referenced_link: {
                    /** @description URL sau khi X đã expand. Collector KHÔNG tự đi theo redirect ngoài policy (PC08). */
                    expanded_url?: components["schemas"]["https_url"];
                    /**
                     * @description GỢI Ý của collector, không phải kết luận identity. Server chuẩn hóa và quyết định (identity.md §3).
                     * @enum {string}
                     */
                    link_kind_hint?: "arxiv_abs" | "arxiv_pdf" | "doi_org" | "publisher" | "code_repo" | "other";
                    url: components["schemas"]["https_url"];
                };
                thread_context: {
                    /** @description true khi post thuộc thread do chính tác giả viết. Replies của người ngoài KHÔNG được ingest (REQ-D31, REQ-P1-02). */
                    is_author_thread_member: boolean;
                    position_in_thread?: number;
                    thread_root_x_post_id?: string;
                    thread_size_observed?: number;
                };
                /** @description Nơi collector nhìn thấy post. Cần để ghi giới hạn bao phủ X trong metadata run (B05). */
                source_provenance: {
                    /** @enum {string} */
                    discovery_surface: "search_query" | "home_timeline" | "author_profile" | "thread_expansion";
                    page_cursor_observed?: string;
                    /** @description Tag chỉ dùng để TÌM KIẾM, không dùng để lọc (REQ-D24). */
                    query_text?: string;
                };
                checkpoint_proposal: {
                    /** @enum {string} */
                    cursor_state: "valid" | "invalidated";
                    /** @description null hợp lệ khi cursor mất hiệu lực; khi đó cursor_state = 'invalidated' và recovery policy cho phép đọc lại, dedup ở ingest (AMD-B05). */
                    cursor_token?: string | null;
                    items_collected_in_run?: number;
                    /** @enum {string} */
                    phase: "collecting" | "enriching" | "analyzing" | "reporting";
                    /**
                     * @description GỢI Ý; trạng thái run do server quyết (PC03). Collector không tự đặt run sang needs_user.
                     * @enum {string}
                     */
                    stop_hint?: "none" | "limit_reached" | "captcha" | "session_expired" | "source_blocked";
                };
            };
        };
        /**
         * Ingest receipt và checkpoint-only request (backend → collector)
         * @description Biên nhận bất biến của một lô ingest đã COMMIT (`ingest.submit_batch`), của một bước tiến con trỏ thuần túy (`ingest.commit_checkpoint`, ruling R-01), và của tra cứu sau khi mất ACK (`ingest.get_receipt`). Receipt là BẰNG CHỨNG DUY NHẤT rằng dữ liệu đã bền: khi client mất ACK, nó tra receipt chứ không đoán (SRC-PLAN §5.1, I02).
         */
        "ingest-receipt.schema": {
            checkpoint_only_request?: components["schemas"]["checkpoint_only_request"];
            not_committed?: components["schemas"]["not_committed"];
            receipt?: components["schemas"]["receipt"];
            $defs: {
                ulid: string;
                semver: string;
                sha256: string;
                /** @description UTC RFC 3339 mili giây (AMD-B08). */
                timestamp_utc_ms: string;
                /** @description ID post của X, dạng chuỗi số. ID truyền dưới dạng string (SRC-PLAN §5.1). */
                x_post_id: string;
                receipt: {
                    /** @description Ánh xạ item đã chấp nhận. RỖNG hợp lệ cho `receipt_kind = checkpoint_only` và cho một replay mà client chỉ cần đếm. */
                    accepted_items: components["schemas"]["accepted_item"][];
                    checkpoint_ack: components["schemas"]["checkpoint_ack"];
                    /** @description GIỜ SERVER tại commit point. Đồng hồ worker không được dùng (SRC-PLAN §9.1). */
                    committed_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
                    counts: components["schemas"]["counts"];
                    /** @description UNIQUE(owner_id, idempotency_key). */
                    idempotency_key: string;
                    job_id: components["schemas"]["ulid"];
                    /** @description Epoch TẠI LÚC COMMIT. Lease cũ bị từ chối bằng STALE_LEASE (I10). */
                    lease_epoch: number;
                    lease_id: components["schemas"]["ulid"];
                    /** @description Hash của payload_core đã commit. Client so sánh để chắc rằng replay trả đúng receipt của LÔ CỦA MÌNH. */
                    payload_hash: components["schemas"]["sha256"];
                    /** @description sha256 của JCS({idempotency_key, payload_hash, counts, checkpoint_id, max_ingest_sequence}) — contracts/data/entities.yaml ENT-ingest-receipt. Client so sánh để biết replay trả ĐÚNG receipt cũ; giá trị này KHÔNG ĐỔI giữa lần commit và mọi lần replay. */
                    receipt_hash: components["schemas"]["sha256"];
                    /** @description PK của hàng `ingest_receipt` (ENT-ingest-receipt). Bất biến sau commit. */
                    receipt_id: components["schemas"]["ulid"];
                    /**
                     * @description `batch_ingest` từ `ingest.submit_batch`; `checkpoint_only` từ `ingest.commit_checkpoint` (ruling R-01). Cần thiết để 0 item của một checkpoint-only KHÔNG bị đọc nhầm thành một batch bị từ chối (contracts/data/entities.yaml ENT-ingest-receipt.receipt_kind).
                     * @enum {string}
                     */
                    receipt_kind: "batch_ingest" | "checkpoint_only";
                    /** @description request_id của lần gọi ĐÃ TẠO receipt. Một replay có request_id KHÁC nhưng receipt KHÔNG đổi. */
                    request_id: components["schemas"]["ulid"];
                    run_id: components["schemas"]["ulid"];
                    schema_version: components["schemas"]["semver"];
                    /**
                     * @description `committed`: lần gọi này đã tạo receipt. `duplicate_replay`: receipt đã tồn tại từ trước và được trả lại nguyên vẹn — KHÔNG có hàng `post` mới, `checkpoint.sequence` KHÔNG tăng.
                     * @enum {string}
                     */
                    status: "committed" | "duplicate_replay";
                    /**
                     * @description Chỉ hai giá trị này xuất hiện trên một receipt: một receipt CHỈ tồn tại khi transaction đã commit, nên `write_blocked` và `recovery_required` không thể đi kèm một receipt (contracts/state/storage.yaml).
                     * @enum {string}
                     */
                    storage_state: "healthy" | "maintenance";
                    /** @description Sự kiện KHÔNG làm hỏng lô nhưng phải hiện ra: item bị quarantine vì xung đột định danh, item bị từ chối ở mức nghiệp vụ, con trỏ bị vô hiệu. Lô vẫn commit (contracts/errors.yaml IDENTITY_CONFLICT: 'ingest của các item khác trong lô vẫn commit'). */
                    warnings: components["schemas"]["warning"][];
                };
                /** @description Bất biến số học: received = inserted + deduplicated + quarantined + rejected (contracts/data/entities.yaml ENT-ingest-receipt CHECK). */
                counts: {
                    /** @description Số item trùng `x_post_id` đã có. Cam kết là KHÔNG INGEST TRÙNG, không phải 'không bao giờ đọc lại' (AMD-B05). */
                    deduplicated: number;
                    /** @description Số hàng `post` MỚI. Đây là oracle của AMD-B05: sau replay, tổng số này không tăng. */
                    inserted: number;
                    /** @description Sequence lớn nhất đã cấp trong lô. Là MỐC ACK. */
                    max_ingest_sequence: number;
                    /** @description Item bị giữ lại vì `IDENTITY_CONFLICT`; nguồn của cả hai phía được giữ, KHÔNG merge đoán (B15, I03). */
                    quarantined: number;
                    /** @description Số item trong lô. 0 hợp lệ CHỈ khi `receipt_kind = checkpoint_only`. */
                    received: number;
                    /** @description Item không hợp lệ ở mức nghiệp vụ (đã qua schema). Vượt giới hạn kích thước ⇒ vào đây, KHÔNG cắt cụt âm thầm. */
                    rejected: number;
                    /** @description Số cạnh `post_work` mới. */
                    works_linked: number;
                };
                accepted_item: {
                    /** @description GIỜ SERVER chấp nhận LẦN ĐẦU, không tin clock worker (SRC-PLAN §9.1). Với `deduplicated`, đây là giá trị CŨ, không phải giờ của lần gửi lại. */
                    discovered_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
                    /** @description Tie-break thứ tự cho các mục cùng mili giây (AMD-B08). */
                    ingest_sequence: number;
                    /** @enum {string} */
                    outcome: "inserted" | "deduplicated" | "quarantined" | "rejected";
                    /** @description ID nội bộ của hàng `post`. */
                    post_id: components["schemas"]["ulid"];
                    /**
                     * @description NOT NULL khi `outcome ∈ {rejected, quarantined}`. Lý do đọc được, KHÔNG kèm nội dung post (redaction — contracts/errors.yaml VALIDATION_ERROR).
                     * @enum {string|null}
                     */
                    rejection_reason?: "text_too_large" | "too_many_media_refs" | "too_many_links" | "thread_context_too_long" | "malformed_x_post_id" | "identity_conflict" | null;
                    /** @description Target đã resolve, nếu có. Tagged union `work | post` (B06/ADR-0009). null khi chưa resolve được — KHÔNG đoán (REQ-D33). */
                    target_ref?: {
                        key: string;
                        /** @enum {string} */
                        kind: "work" | "post";
                    } | null;
                    x_post_id: components["schemas"]["x_post_id"];
                };
                /** @description Checkpoint được commit TRONG CÙNG transaction với post + receipt (TXN-ingest-batch, I02). Checkpoint KHÔNG BAO GIỜ đi trước dữ liệu bền. */
                checkpoint_ack: {
                    /** @description BẤT BIẾN R-01: giá trị này KHÔNG BAO GIỜ vượt `max(committed ingest_receipt.max_ingest_sequence)` của run. */
                    acked_through_ingest_sequence: number;
                    checkpoint_id: components["schemas"]["ulid"];
                    /** @description Append-only, đơn điệu tăng trong một run; seq lùi bị từ chối. */
                    checkpoint_sequence: number;
                    /**
                     * @description `invalidated` ⇒ recovery policy cho phép đọc lại; dedup vẫn ở ingest (AMD-B05).
                     * @enum {string}
                     */
                    cursor_state: "valid" | "invalidated";
                    /** @description Con trỏ ĐÃ LƯU (server chỉ lưu SAU khi dữ liệu kèm theo đã commit). null khi cursor mất hiệu lực. */
                    cursor_token: string | null;
                    items_ingested_total: number;
                };
                warning: {
                    /**
                     * @description Mã theo contracts/errors.yaml. Chúng xuất hiện Ở ĐÂY (trong một response 2xx) chứ không phải như một error envelope, vì lô VẪN COMMIT — chỉ item liên quan bị giữ lại.
                     * @enum {string}
                     */
                    code: "IDENTITY_CONFLICT" | "VALIDATION_ERROR" | "SOURCE_METADATA_UNAVAILABLE";
                    /** @description Có mặt khi `code = IDENTITY_CONFLICT`; trỏ tới hàng `identity_conflict` để Owner xử lý qua `identity.resolve_conflict`. */
                    conflict_id?: components["schemas"]["ulid"];
                    /** @description Tiếng Việt, đã che dữ liệu. KHÔNG chứa nội dung post, URL đầy đủ hay transcript. */
                    message_safe: string;
                    x_post_id: components["schemas"]["x_post_id"];
                };
                /** @description Response của `ingest.get_receipt` khi server CHƯA TỪNG commit key đó. Đây là câu trả lời DỨT KHOÁT (server là nguồn sự thật), khác hẳn với 'không biết' của một timeout. */
                not_committed: {
                    checked_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
                    idempotency_key: string;
                    /**
                     * @description Client được phép gửi lại CÙNG key + CÙNG payload_hash. Đây là điểm duy nhất trong hợp đồng khẳng định điều đó.
                     * @constant
                     */
                    safe_to_resubmit?: true;
                    /** @constant */
                    status: "not_committed";
                };
                /** @description Request của `ingest.commit_checkpoint` (ruling R-01): TIẾN CON TRỎ THUẦN TÚY, KHÔNG có item. */
                checkpoint_only_request: {
                    assignment_id: components["schemas"]["ulid"];
                    /** @description Idempotency key cùng với assignment_id. Seq lùi bị từ chối; cùng seq + cùng payload trả bản đã ghi. */
                    checkpoint_seq: number;
                    /** @enum {string} */
                    cursor_state: "valid" | "invalidated";
                    cursor_token: string | null;
                    lease_epoch: number;
                    lease_id: components["schemas"]["ulid"];
                    /** @description GUARD (R-01): server CHẤP NHẬN chỉ khi giá trị này <= `acked_through_ingest_sequence` đã commit cho run đó. Vượt quá ⇒ `VALIDATION_ERROR` (422) và KHÔNG có write một phần. Đây chính là counterexample 2 của I02 được biến thành một guard kiểm được. */
                    proposed_acked_through_ingest_sequence: number;
                    /**
                     * @description Ba tình huống duy nhất được phép dùng đường này. Nộp item PHẢI đi qua `ingest.submit_batch`.
                     * @enum {string}
                     */
                    reason: "empty_page" | "end_of_feed" | "segment_close";
                    request_id: components["schemas"]["ulid"];
                    schema_version: components["schemas"]["semver"];
                };
            };
        } & (unknown | unknown | unknown);
        /** @description UTC RFC 3339 mili giây (AMD-B08). */
        "ingest-receipt.schema_$defs-timestamp_utc_ms": string;
        /** @description Quyền độc quyền trên một assignment (ENT-assignment-lease). Con số ở contracts/retry-policy.yaml; giá trị dưới đây do SERVER cấp cho từng lease, client không tự chọn. */
        lease: {
            /** @description Giờ SERVER. Lease hết hạn khi `now > expires_at + heartbeat_grace` (30 s). */
            expires_at: components["schemas"]["timestamp_utc_ms"];
            /** @description PROVISIONAL 30 giây (contracts/ops/deployment.md, PC01). */
            heartbeat_interval_s: number;
            /** @description Đơn điệu tăng cho một job; epoch cũ ⇒ STALE_LEASE và KHÔNG dữ liệu authoritative nào đổi (I10). */
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /** @description PROVISIONAL 120 giây (contracts/retry-policy.yaml §lease_ttl_collector). Ràng buộc: >= 4 × heartbeat_interval_s và > online_threshold (90 s). */
            ttl_s: number;
        };
        /** @description Một tài khoản duy nhất (REQ-D05). KHÔNG có signup, KHÔNG có quên-mật-khẩu tự động. Mật khẩu KHÔNG BAO GIỜ được ghi log ở bất kỳ dạng nào. */
        LoginRequest: {
            /** Format: password */
            password: string;
            username: string;
        };
        matched_tag: {
            matched_label_text?: string;
            /** @enum {string} */
            matched_via: "tag" | "alias";
            score: components["schemas"]["score"];
            /** @description NOT NULL khi matched_via = 'alias'. Alias thừa hưởng ngưỡng của tag cha (selection.md §4.2). */
            tag_alias_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
            tag_id: components["schemas"]["report.schema_$defs-ulid"];
            tag_text: string;
            threshold_applied: components["schemas"]["score"];
        };
        media_ref: {
            alt_text?: string;
            /** @enum {string} */
            media_type: "photo" | "video" | "animated_gif" | "unknown";
            url: components["schemas"]["https_url"];
        };
        /** @description Response khi không có việc. KHÔNG phải lỗi. */
        no_work: {
            /**
             * @description `run_needs_user`/`run_blocked`: có run nhưng nó chờ Owner — worker KHÔNG tự claim lại (I10). `storage_not_healthy`: xem contracts/state/storage.yaml.
             * @enum {string}
             */
            reason: "no_due_occurrence" | "run_needs_user" | "run_blocked" | "storage_not_healthy" | "capability_not_met" | "assignment_already_held";
            /** @description Gợi ý theo `claim_idle_backoff` (contracts/retry-policy.yaml: 5/15/45 giây). */
            retry_after_ms: number;
        };
        /** @description Response của `ingest.get_receipt` khi server CHƯA TỪNG commit key đó. Đây là câu trả lời DỨT KHOÁT (server là nguồn sự thật), khác hẳn với 'không biết' của một timeout. */
        not_committed: {
            checked_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
            idempotency_key: string;
            /**
             * @description Client được phép gửi lại CÙNG key + CÙNG payload_hash. Đây là điểm duy nhất trong hợp đồng khẳng định điều đó.
             * @constant
             */
            safe_to_resubmit?: true;
            /** @constant */
            status: "not_committed";
        };
        /**
         * @description Phân trang bằng cursor; `limit` có trần cứng 100 để một response không phình.
         * @default 25
         */
        PageLimit: number;
        pending_item: {
            first_pending_window_sequence: number;
            pending_item_ledger_id: components["schemas"]["report.schema_$defs-ulid"];
            /** @enum {string} */
            reason: "missing_summary" | "analysis_failed" | "analysis_unknown" | "budget_exceeded";
            /** @enum {string} */
            state: "pending" | "resolved_reported_late" | "abandoned_by_owner";
            target_key: components["schemas"]["$defs-target_key"];
        };
        /**
         * Target nhánh post (mục chỉ có post)
         * @description Post không dẫn tới work nào (REQ-D33). `work_id` và `canonical` bị cấm ở nhánh này.
         */
        post_target: {
            /**
             * @description Chỉ `resolved_post_only` mới là target post hợp lệ để Save/summary; `pending` chưa phải target.
             * @enum {string}
             */
            identity_resolution?: "pending" | "resolved_linked" | "resolved_post_only" | "conflict";
            /** @constant */
            kind: "post";
            post_id: components["schemas"]["$defs-ulid"];
            target_key?: string;
            /** @description ID gốc trên X, dạng string. */
            x_post_id?: string;
        };
        /** @description Metadata truy vết. KHÔNG thuộc analysis key (ADR-0008 §6): đổi provider/model không tự invalidate kết quả cũ. */
        provider_ref: {
            /**
             * @description Hai họ provider của REQ-D41. Nguyên văn entities.yaml ENT-provider-config.auth_family.
             * @enum {string}
             */
            auth_family: "api_key" | "cli_acp";
            /** @description Không dùng `latest` (entities.yaml). */
            model_name: string;
            provider_config_id?: components["schemas"]["analysis-result.schema_$defs-ulid"];
            provider_name: string;
        };
        receipt: {
            /** @description Ánh xạ item đã chấp nhận. RỖNG hợp lệ cho `receipt_kind = checkpoint_only` và cho một replay mà client chỉ cần đếm. */
            accepted_items: components["schemas"]["accepted_item"][];
            checkpoint_ack: components["schemas"]["checkpoint_ack"];
            /** @description GIỜ SERVER tại commit point. Đồng hồ worker không được dùng (SRC-PLAN §9.1). */
            committed_at: components["schemas"]["ingest-receipt.schema_$defs-timestamp_utc_ms"];
            counts: components["schemas"]["counts"];
            /** @description UNIQUE(owner_id, idempotency_key). */
            idempotency_key: string;
            job_id: components["schemas"]["ulid"];
            /** @description Epoch TẠI LÚC COMMIT. Lease cũ bị từ chối bằng STALE_LEASE (I10). */
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /** @description Hash của payload_core đã commit. Client so sánh để chắc rằng replay trả đúng receipt của LÔ CỦA MÌNH. */
            payload_hash: components["schemas"]["sha256"];
            /** @description sha256 của JCS({idempotency_key, payload_hash, counts, checkpoint_id, max_ingest_sequence}) — contracts/data/entities.yaml ENT-ingest-receipt. Client so sánh để biết replay trả ĐÚNG receipt cũ; giá trị này KHÔNG ĐỔI giữa lần commit và mọi lần replay. */
            receipt_hash: components["schemas"]["sha256"];
            /** @description PK của hàng `ingest_receipt` (ENT-ingest-receipt). Bất biến sau commit. */
            receipt_id: components["schemas"]["ulid"];
            /**
             * @description `batch_ingest` từ `ingest.submit_batch`; `checkpoint_only` từ `ingest.commit_checkpoint` (ruling R-01). Cần thiết để 0 item của một checkpoint-only KHÔNG bị đọc nhầm thành một batch bị từ chối (contracts/data/entities.yaml ENT-ingest-receipt.receipt_kind).
             * @enum {string}
             */
            receipt_kind: "batch_ingest" | "checkpoint_only";
            /** @description request_id của lần gọi ĐÃ TẠO receipt. Một replay có request_id KHÁC nhưng receipt KHÔNG đổi. */
            request_id: components["schemas"]["ulid"];
            run_id: components["schemas"]["ulid"];
            schema_version: components["schemas"]["semver"];
            /**
             * @description `committed`: lần gọi này đã tạo receipt. `duplicate_replay`: receipt đã tồn tại từ trước và được trả lại nguyên vẹn — KHÔNG có hàng `post` mới, `checkpoint.sequence` KHÔNG tăng.
             * @enum {string}
             */
            status: "committed" | "duplicate_replay";
            /**
             * @description Chỉ hai giá trị này xuất hiện trên một receipt: một receipt CHỈ tồn tại khi transaction đã commit, nên `write_blocked` và `recovery_required` không thể đi kèm một receipt (contracts/state/storage.yaml).
             * @enum {string}
             */
            storage_state: "healthy" | "maintenance";
            /** @description Sự kiện KHÔNG làm hỏng lô nhưng phải hiện ra: item bị quarantine vì xung đột định danh, item bị từ chối ở mức nghiệp vụ, con trỏ bị vô hiệu. Lô vẫn commit (contracts/errors.yaml IDENTITY_CONFLICT: 'ingest của các item khác trong lô vẫn commit'). */
            warnings: components["schemas"]["warning"][];
        };
        referenced_link: {
            /** @description URL sau khi X đã expand. Collector KHÔNG tự đi theo redirect ngoài policy (PC08). */
            expanded_url?: components["schemas"]["https_url"];
            /**
             * @description GỢI Ý của collector, không phải kết luận identity. Server chuẩn hóa và quyết định (identity.md §3).
             * @enum {string}
             */
            link_kind_hint?: "arxiv_abs" | "arxiv_pdf" | "doi_org" | "publisher" | "code_repo" | "other";
            url: components["schemas"]["https_url"];
        };
        release_request: {
            /** @description Idempotency key (contracts/ports.yaml: trả lại nhiều lần không đổi trạng thái sau lần đầu). */
            assignment_id: components["schemas"]["ulid"];
            lease_epoch: number;
            lease_id: components["schemas"]["ulid"];
            /**
             * @description Phần CHƯA ACK không được coi là đã lưu (contracts/ports.yaml worker.release_assignment, I02).
             * @enum {string}
             */
            release_reason: "completed_phase" | "worker_shutdown" | "local_storage_unavailable";
            request_id: components["schemas"]["ulid"];
            schema_version: components["schemas"]["semver"];
        };
        /** @description Read model của một hàng report_item. Các trường matched_tags, excluded_by, late_discovery, pending_since_window_sequence, selected_via_backfill, backfill_ledger_id, reference_reason, work_version_label và identity_state là các khóa của cột json report_item.selection_reason (PC04 khóa hình dạng theo entities.yaml); ở đây chúng được trải phẳng cho consumer. */
        report_item: {
            analysis?: components["schemas"]["analysis_ref"];
            backfill_ledger_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
            discovered_at?: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            /** @description Các cặp bị exclusion loại — dùng để giải thích trên màn hình Topics. */
            excluded_by?: components["schemas"]["excluded_by"][];
            first_announced?: components["schemas"]["first_announced_ref"];
            /**
             * @description 'quarantined' = đang có identity_conflict mở; UI phải cảnh báo và mục KHÔNG được đếm vào mật độ (identity.md §5.3).
             * @enum {string}
             */
            identity_state: "active" | "quarantined";
            ingest_sequence?: number;
            /**
             * @description REQ-D29, REQ-AC09. 'phát hiện muộn' KHÔNG phải một item_type — xem late_discovery.
             * @enum {string}
             */
            item_type: "new_discovery" | "prior_reference";
            /** @description true → hiển thị nhãn 'phát hiện muộn' (time-and-tags.md §5.3). Là nhãn hiển thị, không đổi item_type. */
            late_discovery: boolean;
            /** @description Các cặp khớp SỐNG SÓT sau exclusion (selection.md §4.3). */
            matched_tags: components["schemas"]["matched_tag"][];
            pending_since_window_sequence?: number | null;
            /**
             * @description Chỉ có nghĩa khi item_type = 'prior_reference'. 'related_direction' theo REQ-D30 (tag chung + paper cùng được dẫn, KHÔNG dùng AI).
             * @enum {string}
             */
            reference_reason?: "already_announced" | "new_work_version" | "related_direction";
            report_item_id: components["schemas"]["report.schema_$defs-ulid"];
            selected_via_backfill: boolean;
            /** @description Các post dẫn tới work này (REQ-AC07: một mục công trình, các post nằm dưới dạng nguồn dẫn). */
            source_post_ids?: components["schemas"]["report.schema_$defs-ulid"][];
            /**
             * @description 'pending' khi mục được chọn nhưng chưa có summary hợp lệ; mục vẫn hiển thị, không bị ẩn (AMD-B17).
             * @enum {string}
             */
            summary_state?: "present" | "pending";
            /** @description Tagged union work | post (PC02). */
            target: components["schemas"]["target.schema"];
            target_key: components["schemas"]["$defs-target_key"];
            work_version_label?: string;
        } & (unknown & unknown & unknown);
        /**
         * Published report read model
         * @description Read model của một kỳ báo cáo đã publish (SRC-PLAN §8.2 report.status published). Bất biến sau publish (I05). Ngữ nghĩa của từng trường nằm ở contracts/reporting/time-and-tags.md và contracts/reporting/selection.md; schema này chỉ khóa hình dạng wire.
         */
        "report.schema": {
            built_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            /** @description sha256(JCS(nội dung đã publish)). Oracle của I05: delivery không đổi nội dung đã publish. */
            content_hash: components["schemas"]["sha256"];
            coverage: components["schemas"]["coverage"];
            coverage_note: components["schemas"]["coverage_note"];
            embedding_generation: components["schemas"]["embedding_generation_ref"];
            /** @description Luôn có ít nhất một phần tử: khi không nhóm nào đạt ngưỡng, phần tử đó mang evidence_state = 'insufficient_evidence' (B14). */
            emerging_directions: components["schemas"]["emerging_direction"][];
            /** @description Con trỏ tới evidence record (EV-…) hoặc scenario (SC…) liên quan tới kỳ này. Mảng rỗng hợp lệ. */
            evidence_refs: string[];
            /** @description Đã sắp theo selection.md §7.1. Mảng rỗng KHÔNG hợp lệ cho một report đã publish: kỳ rỗng chỉ ghi coverage, không tạo report hiển thị (REQ-D57, AMD-B04). */
            items: components["schemas"]["report_item"][];
            owner_id: components["schemas"]["report.schema_$defs-ulid"];
            /** @description Mục thuộc kỳ này nhưng chưa đủ điều kiện hiển thị đầy đủ. Rỗng là điều kiện cần của quality = 'complete'. */
            pending_items: components["schemas"]["pending_item"][];
            /** @description Commit point của transaction publish; là mốc freeze tag (B01) và mốc first-announcement (I07). */
            published_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            /**
             * @description Trường RIÊNG với status (B17/AMD-B17). `complete` chỉ khi pending_items rỗng cho kỳ này.
             * @enum {string}
             */
            quality: "complete" | "partial";
            /**
             * Format: uuid
             * @description UUIDv4. Mỏ neo idempotency ĐÃ BỀN của report.publish — cột report.report_build_id (entities.yaml, UNIQUE ux_report_owner_build_id). Replay sau khi mất ACK tra theo khóa này thay vì thử advance coverage lần hai (SRC-PLAN §5.1). Đây là tiền đề của quyết định kỳ rỗng ở time-and-tags.md §4.7.1.
             */
            report_build_id: string;
            report_id: components["schemas"]["report.schema_$defs-ulid"];
            /**
             * @description Phiên bản của chính schema này (SRC-PLAN §5.1). Không dùng 'latest'.
             * @constant
             */
            schema_version: "0.1.0";
            /** @description Phiên bản thuật toán selection (contracts/reporting/selection.md §1). Ghim bất biến. */
            selection_version: string;
            /**
             * @description Read model chỉ tồn tại cho report đã publish. `building` và `aborted` không có read model hiển thị (SRC-PLAN §8.2).
             * @constant
             */
            status: "published";
            tag_config_version: components["schemas"]["tag_config_version_ref"];
            $defs: {
                /** @description ULID 26 ký tự Crockford base32 chữ hoa; ID luôn truyền dưới dạng string (SRC-PLAN §5.1). */
                ulid: string;
                target_key: string;
                /** @description RFC 3339 UTC, hậu tố Z, đúng ba chữ số mili giây (AMD-B08). */
                timestamp_utc_ms: string;
                sha256: string;
                /** @description Cosine similarity đã làm tròn half-up 4 chữ số thập phân (selection.md §3). */
                score: number;
                coverage: {
                    /** @description Inclusive. */
                    coverage_from: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    /** @description EXCLUSIVE — khoảng nửa mở [from, to) (SRC-PLAN §9.2). */
                    coverage_to: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    coverage_window_id: components["schemas"]["report.schema_$defs-ulid"];
                    /** @description Inclusive. Vị từ thành viên thật sự (time-and-tags.md §4.3). */
                    ingest_sequence_from: number;
                    /** @description EXCLUSIVE. */
                    ingest_sequence_to: number;
                    /** @description NULL chỉ cho cửa sổ đầu tiên. Guard CAS: coverage_from = predecessor.coverage_to (I06). */
                    predecessor_window_id: components["schemas"]["report.schema_$defs-ulid"] | null;
                    sequence: number;
                };
                tag_config_version_ref: {
                    content_hash: components["schemas"]["sha256"];
                    /** @description Bằng published_at: freeze xảy ra TRONG transaction publish (B01/AMD-B01). */
                    frozen_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    sequence: number;
                    tag_config_version_id: components["schemas"]["report.schema_$defs-ulid"];
                };
                embedding_generation_ref: {
                    dimension: number;
                    embedding_generation_id: components["schemas"]["report.schema_$defs-ulid"];
                    model_name: string;
                    /** @description Không dùng 'latest' (entities.yaml). */
                    model_version: string;
                    /** @enum {string} */
                    normalization: "l2" | "none";
                };
                matched_tag: {
                    matched_label_text?: string;
                    /** @enum {string} */
                    matched_via: "tag" | "alias";
                    score: components["schemas"]["score"];
                    /** @description NOT NULL khi matched_via = 'alias'. Alias thừa hưởng ngưỡng của tag cha (selection.md §4.2). */
                    tag_alias_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
                    tag_id: components["schemas"]["report.schema_$defs-ulid"];
                    tag_text: string;
                    threshold_applied: components["schemas"]["score"];
                };
                excluded_by: {
                    /** @enum {string} */
                    exclusion_scope: "global" | "tag_scoped";
                    scoped_tag_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
                    score: components["schemas"]["score"];
                    tag_exclusion_id: components["schemas"]["report.schema_$defs-ulid"];
                    threshold_applied: components["schemas"]["score"];
                };
                analysis_ref: {
                    analysis_id: components["schemas"]["report.schema_$defs-ulid"];
                    /**
                     * @description CHỈ tham chiếu. Nội dung summary do PC06 định nghĩa; schema này không mô tả các trường bên trong payload.
                     * @constant
                     */
                    analysis_result_schema_id: "analysis-result.schema.json";
                    analyzed_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    /**
                     * @description Nhãn mức độ đọc (REQ-D21, REQ-AC11).
                     * @enum {string}
                     */
                    evidence_level: "post_only" | "abstract" | "full_text";
                    generation_number: number;
                    payload_hash: components["schemas"]["sha256"];
                    /** @constant */
                    task_type: "summary";
                };
                /** @description Ánh xạ tới first_announced_ledger (entities.yaml): first_announced_report_id = ledger.first_report_id; first_announced_at = ledger.first_announced_at; merge_audit_id = ledger.merge_audit_id. first_announced_window_sequence và target_key_at_announcement là giá trị DẪN XUẤT ở read model (join coverage_window trên report_id, và report_item của kỳ công bố lần đầu) — không phải cột của sổ. */
                first_announced_ref: {
                    first_announced_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    first_announced_report_id: components["schemas"]["report.schema_$defs-ulid"];
                    first_announced_window_sequence: number;
                    /** @description first_announced_ledger.merge_audit_id: NOT NULL khi ngày công bố được kế thừa từ work bị hợp nhất (time-and-tags.md §8.3). */
                    merge_audit_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
                    target_key_at_announcement?: components["schemas"]["$defs-target_key"];
                };
                /** @description Read model của một hàng report_item. Các trường matched_tags, excluded_by, late_discovery, pending_since_window_sequence, selected_via_backfill, backfill_ledger_id, reference_reason, work_version_label và identity_state là các khóa của cột json report_item.selection_reason (PC04 khóa hình dạng theo entities.yaml); ở đây chúng được trải phẳng cho consumer. */
                report_item: {
                    analysis?: components["schemas"]["analysis_ref"];
                    backfill_ledger_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
                    discovered_at?: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
                    /** @description Các cặp bị exclusion loại — dùng để giải thích trên màn hình Topics. */
                    excluded_by?: components["schemas"]["excluded_by"][];
                    first_announced?: components["schemas"]["first_announced_ref"];
                    /**
                     * @description 'quarantined' = đang có identity_conflict mở; UI phải cảnh báo và mục KHÔNG được đếm vào mật độ (identity.md §5.3).
                     * @enum {string}
                     */
                    identity_state: "active" | "quarantined";
                    ingest_sequence?: number;
                    /**
                     * @description REQ-D29, REQ-AC09. 'phát hiện muộn' KHÔNG phải một item_type — xem late_discovery.
                     * @enum {string}
                     */
                    item_type: "new_discovery" | "prior_reference";
                    /** @description true → hiển thị nhãn 'phát hiện muộn' (time-and-tags.md §5.3). Là nhãn hiển thị, không đổi item_type. */
                    late_discovery: boolean;
                    /** @description Các cặp khớp SỐNG SÓT sau exclusion (selection.md §4.3). */
                    matched_tags: components["schemas"]["matched_tag"][];
                    pending_since_window_sequence?: number | null;
                    /**
                     * @description Chỉ có nghĩa khi item_type = 'prior_reference'. 'related_direction' theo REQ-D30 (tag chung + paper cùng được dẫn, KHÔNG dùng AI).
                     * @enum {string}
                     */
                    reference_reason?: "already_announced" | "new_work_version" | "related_direction";
                    report_item_id: components["schemas"]["report.schema_$defs-ulid"];
                    selected_via_backfill: boolean;
                    /** @description Các post dẫn tới work này (REQ-AC07: một mục công trình, các post nằm dưới dạng nguồn dẫn). */
                    source_post_ids?: components["schemas"]["report.schema_$defs-ulid"][];
                    /**
                     * @description 'pending' khi mục được chọn nhưng chưa có summary hợp lệ; mục vẫn hiển thị, không bị ẩn (AMD-B17).
                     * @enum {string}
                     */
                    summary_state?: "present" | "pending";
                    /** @description Tagged union work | post (PC02). */
                    target: components["schemas"]["target.schema"];
                    target_key: components["schemas"]["$defs-target_key"];
                    work_version_label?: string;
                } & (unknown & unknown & unknown);
                density_parameters: {
                    comparison_window_k: number;
                    /** @constant */
                    metric: "cosine";
                    min_delta: number;
                    min_members: number;
                    min_prior_windows: number;
                    /**
                     * @description REQ-A4 chưa chạy → không bao giờ là 'CALIBRATED' ở giai đoạn Pre-code.
                     * @enum {string}
                     */
                    parameters_status?: "PROVISIONAL" | "PROVISIONAL_BOOTSTRAP" | "CALIBRATED";
                    prior_floor: number;
                    radius: components["schemas"]["score"];
                    /** @constant */
                    rounding_decimals: 4;
                };
                density_measure: {
                    comparison_windows_used: {
                        coverage_window_sequence: number;
                        members_in_radius: number;
                    }[];
                    density_delta: number;
                    /** @description Số target_key riêng biệt trong nhóm ở kỳ này. */
                    density_now: number;
                    /** @description Trung bình cộng trên các kỳ trước TỒN TẠI; không đệm 0 cho kỳ không tồn tại. */
                    density_prior: number;
                    density_ratio: number;
                };
                emerging_direction: {
                    /** @description Vector centroid đã chuẩn hóa L2, độ dài bằng embedding_generation.dimension. Ghi bất biến để kỳ sau so lại được. */
                    centroid?: number[];
                    density?: components["schemas"]["density_measure"];
                    direction_id: components["schemas"]["report.schema_$defs-ulid"];
                    embedding_generation_id: components["schemas"]["report.schema_$defs-ulid"];
                    /**
                     * @description B14: thiếu dữ liệu KHÔNG được gọi là 'đang nổi'.
                     * @enum {string}
                     */
                    evidence_state: "sufficient" | "insufficient_evidence";
                    /** @description Target bị loại khỏi phép đếm vì đang có identity_conflict mở (B15). */
                    excluded_quarantined_target_keys: components["schemas"]["$defs-target_key"][];
                    insufficient_reason?: ("below_min_sample" | "cold_start_insufficient_history" | "delta_below_threshold" | "generation_reset") | null;
                    /**
                     * @description REQ-D54. Chuỗi này là hằng số hợp đồng; 'phát hiện mới' bị cấm.
                     * @constant
                     */
                    label: "ứng viên để đọc sâu";
                    member_target_keys: components["schemas"]["$defs-target_key"][];
                    parameters: components["schemas"]["density_parameters"];
                    /** @description analysis của task direction_phrasing (PC06). NULL hợp lệ: khối tồn tại được khi không có AI. */
                    phrasing_analysis_id?: components["schemas"]["report.schema_$defs-ulid"] | null;
                } & (unknown & unknown);
                pending_item: {
                    first_pending_window_sequence: number;
                    pending_item_ledger_id: components["schemas"]["report.schema_$defs-ulid"];
                    /** @enum {string} */
                    reason: "missing_summary" | "analysis_failed" | "analysis_unknown" | "budget_exceeded";
                    /** @enum {string} */
                    state: "pending" | "resolved_reported_late" | "abandoned_by_owner";
                    target_key: components["schemas"]["$defs-target_key"];
                };
                coverage_note: {
                    /** @description Các tag đã dùng entitlement backfill trong kỳ này (REQ-D28). */
                    backfill_applied_tag_ids?: components["schemas"]["report.schema_$defs-ulid"][];
                    /** @description Luôn false trong một read model đã publish: kỳ rỗng không tạo report hiển thị (REQ-D57). Trường tồn tại để consumer khẳng định được điều đó. */
                    empty_period: boolean;
                    /** @description true = coverage nêu phạm vi dữ liệu ĐÃ QUAN SÁT, không hứa bao phủ toàn bộ thời gian trên X (SRC-PLAN §9.2, B05). */
                    observed_data_only: boolean;
                    /** @description Ví dụ limit_reached, captcha, session_expired (SRC-PLAN §8.1). Null khi run kết thúc bình thường. */
                    run_stop_reason?: string | null;
                    /** @description Câu chữ về giới hạn bao phủ nguồn X (AMD-B05). */
                    source_coverage_limits_note?: string | null;
                    /**
                     * @description REQ-A2 / REQ-OQ08. 'uncalibrated' → UI phải nói rõ ngưỡng chưa hiệu chỉnh; cấm tuyên bố chỉ tiêu chất lượng §1.4.
                     * @enum {string}
                     */
                    threshold_calibration_state: "uncalibrated" | "calibrated";
                };
            };
        };
        /** @description RFC 3339 UTC, hậu tố Z, đúng ba chữ số mili giây (AMD-B08). */
        "report.schema_$defs-timestamp_utc_ms": string;
        /** @description ULID 26 ký tự Crockford base32 chữ hoa; ID luôn truyền dưới dạng string (SRC-PLAN §5.1). */
        "report.schema_$defs-ulid": string;
        /** @description Task `direction_phrasing` — AI CHỈ diễn đạt lại một kết quả ĐÃ TÍNH bởi contracts/reporting/selection.md §8. AI không chọn thành viên, không tính mật độ, không đổi nhãn (CR-PC04-05). */
        result_direction_phrasing: {
            /** @description FK → emerging_direction.id đã tính ở PC04. */
            direction_ref: components["schemas"]["analysis-result.schema_$defs-ulid"];
            /**
             * @description Hằng số hợp đồng (REQ-D54), giống contracts/schemas/report.schema.json. 'phát hiện mới' bị cấm.
             * @constant
             */
            label?: "ứng viên để đọc sâu";
            /** @description PHẢI bằng đúng emerging_direction.member_target_keys — không thêm, không bớt (SV-05). Đây là hàng rào chống việc AI 'chọn lại' thành viên. */
            member_refs: components["schemas"]["target_key"][];
            /** @description Câu chữ mô tả. Kiểm ngữ nghĩa SV-06 cấm các cụm khẳng định tính mới khoa học. */
            text: string;
        };
        /** @description Task `label` — gắn nhãn chủ đề MỞ (REQ-D22): 'bài này thuộc chủ đề gì', KHÔNG hỏi 'có khớp tag hiện tại không'. */
        result_label: {
            labels: {
                /**
                 * @description Ba mức RỜI RẠC, không phải điểm xác suất — cùng lý do với identity.md §7: MVP không có cách hiệu chỉnh một thang liên tục, nên không giả vờ có.
                 * @enum {string}
                 */
                confidence: "low" | "medium" | "high";
                evidence_refs: components["schemas"]["source_id"][];
                /** @description Khớp giới hạn của entities.yaml ENT-work-label.label_text (1..120). */
                label: string;
            }[];
        };
        /** @description Task `summary` — hình dạng D20: nội dung + điểm khác với cái đã có + MỘT dòng hạn chế. Dòng 'khớp tag nào' KHÔNG nằm ở đây: nó là dữ liệu tra từ report_item.selection_reason (PC04), không phải do AI sinh (REQ-D20, SRC-SPEC §10.1). */
        result_summary: {
            content: string;
            difference_from_existing: {
                comparator: components["schemas"]["comparator"];
                text: string;
            };
            /** @description MỘT dòng hạn chế (D20). Không được rỗng: 'không có hạn chế nào' là một phát biểu phải viết ra, không phải một trường bỏ trống. */
            limitation_line: string;
            /**
             * @description SRC-SPEC §10.3: nguồn chưa peer review phải có nhãn tương ứng. `unknown` hợp lệ; cấm đoán `peer_reviewed`.
             * @enum {string}
             */
            peer_review_status?: "preprint_not_peer_reviewed" | "peer_reviewed" | "unknown";
            /** @description Mọi phát biểu đáng kể đã tách theo kind (B16). */
            statements: components["schemas"]["statement"][];
        };
        saved_item: {
            id: components["schemas"]["ulid"];
            /** @description Khóa chống trùng của callback Telegram; NULL cho Save trong app. 5 lần bấm cùng key ⇒ một hàng (REQ-D38). */
            idempotency_key?: string | null;
            /** @description Con trỏ được ghi lại sau identity merge; snapshot KHÔNG bị đụng (I17). */
            moved_by_merge_id?: components["schemas"]["ulid"] | null;
            owner_id: components["schemas"]["ulid"];
            /**
             * @description Nguồn Save, hiển thị ở màn hình Saved (SRC-SPEC §4).
             * @enum {string}
             */
            save_channel: "app" | "telegram";
            saved_at: components["schemas"]["$defs-timestamp_utc_ms"];
            saved_snapshot_id: components["schemas"]["ulid"];
            /** @description Mục đang đọc lúc bấm Save. NULL khi Save từ Work detail ngoài phạm vi một báo cáo. */
            source_report_item_id?: components["schemas"]["ulid"] | null;
            /**
             * @description Tối đa một `active` cho một target (I08). `unsaved` giữ nguyên snapshot.
             * @enum {string}
             */
            state: "active" | "unsaved" | "superseded_by_merge";
            target: components["schemas"]["target"];
            target_key: components["schemas"]["$defs-target_key"];
            /** @description NOT NULL khi và chỉ khi state = 'unsaved'. */
            unsaved_at?: components["schemas"]["$defs-timestamp_utc_ms"] | null;
        };
        saved_snapshot: {
            /** @description Đúng bản phân tích người dùng ĐANG ĐỌC (report_item.analysis_id), KHÔNG phải bản mới hơn vừa xuất hiện. NULL chỉ khi target chưa có analysis valid nào. */
            analysis_id_at_save?: components["schemas"]["ulid"] | null;
            content: components["schemas"]["snapshot_content"];
            /** @description sha256(JCS(content)) — xem x-contract.canonical_json_rule. Oracle của REQ-AC12 và I08/I17. */
            content_hash: components["schemas"]["sha256"];
            created_at: components["schemas"]["$defs-timestamp_utc_ms"];
            id: components["schemas"]["ulid"];
            owner_id: components["schemas"]["ulid"];
            /** @description Kỳ báo cáo mà mục được đọc từ đó. Cho phép chứng minh snapshot khớp đúng revision đã publish (B01). */
            report_ref?: {
                report_content_hash: components["schemas"]["sha256"];
                report_id: components["schemas"]["ulid"];
                report_item_id?: components["schemas"]["ulid"];
                report_published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
            };
            /** @description BẤT BIẾN. Sau merge vẫn trỏ target lúc lưu — bằng chứng lịch sử, không phải con trỏ hiện hành (I17). */
            target_key_at_save: components["schemas"]["$defs-target_key"];
            /** @enum {string} */
            target_kind: "work" | "post";
        };
        /**
         * Saved item + immutable snapshot
         * @description Một mục đã Save cùng ảnh chụp bất biến của nội dung tại thời điểm lưu. Snapshot là lý do bài gốc bị xóa trên X vẫn đọc được (REQ-D55, REQ-AC12).
         */
        "saved-snapshot.schema": {
            saved_item: components["schemas"]["saved_item"];
            schema_version: components["schemas"]["semver"];
            snapshot: components["schemas"]["saved_snapshot"];
            $defs: {
                ulid: string;
                semver: string;
                sha256: string;
                timestamp_utc_ms: string;
                target_key: string;
                https_url: string;
                /** @description Tagged union work|post. Hình dạng chuẩn ở target.schema.json; lặp lại ở đây để fixture validate được độc lập, KHÔNG được lệch khỏi bản gốc. */
                target: {
                    /** @constant */
                    kind: "work";
                    target_key?: string;
                    work_id: components["schemas"]["ulid"];
                } | {
                    /** @constant */
                    kind: "post";
                    post_id: components["schemas"]["ulid"];
                    target_key?: string;
                };
                saved_item: {
                    id: components["schemas"]["ulid"];
                    /** @description Khóa chống trùng của callback Telegram; NULL cho Save trong app. 5 lần bấm cùng key ⇒ một hàng (REQ-D38). */
                    idempotency_key?: string | null;
                    /** @description Con trỏ được ghi lại sau identity merge; snapshot KHÔNG bị đụng (I17). */
                    moved_by_merge_id?: components["schemas"]["ulid"] | null;
                    owner_id: components["schemas"]["ulid"];
                    /**
                     * @description Nguồn Save, hiển thị ở màn hình Saved (SRC-SPEC §4).
                     * @enum {string}
                     */
                    save_channel: "app" | "telegram";
                    saved_at: components["schemas"]["$defs-timestamp_utc_ms"];
                    saved_snapshot_id: components["schemas"]["ulid"];
                    /** @description Mục đang đọc lúc bấm Save. NULL khi Save từ Work detail ngoài phạm vi một báo cáo. */
                    source_report_item_id?: components["schemas"]["ulid"] | null;
                    /**
                     * @description Tối đa một `active` cho một target (I08). `unsaved` giữ nguyên snapshot.
                     * @enum {string}
                     */
                    state: "active" | "unsaved" | "superseded_by_merge";
                    target: components["schemas"]["target"];
                    target_key: components["schemas"]["$defs-target_key"];
                    /** @description NOT NULL khi và chỉ khi state = 'unsaved'. */
                    unsaved_at?: components["schemas"]["$defs-timestamp_utc_ms"] | null;
                };
                saved_snapshot: {
                    /** @description Đúng bản phân tích người dùng ĐANG ĐỌC (report_item.analysis_id), KHÔNG phải bản mới hơn vừa xuất hiện. NULL chỉ khi target chưa có analysis valid nào. */
                    analysis_id_at_save?: components["schemas"]["ulid"] | null;
                    content: components["schemas"]["snapshot_content"];
                    /** @description sha256(JCS(content)) — xem x-contract.canonical_json_rule. Oracle của REQ-AC12 và I08/I17. */
                    content_hash: components["schemas"]["sha256"];
                    created_at: components["schemas"]["$defs-timestamp_utc_ms"];
                    id: components["schemas"]["ulid"];
                    owner_id: components["schemas"]["ulid"];
                    /** @description Kỳ báo cáo mà mục được đọc từ đó. Cho phép chứng minh snapshot khớp đúng revision đã publish (B01). */
                    report_ref?: {
                        report_content_hash: components["schemas"]["sha256"];
                        report_id: components["schemas"]["ulid"];
                        report_item_id?: components["schemas"]["ulid"];
                        report_published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                    };
                    /** @description BẤT BIẾN. Sau merge vẫn trỏ target lúc lưu — bằng chứng lịch sử, không phải con trỏ hiện hành (I17). */
                    target_key_at_save: components["schemas"]["$defs-target_key"];
                    /** @enum {string} */
                    target_kind: "work" | "post";
                };
                /** @description Nội dung TỰ ĐỦ: đọc được mà không cần truy vấn lại bất cứ bảng nào và không cần mở nguồn ngoài (REQ-AC12, REQ-AC10). */
                snapshot_content: {
                    /** @description Truy vết bản phân tích đã chụp. `analyzed_at` hiển thị cùng `discovered_at` (SRC-SPEC §10.3). */
                    analysis_ref?: {
                        analysis_id: components["schemas"]["ulid"];
                        analyzed_at: components["schemas"]["$defs-timestamp_utc_ms"];
                        generation_number?: number;
                        model_name?: string;
                        payload_hash?: components["schemas"]["sha256"];
                        provider_name?: string;
                    };
                    /** @description Phiên bản hình dạng của chính object này. Đổi hình dạng ⇒ đổi cách canonical hóa ⇒ mọi content_hash cũ không tái lập được; vì vậy phải bump và ghi migration (entities.yaml §schema_versioning). */
                    content_version: components["schemas"]["semver"];
                    display_title: string;
                    /**
                     * @description Nhãn mức độ đọc (REQ-D21). Không được nâng cấp khi nguồn tương ứng không tồn tại.
                     * @enum {string}
                     */
                    evidence_level: "post_only" | "abstract" | "full_text";
                    /** @description Nếu mục là tham chiếu tới kỳ trước (REQ-D29, REQ-AC09). */
                    first_announced?: {
                        first_announced_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                        first_report_id?: components["schemas"]["ulid"];
                    };
                    /** @description Dòng 'khớp tag nào' (REQ-D20, REQ-AC10). Là ẢNH CHỤP tag lúc lưu — bỏ tag sau đó KHÔNG làm mảng này đổi (REQ-S8.2-07). */
                    matched_tags: {
                        similarity?: number;
                        tag_id?: components["schemas"]["ulid"];
                        tag_text: string;
                    }[];
                    /** @description Các post dẫn tới target, chụp lúc lưu. Mảng rỗng hợp lệ khi target là work chưa có post nào còn đọc được. */
                    source_posts: {
                        author_handle: string;
                        discovered_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                        published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                        /** @description Văn bản post lúc lưu. Là DỮ LIỆU: escape khi hiển thị, không thực thi (I11). */
                        text: string;
                        url: components["schemas"]["https_url"];
                        x_post_id: string;
                    }[];
                    summary: components["schemas"]["summary_block"];
                    target: components["schemas"]["target"];
                    /** @description Nhãn chủ đề mở do AI gắn (REQ-D22). */
                    topic_labels?: string[];
                    /** @description Vắng mặt hợp lệ với target chỉ-có-post (REQ-D33). */
                    work_metadata?: {
                        abstract_text?: string;
                        canonical_arxiv_id?: string;
                        canonical_doi?: string;
                        code_url?: components["schemas"]["https_url"];
                        paper_url?: components["schemas"]["https_url"];
                        work_version_label?: string;
                    };
                };
                /** @description Hình dạng REQ-D20: nội dung + điểm khác với cái đã có + một dòng hạn chế. Thiếu trường nào thì hiện nhãn thiếu, KHÔNG bịa (B16). */
                summary_block: {
                    /** @description Phân loại phát biểu theo B16 / SRC-SPEC §10.3. */
                    claim_kinds?: ("author_claim" | "source_verified" | "ai_inference")[];
                    /**
                     * @description `unknown` khi không có nguồn so sánh; KHÔNG bịa baseline (B16).
                     * @enum {string}
                     */
                    comparator?: "known" | "unknown";
                    content_vi: string;
                    limitation_vi: string;
                    /** @description Điểm khác với cái đã có. Với evidence_level = post_only, đây là SUY LUẬN, không phải kết luận (REQ-AC11). */
                    novelty_vi: string;
                };
            };
        };
        /** @description Cosine similarity đã làm tròn half-up 4 chữ số thập phân (selection.md §3). */
        score: number;
        /** @description Ảnh chụp cấu hình dùng để TÌM KIẾM. Bất biến trong suốt assignment: đổi tag giữa lúc chạy KHÔNG ảnh hưởng việc lọc (REQ-D24, REQ-S8.2-06). */
        search_config: {
            source_limits: components["schemas"]["source_limits"];
            /** @description Version của ảnh chụp tìm kiếm. Ghi lại để truy vết; điểm ĐÓNG BĂNG tag của báo cáo là transaction publish, không phải ở đây (B01/AMD-B01). */
            tag_config_version_id: components["schemas"]["ulid"];
            /** @description CHỈ là từ khóa tìm kiếm trên X. KHÔNG phải bộ lọc báo cáo. */
            tags: string[];
        };
        semver: string;
        SemVer: string;
        /** @description Ảnh chụp CỦA SERVER về tiến độ ĐÃ ACK. Đây là nguồn sự thật khi worker claim lại (contracts/state/run.yaml §CP-02, I02). Rỗng-mới (sequence 0) cho một run chưa ingest gì. */
        server_checkpoint: {
            /** @description Mọi post có `ingest_sequence <= giá trị này` ĐÃ COMMIT ở server. Đây là định nghĩa vận hành của 'đã ACK' (contracts/state/run.yaml §CP-02). */
            acked_through_ingest_sequence: number;
            /** @description `checkpoint.sequence` hiện hành. Append-only; seq lùi bị từ chối (§CP-04). */
            checkpoint_sequence: number;
            /** @enum {string} */
            cursor_state: "valid" | "invalidated";
            /** @description null hợp lệ khi con trỏ mất hiệu lực; khi đó `cursor_state = invalidated` và recovery policy cho phép ĐỌC LẠI — dedup xảy ra ở ingest theo `x_post_id` (AMD-B05). */
            cursor_token: string | null;
            items_ingested_total: number;
            /** @enum {string} */
            phase: "collecting" | "enriching" | "analyzing" | "reporting";
        };
        SessionInfo: {
            authenticated: boolean;
            /** @description Giá trị để double-submit. Cũng được đặt vào cookie `rr_csrf` không-HttpOnly. */
            csrf_token?: string;
            expires_at?: components["schemas"]["TimestampUtcMs"];
            schema_version?: components["schemas"]["SemVer"];
        };
        sha256: string;
        Sha256: string;
        /** @description Nội dung TỰ ĐỦ: đọc được mà không cần truy vấn lại bất cứ bảng nào và không cần mở nguồn ngoài (REQ-AC12, REQ-AC10). */
        snapshot_content: {
            /** @description Truy vết bản phân tích đã chụp. `analyzed_at` hiển thị cùng `discovered_at` (SRC-SPEC §10.3). */
            analysis_ref?: {
                analysis_id: components["schemas"]["ulid"];
                analyzed_at: components["schemas"]["$defs-timestamp_utc_ms"];
                generation_number?: number;
                model_name?: string;
                payload_hash?: components["schemas"]["sha256"];
                provider_name?: string;
            };
            /** @description Phiên bản hình dạng của chính object này. Đổi hình dạng ⇒ đổi cách canonical hóa ⇒ mọi content_hash cũ không tái lập được; vì vậy phải bump và ghi migration (entities.yaml §schema_versioning). */
            content_version: components["schemas"]["semver"];
            display_title: string;
            /**
             * @description Nhãn mức độ đọc (REQ-D21). Không được nâng cấp khi nguồn tương ứng không tồn tại.
             * @enum {string}
             */
            evidence_level: "post_only" | "abstract" | "full_text";
            /** @description Nếu mục là tham chiếu tới kỳ trước (REQ-D29, REQ-AC09). */
            first_announced?: {
                first_announced_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                first_report_id?: components["schemas"]["ulid"];
            };
            /** @description Dòng 'khớp tag nào' (REQ-D20, REQ-AC10). Là ẢNH CHỤP tag lúc lưu — bỏ tag sau đó KHÔNG làm mảng này đổi (REQ-S8.2-07). */
            matched_tags: {
                similarity?: number;
                tag_id?: components["schemas"]["ulid"];
                tag_text: string;
            }[];
            /** @description Các post dẫn tới target, chụp lúc lưu. Mảng rỗng hợp lệ khi target là work chưa có post nào còn đọc được. */
            source_posts: {
                author_handle: string;
                discovered_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                published_at?: components["schemas"]["$defs-timestamp_utc_ms"];
                /** @description Văn bản post lúc lưu. Là DỮ LIỆU: escape khi hiển thị, không thực thi (I11). */
                text: string;
                url: components["schemas"]["https_url"];
                x_post_id: string;
            }[];
            summary: components["schemas"]["summary_block"];
            target: components["schemas"]["target"];
            /** @description Nhãn chủ đề mở do AI gắn (REQ-D22). */
            topic_labels?: string[];
            /** @description Vắng mặt hợp lệ với target chỉ-có-post (REQ-D33). */
            work_metadata?: {
                abstract_text?: string;
                canonical_arxiv_id?: string;
                canonical_doi?: string;
                code_url?: components["schemas"]["https_url"];
                paper_url?: components["schemas"]["https_url"];
                work_version_label?: string;
            };
        };
        /** @description Định danh của MỘT nguồn cụ thể đã được cấp trong input: một hàng `post` hoặc một hàng `work_version`. Citation chỉ được trỏ tới đây — không trỏ tới URL tự do, không trỏ tới tên tác giả, không trỏ tới văn bản tự do. */
        source_id: string;
        /** @description Giới hạn nguồn, gửi kèm assignment để collector không phải suy diễn. Xem contracts/ops/collector-probe.md §Giới hạn nguồn. */
        source_limits: {
            /**
             * @description Chỉ mở thread khi đó là thread do CHÍNH TÁC GIẢ viết (REQ-D31).
             * @constant
             */
            author_thread_only: true;
            /**
             * @description Chrome của collector CHỈ lo X; không mở arXiv/OpenAlex (REQ-D32, denied case NC-08).
             * @constant
             */
            chrome_scope: "x_only";
            /**
             * @description Replies của người ngoài bị HOÃN sang P1 (REQ-D31); không ingest.
             * @constant
             */
            external_replies: "excluded";
            /**
             * @description Post chỉ có ảnh chụp paper, không có link ⇒ KHÔNG đoán ID; thành mục 'chỉ có post' (REQ-D33, I03).
             * @constant
             */
            image_only_post_policy: "post_only_no_id_guess";
            /** @description PROVISIONAL 50 (contracts/data/entities.yaml §limits.ingest_thread_context_max_posts). */
            max_thread_context_posts?: number;
            /**
             * @description Metadata paper lấy qua API từ SERVER (REQ-D32), không phải từ trình duyệt của collector.
             * @constant
             */
            paper_metadata_source: "server_api";
        };
        /** @description Nơi collector nhìn thấy post. Cần để ghi giới hạn bao phủ X trong metadata run (B05). */
        source_provenance: {
            /** @enum {string} */
            discovery_surface: "search_query" | "home_timeline" | "author_profile" | "thread_expansion";
            page_cursor_observed?: string;
            /** @description Tag chỉ dùng để TÌM KIẾM, không dùng để lọc (REQ-D24). */
            query_text?: string;
        };
        statement: {
            /** @description Phải là tập con của input_source_ids (SV-02). `ai_inference` được phép rỗng — suy luận không cần nguồn, nhưng PHẢI mang nhãn ai_inference (SV-03). */
            citation_refs: components["schemas"]["source_id"][];
            kind: components["schemas"]["statement_kind"];
            text: string;
        } & unknown;
        /**
         * @description B16 / AMD-B16 / SRC-SPEC §10.3: tách ba loại phát biểu. `source_verified` chỉ dùng khi nội dung kiểm được từ nguồn ĐÃ CẤP; mọi phát biểu về tính mới là `ai_inference` (REQ-AC11).
         * @enum {string}
         */
        statement_kind: "author_claim" | "source_verified" | "ai_inference";
        /** @description Điều kiện dừng phải RÕ RÀNG (REQ-A7: X có thể hạn chế tài khoản dù người dùng tự giải CAPTCHA). */
        stop_conditions: {
            /**
             * @description Chạm ngưỡng nào TRƯỚC thì dừng theo ngưỡng đó; `limit_kind` ghi rõ ngưỡng nào (contracts/state/run.yaml §coverage_metadata).
             * @constant
             */
            evaluation: "first_of_either";
            /** @description PROVISIONAL 1800 giây (contracts/retry-policy.yaml §per_run_duration_limit). */
            max_duration_s: number;
            /** @description PROVISIONAL 200 (contracts/retry-policy.yaml §per_run_post_limit; REQ-OQ05 — Owner chốt số thật sau M0). */
            max_posts: number;
            /**
             * @description Bị chặn ⇒ dừng và báo. KHÔNG luân chuyển account/proxy/fingerprint (SRC-SPEC §2.3, REQ-S9.3-02).
             * @constant
             */
            on_blocked: "report_stop_and_halt_no_rotation";
            /**
             * @description Gặp CAPTCHA/hết phiên ⇒ gọi `worker.report_stop`, DỪNG. Không tự thử lại, không giả lập thao tác xác minh (REQ-S9.3-01, SRC-SPEC §2.3).
             * @constant
             */
            on_challenge: "report_stop_and_halt";
        };
        /**
         * @description Request của `worker.report_stop`. Enum `stop_reason` giữ ĐÚNG tám giá trị của
         *     `contracts/ports.yaml` → `worker.report_stop.request_summary_vi`; trạng thái run mà mỗi giá trị dẫn tới
         *     được khóa ở `contracts/state/run.yaml`:
         *
         *       challenge_required        -> run needs_user  (T-RUN-09) + TOI DA MOT alert intent moi run
         *       session_expired           -> run needs_user  (T-RUN-09)
         *       limit_reached             -> dong segment, phase ke tiep (T-RUN-02); KHONG phai loi
         *       rate_limited              -> dong segment, phase ke tiep (T-RUN-25), outcome du kien partial;
         *                                    KHONG retry trong dot; dot theo lich ke tiep chay binh thuong
         *       source_blocked            -> run blocked     (T-RUN-16); can Owner go bang run.resume
         *       source_layout_changed     -> run blocked     (T-RUN-24) + mot alert intent; can sua bo doc
         *       worker_shutdown           -> tra assignment, lease thu hoi
         *       local_storage_unavailable -> tra assignment; server KHONG doi trang thai nghien cuu
         *
         *     `rate_limited` va `source_blocked` la HAI gia tri khac nhau mot cach co chu dich: rate limit nghia la X VAN
         *     cho vao nhung bao cho, con source_blocked nghia la X KHONG cho vao. Gop chung se cho ba hanh vi UI khac nhau
         *     o AC-15 (SRC-SPEC §9.3; ruling CR-PC10-02).
         */
        StopReport: {
            assignment_id: components["schemas"]["Ulid"];
            /** @description Mốc ACK cuối cùng collector quan sát được. Server đối chiếu với `checkpoint.acked_through_ingest_sequence` của chính nó; giá trị của client KHÔNG ghi đè (I02). */
            last_acked_ingest_sequence: number;
            /** @description Epoch cũ ⇒ 409 `STALE_LEASE`, không ghi gì. */
            lease_epoch: number;
            lease_id: components["schemas"]["Ulid"];
            /**
             * @description NOT NULL khi `stop_reason = limit_reached` (REQ-A7: điều kiện dừng phải rõ).
             * @enum {string|null}
             */
            limit_kind?: "posts" | "duration" | null;
            /** @description Có mặt khi `stop_reason = source_layout_changed`. CHỈ TÊN TRƯỜNG theo schema; tuyệt đối không kèm giá trị quan sát được, HTML/DOM hay URL đầy đủ. */
            missing_required_fields?: string[];
            note_vi?: string;
            /** @description Số bài đã TẢI nhưng CHƯA ingest tại thời điểm dừng. Chúng KHÔNG phải checkpoint bền (SRC-PLAN §8.1, run.yaml CP-03); trường này chỉ để truy vết phần bị mất khi dừng đột ngột. */
            posts_downloaded_not_ingested?: number;
            /** @description Tổng số bài quan sát được trong đợt; server ghi vào `run.posts_observed_total`. Là QUAN SÁT của collector, không phải dữ liệu authoritative. */
            posts_observed_total?: number;
            posts_parsed_ok?: number;
            posts_seen?: number;
            /** @description Có mặt khi `stop_reason = rate_limited`. Server ghi `run.rate_limited_at` và bắt buộc nhắc mốc này trong `x_coverage_note_vi` (ruling CR-PC10-02). */
            rate_limited_at?: components["schemas"]["TimestampUtcMs"];
            request_id: components["schemas"]["Ulid"];
            /** @description Giá trị nguồn trả về nếu có. Ghi để truy vết; KHÔNG dùng để thử lại trong đợt (`x_rate_limit_in_run_retries = 0`). */
            retry_after_ms?: number | null;
            schema_version: components["schemas"]["SemVer"];
            /** @enum {string} */
            stop_reason: "challenge_required" | "limit_reached" | "session_expired" | "source_blocked" | "source_layout_changed" | "rate_limited" | "worker_shutdown" | "local_storage_unavailable";
            /** @description Idempotency: `assignment_id + stop_report_id`. Báo lại cùng giá trị KHÔNG tạo alert thứ hai (REQ-AC04). */
            stop_report_id: components["schemas"]["Ulid"];
            /** @description Câu ghi phần feed KHÔNG quan sát được. BẮT BUỘC khi `limit_reached` hoặc `rate_limited` (AMD-B05). */
            x_coverage_note_vi?: string;
        };
        /** @description Hình dạng REQ-D20: nội dung + điểm khác với cái đã có + một dòng hạn chế. Thiếu trường nào thì hiện nhãn thiếu, KHÔNG bịa (B16). */
        summary_block: {
            /** @description Phân loại phát biểu theo B16 / SRC-SPEC §10.3. */
            claim_kinds?: ("author_claim" | "source_verified" | "ai_inference")[];
            /**
             * @description `unknown` khi không có nguồn so sánh; KHÔNG bịa baseline (B16).
             * @enum {string}
             */
            comparator?: "known" | "unknown";
            content_vi: string;
            limitation_vi: string;
            /** @description Điểm khác với cái đã có. Với evidence_level = post_only, đây là SUY LUẬN, không phải kết luận (REQ-AC11). */
            novelty_vi: string;
        };
        tag_config_version_ref: {
            content_hash: components["schemas"]["sha256"];
            /** @description Bằng published_at: freeze xảy ra TRONG transaction publish (B01/AMD-B01). */
            frozen_at: components["schemas"]["report.schema_$defs-timestamp_utc_ms"];
            sequence: number;
            tag_config_version_id: components["schemas"]["report.schema_$defs-ulid"];
        };
        /** @description Tagged union work|post. Hình dạng chuẩn ở target.schema.json; lặp lại ở đây để fixture validate được độc lập, KHÔNG được lệch khỏi bản gốc. */
        target: {
            /** @constant */
            kind: "work";
            target_key?: string;
            work_id: components["schemas"]["ulid"];
        } | {
            /** @constant */
            kind: "post";
            post_id: components["schemas"]["ulid"];
            target_key?: string;
        };
        /** @description Khóa union của target (contracts/schemas/target.schema.json). */
        target_key: string;
        /**
         * Target (tagged union: work | post)
         * @description Đối tượng có thể được Save, phân tích hoặc đưa vào một mục báo cáo. Tagged union hai nhánh phân biệt bằng `kind`; đúng một cột id được đặt (SRC-PLAN §9.1, B06).
         */
        "target.schema": {
            $defs: {
                /** @description ULID 26 ký tự Crockford base32 chữ hoa. ID luôn truyền dưới dạng string (SRC-PLAN §5.1). */
                ulid: string;
                /** @description Khóa union `work:<ulid>` hoặc `post:<ulid>`. Là cột mang UNIQUE của Saved (I08). */
                target_key: string;
                /** @description DOI đã chuẩn hóa theo contracts/data/identity.md §2.1: chữ thường, không tiền tố URL, không dấu câu cuối. */
                doi_canonical: string;
                /** @description arXiv base ID đã chuẩn hóa theo identity.md §2.2, KHÔNG kèm hậu tố phiên bản. Kiểu mới `YYMM.NNNNN` hoặc kiểu cũ `archive[.CC]/YYMMNNN`. */
                arxiv_base_canonical: string;
                /** @description Nhãn phiên bản arXiv; sống ở work_version, không thuộc canonical id. */
                arxiv_version_label: string;
                /** @description Định danh canonical đã biết của một work. Vắng mặt hoàn toàn là hợp lệ: work có thể tồn tại trước khi metadata về (metadata_state = 'none'). */
                canonical_identifiers: {
                    arxiv_base?: components["schemas"]["arxiv_base_canonical"];
                    doi?: components["schemas"]["doi_canonical"];
                };
                /** @description Một định danh đã quan sát được, canonical hoặc alias, kèm provenance bắt buộc (identity.md §7). */
                alias_identifier: {
                    /**
                     * @description Ba mức rời rạc, không phải điểm xác suất — MVP không đoán.
                     * @enum {string}
                     */
                    confidence: "asserted_by_source" | "confirmed_by_two_sources" | "owner_confirmed";
                    evidence_ref?: {
                        api_endpoint?: string;
                        post_id?: components["schemas"]["$defs-ulid"];
                        response_hash?: components["schemas"]["sha256"];
                        retrieved_at?: components["schemas"]["target.schema_$defs-timestamp_utc_ms"];
                    };
                    /**
                     * @description Không có giá trị suy luận AI: AI không được tạo bằng chứng identity (B15).
                     * @enum {string}
                     */
                    evidence_source: "post_link" | "arxiv_api" | "openalex_api" | "manual_owner";
                    /**
                     * @description Chỉ `doi` và `arxiv` là canonical; còn lại là alias-only.
                     * @enum {string}
                     */
                    id_scheme: "doi" | "arxiv" | "openalex" | "pmid" | "landing_url";
                    id_value_normalized: string;
                    id_value_raw: string;
                };
                /** @description RFC 3339 UTC, hậu tố Z, độ chính xác mili-giây bắt buộc (SRC-PLAN §5.1, B08). */
                timestamp_utc_ms: string;
                sha256: string;
                /**
                 * Target nhánh work
                 * @description Công trình có canonical identity. `post_id` bị cấm ở nhánh này (exactly-one).
                 */
                work_target: {
                    canonical?: components["schemas"]["canonical_identifiers"];
                    /**
                     * @description Consumer phải loại `merged` bằng resolve_work() và phải xử lý `quarantined` riêng (identity.md §5).
                     * @enum {string}
                     */
                    identity_state?: "active" | "merged" | "quarantined";
                    /** @constant */
                    kind: "work";
                    target_key?: string;
                    work_id: components["schemas"]["$defs-ulid"];
                    work_version_label?: components["schemas"]["arxiv_version_label"];
                };
                /**
                 * Target nhánh post (mục chỉ có post)
                 * @description Post không dẫn tới work nào (REQ-D33). `work_id` và `canonical` bị cấm ở nhánh này.
                 */
                post_target: {
                    /**
                     * @description Chỉ `resolved_post_only` mới là target post hợp lệ để Save/summary; `pending` chưa phải target.
                     * @enum {string}
                     */
                    identity_resolution?: "pending" | "resolved_linked" | "resolved_post_only" | "conflict";
                    /** @constant */
                    kind: "post";
                    post_id: components["schemas"]["$defs-ulid"];
                    target_key?: string;
                    /** @description ID gốc trên X, dạng string. */
                    x_post_id?: string;
                };
            };
        } & (components["schemas"]["work_target"] | components["schemas"]["post_target"]);
        /** @description RFC 3339 UTC, hậu tố Z, độ chính xác mili-giây bắt buộc (SRC-PLAN §5.1, B08). */
        "target.schema_$defs-timestamp_utc_ms": string;
        /** @description Tagged union `work | post` (B06/ADR-0009). Hai cột nullable với một UNIQUE mơ hồ KHÔNG đủ (contracts/data/invariants.md Phụ lục A). */
        TargetRef: string;
        /**
         * @description Nguyên văn contracts/data/entities.yaml ENT-analysis.task_type (ruling R-03). `embedding` KHÔNG có ở đây: embedding chạy local ở server, không qua AI adapter (REQ-D48, SRC-SPEC §10.1).
         * @enum {string}
         */
        task_type: "label" | "summary" | "direction_phrasing";
        thread_context: {
            /** @description true khi post thuộc thread do chính tác giả viết. Replies của người ngoài KHÔNG được ingest (REQ-D31, REQ-P1-02). */
            is_author_thread_member: boolean;
            position_in_thread?: number;
            thread_root_x_post_id?: string;
            thread_size_observed?: number;
        };
        /** @description UTC RFC 3339, độ chính xác mili giây (AMD-B08). Không có offset nào khác `Z`. */
        timestamp_utc_ms: string;
        /** @description UTC RFC 3339 với độ chính xác mili giây; tie-break bằng ingest sequence (AMD-B08). Không có offset nào khác `Z`. */
        TimestampUtcMs: string;
        ulid: string;
        /** @description ID truyền dưới dạng string (SRC-PLAN §5.1). */
        Ulid: string;
        /** @description REQ-D44 + I14: 'không rõ' là giá trị hợp lệ và CẤM ghi thành 0. Cấu trúc ép điều đó ở mức schema. */
        usage: {
            /** @description Micro-USD nguyên để tránh số thực. null khi không biết. */
            cost_micro_usd: number | null;
            tokens_in: number | null;
            tokens_out: number | null;
            /** @description true = adapter không báo được usage (điển hình đường CLI/ACP, REQ-D44). */
            unknown: boolean;
        } & (unknown & unknown);
        warning: {
            /**
             * @description Mã theo contracts/errors.yaml. Chúng xuất hiện Ở ĐÂY (trong một response 2xx) chứ không phải như một error envelope, vì lô VẪN COMMIT — chỉ item liên quan bị giữ lại.
             * @enum {string}
             */
            code: "IDENTITY_CONFLICT" | "VALIDATION_ERROR" | "SOURCE_METADATA_UNAVAILABLE";
            /** @description Có mặt khi `code = IDENTITY_CONFLICT`; trỏ tới hàng `identity_conflict` để Owner xử lý qua `identity.resolve_conflict`. */
            conflict_id?: components["schemas"]["ulid"];
            /** @description Tiếng Việt, đã che dữ liệu. KHÔNG chứa nội dung post, URL đầy đủ hay transcript. */
            message_safe: string;
            x_post_id: components["schemas"]["x_post_id"];
        };
        /**
         * Target nhánh work
         * @description Công trình có canonical identity. `post_id` bị cấm ở nhánh này (exactly-one).
         */
        work_target: {
            canonical?: components["schemas"]["canonical_identifiers"];
            /**
             * @description Consumer phải loại `merged` bằng resolve_work() và phải xử lý `quarantined` riêng (identity.md §5).
             * @enum {string}
             */
            identity_state?: "active" | "merged" | "quarantined";
            /** @constant */
            kind: "work";
            target_key?: string;
            work_id: components["schemas"]["$defs-ulid"];
            work_version_label?: components["schemas"]["arxiv_version_label"];
        };
        /**
         * Worker assignment (claim / heartbeat / release)
         * @description Hình dạng wire của assignment mà server giao cho collector: request và response của `worker.claim_assignment`, `worker.heartbeat`, `worker.release_assignment`. Trạng thái và ngữ nghĩa transition thuộc contracts/state/run.yaml (PC03); file này chỉ khóa hình dạng dữ liệu trên dây. Checkpoint trong assignment CHỈ chứa dữ liệu server đã ACK (I02, AMD-B05, ruling R-01).
         */
        "worker-assignment.schema": {
            assignment?: components["schemas"]["assignment"];
            claim_request?: components["schemas"]["claim_request"];
            heartbeat_request?: components["schemas"]["heartbeat_request"];
            heartbeat_response?: components["schemas"]["heartbeat_response"];
            no_work?: components["schemas"]["no_work"];
            release_request?: components["schemas"]["release_request"];
            $defs: {
                ulid: string;
                semver: string;
                sha256: string;
                /** @description UTC RFC 3339, độ chính xác mili giây (AMD-B08). Không có offset nào khác `Z`. */
                timestamp_utc_ms: string;
                claim_request: {
                    capabilities: components["schemas"]["collector_capabilities"];
                    /** @description Idempotency key của claim (contracts/ports.yaml: 'Cùng claim_request_id trả cùng assignment; không cấp hai lease'). Timeout của claim là KHÔNG BIẾT KẾT QUẢ (SRC-PLAN §5.1): worker phải gọi lại với CÙNG key, không sinh key mới. */
                    claim_request_id: string;
                    /** @description Cố định 1: MVP một người dùng, một collector, một run đang chạy (contracts/state/run.yaml T-RUN-21 coalesce). */
                    max_assignments: number;
                    /** @description ID của lần gọi này. Retry sinh request_id mới nhưng GIỮ NGUYÊN claim_request_id. */
                    request_id: components["schemas"]["ulid"];
                    schema_version: components["schemas"]["semver"];
                    worker_instance_id: components["schemas"]["ulid"];
                    /**
                     * @description `worker.claim_assignment` chỉ dành cho collector. Analysis worker dùng `analysis.claim_task` (PC06).
                     * @enum {string}
                     */
                    worker_kind: "collector";
                };
                collector_capabilities: {
                    /** @description Chrome thật với PROFILE RIÊNG CỦA DỰ ÁN (REQ-D09), không phải profile mặc định. false ⇒ server không giao việc. */
                    chrome_profile_ready: boolean;
                    collector_online: boolean;
                    collector_version?: components["schemas"]["semver"];
                    /**
                     * @description LUÔN false. Server TỪ CHỐI bản đăng ký khai true bằng VALIDATION_ERROR — guard cho D50/B12: embedding không bao giờ chạy trên máy cá nhân.
                     * @constant
                     */
                    embedding_supported: false;
                    /**
                     * @description `unknown` được đối xử như KHÔNG dùng được khi quyết định giao việc, nhưng hiển thị khác `unusable` (contracts/ops/deployment.md §7).
                     * @enum {string}
                     */
                    x_session_state: "ok" | "challenge" | "expired" | "unknown";
                };
                assignment: {
                    assignment_id: components["schemas"]["ulid"];
                    capability_requirements: {
                        /** @constant */
                        requires_chrome_profile: true;
                        /**
                         * @description Server chỉ giao khi worker khai `x_session_state = ok`. `challenge`/`expired`/`unknown` ⇒ không giao (contracts/state/run.yaml T-RUN-01 guard).
                         * @constant
                         */
                        requires_x_session_ok: true;
                    };
                    /** @description NOT NULL khi run này gộp nhiều occurrence quá hạn (REQ-D15). Chỉ để hiển thị và để ghi khoảng bao trùm; KHÔNG phải bộ lọc dữ liệu (REQ-D12). */
                    catch_up_window?: {
                        from: components["schemas"]["timestamp_utc_ms"];
                        occurrence_count: number;
                        to: components["schemas"]["timestamp_utc_ms"];
                    } | null;
                    checkpoint: components["schemas"]["server_checkpoint"];
                    /** @description true khi assignment này đến sau `run.resume` (needs_user → queued). Lease LUÔN mới; không có đường tiếp tục bằng lease cũ (contracts/state/run.yaml §LM-07, I10). */
                    is_resume: boolean;
                    lease: components["schemas"]["lease"];
                    /**
                     * @description Phase cần làm tiếp. Collector chỉ nhận assignment ở `collecting`.
                     * @enum {string}
                     */
                    phase: "collecting" | "enriching" | "analyzing" | "reporting";
                    /** @description FK → run.id (contracts/data/entities.yaml ENT-run). */
                    run_id: components["schemas"]["ulid"];
                    search_config: components["schemas"]["search_config"];
                    stop_conditions: components["schemas"]["stop_conditions"];
                    /**
                     * @description REQ-D14.
                     * @enum {string}
                     */
                    trigger_type: "scheduled" | "manual";
                    /** @description Câu ghi rõ giới hạn bao phủ X cho đợt này. BẮT BUỘC không rỗng: `completed` không có nghĩa đã quét đủ toàn bộ X (AMD-B05). Collector chép lại nguyên văn vào metadata run khi báo dừng. */
                    x_coverage_note_vi: string;
                };
                /** @description Response khi không có việc. KHÔNG phải lỗi. */
                no_work: {
                    /**
                     * @description `run_needs_user`/`run_blocked`: có run nhưng nó chờ Owner — worker KHÔNG tự claim lại (I10). `storage_not_healthy`: xem contracts/state/storage.yaml.
                     * @enum {string}
                     */
                    reason: "no_due_occurrence" | "run_needs_user" | "run_blocked" | "storage_not_healthy" | "capability_not_met" | "assignment_already_held";
                    /** @description Gợi ý theo `claim_idle_backoff` (contracts/retry-policy.yaml: 5/15/45 giây). */
                    retry_after_ms: number;
                };
                /** @description Quyền độc quyền trên một assignment (ENT-assignment-lease). Con số ở contracts/retry-policy.yaml; giá trị dưới đây do SERVER cấp cho từng lease, client không tự chọn. */
                lease: {
                    /** @description Giờ SERVER. Lease hết hạn khi `now > expires_at + heartbeat_grace` (30 s). */
                    expires_at: components["schemas"]["timestamp_utc_ms"];
                    /** @description PROVISIONAL 30 giây (contracts/ops/deployment.md, PC01). */
                    heartbeat_interval_s: number;
                    /** @description Đơn điệu tăng cho một job; epoch cũ ⇒ STALE_LEASE và KHÔNG dữ liệu authoritative nào đổi (I10). */
                    lease_epoch: number;
                    lease_id: components["schemas"]["ulid"];
                    /** @description PROVISIONAL 120 giây (contracts/retry-policy.yaml §lease_ttl_collector). Ràng buộc: >= 4 × heartbeat_interval_s và > online_threshold (90 s). */
                    ttl_s: number;
                };
                /** @description Ảnh chụp cấu hình dùng để TÌM KIẾM. Bất biến trong suốt assignment: đổi tag giữa lúc chạy KHÔNG ảnh hưởng việc lọc (REQ-D24, REQ-S8.2-06). */
                search_config: {
                    source_limits: components["schemas"]["source_limits"];
                    /** @description Version của ảnh chụp tìm kiếm. Ghi lại để truy vết; điểm ĐÓNG BĂNG tag của báo cáo là transaction publish, không phải ở đây (B01/AMD-B01). */
                    tag_config_version_id: components["schemas"]["ulid"];
                    /** @description CHỈ là từ khóa tìm kiếm trên X. KHÔNG phải bộ lọc báo cáo. */
                    tags: string[];
                };
                /** @description Giới hạn nguồn, gửi kèm assignment để collector không phải suy diễn. Xem contracts/ops/collector-probe.md §Giới hạn nguồn. */
                source_limits: {
                    /**
                     * @description Chỉ mở thread khi đó là thread do CHÍNH TÁC GIẢ viết (REQ-D31).
                     * @constant
                     */
                    author_thread_only: true;
                    /**
                     * @description Chrome của collector CHỈ lo X; không mở arXiv/OpenAlex (REQ-D32, denied case NC-08).
                     * @constant
                     */
                    chrome_scope: "x_only";
                    /**
                     * @description Replies của người ngoài bị HOÃN sang P1 (REQ-D31); không ingest.
                     * @constant
                     */
                    external_replies: "excluded";
                    /**
                     * @description Post chỉ có ảnh chụp paper, không có link ⇒ KHÔNG đoán ID; thành mục 'chỉ có post' (REQ-D33, I03).
                     * @constant
                     */
                    image_only_post_policy: "post_only_no_id_guess";
                    /** @description PROVISIONAL 50 (contracts/data/entities.yaml §limits.ingest_thread_context_max_posts). */
                    max_thread_context_posts?: number;
                    /**
                     * @description Metadata paper lấy qua API từ SERVER (REQ-D32), không phải từ trình duyệt của collector.
                     * @constant
                     */
                    paper_metadata_source: "server_api";
                };
                /** @description Điều kiện dừng phải RÕ RÀNG (REQ-A7: X có thể hạn chế tài khoản dù người dùng tự giải CAPTCHA). */
                stop_conditions: {
                    /**
                     * @description Chạm ngưỡng nào TRƯỚC thì dừng theo ngưỡng đó; `limit_kind` ghi rõ ngưỡng nào (contracts/state/run.yaml §coverage_metadata).
                     * @constant
                     */
                    evaluation: "first_of_either";
                    /** @description PROVISIONAL 1800 giây (contracts/retry-policy.yaml §per_run_duration_limit). */
                    max_duration_s: number;
                    /** @description PROVISIONAL 200 (contracts/retry-policy.yaml §per_run_post_limit; REQ-OQ05 — Owner chốt số thật sau M0). */
                    max_posts: number;
                    /**
                     * @description Bị chặn ⇒ dừng và báo. KHÔNG luân chuyển account/proxy/fingerprint (SRC-SPEC §2.3, REQ-S9.3-02).
                     * @constant
                     */
                    on_blocked: "report_stop_and_halt_no_rotation";
                    /**
                     * @description Gặp CAPTCHA/hết phiên ⇒ gọi `worker.report_stop`, DỪNG. Không tự thử lại, không giả lập thao tác xác minh (REQ-S9.3-01, SRC-SPEC §2.3).
                     * @constant
                     */
                    on_challenge: "report_stop_and_halt";
                };
                /** @description Ảnh chụp CỦA SERVER về tiến độ ĐÃ ACK. Đây là nguồn sự thật khi worker claim lại (contracts/state/run.yaml §CP-02, I02). Rỗng-mới (sequence 0) cho một run chưa ingest gì. */
                server_checkpoint: {
                    /** @description Mọi post có `ingest_sequence <= giá trị này` ĐÃ COMMIT ở server. Đây là định nghĩa vận hành của 'đã ACK' (contracts/state/run.yaml §CP-02). */
                    acked_through_ingest_sequence: number;
                    /** @description `checkpoint.sequence` hiện hành. Append-only; seq lùi bị từ chối (§CP-04). */
                    checkpoint_sequence: number;
                    /** @enum {string} */
                    cursor_state: "valid" | "invalidated";
                    /** @description null hợp lệ khi con trỏ mất hiệu lực; khi đó `cursor_state = invalidated` và recovery policy cho phép ĐỌC LẠI — dedup xảy ra ở ingest theo `x_post_id` (AMD-B05). */
                    cursor_token: string | null;
                    items_ingested_total: number;
                    /** @enum {string} */
                    phase: "collecting" | "enriching" | "analyzing" | "reporting";
                };
                heartbeat_request: {
                    assignment_id: components["schemas"]["ulid"];
                    /** @description Epoch cũ ⇒ STALE_LEASE và KHÔNG đổi dữ liệu (contracts/ports.yaml worker.heartbeat). */
                    lease_epoch: number;
                    lease_id: components["schemas"]["ulid"];
                    /** @description QUAN SÁT của collector, KHÔNG phải dữ liệu authoritative. Server không ghi các số này vào bảng nghiên cứu. */
                    observed_progress: {
                        elapsed_s: number;
                        posts_seen_in_run: number;
                        posts_submitted_in_run: number;
                    };
                    request_id: components["schemas"]["ulid"];
                    schema_version: components["schemas"]["semver"];
                    /** @enum {string} */
                    x_session_state: "ok" | "challenge" | "expired" | "unknown";
                };
                heartbeat_response: {
                    /**
                     * @description `stop_cancelled`: Owner đã gọi `run.cancel` (contracts/state/run.yaml T-RUN-17b) — collector dừng ngay, không commit thêm. `stop_storage_unavailable`: xem contracts/state/storage.yaml.
                     * @enum {string}
                     */
                    directive: "continue" | "stop_cancelled" | "stop_storage_unavailable" | "stop_lease_revoked";
                    /** @description Hạn mới sau khi gia hạn. Vắng mặt khi `lease_valid = false`. */
                    lease_expires_at?: components["schemas"]["timestamp_utc_ms"];
                    lease_valid: boolean;
                    /** @enum {string} */
                    storage_health?: "healthy" | "write_blocked" | "maintenance" | "recovery_required";
                };
                release_request: {
                    /** @description Idempotency key (contracts/ports.yaml: trả lại nhiều lần không đổi trạng thái sau lần đầu). */
                    assignment_id: components["schemas"]["ulid"];
                    lease_epoch: number;
                    lease_id: components["schemas"]["ulid"];
                    /**
                     * @description Phần CHƯA ACK không được coi là đã lưu (contracts/ports.yaml worker.release_assignment, I02).
                     * @enum {string}
                     */
                    release_reason: "completed_phase" | "worker_shutdown" | "local_storage_unavailable";
                    request_id: components["schemas"]["ulid"];
                    schema_version: components["schemas"]["semver"];
                };
            };
        } & (unknown | unknown | unknown | unknown | unknown | unknown);
        /** @description ID post của X, dạng chuỗi số. ID truyền dưới dạng string (SRC-PLAN §5.1). */
        x_post_id: string;
    };
    responses: never;
    parameters: {
        /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
        CsrfTokenHeader: string;
        /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
        IdempotencyKeyHeader: components["schemas"]["IdempotencyKey"];
        /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
        RequestIdHeader: components["schemas"]["Ulid"];
        /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
        SchemaVersionHeader: components["schemas"]["SemVer"];
        /** @description Bí mật webhook. Sai ⇒ 401, không xử lý, không trả lời chat. */
        TelegramSecretHeader: string;
    };
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    "health.get_liveness": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Chỉ `up` + phiên bản schema; **không** lộ cấu hình, tên provider, chat ID hay bất kỳ dữ liệu nghiệp vụ nào. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.request_reanalysis": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description generation mới + task đã xếp hàng. */
            202: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.report_attempt_unknown": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Task đang giữ. */
                task_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Đã ghi nhận một lần thử KHÔNG RÕ KẾT QUẢ. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.heartbeat": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Task đang giữ. */
                task_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Lease còn hiệu lực hay không; lệnh hủy nếu có. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `WORKER_LEASE_EXPIRED`. */
            412: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.get_task_input": {
        parameters: {
            query: {
                /** @description Epoch hiện hành. */
                lease_epoch: number;
                /** @description Lease đang giữ. */
                lease_id: components["schemas"]["Ulid"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Task đang giữ. */
                task_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Nội dung nguồn kèm source ID/hash/evidence level, ranh giới dữ liệu rõ ràng; nội dung này là **dữ liệu**, không phải lệnh (SRC-SPEC §11.4). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.submit_result": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Task đang giữ. */
                task_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["analysis-result.schema"];
            };
        };
        responses: {
            /** @description Trạng thái commit + generation của kết quả. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["analysis-result.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `WORKER_LEASE_EXPIRED`. */
            412: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`, `AI_OUTPUT_INVALID`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "analysis.claim_task": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description task_id, task type, analysis_key, lease_id, lease_epoch, tham chiếu input. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`, `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "auth.login": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Đăng nhập thành công; server đặt cookie phiên HttpOnly và trả CSRF token. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionInfo"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "auth.logout": {
        parameters: {
            query?: never;
            header: {
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Phiên bị hủy; cookie bị xóa. */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "auth.get_session": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Trạng thái đăng nhập, thời điểm hết hạn; không có secret. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SessionInfo"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "backup.restore_snapshot": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Đã bắt đầu restore; `storage.health` chuyển `recovery_required`. */
            202: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RESTORE_UNVERIFIED`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "backup.reconcile_after_restore": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Restore cần đối soát. */
                restore_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Kết quả đối soát; danh sách delivery cũ bị hủy/giữ; lease bị thu hồi. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RESTORE_UNVERIFIED`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "backup.create_snapshot": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description snapshot_id, manifest (DB + schema version + hash + embedding artifacts/config), thời điểm. */
            202: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "backup.verify_snapshot": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Snapshot cần kiểm. */
                snapshot_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Kết quả integrity check + count/hash của Saved/report/ledger. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RESTORE_UNVERIFIED`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "data.purge_all": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Phase 1: `purge_challenge_id`, cụm từ phải gõ, thời điểm hết hạn. Phase 2: `purge_id`, số hàng đã xóa theo bảng, danh sách phạm vi **được loại trừ**. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CONFLICT`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "data.delete_target": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Target cần xóa dữ liệu gốc. */
                target_ref: components["schemas"]["TargetRef"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description `deletion_id`, số hàng đã xóa theo từng loại, và danh sách những gì **được giữ lại** (snapshot, ledger) để người dùng thấy rõ phạm vi. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CONFLICT`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "delivery.get_status": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Delivery hoặc report cần xem trạng thái gửi. */
                delivery_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Trạng thái aggregate + từng part: `pending | sending | sent | retry_wait | unknown | failed | cancelled`, số attempt, thời điểm. Bốn trạng thái incomplete/empty/failed/unknown hiển thị riêng (I13). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "delivery.decide_unknown": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Part đang ở trạng thái `unknown`. */
                delivery_part_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Trạng thái part sau quyết định. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`, `TELEGRAM_SEND_UNCERTAIN`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "health.get_readiness": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Trạng thái từng module theo định nghĩa readiness ở contracts/ops/deployment.md: storage health, scheduler, dispatcher (có bị khóa vì recovery không), embedding generation, connector nguồn, worker online/offline. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "identity.resolve_conflict": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Xung đột định danh cần Owner xử lý. */
                conflict_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Kết quả merge, danh sách reference/first-announcement/Saved đã chuyển. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "ingest.submit_batch": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ingest-batch.schema"];
            };
        };
        responses: {
            /** @description Receipt của lô đã COMMIT (`status: committed`), hoặc receipt cũ được trả nguyên vẹn (`status: duplicate_replay`). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ingest-receipt.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `WORKER_LEASE_EXPIRED`. */
            412: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "ingest.commit_checkpoint": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["checkpoint_only_request"];
            };
        };
        responses: {
            /** @description Receipt `receipt_kind: checkpoint_only` với con trỏ đã lưu. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ingest-receipt.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "ingest.get_receipt": {
        parameters: {
            query: {
                /** @description Assignment đã tạo lô. */
                assignment_id: components["schemas"]["Ulid"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Khóa của lô cần tra. */
                idempotency_key: components["schemas"]["IdempotencyKey"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Receipt đã commit, hoặc `not_committed` nếu server CHƯA TỪNG commit key đó. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ingest-receipt.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "report.list": {
        parameters: {
            query?: {
                /** @description Con trỏ trang. */
                cursor?: string;
                /** @description Số report tối đa. */
                limit?: components["schemas"]["PageLimit"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Ngày, coverage `[from, to)`, số mục, số hướng nổi, quality. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["report.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "report.get": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Report cần xem. */
                report_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Khối "hướng đang nổi" (nhãn "ứng viên để đọc sâu"), danh sách mục + summary, tag_config_version đã dùng, coverage, quality + danh sách pending, ghi chú đợt dừng sớm nếu có. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["report.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "run.list": {
        parameters: {
            query?: {
                /** @description Con trỏ trang. */
                cursor?: string;
                /** @description Số run tối đa. */
                limit?: components["schemas"]["PageLimit"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Mỗi run: phase, status, outcome, stop_reason, trigger_type, tiến độ. Ba trạng thái `empty`, `stopped/limit`, `failed` hiển thị khác nhau (SRC-SPEC §8.3, I13). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED_COMMAND`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "run.get": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Run cần xem. */
                run_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description trigger_type, cấu hình đã áp, số bài lấy, số bài mới, checkpoint đã ACK, lỗi, log **đã che secrets**. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "run.cancel": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Run chưa kết thúc. */
                run_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Trạng thái run sau khi hủy. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "run.resume": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Run đang `needs_user`. */
                run_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Trạng thái run sau khi chuyển về `queued`. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CONFLICT`, `STALE_LEASE`, `X_CHALLENGE_REQUIRED`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "run.run_now": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Trả run đã xếp hàng, HOẶC run đang chạy hiện có (chính sách COALESCE). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `UNAUTHORIZED_COMMAND`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "save.list": {
        parameters: {
            query?: {
                /** @description Con trỏ trang. */
                cursor?: string;
                /** @description Số mục tối đa. */
                limit?: components["schemas"]["PageLimit"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Bài đã Save, ngày lưu, snapshot, nguồn Save. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["saved-snapshot.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "save.create": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description saved_item_id + trạng thái (`created` | `already_saved`) + ngày lưu. */
            201: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["saved-snapshot.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `UNAUTHORIZED_COMMAND`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CONFLICT`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "save.remove": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Target đã Save. */
                target_ref: components["schemas"]["TargetRef"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Xác nhận đã bỏ lưu. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["saved-snapshot.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "save.export": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Tệp export chứa snapshot đã lưu. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["saved-snapshot.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "secret.issue_task_credential": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Credential **chỉ của provider gắn với task đó**, có hạn ngắn. Không trả toàn bộ key store, không trả key của provider khác. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "settings.get_config": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Cấu hình đầy đủ với secret ở dạng **tham chiếu + trạng thái đã cấu hình**, không bao giờ là giá trị key (SRC-SPEC §11.2). Kèm timezone IANA đang dùng (B08). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "settings.update_config": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Cấu hình sau khi ghi, secret vẫn ở dạng tham chiếu. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "settings.test_provider": {
        parameters: {
            query?: never;
            header: {
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Tên provider đã cấu hình. */
                provider_name: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Kết quả `usable | unusable | unknown` kèm lý do đã che secrets. Đường CLI/ACP **không** thử được từ server; trạng thái của nó chỉ đến từ worker.register_capabilities trên máy cá nhân. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `AI_PROVIDER_UNAVAILABLE`. */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.list": {
        parameters: {
            query?: {
                /** @description Con trỏ trang. */
                cursor?: string;
                /** @description Số mục tối đa. */
                limit?: components["schemas"]["PageLimit"];
            };
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Tag + alias + exclusion + phiên bản cấu hình tag đang hoạt động. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.create": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Tag đã tạo + tag_config_version mới. */
            201: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`, `EMBEDDING_GENERATION_MISMATCH`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.delete": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Tag cần bỏ. */
                tag_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description tag_config_version mới. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.update": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Tag cần sửa. */
                tag_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Tag sau khi sửa + tag_config_version mới. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.preview_matches": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Danh sách nhãn khớp + điểm tương đồng + embedding generation đã dùng. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `EMBEDDING_GENERATION_MISMATCH`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "tag.rescan_corpus": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Đã nhận yêu cầu quét lại kho. Đây là COMMAND RIÊNG với ledger riêng; KHÔNG reset first-announcement hay coverage chính (SRC-PLAN §9.2). */
            202: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "telegram.unlink": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Trạng thái liên kết sau khi hủy. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "telegram.issue_link_code": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description Double-submit CSRF; phải khớp cookie `rr_csrf`. Chỉ xuất hiện trên MUTATION dùng phiên owner. Thiếu/lệch ⇒ 403 `CSRF_REJECTED`. */
                "X-CSRF-Token": components["parameters"]["CsrfTokenHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Mã một lần + thời điểm hết hạn. */
            201: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `CSRF_REJECTED`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "telegram.receive_update": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
                /** @description Bí mật webhook. Sai ⇒ 401, không xử lý, không trả lời chat. */
                "X-Telegram-Bot-Api-Secret-Token": components["parameters"]["TelegramSecretHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description LUÔN 204 với mọi update hợp lệ về mặt transport — kể cả update bị bỏ im lặng. */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED_COMMAND`, `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.heartbeat": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Assignment đang giữ. */
                assignment_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["heartbeat_request"];
            };
        };
        responses: {
            /** @description Lease còn hiệu lực hay không, lệnh dừng nếu owner đã cancel. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["heartbeat_response"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `WORKER_LEASE_EXPIRED`. */
            412: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.release_assignment": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Assignment cần trả. */
                assignment_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["release_request"];
            };
        };
        responses: {
            /** @description Lease đã thu hồi. Phần CHƯA ACK không được coi là đã lưu (I02). */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.report_stop": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Assignment đang giữ. */
                assignment_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["StopReport"];
            };
        };
        responses: {
            /** @description Server đã ghi nhận điểm dừng; response nêu trạng thái run và có tạo alert intent hay không. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STALE_LEASE`, `SOURCE_LAYOUT_CHANGED`, `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.claim_assignment": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["claim_request"];
            };
        };
        responses: {
            /** @description Assignment kèm lease/epoch và checkpoint ĐÃ ACK; hoặc `no_work` khi không có việc (không phải lỗi). */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["worker-assignment.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`, `STALE_LEASE`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.register_capabilities": {
        parameters: {
            query?: never;
            header: {
                /** @description Khóa chống trùng do client cấp; phạm vi khóa nằm ở `x-idempotency.key_scope` của từng operation. Cùng key + cùng payload_hash ⇒ trả kết quả đã commit. Cùng key + payload khác ⇒ 409 `IDEMPOTENCY_CONFLICT`, KHÔNG ghi đè (SRC-PLAN §5.1). */
                "Idempotency-Key": components["parameters"]["IdempotencyKeyHeader"];
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["GenericObject"];
            };
        };
        responses: {
            /** @description Xác nhận đăng ký + thời điểm server ghi nhận + chu kỳ heartbeat yêu cầu. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `IDEMPOTENCY_CONFLICT`. */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `VALIDATION_ERROR`. */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `RATE_LIMITED`. */
            429: {
                headers: {
                    /** @description Giây do nguồn/API chỉ định. Giá trị này THẮNG mọi backoff cấu hình. */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `STORAGE_WRITE_FAILED`. `storage.health = write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi (SRC-PLAN §8.4, I02). */
            503: {
                headers: {
                    /** @description Giây. Gợi ý theo `storage_recovery_probe` (30 s). */
                    "Retry-After"?: number;
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "worker.get_status": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Với từng worker: kind, online/offline theo ngưỡng heartbeat (xem contracts/ops/deployment.md), last_seen_at, capability đã khai, `x_session_state`, danh sách provider `usable|unusable|unknown`. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["GenericObject"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    "work.get_detail": {
        parameters: {
            query?: never;
            header: {
                /** @description ID của LẦN GỌI này. Một retry sinh `X-Request-Id` MỚI nhưng GIỮ NGUYÊN `Idempotency-Key` — đó là cách server phân biệt replay với một yêu cầu mới. */
                "X-Request-Id": components["parameters"]["RequestIdHeader"];
                /** @description Phiên bản wire schema của request. KHÔNG dùng 'latest' (SRC-PLAN §5). Lệch major ⇒ 422 `VALIDATION_ERROR` với `details_safe.violation_kind = schema_version_unsupported`. */
                "X-Schema-Version": components["parameters"]["SchemaVersionHeader"];
            };
            path: {
                /** @description Work cần xem. */
                work_id: components["schemas"]["Ulid"];
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Summary + nhãn mức độ đọc + nhãn chủ đề + tag khớp + danh sách post dẫn + paper/DOI + lịch sử phân tích (mọi generation) + mục liên quan đã báo cáo kèm ngày. */
            200: {
                headers: {
                    /** @description Phiên bản schema của response. */
                    "X-Schema-Version"?: components["schemas"]["SemVer"];
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["target.schema"];
                };
            };
            /** @description Lỗi: `UNAUTHORIZED`. */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `FORBIDDEN_EDGE`. */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `NOT_FOUND`. */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Lỗi: `INTERNAL`. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
}
