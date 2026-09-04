"""Fast, deterministic unit tests for scripts/eco_collector.py -- no network,
no dependency on the real component checkouts existing. The real end-to-end
run (against the actual six repos) is exercised manually via `scripts/eco.sh
status` and recorded in this PR's own verification output, not re-run here
on every CI invocation where the sibling repos may not even be checked out.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import eco_collector  # noqa: E402


class TestAllowList(unittest.TestCase):
    def test_rejects_a_path_outside_the_allowed_basenames(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "scripts" / "eco-components.json"
            config_path.parent.mkdir()
            config = {"base_dir_env": "X", "base_dir_default": ".."}
            component = {"name": "evil", "kind": "cli", "relative_path": "veil-ecosystem-private"}
            with self.assertRaises(ValueError):
                eco_collector.resolve_component_path(component, config_path, config)

    def test_accepts_every_basename_the_shipped_config_actually_uses(self):
        config_path = eco_collector.DEFAULT_CONFIG
        config = eco_collector.load_config(config_path)
        for component in config["components"]:
            # Should not raise -- every shipped entry must resolve to an
            # allow-listed basename by construction.
            eco_collector.resolve_component_path(component, config_path, config)


class TestProvenance(unittest.TestCase):
    def test_provenance_shape(self):
        p = eco_collector.provenance("x", "probed")
        self.assertEqual(p["value"], "x")
        self.assertEqual(p["source"], "probed")
        self.assertIsNotNone(p["observed_at"])

    def test_unavailable_shape(self):
        u = eco_collector.unavailable()
        self.assertIsNone(u["value"])
        self.assertEqual(u["source"], "unavailable")
        self.assertIsNone(u["observed_at"])


class TestConfigShape(unittest.TestCase):
    def test_shipped_config_has_exactly_six_components(self):
        config = eco_collector.load_config(eco_collector.DEFAULT_CONFIG)
        names = [c["name"] for c in config["components"]]
        self.assertEqual(
            sorted(names),
            sorted(
                [
                    "veil-proxy",
                    "veil-foundations",
                    "veil-custodian",
                    "veil-enrol",
                    "veil-observatory",
                    "veil-demo",
                ]
            ),
        )

    def test_veil_proxy_carries_its_former_name_as_an_alias(self):
        config = eco_collector.load_config(eco_collector.DEFAULT_CONFIG)
        proxy = next(c for c in config["components"] if c["name"] == "veil-proxy")
        self.assertIn("dermdunc/veilgremlin", proxy["github_repo_aliases"])

    def test_config_never_names_a_private_sibling(self):
        config = eco_collector.load_config(eco_collector.DEFAULT_CONFIG)
        raw = json.dumps(config)
        self.assertNotIn("veil-ecosystem-private", raw)
        self.assertNotIn("veil-foundations-private", raw)


class TestDeriveTier(unittest.TestCase):
    def test_public_only_when_both_signals_agree(self):
        privacy = eco_collector.provenance("public", "machine-derived")
        visibility = eco_collector.provenance("public", "probed")
        self.assertEqual(eco_collector.derive_tier(privacy, visibility), "public")

    def test_fails_closed_when_declared_public_but_actually_private(self):
        privacy = eco_collector.provenance("public", "machine-derived")
        visibility = eco_collector.provenance("private", "probed")
        self.assertEqual(eco_collector.derive_tier(privacy, visibility), "internal")

    def test_fails_closed_when_either_signal_is_unavailable(self):
        privacy = eco_collector.provenance("public", "machine-derived")
        self.assertEqual(eco_collector.derive_tier(privacy, eco_collector.unavailable()), "internal")
        visibility = eco_collector.provenance("public", "probed")
        self.assertEqual(eco_collector.derive_tier(eco_collector.unavailable(), visibility), "internal")


class TestCollectDeterminism(unittest.TestCase):
    def test_generated_at_is_injectable_for_reproducible_runs(self):
        # Exercises the real collect() end-to-end against whatever sibling
        # checkouts actually exist on this machine -- individual repo
        # facts will vary, but generated_at must exactly match what was
        # injected, per the schema's own stated contract for this field.
        fixed_timestamp = "2026-01-01T00:00:00+00:00"
        doc = eco_collector.collect(eco_collector.DEFAULT_CONFIG, now=fixed_timestamp)
        self.assertEqual(doc["generated_at"], fixed_timestamp)
        self.assertEqual(doc["schema_version"], "veil.ecostatus.v1")
        self.assertEqual(len(doc["repos"]), 6)


if __name__ == "__main__":
    unittest.main()
