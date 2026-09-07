# `tests/` — Python contract and integration tests

Hai thư mục, đúng theo `agent-tasks/README.md` §5.3:

| Thư mục | Nội dung |
| --- | --- |
| `tests/contract/` | E1 — kiểm một hợp đồng đơn lẻ (schema, allowlist, ma trận scheme) trên fixture |
| `tests/integration/` | E1/E2 — kiểm một hành vi xuyên module, kể cả tiêm lỗi (crash, disk-full, lease đôi) |

Ở Giai đoạn 0 hai thư mục này **rỗng**: chưa card nào chạy. Tệp duy nhất có nội dung là
`tests/conftest.py`, thứ mà mọi card Giai đoạn 1 sẽ dùng.

---

## 1. Quy tắc không thương lượng: fixture **là** oracle

`docs/master-plan.md` §2.3 và SRC-PLAN §15: test **nạp thẳng** `acceptance/fixtures/**`.

- **Không có bộ dữ liệu test thứ hai.** Không sinh dữ liệu giả trong test, không sao chép
  một fixture vào `tests/`.
- **Sửa fixture để test pass là vi phạm.** Nếu fixture sai, đó là một change request theo
  `precode/change-control.md`, không phải một lần sửa trong nhánh của card.
- Fixture nằm dưới `acceptance/` — **read-only** với mọi card triển khai.

Chín thư mục fixture (`evidence/tools/README.md` §4): `ai`, `boundary`, `collection`,
`e2e`, `identity`, `recovery`, `reporting`, `telegram`, `ui`.

---

## 2. Hợp đồng của fixture loader

`tests/conftest.py` cung cấp ba pytest fixture. Chúng là **session-scoped** và chỉ đọc.

| Tên | Kiểu | Dùng để |
| --- | --- | --- |
| `fixture_loader` | `(ref: str) -> Fixture` | nạp một file, `"identity/pos-ingest-batch-valid"` |
| `fixture_directory_loader` | `(dir: str) -> list[Fixture]` | nạp cả thư mục, đã sắp xếp |
| `fixture_root` | `pathlib.Path` | đường dẫn `acceptance/fixtures/` |

`ref` chấp nhận `"<thư mục>/<tên>"` (không đuôi `.json`), hoặc tên trần khi tên đó là duy
nhất trên cả chín thư mục. Tên trần trùng nhau ⇒ `FixtureNotFound` **kèm danh sách ứng
viên**, không phải một lựa chọn ngầm.

### `Fixture`

| Thành viên | Trả về | Khi thiếu |
| --- | --- | --- |
| `.ref`, `.path`, `.data` | định danh, đường dẫn, JSON thô | — |
| `.given` / `.expected` | `dict` khối tương ứng | `FixtureShapeError` |
| `.events` | `list[dict]` | `FixtureShapeError` |
| `.scenario_refs` | `list[str]` (gộp `scenario_ref` và `scenario_refs`) | `[]` |
| `.rows(entity, block="given")` | `list[dict]` của `<block>.rows.<entity>[]` | `FixtureShapeError` |
| `.entities(block="given")` | tên entity có trong khối | `[]` |

**Vì sao thiếu khối là lỗi chứ không phải danh sách rỗng.** Hai thư mục `collection/` và
`recovery/` nêu oracle bằng **văn xuôi** (`durable_rows_expected`, `expected_target_state`)
chứ không bằng `rows`. `evidence/tools/README.md` §5.1 ghi thẳng rằng E0 **không đo được**
chúng và báo `NOT_APPLICABLE_FREEFORM` chứ không báo sạch. Nếu `.rows()` trả `[]` ở đó thì
một test sẽ **pass vì không assert gì**. Loader vì vậy ném lỗi, và card phải đọc oracle văn
xuôi một cách tường minh.

### Ví dụ

```python
def test_ingest_replay_is_idempotent(fixture_loader):
    fx = fixture_loader("identity/f-ingest-replay-idempotent")
    assert "SC13" in fx.scenario_refs
    for event in fx.events:
        ...                      # drive the system under test
    assert len(fx.rows("work", block="expected")) == 1
```

---

## 3. Chạy

```bash
uv sync --all-packages
PYTHONDONTWRITEBYTECODE=1 uv run pytest            # cả cây Python
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests      # chỉ tests/
```

`pythonpath` và `testpaths` khai ở `pyproject.toml` gốc. Gốc repo là import root, nên
`server/app/...` import là `server.app....`, `collector/app/...` là `collector.app....`
— ba gói `app` không đụng nhau trên cùng một `sys.path`.

**Đường dẫn file mà card pin ở §3 không đổi vì điều này.**

---

## 4. Giới hạn đã biết ở Giai đoạn 0

- Loader **chưa có test của chính nó trong CI**: write set của `PKT-P0-SKELETON` chỉ gồm
  `tests/README.md` và `tests/conftest.py`, không gồm một `tests/test_*.py`. Nó đã được
  chạy tay trên fixture thật (xem `evidence/handoffs/P0-skeleton-handoff.md`,
  `EV-P0-08`), nhưng đó là `SELF_VALIDATION` một lần, không phải một cửa hồi quy. Card đầu
  tiên của Giai đoạn 1 dùng loader sẽ biến nó thành cửa thật.
- Không có `tests/unit/`. `agent-tasks/README.md` §5.3 nêu `contract/`, `unit/`,
  `integration/` ở một chỗ và `contract/` + `integration/` ở chỗ khác; §3 của cả 18 card
  chỉ dùng hai thư mục sau. Thư mục `unit/` sẽ được tạo bởi card đầu tiên thực sự cần nó.
