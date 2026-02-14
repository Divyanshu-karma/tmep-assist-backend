from bs4 import BeautifulSoup
from pathlib import Path
import re


SECTION_ID_RE = re.compile(
    r"^([0-9]+(?:\.[0-9]+)*(?:\([a-z0-9]+\))*)\s+(.*)$"
)


def parse_tmep_html(html_path: Path) -> list[dict]:
    """
    Parse TMEP HTML into ATOMIC legal units.

    Atomic = lowest citable authority:
    - TMEP subsection (e.g. 301.01(a))
    - CFR block
    - USC block
    """

    if not html_path.exists():
        raise FileNotFoundError(f"TMEP HTML file not found: {html_path}")

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    sections: list[dict] = []

    # Iterate ALL Section divs (do NOT skip nested ones)
    for section_div in soup.find_all("div", class_="Section"):
        heading = _extract_heading(section_div)
        section_id, title = _split_heading(heading)

        # Skip structural wrappers without IDs
        if not section_id:
            continue

        text_parts: list[str] = []

        for el in section_div.find_all(
            ["p", "li"], recursive=False
        ):
            txt = el.get_text(" ", strip=True)
            if txt:
                text_parts.append(txt)

        full_text = "\n".join(text_parts).strip()

        if len(full_text) < 80:
            continue

        sections.append({
            "section_id": section_id,
            "section_title": title,
            "full_text": full_text,
        })

    return sections


def _extract_heading(section_div) -> str:
    headings = section_div.find_all("h1", class_="page-title")
    if headings:
        return headings[-1].get_text(" ", strip=True)

    for tag in ("h2", "h3", "h4"):
        h = section_div.find(tag)
        if h:
            return h.get_text(" ", strip=True)

    return ""


def _split_heading(heading: str) -> tuple[str | None, str]:
    match = SECTION_ID_RE.match(heading)
    if match:
        return match.group(1), match.group(2).strip()
    return None, heading.strip()





# from bs4 import BeautifulSoup
# from pathlib import Path
# import re


# def parse_tmep_html(html_path: Path) -> list[dict]:
#     if not html_path.exists():
#         raise FileNotFoundError(f"TMEP HTML file not found: {html_path}")

#     with html_path.open("r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "html.parser")

#     sections: list[dict] = []

#     # 🔑 CORE STRATEGY: iterate legal Section containers
#     for section_div in soup.select("div.Section"):
#         heading_text = _extract_section_heading(section_div)
#         section_id, section_title = _split_heading(heading_text)

#         text_parts: list[str] = []
#         for p in section_div.find_all("p", recursive=True):
#             paragraph = p.get_text(" ", strip=True)
#             if paragraph:
#                 text_parts.append(paragraph)

#         full_text = "\n".join(text_parts)

#         if not full_text or len(full_text) < 50:
#             continue

#         sections.append({
#             "section_id": section_id,
#             "section_title": section_title,
#             "full_text": full_text
#         })

#     return sections


# def _extract_section_heading(section_div) -> str:
#     # Highest priority: official page title
#     page_title = section_div.find("h1", class_="page-title")
#     if page_title:
#         return page_title.get_text(" ", strip=True)

#     # Fallback: first heading tag inside section
#     for tag in ["h1", "h2", "h3", "h4"]:
#         heading = section_div.find(tag)
#         if heading:
#             return heading.get_text(" ", strip=True)

#     # Last fallback: section div ID
#     return section_div.get("id", "Unknown Section")


# def _split_heading(heading: str) -> tuple[str | None, str]:
#     match = re.match(r"^([0-9A-Za-z().-]+)\s+(.*)$", heading)
#     if match:
#         return match.group(1), match.group(2)
#     return None, heading
