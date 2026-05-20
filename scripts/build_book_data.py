#!/usr/bin/env python3
"""Build website-ready structured data from a plain-text Chinese novel."""

import argparse
import datetime as dt
import hashlib
import json
import logging
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


LOG = logging.getLogger("build_book_data")
SCHEMA_VERSION = "book-data-v1"


@dataclass
class SourceText:
    path: Path
    raw_bytes: bytes
    text: str
    encoding: str
    sha256: str

    @property
    def lines(self) -> List[str]:
        return self.text.splitlines()


@dataclass
class Paragraph:
    id: str
    order: int
    text: str
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "text": self.text,
            "char_count": self.char_count,
        }


@dataclass
class Chapter:
    id: str
    order: int
    title: str
    declared_number_text: str
    declared_number: Optional[int]
    source_line: int
    volume_id: Optional[str]
    volume_order: Optional[int]
    paragraphs: List[Paragraph] = field(default_factory=list)
    pages: List[Dict[str, Any]] = field(default_factory=list)
    content_start_line: Optional[int] = None
    content_end_line: Optional[int] = None
    anomalies: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def char_count(self) -> int:
        return sum(paragraph.char_count for paragraph in self.paragraphs)

    def manifest_entry(self, volume_file: Optional[str]) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "title": self.title,
            "declared_number_text": self.declared_number_text,
            "declared_number": self.declared_number,
            "volume_id": self.volume_id,
            "volume_order": self.volume_order,
            "volume_file": volume_file,
            "source_span": {
                "heading_line": self.source_line,
                "content_start_line": self.content_start_line,
                "content_end_line": self.content_end_line,
            },
            "paragraph_count": len(self.paragraphs),
            "char_count": self.char_count,
            "page_count": len(self.pages),
            "anomaly_count": len(self.anomalies),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "title": self.title,
            "declared_number_text": self.declared_number_text,
            "declared_number": self.declared_number,
            "volume_id": self.volume_id,
            "volume_order": self.volume_order,
            "source_span": {
                "heading_line": self.source_line,
                "content_start_line": self.content_start_line,
                "content_end_line": self.content_end_line,
            },
            "paragraph_count": len(self.paragraphs),
            "char_count": self.char_count,
            "page_count": len(self.pages),
            "paragraphs": [paragraph.to_dict() for paragraph in self.paragraphs],
            "pages": self.pages,
            "anomalies": self.anomalies,
        }


@dataclass
class Volume:
    id: str
    order: int
    title: str
    declared_number_text: str
    declared_number: Optional[int]
    source_line: Optional[int]
    is_synthetic: bool = False
    chapter_ids: List[str] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)

    def manifest_entry(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order": self.order,
            "title": self.title,
            "declared_number_text": self.declared_number_text,
            "declared_number": self.declared_number,
            "source_line": self.source_line,
            "is_synthetic": self.is_synthetic,
            "chapter_count": len(self.chapter_ids),
            "chapter_ids": self.chapter_ids,
            "file": "volumes/%s.json" % self.id,
            "anomaly_count": len(self.anomalies),
        }

    def to_dict(self, chapters: List[Chapter]) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "id": self.id,
            "order": self.order,
            "title": self.title,
            "declared_number_text": self.declared_number_text,
            "declared_number": self.declared_number,
            "source_line": self.source_line,
            "is_synthetic": self.is_synthetic,
            "chapter_count": len(chapters),
            "chapter_ids": [chapter.id for chapter in chapters],
            "chapters": [chapter.to_dict() for chapter in chapters],
            "anomalies": self.anomalies,
        }


@dataclass
class ParsedBook:
    source: SourceText
    title: str
    author: Optional[str]
    volumes: List[Volume]
    chapters: List[Chapter]
    front_matter: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    page_chars: int

    def chapter_by_id(self) -> Dict[str, Chapter]:
        return {chapter.id: chapter for chapter in self.chapters}

    def volume_by_id(self) -> Dict[str, Volume]:
        return {volume.id: volume for volume in self.volumes}


class ChineseNumberParser:
    DIGITS = {
        "零": 0,
        "〇": 0,
        "一": 1,
        "二": 2,
        "两": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000}

    def parse(self, value: str) -> Optional[int]:
        if value.isdigit():
            return int(value)

        total = 0
        section = 0
        number = 0
        for char in value:
            if char in self.DIGITS:
                number = self.DIGITS[char]
                continue
            if char not in self.UNITS:
                return None

            unit = self.UNITS[char]
            if unit == 10000:
                section = (section + number) * unit
                total += section
                section = 0
            else:
                if number == 0:
                    number = 1
                section += number * unit
            number = 0
        return total + section + number


