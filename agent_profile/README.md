# Bộ agent_profile — Research Radar

Phiên bản 1.0 · 06/09/2026 · Trạng thái tài liệu: **DRAFT_FOR_REVIEW**.

Bộ hồ sơ này quy định ai được quyết định, ai được ghi, ai được kiểm tra và bằng chứng nào cần có. Đây là hợp đồng điều hành agent phát triển; **Worker ở đây không phải analysis worker hay collector trong sản phẩm Research Radar**. Bộ này không thay capability/module contract của sản phẩm.

## Bắt đầu sử dụng

1. Owner giao mục tiêu cho Coordinator; dùng nguyên hồ sơ `coordinator.md`, kèm `protocol.md`, `registry.json`, trạng thái và baseline nguồn đã pin.
2. Coordinator đọc trạng thái thực, authority, dependencies, risk/uncertainty; tạo TASK_PACKET trong thông điệp. Chỉ Coordinator dispatch Worker hoặc Auditor. Owner chat không spawn Worker/Specialist/Auditor trực tiếp.
3. Worker nhận `worker.md`, packet, nguồn đúng hash, authority chain và lease riêng. Thiếu một điều kiện thì dừng trước mutation. Mọi file mới, state file, log, handoff, manifest, archive hoặc upload đều cần Worker cùng grant thích hợp.
4. Worker kiểm tra thay đổi trong scope, chạy validation được cho phép, trả HANDOFF qua thông điệp và nhả lease. Self-check không phải independent audit.
5. Coordinator kiểm stop gates, thu hồi lease/đợi acknowledgment hoặc dùng runtime fencing đủ mạnh, freeze candidate đầy đủ cùng dependency và evidence. Coordinator quyết định route audit theo tiêu chí ở protocol.
6. Nếu cần, Auditor nhận `auditor.md` và exact frozen snapshot, chỉ trả AUDIT_REPORT qua thông điệp. Sửa finding là một packet Worker mới, baseline mới, lease mới; sau đó freeze và kiểm chứng lại.
7. Coordinator chỉ báo claim bằng mức đã được bằng chứng hỗ trợ. Owner quyết định vấn đề trọng yếu qua OWNER_DECISION_REQUEST; không hỏi lại quyền soạn bộ hồ sơ đã được cấp.

## Các file

| File | Vai trò |
| --- | --- |
| coordinator.md | Hồ sơ điều phối, dispatch và stop gates |
| worker.md | Hồ sơ duy nhất được ghi vật lý |
| auditor.md | Hồ sơ thanh tra độc lập, chỉ đọc |
| protocol.md | Authority, lease, freeze, handoff, finding và completion |
| registry.json | Quyền/đường giao tiếp và baseline nguồn |
| packets.schema.json | JSON Schema Draft 2020-12 cho thông điệp |
| examples.json | Ví dụ synthetic, không có quyền thực thi; positive/negative fixtures |

Profile là chỉ dẫn cho agent, **không phải sandbox, khóa filesystem hoặc lease service đã triển khai**. Runtime vận hành phải có identity xác thực, quyền tool/OS, authority registry, exclusive leases với fencing và audit log. Nếu không kiểm chứng được những guard này thì operational mutation phải BLOCKED. `DOCUMENTARY_DRAFT` chỉ dành cho một phiên soạn tài liệu mà Owner đã cấp rõ và Coordinator theo dõi lease bằng thông điệp; không được dùng làm đường dự phòng cho code sản phẩm hay side effect. Phiên tạo bộ tài liệu này dùng cơ chế đó; chưa chứng minh enforcement runtime.

## Trạng thái và giới hạn thật

- Nguồn: đặc tả v0.2 và kế hoạch Pre-code v0.1; đường dẫn, byte count, SHA-256 ở registry.
- Trạng thái sản phẩm vẫn **NOT_READY_FOR_PRODUCT_CODE**; B01–B17 giữ **OPEN**. Bộ profiles không chốt stack, topology, tag freeze, delivery policy hay backup strategy.
- Specialist chưa enabled. Khi cần, Coordinator phải có profile read-only đã được Owner/authority phù hợp chấp nhận; không đổi tên Specialist thành Worker để lách quyền.
- Schema validation chỉ chứng minh cấu trúc; authority, danh tính, thời gian, lease overlap, hash, independence và tool side effects cần runtime guards riêng.
- Kết quả validation/audit thực tế nằm trong handoff/thông điệp của phiên giao việc. Không suy ra PASS từ việc có file example. Khi snapshot đổi, bằng chứng liên quan thành STALE.
- `CONTRACT_READY` chỉ áp dụng phạm vi đã đóng blocker và có validation/evidence; không được suy ra `IMPLEMENTATION_VERIFIED`, `LIVE_FEASIBILITY_VERIFIED` hay `PRODUCT_ACCEPTED`.

## Ví dụ thao tác tối thiểu

Owner: “Soạn contract X trong file đã chỉ định theo baseline Y.” Coordinator kiểm authority rồi giao một Worker với exact allowlist, byte regions, stop gates và lease. Worker trả hash/byte count và bằng chứng. Với sửa chính tả thuần túy, scope nhỏ, oracle trực tiếp và uncertainty thấp, Coordinator có thể ghi `NO_INDEPENDENT_AUDIT` kèm lý do/authority/rủi ro còn lại. Với hợp đồng quyền ghi như bộ này, rủi ro lan rộng và residual uncertainty về privilege/lease khiến independent audit được route trước claim contract-ready.

Mọi example dùng workspace giả `/example/research-radar` và authority **NONEXECUTABLE_EXAMPLE**. Không copy ID, lease hay timestamp trong example để cấp quyền thực tế.
