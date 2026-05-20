import tempfile
import unittest
from pathlib import Path

from init_optimizer_run import main, normalize_slug


class InitOptimizerRunTests(unittest.TestCase):
    def test_normalize_slug(self) -> None:
        self.assertEqual(normalize_slug("Set Discovery Optimizer!"), "set-discovery-optimizer")

    def test_creates_standard_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "run"
            exit_code = main(
                [
                    "--slug",
                    "Set Discovery",
                    "--target",
                    "src/discovery.py::discover_sets",
                    "--goal",
                    "Find more valid sets without reducing precision.",
                    "--primary-metric",
                    "recall higher_is_better",
                    "--guard-metric",
                    "precision must stay >= baseline",
                    "--secondary-metric",
                    "p95 runtime lower_is_better",
                    "--benchmark-command",
                    "python benchmark.py",
                    "--verify-command",
                    "pytest tests/test_discover.py",
                    "--output-dir",
                    str(output_dir),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "optimizer_brief.md").exists())
            self.assertTrue((output_dir / "ideas.tsv").exists())
            self.assertTrue((output_dir / "results.tsv").exists())
            self.assertTrue((output_dir / "report.md").exists())
            self.assertIn("baseline", (output_dir / "results.tsv").read_text(encoding="utf-8"))

    def test_existing_files_are_not_overwritten_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "run"
            output_dir.mkdir()
            brief = output_dir / "optimizer_brief.md"
            brief.write_text("existing", encoding="utf-8")

            exit_code = main(
                [
                    "--slug",
                    "safe",
                    "--target",
                    "module.func",
                    "--goal",
                    "Improve metric.",
                    "--primary-metric",
                    "score higher_is_better",
                    "--output-dir",
                    str(output_dir),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(brief.read_text(encoding="utf-8"), "existing")
            self.assertTrue((output_dir / "ideas.tsv").exists())


if __name__ == "__main__":
    unittest.main()