class SourceLoader:
    CANDIDATE_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "gbk")

    def load(self, path: Path) -> SourceText:
        raw_bytes = path.read_bytes()
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        errors: List[str] = []
        for encoding in self.CANDIDATE_ENCODINGS:
            try:
                text = raw_bytes.decode(encoding)
            except UnicodeDecodeError as exc:
                errors.append("%s:%s" % (encoding, exc.reason))
                continue
            if self._looks_like_text(text):
                LOG.info("Loaded source with %s encoding", encoding)
                return SourceText(path, raw_bytes, text, encoding, sha256)

        raise UnicodeDecodeError(
            "unknown",
            raw_bytes,
            0,
            1,
            "No supported encoding matched: %s" % ", ".join(errors),
        )

    def _looks_like_text(self, text: str) -> bool:
        if not text:
            return False
        sample = text[:20000]
        cjk_count = sum(1 for char in sample if "\u4e00" <= char <= "\u9fff")
        return cjk_count > 100 or len(sample) < 1000


class MetadataParser:
    FILENAME_RE = re.compile(r"《(?P<title>[^》]+)》.*作者[：:](?P<author>[^.。]+)")

    def parse(self, path: Path) -> Tuple[str, Optional[str]]:
        match = self.FILENAME_RE.search(path.name)
        if match:
            return match.group("title").strip(), match.group("author").strip()
        return path.stem, None


