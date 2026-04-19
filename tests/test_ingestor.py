"""
Tests for ingestor module (Layer 1).
Run with: pytest tests/test_ingestor.py -v

Covers:
  - supported_formats()
  - extract_outline() for PDF and DOCX
  - load_and_chunk() chunk schema, heading attachment, overlap behaviour
  - Error handling: unsupported format, missing file
"""

import io
import os
import struct
import tempfile
import textwrap
from pathlib import Path

import pytest

from modules.ingestor import (
    extract_outline,
    load_and_chunk,
    supported_formats,
)


# ---------------------------------------------------------------------------
# Helpers — create minimal in-memory test documents
# ---------------------------------------------------------------------------

def _make_pdf(tmp_path: Path, text_pages: list[str], title: str = "Test Doc") -> Path:
    """
    Create a minimal valid single/multi-page PDF using only the stdlib.
    Each string in ``text_pages`` becomes one page.
    No external dependency required.
    """
    import pypdf
    from pypdf import PdfWriter

    writer = PdfWriter()
    for text in text_pages:
        page = writer.add_blank_page(width=612, height=792)
        # pypdf doesn't support writing text directly; we build a raw content stream
        content = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET"
        page.merge_page(page)  # no-op merge to register the page
        # Inject raw content stream — simplest approach for test fixture
        from pypdf.generic import ContentStream, DecodedStreamObject
        stream = DecodedStreamObject()
        stream.set_data(content.encode())
        page["/Contents"] = stream

    out = tmp_path / "test.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    return out


def _make_docx(tmp_path: Path, paragraphs: list[tuple[str, str]]) -> Path:
    """
    Create a minimal DOCX.
    paragraphs: list of (style_name, text) e.g. [("Heading 1", "Intro"), ("Normal", "Body text")]
    Requires python-docx.
    """
    docx = pytest.importorskip("docx", reason="python-docx not installed")
    doc = docx.Document()
    for style, text in paragraphs:
        doc.add_paragraph(text, style=style)
    out = tmp_path / "test.docx"
    doc.save(str(out))
    return out


# ---------------------------------------------------------------------------
# supported_formats
# ---------------------------------------------------------------------------

class TestSupportedFormats:
    def test_contains_pdf(self):
        assert ".pdf" in supported_formats()

    def test_contains_docx(self):
        assert ".docx" in supported_formats()

    def test_returns_list_of_strings(self):
        fmts = supported_formats()
        assert isinstance(fmts, list)
        assert all(isinstance(f, str) for f in fmts)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_unsupported_extension_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported"):
            load_and_chunk("document.xyz")

    def test_unsupported_extension_in_extract_outline(self):
        with pytest.raises(ValueError, match="Unsupported"):
            extract_outline("document.txt")

    def test_missing_file_raises_file_not_found(self, tmp_path):
        ghost = tmp_path / "ghost.pdf"
        with pytest.raises(FileNotFoundError):
            load_and_chunk(str(ghost))

    def test_unsupported_raises_not_pdf_or_docx(self):
        """Verify the error mentions the extension."""
        with pytest.raises(ValueError, match=r"\.csv"):
            load_and_chunk("data.csv")


# ---------------------------------------------------------------------------
# DOCX tests (require python-docx)
# ---------------------------------------------------------------------------

