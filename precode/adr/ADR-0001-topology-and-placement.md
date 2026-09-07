---
adr_id: ADR-0001
title: Topology và nơi chạy từng module
status: proposed
decision_owner: Owner
date: 2026-09-06
blocker_refs: [B12]
source_refs: [SRC-SPEC §3.1, SRC-SPEC §3.2, SRC-SPEC §6.1, SRC-SPEC §6.2, SRC-SPEC §6.4, SRC-PLAN §3, SRC-PLAN §6, SRC-PLAN §6.1]
requirement_refs: [REQ-D06, REQ-D08, REQ-D09, REQ-D42, REQ-D50, REQ-D11, REQ-D32, REQ-S6.1-01, REQ-S6.1-02, REQ-S6.1-03, REQ-S6.2-01, REQ-S6.4-02, REQ-S6.4-03, REQ-OQ01]
invariant_refs: [I01, I02, I10, I11]
amendment_refs: [AMD-B12]
decision_refs: [B12, AMD-B12]
consumers: [PC01, PC05, PC06]
affected_packages: [PC01, PC05, PC06]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0001 — Topology và nơi chạy từng module

## Bối cảnh

Bốn quyết định bố trí module của đặc tả đều còn **ĐX**: D08 (collector đẩy dữ liệu qua API có xác thực), D09 (Chrome profile riêng của dự án), D42 (bước LLM chạy cùng máy collector), D50 (embedding chạy ở server). Đồng thời sơ đồ SRC-SPEC §6.2 vẽ cạnh `COL --> AW`: collector đưa dữ liệu **thẳng** cho analysis worker trên máy cá nhân. Cạnh này mâu thuẫn trực tiếp với D08 và cho phép phân tích chạy trên dữ liệu chưa commit.

SRC-PLAN §6 yêu cầu một bảng ranh giới quyền với **default deny**: mọi edge không có trong registry bị cấm. Không thể lập bảng đó khi bốn quyết định trên còn mở.

## Quyết định

1. **Máy cá nhân** chạy: X collector, analysis worker, AI adapter. Cả ba cài như tiến trình trên máy, **không** trong container, vì Chrome phải hiện cửa sổ cho người dùng bấm và CLI/ACP cần phiên đăng nhập của người dùng.
2. **Server** chạy: web app, backend và API, job queue, data store SQLite, embedding service, report builder, Telegram adapter, research connector (arXiv/OpenAlex).
3. Collector chỉ có **một đường ra duy nhất**: Worker API của backend. Không ghi SQLite, không gọi Telegram, không giữ secret AI, không đẩy việc thẳng cho analysis worker.
4. Analysis worker **nhận task từ server sau ingest commit** và submit kết quả qua Analysis API. Cạnh `COL --> AW` của SRC-SPEC §6.2 bị xóa (AMD-B12).
5. Chrome dùng **profile riêng của dự án**, không phải profile mặc định. Cổng debug chỉ bind loopback.
6. Embedding chạy ở server bằng model local; adapter API/CLI **không** được dùng cho embedding.
7. Mọi edge không nằm trong `contracts/modules.yaml` bị cấm (default deny) và phải có negative case.

## Trạng thái

`proposed`. Owner phải chốt hai điểm: (a) xác nhận D09 — đây chính là REQ-OQ01 và nó **chặn M0**; (b) chấp nhận xóa cạnh `COL --> AW`. Trạng thái chỉ đổi khi có quyết định của Owner kèm authority ref.

## Hệ quả

### Tích cực
- Mọi input của analysis đều đã có canonical id và đã commit, nên I02 giữ được và kết quả phân tích luôn gắn được vào dữ liệu authoritative.
- Một owner duy nhất cho mỗi mutation: backend domain sở hữu identity, tag version, Saved, report và state transition.
- Phiên X và phiên CLI không bao giờ rời máy cá nhân, giảm bề mặt rủi ro của server.

### Tiêu cực và chi phí
- Thêm một vòng mạng: dữ liệu đi collector → server → (task) → analysis worker, thay vì đi thẳng trong máy. Với khối lượng một người dùng, chi phí này chấp nhận được nhưng phải đo trong M1.
- Analysis worker phải chịu được việc server offline: task chỉ được claim khi kết nối được.
- Profile Chrome riêng nghĩa là người dùng phải đăng nhập X thêm một lần và duy trì một profile nữa.

### Bất biến được giữ
I01 (mutation chỉ qua domain port đã xác thực), I02 (ACK sau commit), I10 (worker stale không commit), I11 (nội dung nguồn không đọc được secret).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Giữ cạnh `COL --> AW` như sơ đồ §6.2 | Ít vòng mạng, phân tích bắt đầu sớm hơn | Phân tích chạy trên dữ liệu chưa commit; không có canonical id; phá I02 và D08 | Không có cách gắn kết quả vào dữ liệu authoritative một cách xác định |
| Đưa analysis worker lên server | Một nơi chạy, dễ vận hành | Đường CLI/ACP cần phiên đăng nhập của người dùng, không tồn tại trên server; phá D41 và D51 | Loại bỏ một trong hai họ provider đã được xác nhận |
| Dùng profile Chrome mặc định của người dùng | Không phải đăng nhập lại | Trộn phiên cá nhân với phiên tự động; rủi ro tài khoản và rò rỉ cookie sang server backup | Trái tinh thần §11.2 về tách phiên X |
| Embedding chạy ở máy cá nhân | Cùng chỗ với analysis worker | Máy cá nhân có thể tắt; report builder ở server sẽ không tính được selection | Selection phải chạy được khi máy cá nhân offline |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.1 (D06, D08, D42, D50), §3.2 (D09, D32), §6.1, §6.2, §6.4; SRC-PLAN §3 hàng B12, §6, §6.1.
- Oracle bị ảnh hưởng: thêm negative case "collector gọi thẳng analysis worker bị từ chối"; REQ-AC16 kiểm bằng capability run không phát sinh route ngoài cấu hình.
- Amendment: AMD-B12 (xóa cạnh `COL --> AW`).
- Nếu Owner bác bỏ D09: M0 ở lại BLOCKED; xem `precode/owner-decision-request.md` §B12.
