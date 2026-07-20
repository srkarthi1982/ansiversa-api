"""Read-only production smoke checks for public AI knowledge artifacts."""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
from dataclasses import dataclass
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

import certifi


PUBLIC_ARTIFACTS = (
    ("/robots.txt", "text/plain"),
    ("/llms.txt", "text/plain"),
    ("/llms-full.txt", "text/plain"),
    ("/ai-sitemap.xml", "application/xml"),
    ("/public-ai-knowledge.json", "application/json"),
    ("/public-ai-jsonld.json", "application/ld+json"),
    ("/public-ai-metadata.json", "application/json"),
)

API_ARTIFACTS = (
    ("/api/v1/knowledge/public", "application/json"),
    ("/api/v1/knowledge/public/jsonld", "application/ld+json"),
    ("/api/v1/knowledge/public/metadata", "application/json"),
)

FORBIDDEN_PATTERNS = {
    "100-plus": re.compile(r"\b100\+"),
    "internal": re.compile(r"\binternal\b|\brestricted\b|\bauthenticated\b", re.I),
    "source-path": re.compile(r"AGENTS\.md|story\.md|certification|promotion", re.I),
    "future": re.compile(r"futureDirection|Future Version Ideas|V1\.\d|V2:|\bin V\d\b", re.I),
    "secret": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|authorization\s*:\s*bearer\s+\S+|(?:API_KEY|TOKEN|PASSWORD|DATABASE_URL)\s*=",
        re.I,
    ),
}


class NoRedirectHandler(HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):  # noqa: ANN001
        return fp

    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


@dataclass(frozen=True)
class FetchResult:
    path: str
    url: str
    status: int
    final_url: str
    redirects: int
    content_type: str
    content_length: int
    cache_control: str
    etag: str
    last_modified: str
    cors: str
    body: str


def _normalized_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("base URLs must be absolute HTTPS URLs")
    if parsed.query or parsed.fragment:
        raise ValueError("base URLs must not contain query strings or fragments")
    return f"https://{parsed.netloc}{parsed.path.rstrip('/')}"


def _fetch(base_url: str, path: str, timeout: float, user_agent: str, ssl_context: ssl.SSLContext) -> FetchResult:
    url = urljoin(f"{base_url}/", path.lstrip("/"))
    opener = build_opener(NoRedirectHandler, HTTPSHandler(context=ssl_context))
    redirects = 0
    current_url = url
    while True:
        request = Request(current_url, headers={"User-Agent": user_agent, "Accept": "*/*"})
        try:
            with opener.open(request, timeout=timeout) as response:
                status = response.status
                headers = response.headers
                location = headers.get("Location")
                if status in {301, 302, 303, 307, 308} and location:
                    redirects += 1
                    if redirects > 5:
                        raise RuntimeError(f"too many redirects for {url}")
                    current_url = urljoin(current_url, location)
                    continue
                body_bytes = response.read()
        except HTTPError as exc:
            status = exc.code
            headers = exc.headers
            body_bytes = exc.read()
        except URLError as exc:
            raise RuntimeError(f"fetch failed for {url}: {exc.reason}") from exc
        return FetchResult(
            path=path,
            url=url,
            status=status,
            final_url=current_url,
            redirects=redirects,
            content_type=headers.get("Content-Type", ""),
            content_length=len(body_bytes),
            cache_control=headers.get("Cache-Control", ""),
            etag=headers.get("ETag", ""),
            last_modified=headers.get("Last-Modified", ""),
            cors=headers.get("Access-Control-Allow-Origin", ""),
            body=body_bytes.decode("utf-8", errors="replace"),
        )


def _assert_no_forbidden_content(result: FetchResult) -> list[str]:
    failures = []
    for label, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(result.body):
            failures.append(f"{result.path}: forbidden content detected: {label}")
    return failures