class TestDocxIngestor:
    def test_docx_outline_extracts_headings(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Introduction"),
            ("Normal", "Some body text here."),
            ("Heading 2", "Background"),
            ("Normal", "More body text goes here for the background section."),
            ("Heading 1", "Conclusion"),
            ("Normal", "Final thoughts."),
        ])
        outline = extract_outline(str(path))
        assert "Introduction" in outline
        assert "Background" in outline
        assert "Conclusion" in outline

    def test_docx_outline_excludes_normal_paragraphs(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Section One"),
            ("Normal", "This is body text, not a heading."),
        ])
        outline = extract_outline(str(path))
        assert "This is body text, not a heading." not in outline

    def test_docx_chunks_have_required_keys(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Overview"),
            ("Normal", " ".join(["word"] * 200)),  # long enough to chunk
        ])
        chunks, outline = load_and_chunk(str(path), chunk_size=100, overlap=20)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text"    in chunk, "chunk missing 'text'"
            assert "source"  in chunk, "chunk missing 'source'"
            assert "page"    in chunk, "chunk missing 'page'"
            assert "heading" in chunk, "chunk missing 'heading'"

    def test_docx_source_is_filename_not_path(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Normal", " ".join(["word"] * 100)),
        ])
        chunks, _ = load_and_chunk(str(path), chunk_size=100, overlap=10)
        for chunk in chunks:
            assert "/" not in chunk["source"]
            assert "\\" not in chunk["source"]
            assert chunk["source"] == path.name

    def test_docx_chunk_text_is_non_empty_string(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Normal", "Hello world. " * 50),
        ])
        chunks, _ = load_and_chunk(str(path), chunk_size=100, overlap=20)
        for chunk in chunks:
            assert isinstance(chunk["text"], str)
            assert len(chunk["text"].strip()) > 0

    def test_docx_page_number_is_positive_int(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Normal", "Content on page one. " * 30),
        ])
        chunks, _ = load_and_chunk(str(path))
        for chunk in chunks:
            assert isinstance(chunk["page"], int)
            assert chunk["page"] >= 1

    def test_docx_heading_attached_to_chunk(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Introduction"),
            ("Normal", "This is the intro body. " * 30),
        ])
        chunks, outline = load_and_chunk(str(path), chunk_size=100, overlap=10)
        assert "Introduction" in outline
        # At least one chunk should have heading = "Introduction"
        headings_found = {c["heading"] for c in chunks}
        assert "Introduction" in headings_found

    def test_docx_returns_outline_as_list_of_strings(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Chapter One"),
            ("Normal", "Body."),
        ])
        _, outline = load_and_chunk(str(path))
        assert isinstance(outline, list)
        assert all(isinstance(h, str) for h in outline)

    def test_docx_chunk_size_respected_approximately(self, tmp_path):
        """Chunks should not wildly exceed the requested chunk_size."""
        docx = pytest.importorskip("docx")
        chunk_size = 150
        path = _make_docx(tmp_path, [
            ("Normal", "word " * 300),
        ])
        chunks, _ = load_and_chunk(str(path), chunk_size=chunk_size, overlap=20)
        for chunk in chunks:
            # Allow 2× headroom because splitter may not cut mid-word
            assert len(chunk["text"]) <= chunk_size * 2, (
                f"Chunk too large: {len(chunk['text'])} chars"
            )

    def test_docx_multiple_headings(self, tmp_path):
        docx = pytest.importorskip("docx")
        path = _make_docx(tmp_path, [
            ("Heading 1", "Part I"),
            ("Normal", "Content of part one. " * 20),
            ("Heading 2", "Subsection A"),
            ("Normal", "Content of subsection A. " * 20),
            ("Heading 1", "Part II"),
            ("Normal", "Content of part two. " * 20),
        ])
        _, outline = load_and_chunk(str(path))
        assert "Part I"       in outline
        assert "Subsection A" in outline
        assert "Part II"      in outline


# ---------------------------------------------------------------------------
# PDF tests
# ---------------------------------------------------------------------------

def _build_pdf(text: str) -> bytes:
    """
    Pure-Python minimal valid PDF generator.
    Computes exact xref byte offsets so pypdf can parse it cleanly.
    No dependencies beyond the stdlib.
    """
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream_data = f"BT /F1 12 Tf 50 700 Td ({safe}) Tj ET\n".encode()

    obj1 = b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    obj2 = b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
    obj3 = (
        b"3 0 obj\n"
        b"<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"/Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>\n"
        b"endobj\n"
    )
    obj4 = (
        b"4 0 obj\n<</Length " + str(len(stream_data)).encode() + b">>\n"
        b"stream\n" + stream_data + b"endstream\nendobj\n"
    )
    obj5 = (
        b"5 0 obj\n"
        b"<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\n"
        b"endobj\n"
    )

    header = b"%PDF-1.4\n"
    objects = [obj1, obj2, obj3, obj4, obj5]

    # Compute per-object byte offsets for the xref table
    offsets: list[int] = []
    pos = len(header)
    for obj in objects:
        offsets.append(pos)
        pos += len(obj)

    xref_pos = pos
    xref = b"xref\n0 6\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer    = b"trailer\n<</Size 6 /Root 1 0 R>>\n"
    startxref  = f"startxref\n{xref_pos}\n".encode()

    return header + b"".join(objects) + xref + trailer + startxref + b"%%EOF\n"


