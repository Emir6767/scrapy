"""
Module for processing Sitemaps.

Note: The main purpose of this module is to provide support for the
SitemapSpider, its API is subject to change without notice.
"""

from typing import Any, Dict, Generator, Iterator, Optional
from urllib.parse import urljoin

import lxml.etree


class Sitemap:
    """Class to parse Sitemap (type=urlset) and Sitemap Index
    (type=sitemapindex) files"""

    def __init__(self, xmltext: str):
        xmlp = lxml.etree.XMLParser(
            recover=True, remove_comments=True, resolve_entities=False
        )
        self._root = lxml.etree.fromstring(xmltext, parser=xmlp)
        rt = self._root.tag
        self.type = self._root.tag.split("}", 1)[1] if "}" in rt else rt

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for elem in self._root.getchildren():
            d: Dict[str, Any] = {}
            for el in elem.getchildren():
                tag = el.tag
                name = tag.split("}", 1)[1] if "}" in tag else tag

                if name == "link":
                    if "href" in el.attrib:
                        d.setdefault("alternate", []).append(el.get("href"))
                else:
                    d[name] = el.text.strip() if el.text else ""

            if "loc" in d:
                yield d


def sitemap_urls_from_robots(
    robots_text: str, base_url: Optional[str] = None
) -> Generator[str, Any, None]:
    """Return an iterator over all sitemap urls contained in the given
    robots.txt file
    """
    for line in robots_text.splitlines():
        if line.lstrip().lower().startswith("sitemap:"):
            url = line.split(":", 1)[1].strip()
            yield urljoin(base_url or "", url)