def _validate_json(result: FetchResult) -> tuple[dict, list[str]]:
    try:
        parsed = json.loads(result.body)
    except json.JSONDecodeError as exc:
        return {}, [f"{result.path}: invalid JSON: {exc}"]
    return parsed, []


def _validate_xml(result: FetchResult) -> list[str]:
    try:
        ElementTree.fromstring(result.body)
    except ElementTree.ParseError as exc:
        return [f"{result.path}: invalid XML: {exc}"]
    return []


def _validate_result(result: FetchResult, expected_content_type: str, canonical_domain: str) -> list[str]:
    failures = []
    if result.status != 200:
        failures.append(f"{result.path}: expected 200, got {result.status}")
    if not result.content_type.lower().startswith(expected_content_type):
        failures.append(f"{result.path}: expected {expected_content_type}, got {result.content_type or 'missing'}")
    if result.content_type.lower().startswith("text/html"):
        failures.append(f"{result.path}: returned HTML fallback")
    if "private" in result.cache_control.lower():
        failures.append(f"{result.path}: private cache header")
    if result.content_length <= 0:
        failures.append(f"{result.path}: empty body")
    if urlparse(result.final_url).hostname not in {canonical_domain, "api.ansiversa.com", "www.ansiversa.com"}:
        failures.append(f"{result.path}: unexpected final host {result.final_url}")
    failures.extend(_assert_no_forbidden_content(result))
    return failures


def _validate_public_knowledge(result: FetchResult) -> list[str]:
    data, failures = _validate_json(result)
    if failures:
        return failures
    apps = data.get("apps") or []
    categories = data.get("categories") or []
    platform = data.get("platform") or {}
    slugs = [app.get("slug") for app in apps]
    routes = [app.get("route") for app in apps]
    if data.get("schemaVersion") != 1:
        failures.append("public knowledge: unexpected schemaVersion")
    if len(apps) != 100:
        failures.append(f"public knowledge: expected 100 apps, got {len(apps)}")
    if len(categories) != 14:
        failures.append(f"public knowledge: expected 14 categories, got {len(categories)}")
    if len(slugs) != len(set(slugs)):
        failures.append("public knowledge: duplicate app slugs")
    if len(routes) != len(set(routes)):
        failures.append("public knowledge: duplicate app routes")
    if any(app.get("visibility") != "public" for app in apps):
        failures.append("public knowledge: non-public app exported")
    if platform.get("appCount") != 100:
        failures.append("public knowledge: platform appCount is not 100")
    if (platform.get("catalogBoundary") or {}).get("fixedAppCount") != 100:
        failures.append("public knowledge: fixed catalog boundary is not 100")
    if "bill-splitter" not in slugs:
        failures.append("public knowledge: Bill Splitter missing")
    for app in apps:
        canonical = app.get("canonicalUrl", "")
        if not canonical.startswith("https://ansiversa.com/"):
            failures.append(f"public knowledge: invalid canonical URL for {app.get('slug')}")
    return failures


def _validate_jsonld(result: FetchResult) -> list[str]:
    data, failures = _validate_json(result)
    if failures:
        return failures
    if data.get("@context") != "https://schema.org":
        failures.append("JSON-LD: invalid @context")
    graph = data.get("@graph") or []
    ids = [node.get("@id") for node in graph if node.get("@id")]
    if len(ids) != len(set(ids)):
        failures.append("JSON-LD: duplicate @id")
    types = {node.get("@type") for node in graph}
    expected = {"Organization", "WebSite", "CollectionPage", "FAQPage", "SoftwareApplication"}
    if not expected <= types:
        failures.append("JSON-LD: missing expected schema.org types")
    if sum(1 for node in graph if node.get("@type") == "SoftwareApplication") != 100:
        failures.append("JSON-LD: expected 100 SoftwareApplication nodes")
    if any(str(node.get("url", "")).startswith("http://") for node in graph):
        failures.append("JSON-LD: non-HTTPS URL found")
    return failures


