"""What a post looks like in X's markup, in one place, plus an offline HTML observer.

Two consumers read this module, and that is the point:

* :mod:`probe.x_feasibility.run_probe` builds Playwright locators from the selectors;
* :func:`observe_html` reads the same markers out of an HTML string with the standard
  library, so the whole run loop can be exercised offline against hand-written pages with
  no browser installed and no request to X.

Both are generated from the same ``TESTID_*`` tokens, so the offline path cannot silently
drift from the live path: a test that changes one changes both.

**Everything here is PROVISIONAL.** X's ``data-testid`` values are what this markup is
*expected* to use; nothing in this package was checked against a live page, because it was
written without network access. When they are wrong the run stops with
``SOURCE_LAYOUT_CHANGED`` (§4 ST-7) instead of returning zero posts quietly -- that is the
fail-closed behaviour ``contracts/errors.yaml`` asks for, and updating these tokens is the
"NGƯỜI PHÁT TRIỂN sửa bộ đọc" step that code names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser

# --- the tokens both paths share ----------------------------------------------------
TESTID_POST = "tweet"
TESTID_AUTHOR = "User-Name"
TESTID_PHOTO = "tweetPhoto"
TESTID_HOME_TAB = "AppTabBar_Home_Link"
TESTID_ACCOUNT_SWITCH = "SideNav_AccountSwitcher_Button"
TESTID_CHALLENGE_INPUT = "ocfEnterTextTextInput"

SELECTOR_POST = f'article[data-testid="{TESTID_POST}"]'
SELECTOR_PERMALINK = 'a[href*="/status/"]'
SELECTOR_AUTHOR = f'[data-testid="{TESTID_AUTHOR}"]'
SELECTOR_TIME = "time[datetime]"
SELECTOR_PHOTO = f'[data-testid="{TESTID_PHOTO}"]'
SELECTOR_LOGGED_IN = f'[data-testid="{TESTID_HOME_TAB}"], [data-testid="{TESTID_ACCOUNT_SWITCH}"]'
SELECTOR_CHALLENGE_WIDGET = (
    'iframe[src*="arkoselabs"], iframe[src*="recaptcha"], iframe[src*="hcaptcha"], '
    f'[data-testid="{TESTID_CHALLENGE_INPUT}"]'
)

#: Hosts that mark a post as carrying a paper link. Read from markup only -- the probe never
#: opens them (SL-4 ``chrome_scope: x_only``; SL-5 says metadata is the server's job).
PAPER_LINK_HOSTS: tuple[str, ...] = (
    "arxiv.org",
    "doi.org",
    "biorxiv.org",
    "medrxiv.org",
    "openreview.net",
    "aclanthology.org",
    "nature.com",
    "science.org",
    "pubmed.ncbi.nlm.nih.gov",
)

#: Post-id shape on X: a numeric snowflake inside a ``/status/<id>`` permalink.
POST_ID_RE = re.compile(r"/status/(\d{5,25})")

#: iframe ``src`` substrings that mean a challenge widget is on the page.
CHALLENGE_IFRAME_HOSTS: tuple[str, ...] = ("arkoselabs", "recaptcha", "hcaptcha")


@dataclass(frozen=True)
class PostObservation:
    """One post container, reduced to the facts §5 counts. Never the post's text."""

    x_post_id: str | None
    has_author_handle: bool
    has_created_at: bool
    has_paper_link: bool
    has_photo: bool

    @property
    def missing_fields(self) -> tuple[str, ...]:
        """Required fields absent from this container -- the ST-7 evidence, named."""
        missing = []
        if not self.x_post_id:
            missing.append("x_post_id")
        if not self.has_author_handle:
            missing.append("author.handle")
        if not self.has_created_at:
            missing.append("created_at")
        return tuple(missing)

    @property
    def parsed_ok(self) -> bool:
        return not self.missing_fields

    @property
    def is_image_only(self) -> bool:
        """§5 ``posts_image_only``: a photo and no paper link ⇒ "chỉ có post", no ID guess."""
        return self.has_photo and not self.has_paper_link