class TestPdfIngestor:
    """PDF tests — fixture creates a valid PDF from raw bytes (no extra deps)."""

    @pytest.fixture()
    def simple_pdf(self, tmp_path):
        """Single-page PDF with known extractable text."""
        out = tmp_path / "simple.pdf"
        out.write_bytes(_build_pdf("Hello VeriDocs page one content here"))
        return out

    @pytest.fixture()
    def multi_page_pdf(self, tmp_path):
        """Two-page PDF built by merging two single-page PDFs via pypdf."""
        import pypdf
        from pypdf import PdfWriter

        page1 = tmp_path / "p1.pdf"
        page2 = tmp_path / "p2.pdf"
        page1.write_bytes(_build_pdf("Introduction section content on page one"))
        page2.write_bytes(_build_pdf("Conclusion section content on page two"))

        writer = PdfWriter()
        for p in [page1, page2]:
            reader = pypdf.PdfReader(str(p))
            for page in reader.pages:
                writer.add_page(page)

        out = tmp_path / "multi.pdf"
        with open(out, "wb") as fh:
            writer.write(fh)
        return out

    # ── basic sanity ──────────────────────────────────────────────────────

    def test_pdf_supported_format(self):
        assert ".pdf" in supported_formats()

    def test_pdf_load_returns_tuple(self, simple_pdf):
        result = load_and_chunk(str(simple_pdf))
        assert isinstance(result, tuple) and len(result) == 2

    def test_pdf_chunks_is_list(self, simple_pdf):
        chunks, _ = load_and_chunk(str(simple_pdf))
        assert isinstance(chunks, list)

    def test_pdf_outline_is_list(self, simple_pdf):
        _, outline = load_and_chunk(str(simple_pdf))
        assert isinstance(outline, list)

    # ── chunk schema ──────────────────────────────────────────────────────

    def test_pdf_chunk_schema(self, simple_pdf):
        chunks, _ = load_and_chunk(str(simple_pdf))
        for c in chunks:
            assert "text"    in c, "missing 'text'"
            assert "source"  in c, "missing 'source'"
            assert "page"    in c, "missing 'page'"
            assert "heading" in c, "missing 'heading'"

    def test_pdf_source_is_basename(self, simple_pdf):
        chunks, _ = load_and_chunk(str(simple_pdf))
        for c in chunks:
            assert c["source"] == simple_pdf.name

    def test_pdf_page_is_positive_int(self, simple_pdf):
        chunks, _ = load_and_chunk(str(simple_pdf))
        for c in chunks:
            assert isinstance(c["page"], int) and c["page"] >= 1

    def test_pdf_chunk_text_is_nonempty_string(self, simple_pdf):
        chunks, _ = load_and_chunk(str(simple_pdf))
        for c in chunks:
            assert isinstance(c["text"], str) and len(c["text"].strip()) > 0

    # ── multi-page page numbering ─────────────────────────────────────────

    def test_pdf_multi_page_numbers(self, multi_page_pdf):
        chunks, _ = load_and_chunk(str(multi_page_pdf))
        page_numbers = {c["page"] for c in chunks}
        # A 2-page PDF should yield chunks from at least page 1
        assert 1 in page_numbers

    # ── chunk size ────────────────────────────────────────────────────────

    def test_pdf_chunk_size_respected(self, simple_pdf):
        chunk_size = 80
        chunks, _ = load_and_chunk(str(simple_pdf), chunk_size=chunk_size, overlap=10)
        for c in chunks:
            assert len(c["text"]) <= chunk_size * 2
