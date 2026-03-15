from src import dataset_loader


def test_load_hf_documents_normalizes_records(monkeypatch):
    sample_records = [
        {"id": "doc-1", "text": "Phishing defense requires MFA and filtering."},
        {"title": "Alert", "report": "CVE-2024-12345 should be patched quickly."},
    ]

    def fake_load_dataset(dataset_name, split):
        assert dataset_name == "zeroshot/cybersecurity-corpus"
        assert split == "train"
        return sample_records

    monkeypatch.setattr(dataset_loader, "load_dataset", fake_load_dataset)

    documents = dataset_loader.load_hf_documents(
        dataset_name="zeroshot/cybersecurity-corpus",
        split="train",
        chunk_size=50,
        chunk_overlap=5,
    )

    assert len(documents) == 2
    assert documents[0]["document_type"] == "dataset"
    assert documents[0]["dataset_name"] == "zeroshot/cybersecurity-corpus"
    assert "phishing" in documents[0]["text"].lower()
    assert any(entity["name"].lower() == "cve-2024-12345" for entity in documents[1]["entities"])


def test_load_hf_documents_respects_text_field(monkeypatch):
    sample_records = [{"body": "ignore me", "content": "Use zero trust."}]

    monkeypatch.setattr(dataset_loader, "load_dataset", lambda dataset_name, split: sample_records)

    documents = dataset_loader.load_hf_documents(
        dataset_name="custom/corpus",
        split="train",
        text_field="content",
        chunk_size=50,
        chunk_overlap=5,
    )

    assert documents[0]["text"] == "Use zero trust."
