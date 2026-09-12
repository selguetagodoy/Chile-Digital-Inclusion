#!/usr/bin/env python3
"""Watch official source landing pages for publication changes.

The watcher is discovery-only: it never promotes new values into canonical data.
It fingerprints only relevant page elements and records changes for human review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

CONFIG = Path("config/source_watch.csv")
STATE = Path("data/metadata/source_watch_state.csv")
REPORT = Path("data/metadata/source_watch_report.csv")
ISSUE_BODY = Path(".source-watch-issue.md")
MAX_BYTES = 10 * 1024 * 1024
USER_AGENT = "Chile-Digital-Inclusion-source-watch/1.0 (+https://github.com/selguetagodoy/Chile-Digital-Inclusion)"

STATE_FIELDS = [
    "watch_id", "publisher", "landing_url", "mode", "fingerprint", "http_status",
    "matched_count", "etag", "last_modified", "first_seen_at", "last_changed_at",
    "status",
]
REPORT_FIELDS = [
    "checked_at", "watch_id", "publisher", "landing_url", "mode", "event", "status",
    "http_status", "matched_count", "fingerprint", "previous_fingerprint", "detail",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(value: str) -> str:
    value = html.unescape(value or "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"\s+", " ", value).strip().casefold()
    return value


def split_terms(raw: str) -> list[str]:
    return [normalize(part) for part in (raw or "").split("||") if normalize(part)]


class RelevantHTMLParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.anchors: list[tuple[str, str]] = []
        self.text_chunks: list[str] = []
        self._href: str | None = None
        self._anchor_text: list[str] = []
        self._ignore_depth = 0

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._ignore_depth += 1
        if tag == "a":
            href = dict(attrs).get("href")
            self._href = urljoin(self.base_url, href) if href else ""
            self._anchor_text = []

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag == "a" and self._href is not None:
            text = " ".join(self._anchor_text).strip()
            self.anchors.append((text, self._href))
            self._href = None
            self._anchor_text = []
        if tag in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1

    def handle_data(self, data: str):
        if self._ignore_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        self.text_chunks.append(text)
        if self._href is not None:
            self._anchor_text.append(text)


@dataclass
class FetchResult:
    status: str
    http_status: str
    final_url: str
    etag: str
    last_modified: str
    body: bytes
    detail: str


def fetch(url: str) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-CL,es;q=0.9,en;q=0.7",
        },
    )
    try:
        with urlopen(request, timeout=35) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return FetchResult(
                    "ERROR", str(getattr(response, "status", "")), response.geturl(),
                    response.headers.get("ETag", ""), response.headers.get("Last-Modified", ""),
                    b"", f"response exceeded {MAX_BYTES} bytes",
                )
            return FetchResult(
                "OK", str(getattr(response, "status", "")), response.geturl(),
                response.headers.get("ETag", ""), response.headers.get("Last-Modified", ""),
                body, "",
            )
    except HTTPError as exc:
        return FetchResult("ERROR", str(exc.code), url, "", "", b"", f"HTTPError: {exc.reason}")
    except URLError as exc:
        return FetchResult("ERROR", "", url, "", "", b"", f"URLError: {exc.reason}")
    except Exception as exc:
        return FetchResult("ERROR", "", url, "", "", b"", f"{type(exc).__name__}: {exc}")


def extract_fingerprint(mode: str, body: bytes, final_url: str, terms: list[str]) -> tuple[str, int, str]:
    if mode == "body_hash":
        digest = hashlib.sha256(body).hexdigest()
        return digest, 1, f"raw body sha256 over {len(body)} bytes"

    text = body.decode("utf-8", errors="replace")
    parser = RelevantHTMLParser(final_url)
    parser.feed(text)

    if mode == "html_links":
        matched = []
        for anchor_text, href in parser.anchors:
            candidate = normalize(f"{anchor_text} {href}")
            if not terms or any(term in candidate for term in terms):
                matched.append(f"{normalize(anchor_text)}\t{href.strip()}")
        items = sorted(set(matched))
    elif mode == "html_text":
        matched = []
        for chunk in parser.text_chunks:
            candidate = normalize(chunk)
            if not terms or any(term in candidate for term in terms):
                matched.append(candidate)
        items = sorted(set(matched))
    else:
        raise ValueError(f"unsupported mode: {mode}")

    canonical = "\n".join(items).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    preview = "; ".join(items[:3])
    return digest, len(items), preview[:500]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_github_output(path: str | None, values: dict[str, str]) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--github-output", default=None)
    args = parser.parse_args()

    config_rows = read_csv_rows(args.config)
    if not config_rows:
        print(f"No source-watch configuration found in {args.config}", file=sys.stderr)
        return 2

    previous_rows = read_csv_rows(args.state)
    previous = {row["watch_id"]: row for row in previous_rows if row.get("watch_id")}
    baseline = not bool(previous_rows)
    checked_at = utc_now()

    state_rows: list[dict[str, str]] = []
    report_rows: list[dict[str, str]] = []
    action_rows: list[dict[str, str]] = []
    state_changed = False

    for cfg in config_rows:
        watch_id = cfg["watch_id"].strip()
        publisher = cfg["publisher"].strip()
        landing_url = cfg["landing_url"].strip()
        mode = cfg["mode"].strip()
        terms = split_terms(cfg.get("include_terms", ""))
        prev = previous.get(watch_id)
        fetched = fetch(landing_url)

        fingerprint = ""
        matched_count = 0
        detail = fetched.detail
        current_status = fetched.status

        if fetched.status == "OK":
            try:
                fingerprint, matched_count, preview = extract_fingerprint(
                    mode, fetched.body, fetched.final_url, terms
                )
                if mode != "body_hash" and matched_count == 0:
                    current_status = "EMPTY"
                    detail = "no configured relevant elements matched"
                else:
                    detail = preview or "fingerprint built"
            except Exception as exc:
                current_status = "ERROR"
                detail = f"extraction error: {type(exc).__name__}: {exc}"

        previous_fingerprint = prev.get("fingerprint", "") if prev else ""
        previous_status = prev.get("status", "") if prev else ""

        if prev is None:
            event = "BASELINE" if current_status == "OK" else f"BASELINE_{current_status}"
        elif current_status == "OK" and previous_status != "OK":
            event = "RECOVERED"
        elif current_status in {"ERROR", "EMPTY"} and previous_status == "OK":
            event = current_status
        elif current_status in {"ERROR", "EMPTY"}:
            event = "UNCHANGED_" + current_status
        elif fingerprint != previous_fingerprint:
            event = "CHANGED"
        else:
            event = "UNCHANGED"

        now_row = {
            "watch_id": watch_id,
            "publisher": publisher,
            "landing_url": landing_url,
            "mode": mode,
            "fingerprint": fingerprint,
            "http_status": fetched.http_status,
            "matched_count": str(matched_count),
            "etag": fetched.etag,
            "last_modified": fetched.last_modified,
            "first_seen_at": prev.get("first_seen_at", checked_at) if prev else checked_at,
            "last_changed_at": (
                checked_at
                if prev is None or event in {"CHANGED", "ERROR", "EMPTY", "RECOVERED"}
                else prev.get("last_changed_at", checked_at)
            ),
            "status": current_status,
        }

        if prev is None or any(now_row.get(k, "") != prev.get(k, "") for k in STATE_FIELDS):
            state_changed = True
        state_rows.append(now_row)

        report_row = {
            "checked_at": checked_at,
            "watch_id": watch_id,
            "publisher": publisher,
            "landing_url": landing_url,
            "mode": mode,
            "event": event,
            "status": current_status,
            "http_status": fetched.http_status,
            "matched_count": str(matched_count),
            "fingerprint": fingerprint,
            "previous_fingerprint": previous_fingerprint,
            "detail": detail,
        }
        report_rows.append(report_row)

        if not baseline and event in {"CHANGED", "ERROR", "EMPTY", "RECOVERED"}:
            action_rows.append(report_row)

        print(
            f"{watch_id}: event={event} status={current_status} "
            f"http={fetched.http_status or '-'} matches={matched_count}"
        )

    configured_ids = {row["watch_id"].strip() for row in config_rows}
    removed_ids = sorted(set(previous) - configured_ids)
    if removed_ids:
        state_changed = True
        for watch_id in removed_ids:
            report_rows.append({
                "checked_at": checked_at,
                "watch_id": watch_id,
                "publisher": previous[watch_id].get("publisher", ""),
                "landing_url": previous[watch_id].get("landing_url", ""),
                "mode": previous[watch_id].get("mode", ""),
                "event": "REMOVED_FROM_CONFIG",
                "status": previous[watch_id].get("status", ""),
                "http_status": previous[watch_id].get("http_status", ""),
                "matched_count": previous[watch_id].get("matched_count", ""),
                "fingerprint": previous[watch_id].get("fingerprint", ""),
                "previous_fingerprint": previous[watch_id].get("fingerprint", ""),
                "detail": "watch definition removed from config",
            })

    write_csv_rows(args.state, STATE_FIELDS, state_rows)
    write_csv_rows(args.report, REPORT_FIELDS, report_rows)

    if action_rows:
        lines = [
            "# Official source watch",
            "",
            f"Check: {checked_at}",
            "",
            "The discovery monitor detected source-level changes or access/extraction problems. "
            "No canonical data were updated automatically.",
            "",
        ]
        for row in action_rows:
            lines.extend([
                f"## {row['watch_id']} — {row['event']}",
                "",
                f"- Publisher: {row['publisher']}",
                f"- URL: {row['landing_url']}",
                f"- Status: {row['status']} (HTTP {row['http_status'] or 'n/a'})",
                f"- Relevant elements: {row['matched_count']}",
                f"- Detail: {row['detail']}",
                "",
            ])
        lines.extend([
            "## Review rule",
            "",
            "Verify the primary publication, preserve its original vintage and methodology, "
            "then update the corresponding extraction pipeline through a reviewed pull request. "
            "Do not interpolate, backcast, average ranges or silently replace a prior vintage.",
            "",
        ])
        ISSUE_BODY.write_text("\n".join(lines), encoding="utf-8")
    elif ISSUE_BODY.exists():
        ISSUE_BODY.unlink()

    action_required = bool(action_rows)
    write_github_output(args.github_output, {
        "baseline": str(baseline).lower(),
        "state_changed": str(state_changed).lower(),
        "action_required": str(action_required).lower(),
        "action_count": str(len(action_rows)),
        "checked_at": checked_at,
    })

    print(
        f"baseline={baseline} state_changed={state_changed} "
        f"action_required={action_required} action_count={len(action_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
