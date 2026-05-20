import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_book_data.py"
SPEC = importlib.util.spec_from_file_location("build_book_data", SCRIPT_PATH)
build_book_data = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_book_data
SPEC.loader.exec_module(build_book_data)


class ChineseNumberParserTest(unittest.TestCase):
    def test_parses_common_chinese_chapter_numbers(self):
        parser = build_book_data.ChineseNumberParser()

        self.assertEqual(parser.parse("一"), 1)
        self.assertEqual(parser.parse("十"), 10)
        self.assertEqual(parser.parse("十一"), 11)
        self.assertEqual(parser.parse("一百七十二"), 172)
        self.assertEqual(parser.parse("两千四百四十六"), 2446)
        self.assertEqual(parser.parse("2446"), 2446)


class BookTextParserTest(unittest.TestCase):
    def parse_sample(self, text, page_chars=12):
        source = build_book_data.SourceText(
            path=Path("《样书》作者：测试.txt"),
            raw_bytes=text.encode("utf-8"),
            text=text,
            encoding="utf-8",
            sha256="sample",
        )
        return build_book_data.BookTextParser(page_chars=page_chars).parse(source)

    def test_extracts_volumes_chapters_and_pages_without_duplicate_text(self):
        parsed = self.parse_sample(
            "\n".join(
                [
                    "下载站说明",
                    "",
                    "第一卷 起始",
                    "",
                    "第一章 开始",
                    "第一段内容",
                    "第二段内容很长",
                    "第三段",
                    "",
                    "第二章 继续",
                    "下一章第一段",
                    "下一章第二段",
                ]
            ),
            page_chars=8,
        )

        self.assertEqual(parsed.title, "样书")
        self.assertEqual(parsed.author, "测试")
        self.assertEqual(len(parsed.front_matter), 1)
        self.assertEqual([volume.id for volume in parsed.volumes], ["v001"])
        self.assertEqual([chapter.id for chapter in parsed.chapters], ["c000001", "c000002"])
        self.assertEqual(parsed.chapters[0].volume_id, "v001")
        self.assertEqual([paragraph.text for paragraph in parsed.chapters[0].paragraphs], [
            "第一段内容",
            "第二段内容很长",
            "第三段",
        ])
        first_page = parsed.chapters[0].pages[0]
        self.assertEqual(first_page["paragraph_start_index"], 0)
        self.assertEqual(first_page["paragraph_end_index_exclusive"], 1)
        self.assertEqual(parsed.chapters[0].pages[-1]["next_page_id"], "c000002-p001")

    def test_records_duplicate_declared_chapter_numbers(self):
        parsed = self.parse_sample(
            "\n".join(
                [
                    "第一卷 起始",
                    "第一章 开始",
                    "内容",
                    "第二章 继续",
                    "内容",
                    "第二章 重复",
                    "内容",
                ]
            )
        )

        duplicate_anomalies = [
            anomaly
            for anomaly in parsed.anomalies
            if anomaly["type"] == "duplicate_declared_chapter_number"
        ]
        self.assertEqual(len(duplicate_anomalies), 1)
        self.assertEqual(duplicate_anomalies[0]["chapter_ids"], ["c000002", "c000003"])

    def test_creates_synthetic_volume_for_unvolumed_chapters(self):
        parsed = self.parse_sample(
            "\n".join(
                [
                    "第一章 序章",
                    "序章内容",
                    "第一卷 正文",
                    "第二章 正文开始",
                    "正文内容",
                ]
            )
        )

        self.assertEqual([volume.id for volume in parsed.volumes], ["v001", "v002"])
        self.assertTrue(parsed.volumes[0].is_synthetic)
        self.assertEqual(parsed.volumes[0].title, "未分卷")
        self.assertEqual(parsed.volumes[0].chapter_ids, ["c000001"])
        self.assertEqual(parsed.volumes[1].chapter_ids, ["c000002"])
        self.assertEqual(parsed.chapters[0].volume_id, "v001")
        self.assertEqual(parsed.chapters[1].volume_id, "v002")
        self.assertTrue(
            any(anomaly["type"] == "synthetic_unvolumed_volume" for anomaly in parsed.anomalies)
        )

    def test_writer_and_validator_accept_generated_output_and_reject_bad_page(self):
        parsed = self.parse_sample(
            "\n".join(
                [
                    "第一卷 起始",
                    "第一章 开始",
                    "段落一",
                    "段落二",
                ]
            )
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            build_book_data.BookDataWriter().write(
                parsed,
                output_dir,
                force=False,
                pretty=True,
            )
            validator = build_book_data.BookDataValidator()
            self.assertTrue(validator.validate(output_dir)["ok"])

            volume_path = output_dir / "volumes" / "v001.json"
            volume_data = json.loads(volume_path.read_text(encoding="utf-8"))
            volume_data["chapters"][0]["paragraphs"][0]["id"] = "wrong"
            volume_data["chapters"][0]["pages"][0]["chapter_id"] = "wrong"
            volume_path.write_text(
                json.dumps(volume_data, ensure_ascii=False),
                encoding="utf-8",
            )

            report = validator.validate(output_dir)
            self.assertFalse(report["ok"])
            self.assertTrue(
                any("Paragraph id mismatch" in error for error in report["errors"])
            )
            self.assertTrue(
                any("chapter_id mismatch" in error for error in report["errors"])
            )


class SourceLoaderAndCliTest(unittest.TestCase):
    def test_loads_gb18030_fixture(self):
        text = "第一卷 起始\n第一章 开始\n中文内容\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "《样书》作者：测试.txt"
            path.write_bytes(text.encode("gb18030"))

            source = build_book_data.SourceLoader().load(path)

            self.assertEqual(source.encoding, "gb18030")
            self.assertIn("中文内容", source.text)

    def test_cli_build_and_validate_smoke(self):
        text = "第一卷 起始\n第一章 开始\n第一段\n第二段\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_path = tmp_path / "《样书》作者：测试.txt"
            output_dir = tmp_path / "book_data"
            source_path.write_bytes(text.encode("gb18030"))

            build_code = build_book_data.BookDataCli().run(
                [
                    "build",
                    "--input",
                    str(source_path),
                    "--output",
                    str(output_dir),
                    "--page-chars",
                    "8",
                ]
            )
            validate_code = build_book_data.BookDataCli().run(
                ["validate", "--output", str(output_dir)]
            )

            self.assertEqual(build_code, 0)
            self.assertEqual(validate_code, 0)
            self.assertTrue((output_dir / "book.json").exists())
            self.assertTrue((output_dir / "volumes" / "v001.json").exists())


if __name__ == "__main__":
    unittest.main()