def _validate_metadata(result: FetchResult) -> list[str]:
    data, failures = _validate_json(result)
    if failures:
        return failures
    pages = data.get("pages") or []
    routes = [page.get("route") for page in pages]
    required = {"/", "/about", "/pricing", "/faq", "/contact", "/apps", "/bill-splitter"}
    if not required <= set(routes):
        failures.append("metadata: missing required public page/app routes")
    if any(not str(page.get("canonical", "")).startswith("https://ansiversa.com") for page in pages):
        failures.append("metadata: non-production canonical URL found")
    return failures


def _validate_sitemap(result: FetchResult) -> list[str]:
    failures = _validate_xml(result)
    if failures:
        return failures
    root = ElementTree.fromstring(result.body)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [loc.text or "" for loc in root.findall(".//sm:loc", namespace)]
    if len(locs) != 106:
        failures.append(f"sitemap: expected 106 URLs, got {len(locs)}")
    if len(locs) != len(set(locs)):
        failures.append("sitemap: duplicate URLs")
    if any(not loc.startswith("https://ansiversa.com") for loc in locs):
        failures.append("sitemap: non-canonical URL found")
    if "https://ansiversa.com/bill-splitter" not in locs:
        failures.append("sitemap: Bill Splitter URL missing")
    return failures


def _validate_robots(result: FetchResult) -> list[str]:
    failures = []
    if "Sitemap: https://ansiversa.com/ai-sitemap.xml" not in result.body:
        failures.append("robots: missing AI sitemap reference")
    if "LLMs: https://ansiversa.com/llms.txt" not in result.body:
        failures.append("robots: missing llms.txt reference")
    if "qa.ansiversa.com" in result.body:
        failures.append("robots: QA hostname leaked")
    return failures


def _fetch_all(
    base_url: str,
    paths: Iterable[tuple[str, str]],
    timeout: float,
    user_agent: str,
    ssl_context: ssl.SSLContext,
) -> list[FetchResult]:
    return [_fetch(base_url, path, timeout, user_agent, ssl_context) for path, _ in paths]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://ansiversa.com")
    parser.add_argument("--api-base-url", default="")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--user-agent", default="AnsiversaPublicKnowledgeVerifier/1.0")
    args = parser.parse_args()

    base_url = _normalized_base_url(args.base_url)
    api_base_url = _normalized_base_url(args.api_base_url) if args.api_base_url else base_url
    canonical_domain = urlparse(base_url).hostname or ""
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    failures: list[str] = []
    results = _fetch_all(base_url, PUBLIC_ARTIFACTS, args.timeout, args.user_agent, ssl_context)
    results.extend(_fetch_all(api_base_url, API_ARTIFACTS, args.timeout, args.user_agent, ssl_context))

    for result, (_, expected_content_type) in zip(results, (*PUBLIC_ARTIFACTS, *API_ARTIFACTS), strict=True):
        failures.extend(_validate_result(result, expected_content_type, canonical_domain))
        if result.path.endswith(".xml"):
            failures.extend(_validate_sitemap(result))
        elif result.path.endswith("robots.txt"):
            failures.extend(_validate_robots(result))
        elif result.path.endswith("public-ai-knowledge.json") or result.path.endswith("/knowledge/public"):
            failures.extend(_validate_public_knowledge(result))
        elif result.path.endswith("public-ai-jsonld.json") or result.path.endswith("/public/jsonld"):
            failures.extend(_validate_jsonld(result))
        elif result.path.endswith("public-ai-metadata.json") or result.path.endswith("/public/metadata"):
            failures.extend(_validate_metadata(result))

    for result in results:
        print(
            f"{result.path}: status={result.status} redirects={result.redirects} "
            f"type={result.content_type or 'missing'} bytes={result.content_length} "
            f"cache={result.cache_control or 'missing'} final={result.final_url}"
        )

    if failures:
        print("\nFAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nPASSED public deployment smoke check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
