"""Tests for file explorer API."""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from webterm.api.app import create_app


class TestFileListEndpoint:
    """Tests for file listing endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "file1.txt").write_text("content1")
            Path(tmpdir, "file2.py").write_text("print('hello')")
            Path(tmpdir, "subdir").mkdir()
            Path(tmpdir, "subdir", "nested.txt").write_text("nested")
            Path(tmpdir, ".hidden").write_text("hidden file")
            yield tmpdir

    def test_list_directory(self, client, temp_dir):
        """Test listing files in a directory."""
        response = client.get(f"/api/files?path={temp_dir}")
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "path" in data

        # Check files are returned
        names = [f["name"] for f in data["items"]]
        assert "file1.txt" in names
        assert "file2.py" in names
        assert "subdir" in names

    def test_list_includes_file_info(self, client, temp_dir):
        """Test that file listing includes metadata."""
        response = client.get(f"/api/files?path={temp_dir}")
        data = response.json()

        for file_info in data["items"]:
            assert "name" in file_info
            assert "is_dir" in file_info
            assert "size" in file_info
            assert "path" in file_info
            assert "modified" in file_info

    def test_list_nonexistent_directory(self, client):
        """Test listing a nonexistent directory."""
        response = client.get("/api/files?path=/nonexistent/path/12345")
        assert response.status_code == 404

    def test_list_default_path(self, client):
        """Test listing with default path (home directory)."""
        response = client.get("/api/files")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "path" in data
        assert "parent" in data

    def test_list_returns_parent(self, client, temp_dir):
        """Test that listing includes parent directory."""
        response = client.get(f"/api/files?path={temp_dir}")
        data = response.json()
        assert "parent" in data
        assert data["parent"] is not None

    def test_directories_sorted_first(self, client, temp_dir):
        """Test that directories appear before files."""
        response = client.get(f"/api/files?path={temp_dir}")
        data = response.json()

        # Find the first non-directory
        first_file_idx = None
        for i, item in enumerate(data["items"]):
            if not item["is_dir"]:
                first_file_idx = i
                break

        # All items before first_file_idx should be directories
        if first_file_idx is not None:
            for i in range(first_file_idx):
                assert data["items"][i]["is_dir"] is True


class TestFileDownloadEndpoint:
    """Tests for file download endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for download testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Download test content")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_download_file(self, client, temp_file):
        """Test downloading a file."""
        response = client.get(f"/api/files/download?path={temp_file}")
        assert response.status_code == 200
        assert response.content == b"Download test content"

    def test_download_nonexistent_file(self, client):
        """Test downloading a nonexistent file."""
        response = client.get("/api/files/download?path=/nonexistent/file.txt")
        assert response.status_code == 404

    def test_download_directory_fails(self, client):
        """Test that downloading a directory fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            response = client.get(f"/api/files/download?path={tmpdir}")
            assert response.status_code == 400


class TestFileUploadEndpoint:
    """Tests for file upload endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for uploads."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_upload_file(self, client, temp_dir):
        """Test uploading a file."""
        # Use 'file' not 'files' - matches the endpoint parameter name
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        response = client.post(f"/api/files/upload?path={temp_dir}", files=files)
        assert response.status_code == 200

        # Verify file was created
        uploaded_path = Path(temp_dir) / "test.txt"
        assert uploaded_path.exists()
        assert uploaded_path.read_text() == "Test content"

    def test_upload_returns_info(self, client, temp_dir):
        """Test that upload returns file info."""
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        response = client.post(f"/api/files/upload?path={temp_dir}", files=files)
        data = response.json()

        assert data["success"] is True
        assert data["filename"] == "test.txt"
        assert data["size"] == len(b"Test content")
        assert "path" in data

    def test_upload_to_nonexistent_directory(self, client):
        """Test uploading to a nonexistent directory."""
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        response = client.post("/api/files/upload?path=/nonexistent/path/12345", files=files)
        assert response.status_code == 404
