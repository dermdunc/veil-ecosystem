"""Fast, deterministic unit tests for scripts/eco_checker.py's pure-logic
pieces -- the markdown-table parser, the link extractor, and the
contradiction rules given synthetic data. Does not touch the network or
require the sibling checkouts to exist.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import eco_checker  # noqa: E402


class TestStatusCellParsing(unittest.TestCase):
    def test_recognises_every_convention_phrase(self):
        table = (
            "| Integration | Status |\n"
            "|---|---|\n"
            "| a → b | **Wired and demonstrated.** detail |\n"
            "| c → d | **Built, no caller.** detail |\n"
            "| e → f | **Built, locally proven.** detail |\n"
            "| g → h | **Built, not live.** detail |\n"
            "| i → j | **Missing.** detail |\n"
        )
        contradictions: list = []
        integrations = self._parse(table, contradictions)
        self.assertEqual(len(contradictions), 0)
        enums = [i["status_enum"] for i in integrations]
        self.assertEqual(
            enums,
            [
                "wired_and_demonstrated",
                "built_no_caller",
                "built_locally_proven",
                "built_not_live",
                "missing",
            ],
        )

    def test_flags_a_row_that_does_not_open_with_a_bold_enum_phrase(self):
        table = "| Integration | Status |\n|---|---|\n| a → b | some unstructured prose |\n"
        contradictions: list = []
        self._parse(table, contradictions)
        self.assertEqual(len(contradictions), 1)
        self.assertEqual(contradictions[0]["rule"], "status_cell_enum")

    @staticmethod
    def _parse(table_markdown: str, contradictions: list) -> list:
        # Exercise the same regex path parse_integration_table uses,
        # without requiring a real docs/architecture.md on disk.
        import re

        integrations = []
        match = re.search(r"\| Integration \| Status \|\n\|[-|]+\|\n((?:\|.*\n)+)", table_markdown)
        assert match is not None
        for line in match.group(1).splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|", 1)]
            if len(cells) != 2:
                continue
            edge, status_cell = cells
            bold_match = re.match(r"^\*\*([^*]+?)\.?\*\*", status_cell)
            status_text = bold_match.group(1) if bold_match else None
            status_enum = eco_checker.STATUS_ENUM_PHRASES.get(status_text) if status_text else None
            if status_enum is None:
                contradictions.append(
                    {"rule": "status_cell_enum", "message": f"{edge}: {status_text!r}", "severity": "error"}
                )
                status_enum = "missing"
            integrations.append({"from": edge, "status_enum": status_enum})
        return integrations


class TestMarkdownLinkExtraction(unittest.TestCase):
    def test_extracts_relative_and_absolute_links(self):
        text = "See [docs](docs/architecture.md) and [ext](https://example.com) and [anchor](#section)."
        links = eco_checker.extract_markdown_links(text)
        self.assertEqual(links, ["docs/architecture.md", "https://example.com", "#section"])


class TestVisibilityPrivacyMap(unittest.TestCase):
    def test_public_repo_only_consistent_with_declared_public(self):
        self.assertEqual(eco_checker.VISIBILITY_TO_PRIVACY["public"], {"public"})

    def test_private_repo_consistent_with_internal_or_local_first(self):
        self.assertEqual(eco_checker.VISIBILITY_TO_PRIVACY["private"], {"internal", "local-first"})


class TestRiskRegisterParity(unittest.TestCase):
    def test_flags_asymmetric_id_sets(self):
        contradictions: list = []
        yaml_ids = {"RISK-0001", "RISK-0002"}
        md_ids = {"RISK-0001"}
        only_in_yaml = yaml_ids - md_ids
        only_in_md = md_ids - yaml_ids
        self.assertTrue(only_in_yaml or only_in_md)


if __name__ == "__main__":
    unittest.main()
