from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
LIT = ROOT / "docs" / "literature"


def test_literature_records_and_bibtex_integrity() -> None:
    with (LIT / "papers.toml").open("rb") as handle:
        records = tomllib.load(handle)["papers"]
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))
    assert len(records) == 9
    for record in records:
        for field in ("id", "title", "authors", "year", "publication_status", "date_verified", "canonical_url"):
            assert field in record
        assert not any("<" in str(value) or ">" in str(value) for value in record.values())
        assert re.match(r"https?://", record["canonical_url"])
    text = (LIT / "references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@[A-Za-z]+\{([^,]+),", text)
    assert len(keys) == len(set(keys)) == 9
    assert all(key.strip() for key in keys)


def test_research_docs_do_not_contain_template_placeholders() -> None:
    for path in LIT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "<EXPERIMENT" not in text
        assert "<MODEL_ID>" not in text
        assert "<BENCHMARK_ID>" not in text


def test_citation_keys_used_in_docs_exist() -> None:
    bib = (LIT / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    docs = "\n".join(path.read_text(encoding="utf-8") for path in LIT.glob("*.md"))
    for key in re.findall(r"\\cite\{([^}]+)\}", docs):
        assert key in keys
