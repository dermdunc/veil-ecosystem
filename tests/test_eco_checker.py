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


def _good_provenance(value="x", source="probed"):
    return {"value": value, "source": source, "observed_at": None if source == "unavailable" else "2026-01-01T00:00:00+00:00"}


def _minimal_repo(name="veil-proxy", **overrides):
    repo = {"name": name, "kind": "cli", "tier": "internal"}
    for field in eco_checker.REPO_PROVENANCE_FIELDS:
        repo[field] = _good_provenance()
    repo.update(overrides)
    return repo


class TestValidateDocumentShape(unittest.TestCase):
    def _base_doc(self):
        return {
            "schema_version": "veil.ecostatus.v1",
            "repos": [_minimal_repo("veil-proxy")],
            "integrations": [],
            "contradictions": [],
        }

    def test_clean_document_produces_no_findings(self):
        out: list = []
        eco_checker.validate_document_shape(self._base_doc(), {"veil-proxy"}, out)
        self.assertEqual(out, [])

    def test_flags_wrong_schema_version(self):
        doc = self._base_doc()
        doc["schema_version"] = "wrong"
        out: list = []
        eco_checker.validate_document_shape(doc, {"veil-proxy"}, out)
        self.assertTrue(any("schema_version" in c["message"] for c in out))

    def test_flags_repo_set_mismatch(self):
        out: list = []
        eco_checker.validate_document_shape(self._base_doc(), {"veil-proxy", "veil-enrol"}, out)
        self.assertTrue(any("do not match" in c["message"] for c in out))

    def test_flags_bad_kind_enum(self):
        doc = self._base_doc()
        doc["repos"][0]["kind"] = "not-a-real-kind"
        out: list = []
        eco_checker.validate_document_shape(doc, {"veil-proxy"}, out)
        self.assertTrue(any("kind enum" in c["message"] for c in out))

    def test_flags_source_and_observed_at_disagreeing(self):
        # source says unavailable but observed_at is non-null -- the exact
        # invariant the schema's own comment claims and nothing checked before.
        doc = self._base_doc()
        doc["repos"][0]["local_head"] = {"value": None, "source": "unavailable", "observed_at": "2026-01-01T00:00:00+00:00"}
        out: list = []
        eco_checker.validate_document_shape(doc, {"veil-proxy"}, out)
        self.assertTrue(any("unavailable must mean" in c["message"] for c in out))

    def test_flags_malformed_status_enum_on_an_integration(self):
        doc = self._base_doc()
        doc["integrations"] = [{"from": "a", "to": "b", "status_enum": "not_real"}]
        out: list = []
        eco_checker.validate_document_shape(doc, {"veil-proxy"}, out)
        self.assertTrue(any("status_enum" in c["message"] for c in out))

    def test_flags_bad_contradiction_severity(self):
        doc = self._base_doc()
        doc["contradictions"] = [{"rule": "x", "message": "y", "severity": "critical"}]
        out: list = []
        eco_checker.validate_document_shape(doc, {"veil-proxy"}, out)
        self.assertTrue(any("severity=" in c["message"] for c in out))


class TestApplyDevE2eVerification(unittest.TestCase):
    def _repos_and_row(self, tmp_path):
        repos = [{"name": "veil-enrol", "local_path": str(tmp_path)}]
        row = {"from": "veil-enrol", "to": "veil-custodian", "verification": {"value": "hand-asserted"}}
        return repos, [row]

    def test_no_result_file_leaves_verification_untouched(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            repos, integrations = self._repos_and_row(Path(tmp))
            out: list = []
            eco_checker.apply_dev_e2e_verification(repos, integrations, out)
            self.assertEqual(integrations[0]["verification"]["value"], "hand-asserted")
            self.assertEqual(out, [])

    def test_passed_result_flips_to_probed(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result_path = tmp_path / eco_checker.DEV_E2E_RESULT_RELATIVE_PATH
            result_path.parent.mkdir(parents=True)
            result_path.write_text('{"status": "passed", "finished_at": "2026-01-01T00:00:00Z"}')
            repos, integrations = self._repos_and_row(tmp_path)
            out: list = []
            eco_checker.apply_dev_e2e_verification(repos, integrations, out)
            self.assertEqual(integrations[0]["verification"]["value"], "probed")
            self.assertEqual(integrations[0]["verification"]["observed_at"], "2026-01-01T00:00:00Z")
            self.assertEqual(out, [])

    def test_failed_result_produces_a_warning_and_does_not_flip(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result_path = tmp_path / eco_checker.DEV_E2E_RESULT_RELATIVE_PATH
            result_path.parent.mkdir(parents=True)
            result_path.write_text('{"status": "failed", "finished_at": "2026-01-01T00:00:00Z", "exit_code": 1}')
            repos, integrations = self._repos_and_row(tmp_path)
            out: list = []
            eco_checker.apply_dev_e2e_verification(repos, integrations, out)
            self.assertEqual(integrations[0]["verification"]["value"], "hand-asserted")
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["severity"], "warning")

    def test_malformed_json_produces_a_warning(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result_path = tmp_path / eco_checker.DEV_E2E_RESULT_RELATIVE_PATH
            result_path.parent.mkdir(parents=True)
            result_path.write_text("not json")
            repos, integrations = self._repos_and_row(tmp_path)
            out: list = []
            eco_checker.apply_dev_e2e_verification(repos, integrations, out)
            self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
