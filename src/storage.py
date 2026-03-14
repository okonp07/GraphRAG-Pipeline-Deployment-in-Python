"""Storage backends for local and cloud artifact persistence."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Dict, Protocol

try:
    import boto3  # type: ignore
except ImportError:  # pragma: no cover
    boto3 = None


class StorageBackend(Protocol):
    def exists(self, key: str) -> bool: ...
    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None: ...
    def download_bytes(self, key: str) -> bytes: ...
    def delete_prefix(self, prefix: str) -> None: ...


class LocalStorageBackend:
    def __init__(self, root: Path | str):
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        return self.root / key

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def download_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete_prefix(self, prefix: str) -> None:
        path = self._path(prefix)
        if path.is_file():
            path.unlink()
            return
        if not path.exists():
            return
        for item in sorted(path.rglob("*"), reverse=True):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()
        path.rmdir()


class S3StorageBackend:
    def __init__(
        self,
        bucket: str,
        prefix: str,
        region: str,
        endpoint_url: str = "",
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
    ):
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3-backed persistence.")
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url or None,
            aws_access_key_id=aws_access_key_id or None,
            aws_secret_access_key=aws_secret_access_key or None,
        )
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    def _key(self, key: str) -> str:
        if not self.prefix:
            return key
        return f"{self.prefix}/{key}"

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._key(key))
            return True
        except Exception:
            return False

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.client.upload_fileobj(
            BytesIO(data),
            self.bucket,
            self._key(key),
            ExtraArgs={"ContentType": content_type},
        )

    def download_bytes(self, key: str) -> bytes:
        buffer = BytesIO()
        self.client.download_fileobj(self.bucket, self._key(key), buffer)
        return buffer.getvalue()

    def delete_prefix(self, prefix: str) -> None:
        full_prefix = self._key(prefix).rstrip("/") + "/"
        continuation_token = None
        while True:
            params = {"Bucket": self.bucket, "Prefix": full_prefix}
            if continuation_token:
                params["ContinuationToken"] = continuation_token
            response = self.client.list_objects_v2(**params)
            contents = response.get("Contents", [])
            if contents:
                self.client.delete_objects(
                    Bucket=self.bucket,
                    Delete={"Objects": [{"Key": item["Key"]} for item in contents]},
                )
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")


class MemoryStorageBackend:
    def __init__(self):
        self.objects: Dict[str, bytes] = {}

    def exists(self, key: str) -> bool:
        return key in self.objects

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.objects[key] = data

    def download_bytes(self, key: str) -> bytes:
        return self.objects[key]

    def delete_prefix(self, prefix: str) -> None:
        keys = [key for key in self.objects if key == prefix or key.startswith(prefix.rstrip("/") + "/")]
        for key in keys:
            del self.objects[key]


def build_storage_backend(settings) -> StorageBackend:
    backend = settings.storage_backend.lower()
    if backend == "s3":
        if not settings.storage_bucket:
            raise RuntimeError("GRAPHRAG storage backend is set to s3 but no bucket was configured.")
        return S3StorageBackend(
            bucket=settings.storage_bucket,
            prefix=settings.storage_prefix,
            region=settings.storage_region,
            endpoint_url=settings.storage_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return LocalStorageBackend(Path("."))
