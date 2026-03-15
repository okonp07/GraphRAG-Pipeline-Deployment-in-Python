from src import utils


def test_read_document_extracts_html_text(tmp_path):
    path = tmp_path / "advisory.html"
    path.write_text(
        "<html><head><title>Ignore</title><style>.x{}</style></head>"
        "<body><h1>Phishing Advisory</h1><p>Enable MFA to reduce phishing risk.</p>"
        "<script>console.log('ignore')</script></body></html>"
    )

    text = utils.read_document(path)

    assert "Phishing Advisory" in text
    assert "Enable MFA to reduce phishing risk." in text
    assert "console.log" not in text


def test_read_document_extracts_pdf_text_via_reader(tmp_path, monkeypatch):
    path = tmp_path / "report.pdf"
    path.write_bytes(b"%PDF-1.4 placeholder")

    class FakePage:
        def extract_text(self):
            return "CVE-2024-12345 patch immediately."

    class FakeReader:
        def __init__(self, filename):
            assert str(path) == filename
            self.pages = [FakePage()]

    monkeypatch.setattr(utils, "PdfReader", FakeReader)

    text = utils.read_document(path)

    assert "CVE-2024-12345 patch immediately." in text


def test_load_documents_tracks_document_type(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "playbook.md").write_text("Use zero trust and patch rapidly.")

    documents = utils.load_documents(data_dir, chunk_size=50, chunk_overlap=5)

    assert documents[0]["document_type"] == "md"