class _XPageParser(HTMLParser):
    """Minimal structural reader for a saved X page. Structure and attributes only.

    It never keeps post text beyond what the paper-link check needs, and the visible text it
    accumulates is used for marker matching, never written to a record.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.posts: list[dict[str, object]] = []
        self.text_parts: list[str] = []
        self.title = ""
        self.logged_in = False
        self.challenge_widget = False
        self._article_depth = 0
        self._current: dict[str, object] | None = None
        self._in_title = False
        self._skip_depth = 0

    # -- helpers
    @staticmethod
    def _testid(attrs: list[tuple[str, str | None]]) -> str:
        for key, value in attrs:
            if key == "data-testid":
                return value or ""
        return ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        testid = self._testid(attrs)

        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if testid in {TESTID_HOME_TAB, TESTID_ACCOUNT_SWITCH}:
            self.logged_in = True
        if testid == TESTID_CHALLENGE_INPUT:
            self.challenge_widget = True
        if tag == "iframe":
            src = attr_map.get("src", "").lower()
            if any(host in src for host in CHALLENGE_IFRAME_HOSTS):
                self.challenge_widget = True

        if tag == "article" and testid == TESTID_POST:
            self._article_depth = 1
            self._current = {
                "post_id": None,
                "author": False,
                "time": False,
                "paper": False,
                "photo": False,
            }
            return
        if self._current is not None:
            if tag == "article":
                self._article_depth += 1
            if testid == TESTID_AUTHOR:
                self._current["author"] = True
            if testid == TESTID_PHOTO:
                self._current["photo"] = True
            if tag == "time" and "datetime" in attr_map:
                self._current["time"] = True
            if tag == "a":
                href = attr_map.get("href", "")
                if self._current["post_id"] is None:
                    match = POST_ID_RE.search(href)
                    if match:
                        self._current["post_id"] = match.group(1)
                lowered = href.lower()
                if any(host in lowered for host in PAPER_LINK_HOSTS):
                    self._current["paper"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag == "article" and self._current is not None:
            self._article_depth -= 1
            if self._article_depth <= 0:
                self.posts.append(self._current)
                self._current = None
                self._article_depth = 0

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
            return
        stripped = data.strip()
        if stripped:
            self.text_parts.append(stripped)
            if self._current is not None:
                lowered = stripped.lower()
                if any(host in lowered for host in PAPER_LINK_HOSTS):
                    self._current["paper"] = True

    @property
    def visible_text(self) -> str:
        return " ".join(self.text_parts)


def parse_posts(html: str) -> list[PostObservation]:
    """Extract every post container from an HTML string."""
    parser = _XPageParser()
    parser.feed(html)
    parser.close()
    return [
        PostObservation(
            x_post_id=p["post_id"],  # type: ignore[arg-type]
            has_author_handle=bool(p["author"]),
            has_created_at=bool(p["time"]),
            has_paper_link=bool(p["paper"]),
            has_photo=bool(p["photo"]),
        )
        for p in parser.posts
    ]


def observe_html(
    html: str,
    *,
    url: str = "",
    http_status: int | None = None,
    expects_feed: bool = True,
) -> tuple[object, list[PostObservation]]:
    """Build a ``PageObservation`` and the post list from a saved page.

    Returned as ``object`` to keep this module free of a cycle with
    :mod:`probe.x_feasibility.signals`; the concrete type is imported lazily below.
    """
    from probe.x_feasibility.signals import PageObservation  # noqa: PLC0415 - avoid cycle

    parser = _XPageParser()
    parser.feed(html)
    parser.close()
    posts = parse_posts(html)
    missing: set[str] = set()
    for post in posts:
        missing.update(post.missing_fields)
    observation = PageObservation(
        url=url,
        title=parser.title.strip(),
        visible_text=parser.visible_text,
        http_status=http_status,
        post_node_count=len(posts),
        parsed_ok_count=sum(1 for p in posts if p.parsed_ok),
        missing_required_fields=tuple(sorted(missing)),
        logged_in_marker_present=parser.logged_in,
        expects_feed=expects_feed,
        challenge_widget_present=parser.challenge_widget,
    )
    return observation, posts
