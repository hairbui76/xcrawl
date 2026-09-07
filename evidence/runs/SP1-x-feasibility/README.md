# `evidence/runs/SP1-x-feasibility/` — kết quả probe SP1

> **Chưa có đợt nào chạy.** Thư mục này trống về bằng chứng, và đó là trạng thái đúng tại
> 2026-09-07. `runs.jsonl` **chưa tồn tại**; file duy nhất mang hình dạng bản ghi ở đây là
> `TEMPLATE-run-record.json`, và nó là **biểu mẫu**, không phải một đợt.
>
> Trạng thái bằng chứng của mọi con số về khả thi nguồn X: **`NOT_RUN`**.

Hai điều chặn, cả hai đều nằm ngoài tay Worker:

1. **Cổng Owner** — `contracts/ops/collector-probe.md` §6 đòi bốn xác nhận bằng văn bản
   trước khi đợt đầu tiên chạy. Mục 1 (D09) đã được trả lời (`OD-20260907-01`); **mục 2, 3
   và 4 vẫn `OWNER_DECISION_REQUIRED`** (`OD-20260907-03`, "Not decided in this round").
2. **Máy của Owner** — probe chạy trên Chrome thật, profile riêng của dự án, tài khoản X
   thật của Owner (REQ-D09, `ADR-0001`). Không môi trường CI hay agent nào chạy được nó,
   và không được phép thử.

`probe/x_feasibility/run_probe.py` **từ chối mở trình duyệt** khi cổng §6 chưa đủ bốn xác
nhận. Cổng nằm trong code chứ không chỉ trong tài liệu, vì một cổng chỉ có trong văn xuôi là
cổng không ai kiểm được.

## File trong thư mục này

| File | Sinh bởi | Ý nghĩa |
| --- | --- | --- |
| `README.md` | người | file này |
| `TEMPLATE-run-record.json` | người | biểu mẫu §5: tên trường + ràng buộc. **Không phải một đợt.** Giá trị là chỗ trống có nhãn |
| `runs.jsonl` | probe | *(chưa tồn tại)* mỗi dòng một đợt, đúng hình dạng §5 |
| `probe.log` | probe | log đã che danh tính (`RedactingFormatter`) |
| `seen-post-ids.sha256` | probe | sổ **digest sha256** của `x_post_id` đã gặp, để tính `posts_new_vs_previous_runs` giữa các đợt |

Vì sao sổ chỉ chứa digest: §5 cần con số "bao nhiêu bài chưa từng thấy ở đợt trước", tức cần
trí nhớ xuyên đợt — nhưng **không** cần chính các id. Digest đủ trả lời "đã gặp chưa?" và vô
dụng cho việc dựng lại ai đăng gì.

## Vì sao không có bản ghi nào được viết tay ở đây

Một dòng trong `runs.jsonl` là một phép đo trên tài khoản X thật. Viết tay một dòng như vậy
— kể cả "để test cho đủ" — là **bằng chứng giả**, và `contracts/ops/collector-probe.md` §2
nói thẳng lý do: một probe đo "lấy được bao nhiêu bài" tạo áp lực tự nhiên lên chính ranh
giới của nó. Dữ liệu tổng hợp dùng cho test nằm ở `tests/contract/test_x_probe_go_no_go.py`,
trong bộ nhớ của test, và không bao giờ chạm thư mục này.

`probe/x_feasibility/record.py` từ chối ghi một bản ghi không thỏa §5, nên một dòng ở đây
hoặc là một đợt thật hợp lệ, hoặc không tồn tại.

## Khi đã có đợt

```bash
# Tính go/no-go theo §7 (nguyên văn, không nới)
uv run python probe/go_no_go.py evidence/runs/SP1-x-feasibility/runs.jsonl
```

Mã thoát: `0` GO · `1` NO-GO · `2` KHÔNG KẾT LUẬN · `3` không đọc được file.

Kết luận GO chỉ có nghĩa *"nguồn X khả thi ở mức ngân sách đã thử, trong cửa sổ đã đo"*. Nó
**không** nói nguồn X ổn định lâu dài (REQ-A7 vẫn `KC`), **không** nói collector đã hoạt
động, **không** nói AC-01/AC-04 đã pass. Danh sách đầy đủ những điều probe này không chứng
minh nằm ở `contracts/ops/collector-probe.md` §10.