class BookTextParser:
    HEADING_NUMBER = r"[\d零〇一二三四五六七八九十百千万两]+"
    VOLUME_RE = re.compile(
        r"^第(?P<number>%s)[卷部集](?P<suffix>(?:\s+|　+|：|:|$).{0,80})$"
        % HEADING_NUMBER
    )
    CHAPTER_RE = re.compile(
        r"^(?:正文\s*)?第(?P<number>%s)章(?P<suffix>(?:\s+|　+|：|:|$).{0,80})$"
        % HEADING_NUMBER
    )

    def __init__(self, page_chars: int) -> None:
        self.page_chars = page_chars
        self.number_parser = ChineseNumberParser()
        self.metadata_parser = MetadataParser()

    def parse(self, source: SourceText) -> ParsedBook:
        title, author = self.metadata_parser.parse(source.path)
        lines = source.lines
        volumes: List[Volume] = []
        chapters: List[Chapter] = []
        front_matter: List[Dict[str, Any]] = []
        markers: List[Tuple[int, str, str]] = []
        current_volume: Optional[Volume] = None

        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue

            volume_match = self.VOLUME_RE.match(stripped)
            if volume_match:
                volume = self._build_volume(
                    volume_match,
                    stripped,
                    line_number,
                    len(volumes) + 1,
                )
                volumes.append(volume)
                current_volume = volume
                markers.append((line_number, "volume", volume.id))
                continue

            chapter_match = self.CHAPTER_RE.match(stripped)
            if chapter_match:
                if current_volume is None:
                    current_volume = self._build_synthetic_volume(len(volumes) + 1)
                    volumes.append(current_volume)
                chapter = self._build_chapter(
                    chapter_match,
                    stripped,
                    line_number,
                    current_volume,
                    len(chapters) + 1,
                )
                chapters.append(chapter)
                if current_volume is not None:
                    current_volume.chapter_ids.append(chapter.id)
                markers.append((line_number, "chapter", chapter.id))
                continue

            if not chapters:
                front_matter.append({"line": line_number, "text": stripped})

        self._attach_paragraphs(lines, chapters, markers)
        self._attach_pages(chapters)
        anomalies = self._attach_anomalies(volumes, chapters)
        LOG.info(
            "Parsed %s volumes, %s chapters, %s pages",
            len(volumes),
            len(chapters),
            sum(len(chapter.pages) for chapter in chapters),
        )
        return ParsedBook(
            source=source,
            title=title,
            author=author,
            volumes=volumes,
            chapters=chapters,
            front_matter=front_matter,
            anomalies=anomalies,
            page_chars=self.page_chars,
        )

    def _build_volume(
        self,
        match: re.Match,
        title: str,
        line_number: int,
        order: int,
    ) -> Volume:
        number_text = match.group("number")
        declared_number = self.number_parser.parse(number_text)
        return Volume(
            id="v%03d" % order,
            order=order,
            title=title,
            declared_number_text=number_text,
            declared_number=declared_number,
            source_line=line_number,
        )

    def _build_synthetic_volume(self, order: int) -> Volume:
        return Volume(
            id="v%03d" % order,
            order=order,
            title="未分卷",
            declared_number_text="",
            declared_number=None,
            source_line=None,
            is_synthetic=True,
        )

    def _build_chapter(
        self,
        match: re.Match,
        title: str,
        line_number: int,
        current_volume: Optional[Volume],
        order: int,
    ) -> Chapter:
        number_text = match.group("number")
        declared_number = self.number_parser.parse(number_text)
        volume_id = current_volume.id if current_volume is not None else None
        volume_order = current_volume.order if current_volume is not None else None
        return Chapter(
            id="c%06d" % order,
            order=order,
            title=title,
            declared_number_text=number_text,
            declared_number=declared_number,
            source_line=line_number,
            volume_id=volume_id,
            volume_order=volume_order,
        )

    def _attach_paragraphs(
        self,
        lines: List[str],
        chapters: List[Chapter],
        markers: List[Tuple[int, str, str]],
    ) -> None:
        marker_lines = sorted(line_number for line_number, _, _ in markers)
        chapter_by_id = {chapter.id: chapter for chapter in chapters}
        for index, (line_number, marker_type, marker_id) in enumerate(markers):
            if marker_type != "chapter":
                continue
            chapter = chapter_by_id[marker_id]
            next_line = (
                marker_lines[index + 1]
                if index + 1 < len(marker_lines)
                else len(lines) + 1
            )
            content_start = line_number + 1
            content_end = next_line - 1
            chapter.content_start_line = content_start
            chapter.content_end_line = content_end
            paragraph_order = 1
            for raw_line in lines[content_start - 1 : content_end]:
                paragraph_text = raw_line.strip()
                if not paragraph_text:
                    continue
                paragraph = Paragraph(
                    id="%s-para-%04d" % (chapter.id, paragraph_order),
                    order=paragraph_order,
                    text=paragraph_text,
                    char_count=len(paragraph_text),
                )
                chapter.paragraphs.append(paragraph)
                paragraph_order += 1

    def _attach_pages(self, chapters: List[Chapter]) -> None:
        all_pages: List[Dict[str, Any]] = []
        for chapter in chapters:
            pages = self._paginate_chapter(chapter)
            chapter.pages = pages
            all_pages.extend(pages)

        for index, page in enumerate(all_pages):
            page["prev_page_id"] = all_pages[index - 1]["id"] if index > 0 else None
            page["next_page_id"] = (
                all_pages[index + 1]["id"] if index + 1 < len(all_pages) else None
            )

    def _paginate_chapter(self, chapter: Chapter) -> List[Dict[str, Any]]:
        if not chapter.paragraphs:
            chapter.anomalies.append(
                {
                    "type": "empty_chapter",
                    "message": "Chapter has no non-empty paragraphs.",
                }
            )
            return []

        pages: List[Dict[str, Any]] = []
        start_index = 0
        running_chars = 0
        for index, paragraph in enumerate(chapter.paragraphs):
            if index > start_index and running_chars + paragraph.char_count > self.page_chars:
                pages.append(
                    self._page_dict(
                        chapter,
                        len(pages) + 1,
                        start_index,
                        index,
                        running_chars,
                    )
                )
                start_index = index
                running_chars = 0
            running_chars += paragraph.char_count

        pages.append(
            self._page_dict(
                chapter,
                len(pages) + 1,
                start_index,
                len(chapter.paragraphs),
                running_chars,
            )
        )
        return pages

    def _page_dict(
        self,
        chapter: Chapter,
        page_order: int,
        start_index: int,
        end_index: int,
        char_count: int,
    ) -> Dict[str, Any]:
        return {
            "id": "%s-p%03d" % (chapter.id, page_order),
            "order": page_order,
            "chapter_id": chapter.id,
            "paragraph_start_index": start_index,
            "paragraph_end_index_exclusive": end_index,
            "char_count": char_count,
            "prev_page_id": None,
            "next_page_id": None,
        }

    def _attach_anomalies(
        self,
        volumes: List[Volume],
        chapters: List[Chapter],
    ) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        anomalies.extend(self._record_synthetic_volumes(volumes))
        anomalies.extend(self._record_duplicate_volumes(volumes))
        anomalies.extend(self._record_duplicate_chapters(chapters))
        anomalies.extend(self._record_sequence_anomalies(chapters))
        anomalies.extend(self._record_empty_content(chapters))
        return anomalies

    def _record_synthetic_volumes(self, volumes: List[Volume]) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        for volume in volumes:
            if not volume.is_synthetic:
                continue
            anomaly = {
                "type": "synthetic_unvolumed_volume",
                "volume_id": volume.id,
                "message": "Chapters appeared before any source volume heading.",
            }
            anomalies.append(anomaly)
            volume.anomalies.append(anomaly)
        return anomalies

    def _record_duplicate_volumes(self, volumes: List[Volume]) -> List[Dict[str, Any]]:
        by_number: Dict[Optional[int], List[Volume]] = {}
        for volume in volumes:
            by_number.setdefault(volume.declared_number, []).append(volume)

        anomalies: List[Dict[str, Any]] = []
        for declared_number, group in by_number.items():
            if declared_number is None or len(group) <= 1:
                continue
            anomaly = {
                "type": "duplicate_declared_volume_number",
                "declared_number": declared_number,
                "volume_ids": [volume.id for volume in group],
                "message": "Multiple volumes share the same declared number.",
            }
            anomalies.append(anomaly)
            for volume in group:
                volume.anomalies.append(anomaly)
        return anomalies

    def _record_duplicate_chapters(self, chapters: List[Chapter]) -> List[Dict[str, Any]]:
        by_number: Dict[Optional[int], List[Chapter]] = {}
        for chapter in chapters:
            by_number.setdefault(chapter.declared_number, []).append(chapter)

        anomalies: List[Dict[str, Any]] = []
        for declared_number, group in by_number.items():
            if declared_number is None or len(group) <= 1:
                continue
            anomaly = {
                "type": "duplicate_declared_chapter_number",
                "declared_number": declared_number,
                "chapter_ids": [chapter.id for chapter in group],
                "message": "Multiple chapters share the same declared number.",
            }
            anomalies.append(anomaly)
            for chapter in group:
                chapter.anomalies.append(anomaly)
        return anomalies

    def _record_sequence_anomalies(self, chapters: List[Chapter]) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        previous: Optional[Chapter] = None
        for chapter in chapters:
            if previous is None:
                previous = chapter
                continue
            if (
                previous.declared_number is not None
                and chapter.declared_number is not None
                and chapter.declared_number != previous.declared_number + 1
            ):
                anomaly = {
                    "type": "chapter_declared_number_sequence",
                    "previous_chapter_id": previous.id,
                    "previous_declared_number": previous.declared_number,
                    "chapter_id": chapter.id,
                    "declared_number": chapter.declared_number,
                    "message": "Declared chapter number is not previous + 1.",
                }
                anomalies.append(anomaly)
                chapter.anomalies.append(anomaly)
            previous = chapter
        return anomalies

    def _record_empty_content(self, chapters: List[Chapter]) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        for chapter in chapters:
            if chapter.paragraphs:
                continue
            anomaly = {
                "type": "empty_chapter",
                "chapter_id": chapter.id,
                "message": "Chapter has no non-empty paragraphs.",
            }
            anomalies.append(anomaly)
            chapter.anomalies.append(anomaly)
        return anomalies


