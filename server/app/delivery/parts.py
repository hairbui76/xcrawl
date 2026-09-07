"""``ENT-delivery-part``: part index, payload hash, per-part receipt, and the split rule.

Three separable things live here, and only these three:

* **Splitting** a plain-text digest into parts (``contracts/telegram/delivery.md`` §3.5).
* **Hashing** a part payload (``entities.yaml`` §conventions: ``sha256:`` + 64 lowercase hex).
* **Deriving** the aggregate ``delivery.state`` from its parts (``DP-03`` precedence).

Why the split rule counts the way it does
-----------------------------------------
``contracts/telegram/delivery.md`` §3.4 pins exactly one length fact as ``DOCS_derived`` --
*"1-4096 characters"* for ``sendMessage.text`` -- and then says three things that number does
**not** settle. The one that reaches this module is (c): the counting *unit* (Unicode
scalars, or UTF-16 code units) has no source, so an emoji or any character outside the BMP
may count once or twice. §3.4 forbids writing a margin number into the contract while the
source is unread, so this module does not invent one either. Instead
:func:`message_length` reports the **larger** of the two readings and the limit is applied
to that: a part that fits under the pessimistic reading fits under both. That is a
one-directional safe inference, not a guess about the number.

``parse_mode`` is never set (§3.4, three ``KC`` rows; §3.3's safe branch), so escaping cannot
lengthen the string after this measurement: what is counted is what is sent.

What splitting deliberately does not do
---------------------------------------
It never cuts inside an item (§3.5), and a block that is too large on its own raises rather
than being halved -- §3.5 says an oversized item is truncated by its *builder* with a deep
link, which is ``MOD-report-service``'s decision and not this module's. Silently splitting
one item across two messages would show the reader half an item, which §3.5 forbids in the
same sentence.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from rr_contracts.generated.states import DeliveryPartState, DeliveryState

#: ``contracts/telegram/delivery.md`` §3.4, row "Độ dài tối đa một tin", status
#: ``DOCS_derived`` (read 2026-09-08 from ``core.telegram.org/bots/tutorial``): *"A String
#: object containing the message text, 1-4096 characters."* It expires when Telegram changes
#: policy, not when someone changes their mind.
MAX_MESSAGE_LENGTH = 4096

#: Separator between blocks inside one part. A blank line: plain text, no markup.
BLOCK_SEPARATOR = "\n\n"

#: ``DP-03`` precedence, most-attention-needed first. The order IS the invariant: taking the
#: last part's state instead would let the UI say "sent" while a part is still ``unknown``,
#: which is the counterexample ``contracts/state/delivery.yaml`` §invariants_owned/I13 names.
AGGREGATE_PRECEDENCE: tuple[DeliveryState, ...] = (
    DeliveryState.UNKNOWN,
    DeliveryState.FAILED,
    DeliveryState.RETRY_WAIT,
    DeliveryState.SENDING,
    DeliveryState.PENDING,
    DeliveryState.SENT,
)

#: ``delivery_part_state`` -> the aggregate state that part contributes. ``retry_wait`` has
#: no part-level member (``contracts/state/delivery.yaml`` §enums), so it is contributed by
#: the delivery row itself; see :func:`aggregate_state`.
_PART_TO_AGGREGATE: dict[DeliveryPartState, DeliveryState] = {
    DeliveryPartState.PENDING: DeliveryState.PENDING,
    DeliveryPartState.SENDING: DeliveryState.SENDING,
    DeliveryPartState.SENT: DeliveryState.SENT,
    DeliveryPartState.UNKNOWN: DeliveryState.UNKNOWN,
    DeliveryPartState.FAILED: DeliveryState.FAILED,
}


class PartTooLarge(ValueError):
    """One block does not fit in a single message even alone.

    Raised instead of splitting it: ``contracts/telegram/delivery.md`` §3.5 assigns the
    truncate-and-deep-link remedy to whoever builds the item, not to the sender.
    """

    def __init__(self, index: int, length: int) -> None:
        super().__init__(
            f"block {index} measures {length} units, over the {MAX_MESSAGE_LENGTH} limit; "
            "contracts/telegram/delivery.md §3.5 requires the builder to truncate it and add "
            "a deep link, and forbids cutting one item across two messages"
        )
        self.index = index
        self.length = length


def message_length(text: str) -> int:
    """Length of ``text`` under the *pessimistic* of the two possible counting units.

    ``len(text)`` counts Unicode scalars; ``len(text.encode("utf-16-le")) // 2`` counts
    UTF-16 code units, which is larger exactly when the string carries characters outside
    the BMP. Returning the maximum means a string accepted here is within 4096 under either
    reading of §3.4, without this module choosing between them.
    """
    return max(len(text), len(text.encode("utf-16-le")) // 2)


def payload_hash(text: str) -> str:
    """``sha256:`` + 64 lowercase hex over the UTF-8 bytes actually sent.

    Hashing the *sent* string (not a structure that renders to it) is what makes the hash
    usable as the ``I05`` oracle: two attempts whose payload hashes are equal sent the same
    bytes, whatever happened to the tags in between (fixture
    ``reporting/c-tag-changed-after-publish-before-send``).
    """
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def position_line(part_index: int, total_parts: int) -> str:
    """§3.5: *"Mỗi part tự nêu vị trí (ví dụ 'phần 2/3')"*. 1-based for the reader."""
    return f"Phần {part_index + 1}/{total_parts}"


@dataclass(frozen=True)
class SplitPart:
    """One rendered message: its 0-based index, its text and the hash of that text."""

    part_index: int
    text: str
    payload_hash: str


def split_plain_text(blocks: Sequence[str]) -> list[SplitPart]:
    """Group ``blocks`` into the fewest plain-text messages that respect §3.5.

    :param blocks: item-sized pieces, already rendered to plain text by the caller and in
        reading order. ``blocks[0]`` is expected to be the header plus the "emerging
        directions" block, which §3.5 requires to sit whole inside part 0 -- keeping them in
        one block is what makes that true by construction rather than by a later check.
    :raises PartTooLarge: if one block alone exceeds the limit (see the class docstring).
    :raises ValueError: if ``blocks`` is empty. An empty period creates no intent at all
        (``REQ-D57``), so an empty digest reaching here is a caller bug, and returning zero
        parts would quietly send nothing.

    The position line ("Phần 2/3") is part of the message, so it consumes budget. Its length
    depends on the number of parts, which depends on the split -- so the grouping is redone
    while the total changes, starting from an optimistic total of 1. The loop terminates
    because each pass either agrees with its assumption or raises the assumed total, and the
    total is bounded by ``len(blocks)``.
    """
    if not blocks:
        raise ValueError(
            "split_plain_text() needs at least one block; an empty period creates no digest "
            "intent at all (contracts/telegram/delivery.md §7, REQ-D57)"
        )

    assumed_total = 1
    while True:
        grouped = _group(blocks, assumed_total)
        if len(grouped) == assumed_total:
            break
        assumed_total = len(grouped)

    parts: list[SplitPart] = []
    for index, group in enumerate(grouped):
        text = BLOCK_SEPARATOR.join([position_line(index, assumed_total), *group])
        parts.append(SplitPart(part_index=index, text=text, payload_hash=payload_hash(text)))
    return parts


def _group(blocks: Sequence[str], assumed_total: int) -> list[list[str]]:
    """Greedy grouping under a fixed assumption about how many parts there will be."""
    # The worst-case position line under the assumption: the last index is the longest.
    reserved = message_length(position_line(assumed_total - 1, assumed_total)) + len(
        BLOCK_SEPARATOR
    )
    budget = MAX_MESSAGE_LENGTH - reserved

    groups: list[list[str]] = []
    current: list[str] = []
    used = 0
    for index, block in enumerate(blocks):
        length = message_length(block)
        if length > budget:
            raise PartTooLarge(index, length + reserved)
        addition = length if not current else length + len(BLOCK_SEPARATOR)
        if current and used + addition > budget:
            groups.append(current)
            current = [block]
            used = length
            continue
        current.append(block)
        used += addition
    groups.append(current)
    return groups


def aggregate_state(
    part_states: Sequence[DeliveryPartState],
    *,
    cancelled: bool = False,
    retry_wait: bool = False,
) -> DeliveryState:
    """``DP-03``: derive ``delivery.state`` from its parts, most urgent state winning.

    :param cancelled: the delivery row itself was cancelled (``T-DL-08`` unlink/relink, or
        an ``abandon`` decision on the last undecided part). ``cancelled`` is not derivable
        from part states -- ``delivery_part_state`` has no such member -- so it is passed in.
    :param retry_wait: the delivery is waiting out a backoff (``T-DL-03``). Also not a part
        state; ``contracts/state/delivery.yaml`` keeps the retry clock on the delivery row.

    ``cancelled`` wins outright rather than entering the precedence list: a cancelled intent
    has no recipient any more, so "still pending" would invite a send that ``T-DL-08``
    forbids. ``retry_wait`` does enter the list, below ``unknown`` and ``failed``, exactly
    where ``DP-03`` puts it.
    """
    if cancelled:
        return DeliveryState.CANCELLED
    if not part_states:
        return DeliveryState.PENDING
    candidates = {_PART_TO_AGGREGATE[state] for state in part_states}
    if retry_wait:
        candidates.discard(DeliveryState.PENDING)
        candidates.add(DeliveryState.RETRY_WAIT)
    for state in AGGREGATE_PRECEDENCE:
        if state in candidates:
            return state
    raise AssertionError(f"unreachable: {candidates!r} outside DP-03 precedence")


#: The four labels ``I13`` requires to stay distinct. ``delivery.get_status`` returns the
#: key; the UI renders the text (``contracts/ui/screens.yaml``). They are listed here so a
#: reader can see that ``unknown`` has a label of its own and is never folded into ``sent``
#: or ``failed`` -- fixture ``telegram/a`` asserts exactly that, by forbidding the other two
#: labels.
STATUS_LABELS: dict[DeliveryState, str] = {
    DeliveryState.PENDING: "pending",
    DeliveryState.SENDING: "sending",
    DeliveryState.RETRY_WAIT: "retry_wait",
    DeliveryState.SENT: "sent",
    DeliveryState.UNKNOWN: "unknown",
    DeliveryState.FAILED: "failed",
    DeliveryState.CANCELLED: "cancelled",
}
