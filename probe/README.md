# `probe/` — kịch bản probe khả thi SP1

**Chưa có code ở đây, và đó là đúng.**

Thư mục này thuộc về card [`agent-tasks/TC-x-feasibility-probe.md`](../agent-tasks/TC-x-feasibility-probe.md)
(milestone M0, cổng **SP1**). Giai đoạn 0 chỉ tạo chỗ đứng cho nó; không viết một dòng
probe nào.

## Vì sao trống

Probe SP1 là **thao tác sống trên X bằng máy và tài khoản của Owner**. Nó không được chạy
trước khi bốn xác nhận ở `contracts/ops/collector-probe.md` §6 được Owner mở — cổng đó nằm
**trước** khi probe chạy, không phải sau. Viết sẵn code probe ở đây sẽ tạo ra một thứ chạy
được trước khi cổng mở, và đó chính là rủi ro cổng dựng lên để chặn.

Ngoài ra: cổng SP1 hiện `NOT_MET` và bằng chứng probe là `NOT_RUN`
(`docs/master-plan.md` §1.3). Hai từ đó khác nhau — một là từ vựng của cổng, một là của
bằng chứng — và Giai đoạn 0 không đổi được từ nào.

## Card sẽ tạo gì

Theo §3 của card:

| Đường dẫn | Vai trò |
| --- | --- |
| `probe/x_feasibility/run_probe.py` | chạy một đợt probe theo biểu mẫu §5 của card |
| `probe/x_feasibility/record.py` | ghi mỗi đợt thành JSONL đã che danh tính |

Đầu ra **không** phải code: nó là bằng chứng ở `evidence/runs/SP1-x-feasibility/`
(JSONL mỗi đợt, log đã che, manifest).

## Điều tuyệt đối không được làm

`docs/master-plan.md` §3 Giai đoạn 2A nói thẳng: mọi hành vi né CAPTCHA hay che giấu danh
tính làm card **FAIL ngay**, bất kể kết quả thu được. Bị chặn ⇒ **dừng và báo**; no-go ⇒
báo blocked cho nguồn X, **không** tự chuyển sang X API trả phí.

Ngôn ngữ: Python (`agent-tasks/README.md` §5.3).