class BookDataWriter:
    def write(
        self,
        parsed: ParsedBook,
        output_dir: Path,
        force: bool,
        pretty: bool,
    ) -> None:
        self._prepare_output_dir(output_dir, force)
        volumes_dir = output_dir / "volumes"
        volumes_dir.mkdir(parents=True, exist_ok=True)

        chapters_by_volume: Dict[str, List[Chapter]] = {}
        for chapter in parsed.chapters:
            if chapter.volume_id is not None:
                chapters_by_volume.setdefault(chapter.volume_id, []).append(chapter)

        volume_by_id = parsed.volume_by_id()
        for volume in parsed.volumes:
            volume_path = volumes_dir / ("%s.json" % volume.id)
            volume_chapters = chapters_by_volume.get(volume.id, [])
            self._write_json(volume_path, volume.to_dict(volume_chapters), pretty)
            LOG.info(
                "Wrote %s with %s chapters",
                volume_path,
                len(volume_chapters),
            )

        book_manifest = self._book_manifest(parsed, volume_by_id)
        self._write_json(output_dir / "book.json", book_manifest, True)
        self._write_json(output_dir / "inspection_report.json", self.inspect(parsed), True)
        LOG.info("Wrote manifest and inspection report to %s", output_dir)

    def ensure_can_write(self, output_dir: Path, force: bool) -> None:
        existing = self._existing_generated_paths(output_dir)
        if existing and not force:
            raise FileExistsError(
                "Output already contains generated files. Re-run with --force: %s"
                % ", ".join(str(path) for path in existing)
            )

    def inspect(self, parsed: ParsedBook) -> Dict[str, Any]:
        nonempty_lines = [line for line in parsed.source.lines if line.strip()]
        chapter_char_counts = [chapter.char_count for chapter in parsed.chapters]
        chapter_page_counts = [len(chapter.pages) for chapter in parsed.chapters]
        paragraph_lines = sum(len(chapter.paragraphs) for chapter in parsed.chapters)
        source_volume_heading_count = sum(
            1 for volume in parsed.volumes if not volume.is_synthetic
        )
        accounted_nonempty_lines = (
            len(parsed.front_matter)
            + source_volume_heading_count
            + len(parsed.chapters)
            + paragraph_lines
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "source": {
                "path": str(parsed.source.path),
                "filename": parsed.source.path.name,
                "encoding": parsed.source.encoding,
                "bytes": len(parsed.source.raw_bytes),
                "sha256": parsed.source.sha256,
                "chars": len(parsed.source.text),
                "lines": len(parsed.source.lines),
                "nonempty_lines": len(nonempty_lines),
                "blank_lines": len(parsed.source.lines) - len(nonempty_lines),
            },
            "metadata": {
                "title": parsed.title,
                "author": parsed.author,
            },
            "counts": {
                "volumes": len(parsed.volumes),
                "chapters": len(parsed.chapters),
                "paragraphs": sum(len(chapter.paragraphs) for chapter in parsed.chapters),
                "pages": sum(len(chapter.pages) for chapter in parsed.chapters),
                "front_matter_lines": len(parsed.front_matter),
                "synthetic_volumes": sum(1 for volume in parsed.volumes if volume.is_synthetic),
                "anomalies": len(parsed.anomalies),
            },
            "line_accounting": {
                "nonempty_source_lines": len(nonempty_lines),
                "front_matter_lines": len(parsed.front_matter),
                "volume_heading_lines": source_volume_heading_count,
                "synthetic_volume_count": sum(
                    1 for volume in parsed.volumes if volume.is_synthetic
                ),
                "chapter_heading_lines": len(parsed.chapters),
                "paragraph_lines": paragraph_lines,
                "accounted_nonempty_lines": accounted_nonempty_lines,
                "unaccounted_nonempty_lines": len(nonempty_lines) - accounted_nonempty_lines,
            },
            "chapter_stats": {
                "char_count": self._stats(chapter_char_counts),
                "page_count": self._stats(chapter_page_counts),
            },
            "samples": {
                "first_volumes": [self._volume_sample(volume) for volume in parsed.volumes[:5]],
                "first_chapters": [
                    chapter.manifest_entry(self._volume_file(chapter)) for chapter in parsed.chapters[:5]
                ],
                "last_chapters": [
                    chapter.manifest_entry(self._volume_file(chapter)) for chapter in parsed.chapters[-5:]
                ],
                "anomalies": parsed.anomalies[:20],
            },
        }

    def _book_manifest(
        self,
        parsed: ParsedBook,
        volume_by_id: Dict[str, Volume],
    ) -> Dict[str, Any]:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": now,
            "metadata": {
                "title": parsed.title,
                "author": parsed.author,
                "source_filename": parsed.source.path.name,
                "source_encoding": parsed.source.encoding,
                "source_sha256": parsed.source.sha256,
            },
            "stats": {
                "volume_count": len(parsed.volumes),
                "chapter_count": len(parsed.chapters),
                "paragraph_count": sum(len(chapter.paragraphs) for chapter in parsed.chapters),
                "page_count": sum(len(chapter.pages) for chapter in parsed.chapters),
                "synthetic_volume_count": sum(
                    1 for volume in parsed.volumes if volume.is_synthetic
                ),
                "anomaly_count": len(parsed.anomalies),
            },
            "pagination": {
                "strategy": "paragraph_span",
                "target_chars": parsed.page_chars,
                "text_storage": "paragraphs",
                "page_storage": "paragraph_start_index/end_index_exclusive",
            },
            "front_matter": parsed.front_matter,
            "volumes": [volume.manifest_entry() for volume in parsed.volumes],
            "chapters": [
                chapter.manifest_entry(
                    "volumes/%s.json" % volume_by_id[chapter.volume_id].id
                    if chapter.volume_id in volume_by_id
                    else None
                )
                for chapter in parsed.chapters
            ],
            "anomalies": parsed.anomalies,
        }

    def _prepare_output_dir(self, output_dir: Path, force: bool) -> None:
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
            return

        self.ensure_can_write(output_dir, force)
        existing = self._existing_generated_paths(output_dir)

        for path in existing:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def _existing_generated_paths(self, output_dir: Path) -> List[Path]:
        generated_paths = [
            output_dir / "book.json",
            output_dir / "inspection_report.json",
            output_dir / "validation_report.json",
            output_dir / "volumes",
        ]
        return [path for path in generated_paths if path.exists()]

    def _write_json(self, path: Path, data: Dict[str, Any], pretty: bool) -> None:
        with path.open("w", encoding="utf-8") as handle:
            if pretty:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            else:
                json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")

    def _stats(self, values: List[int]) -> Dict[str, Optional[float]]:
        if not values:
            return {"min": None, "median": None, "p95": None, "max": None}
        sorted_values = sorted(values)
        median = sorted_values[len(sorted_values) // 2]
        p95 = sorted_values[int(len(sorted_values) * 0.95)]
        return {
            "min": sorted_values[0],
            "median": median,
            "p95": p95,
            "max": sorted_values[-1],
        }

    def _volume_file(self, chapter: Chapter) -> Optional[str]:
        if chapter.volume_id is None:
            return None
        return "volumes/%s.json" % chapter.volume_id

    def _volume_sample(self, volume: Volume) -> Dict[str, Any]:
        return {
            "id": volume.id,
            "order": volume.order,
            "title": volume.title,
            "declared_number_text": volume.declared_number_text,
            "declared_number": volume.declared_number,
            "source_line": volume.source_line,
            "is_synthetic": volume.is_synthetic,
            "chapter_count": len(volume.chapter_ids),
            "first_chapter_id": volume.chapter_ids[0] if volume.chapter_ids else None,
            "last_chapter_id": volume.chapter_ids[-1] if volume.chapter_ids else None,
            "file": "volumes/%s.json" % volume.id,
            "anomaly_count": len(volume.anomalies),
        }


class BookDataValidator:
    def validate(self, output_dir: Path) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        book_path = output_dir / "book.json"
        if not book_path.exists():
            return {
                "ok": False,
                "errors": ["Missing book.json at %s" % book_path],
                "warnings": [],
                "stats": {},
            }

        book = self._read_json(book_path)
        if book.get("schema_version") != SCHEMA_VERSION:
            errors.append("Unexpected schema_version in book.json")

        manifest_chapter_ids = [chapter["id"] for chapter in book.get("chapters", [])]
        manifest_chapter_by_id = {
            chapter["id"]: chapter for chapter in book.get("chapters", [])
        }
        self._check_unique("chapter id", manifest_chapter_ids, errors)
        manifest_volume_ids = [volume["id"] for volume in book.get("volumes", [])]
        self._check_unique("volume id", manifest_volume_ids, errors)

        pages_in_order: List[Dict[str, Any]] = []
        loaded_chapter_ids: List[str] = []
        computed_stats = {
            "volume_count": 0,
            "chapter_count": 0,
            "paragraph_count": 0,
            "page_count": 0,
            "char_count": 0,
        }

        for volume in book.get("volumes", []):
            computed_stats["volume_count"] += 1
            volume_path = output_dir / volume["file"]
            if not volume_path.exists():
                errors.append("Missing volume file: %s" % volume_path)
                continue
            volume_data = self._read_json(volume_path)
            if volume_data.get("schema_version") != SCHEMA_VERSION:
                errors.append("Unexpected schema_version in %s" % volume_path)
            if volume_data.get("id") != volume.get("id"):
                errors.append("Volume id differs between manifest and %s" % volume_path)
            volume_chapters = volume_data.get("chapters", [])
            if volume_data.get("chapter_count") != len(volume_chapters):
                errors.append("Volume chapter_count mismatch in %s" % volume_path)
            volume_chapter_ids = [chapter["id"] for chapter in volume_chapters]
            if volume_chapter_ids != volume.get("chapter_ids", []):
                errors.append("Chapter ids differ between manifest and %s" % volume_path)

            for chapter in volume_chapters:
                loaded_chapter_ids.append(chapter["id"])
                self._validate_manifest_chapter(
                    manifest_chapter_by_id.get(chapter["id"]),
                    chapter,
                    volume.get("file"),
                    errors,
                )
                self._validate_chapter(chapter, pages_in_order, errors, warnings)
                computed_stats["chapter_count"] += 1
                computed_stats["paragraph_count"] += len(chapter.get("paragraphs", []))
                computed_stats["page_count"] += len(chapter.get("pages", []))
                computed_stats["char_count"] += chapter.get("char_count", 0)

        if manifest_chapter_ids != loaded_chapter_ids:
            errors.append("Manifest chapter order differs from loaded volume chapter order")

        self._validate_page_links(pages_in_order, errors)
        book_stats = book.get("stats", {})
        for key in ["volume_count", "chapter_count", "paragraph_count", "page_count"]:
            if book_stats.get(key) != computed_stats[key]:
                errors.append(
                    "book.stats.%s=%s but computed %s"
                    % (key, book_stats.get(key), computed_stats[key])
                )

        return {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "stats": computed_stats,
        }

    def write_report(self, output_dir: Path, report: Dict[str, Any]) -> None:
        with (output_dir / "validation_report.json").open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def _validate_chapter(
        self,
        chapter: Dict[str, Any],
        pages_in_order: List[Dict[str, Any]],
        errors: List[str],
        warnings: List[str],
    ) -> None:
        paragraphs = chapter.get("paragraphs", [])
        pages = chapter.get("pages", [])
        if not paragraphs:
            errors.append("Chapter %s has no paragraphs" % chapter.get("id"))
        if not pages:
            errors.append("Chapter %s has no pages" % chapter.get("id"))
        if chapter.get("paragraph_count") != len(paragraphs):
            errors.append("Chapter %s paragraph_count mismatch" % chapter.get("id"))
        if chapter.get("page_count") != len(pages):
            errors.append("Chapter %s page_count mismatch" % chapter.get("id"))

        paragraph_chars = sum(paragraph.get("char_count", 0) for paragraph in paragraphs)
        if paragraph_chars != chapter.get("char_count"):
            errors.append("Chapter %s char_count does not match paragraphs" % chapter.get("id"))

        for index, paragraph in enumerate(paragraphs, 1):
            expected_id = "%s-para-%04d" % (chapter.get("id"), index)
            if paragraph.get("id") != expected_id:
                errors.append(
                    "Paragraph id mismatch in %s: %s != %s"
                    % (chapter.get("id"), paragraph.get("id"), expected_id)
                )
            if paragraph.get("order") != index:
                errors.append(
                    "Paragraph order mismatch in %s at %s"
                    % (chapter.get("id"), paragraph.get("id"))
                )
            text = paragraph.get("text")
            if not isinstance(text, str) or not text:
                errors.append("Paragraph %s has invalid text" % paragraph.get("id"))
                continue
            if paragraph.get("char_count") != len(text):
                errors.append("Paragraph %s char_count mismatch" % paragraph.get("id"))

        expected_start = 0
        for page_index, page in enumerate(pages, 1):
            expected_page_id = "%s-p%03d" % (chapter.get("id"), page_index)
            if page.get("id") != expected_page_id:
                errors.append(
                    "Page id mismatch in %s: %s != %s"
                    % (chapter.get("id"), page.get("id"), expected_page_id)
                )
            if page.get("order") != page_index:
                errors.append("Page %s order mismatch" % page.get("id"))
            if page.get("chapter_id") != chapter.get("id"):
                errors.append("Page %s chapter_id mismatch" % page.get("id"))
            start = page.get("paragraph_start_index")
            end = page.get("paragraph_end_index_exclusive")
            if not isinstance(start, int):
                errors.append("Page %s has invalid paragraph start" % page.get("id"))
                continue
            if start != expected_start:
                errors.append(
                    "Page %s starts at %s, expected %s"
                    % (page.get("id"), start, expected_start)
                )
            if not isinstance(end, int) or end <= start or end > len(paragraphs):
                errors.append("Page %s has invalid paragraph range" % page.get("id"))
                continue
            page_chars = sum(paragraphs[index].get("char_count", 0) for index in range(start, end))
            if page_chars != page.get("char_count"):
                errors.append("Page %s char_count mismatch" % page.get("id"))
            expected_start = end
            pages_in_order.append(page)

        if expected_start != len(paragraphs):
            errors.append("Chapter %s pages do not cover all paragraphs" % chapter.get("id"))
        if chapter.get("anomalies"):
            warnings.append(
                "Chapter %s has %s anomalies"
                % (chapter.get("id"), len(chapter.get("anomalies")))
            )

    def _validate_manifest_chapter(
        self,
        manifest_chapter: Optional[Dict[str, Any]],
        volume_chapter: Dict[str, Any],
        volume_file: Optional[str],
        errors: List[str],
    ) -> None:
        chapter_id = volume_chapter.get("id")
        if manifest_chapter is None:
            errors.append("Chapter %s exists in volume but not manifest" % chapter_id)
            return

        comparable_fields = [
            "order",
            "title",
            "declared_number_text",
            "declared_number",
            "volume_id",
            "volume_order",
            "paragraph_count",
            "char_count",
            "page_count",
            "anomaly_count",
        ]
        for field_name in comparable_fields:
            expected = manifest_chapter.get(field_name)
            if field_name == "page_count":
                actual = len(volume_chapter.get("pages", []))
            elif field_name == "paragraph_count":
                actual = len(volume_chapter.get("paragraphs", []))
            elif field_name == "anomaly_count":
                actual = len(volume_chapter.get("anomalies", []))
            else:
                actual = volume_chapter.get(field_name)
            if expected != actual:
                errors.append(
                    "Manifest mismatch for %s.%s: %s != %s"
                    % (chapter_id, field_name, expected, actual)
                )
        if manifest_chapter.get("volume_file") != volume_file:
            errors.append("Manifest volume_file mismatch for %s" % chapter_id)

    def _validate_page_links(
        self,
        pages_in_order: List[Dict[str, Any]],
        errors: List[str],
    ) -> None:
        page_ids = [page["id"] for page in pages_in_order]
        self._check_unique("page id", page_ids, errors)
        for index, page in enumerate(pages_in_order):
            expected_prev = page_ids[index - 1] if index > 0 else None
            expected_next = page_ids[index + 1] if index + 1 < len(page_ids) else None
            if page.get("prev_page_id") != expected_prev:
                errors.append("Page %s has wrong prev_page_id" % page.get("id"))
            if page.get("next_page_id") != expected_next:
                errors.append("Page %s has wrong next_page_id" % page.get("id"))

    def _check_unique(self, label: str, values: List[str], errors: List[str]) -> None:
        seen = set()
        duplicates = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        if duplicates:
            errors.append("Duplicate %s values: %s" % (label, sorted(duplicates)))

    def _read_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


class BookDataCli:
    def run(self, argv: Optional[List[str]] = None) -> int:
        args = self._parse_args(argv)
        self._configure_logging(args.verbose)

        if args.command == "validate":
            report = BookDataValidator().validate(args.output)
            BookDataValidator().write_report(args.output, report)
            self._write_stdout_json(report)
            return 0 if report["ok"] else 1

        writer = BookDataWriter()
        if args.command == "build":
            try:
                writer.ensure_can_write(args.output, args.force)
            except FileExistsError as exc:
                LOG.error("%s", exc)
                return 1

        source = SourceLoader().load(args.input)
        parser = BookTextParser(page_chars=args.page_chars)
        parsed = parser.parse(source)

        if args.command == "inspect":
            self._write_stdout_json(writer.inspect(parsed))
            return 0

        if args.command == "build":
            writer.write(parsed, args.output, args.force, args.pretty)
            report = BookDataValidator().validate(args.output)
            BookDataValidator().write_report(args.output, report)
            LOG.info(
                "Validation %s with %s errors and %s warnings",
                "passed" if report["ok"] else "failed",
                len(report["errors"]),
                len(report["warnings"]),
            )
            return 0 if report["ok"] else 1

        raise ValueError("Unknown command: %s" % args.command)

    def _parse_args(self, argv: Optional[List[str]]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
        subparsers = parser.add_subparsers(dest="command", required=True)

        inspect_parser = subparsers.add_parser("inspect", help="Inspect source structure.")
        self._add_source_args(inspect_parser)

        build_parser = subparsers.add_parser("build", help="Build structured data.")
        self._add_source_args(build_parser)
        build_parser.add_argument(
            "--output",
            type=Path,
            default=Path("book_data"),
            help="Output directory for generated JSON.",
        )
        build_parser.add_argument(
            "--force",
            action="store_true",
            help="Replace prior generated files in the output directory.",
        )
        build_parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty-print volume JSON files.",
        )

        validate_parser = subparsers.add_parser("validate", help="Validate generated data.")
        validate_parser.add_argument(
            "--output",
            type=Path,
            default=Path("book_data"),
            help="Output directory containing generated JSON.",
        )
        return parser.parse_args(argv)

    def _add_source_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--input", required=True, type=Path, help="Source TXT path.")
        parser.add_argument(
            "--page-chars",
            type=int,
            default=2200,
            help="Target characters per reading page.",
        )

    def _configure_logging(self, verbose: bool) -> None:
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(levelname)s %(message)s",
        )

    def _write_stdout_json(self, data: Dict[str, Any]) -> None:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def main() -> int:
    return BookDataCli().run()


if __name__ == "__main__":
    raise SystemExit(main())
