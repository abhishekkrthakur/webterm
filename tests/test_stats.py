"""Tests for system stats module."""

from webterm.core.stats import (
    format_bytes,
    get_cpu_per_core,
    get_cpu_percent,
    get_gpu_info,
    get_memory_details,
    get_memory_percent,
    get_system_stats,
    get_top_processes,
)


class TestCPUUsage:
    """Tests for CPU usage functions."""

    def test_get_cpu_percent_returns_float(self):
        """Test that CPU usage returns a float."""
        usage = get_cpu_percent()
        assert isinstance(usage, (int, float))
        assert 0 <= usage <= 100

    def test_get_cpu_per_core_returns_list(self):
        """Test that per-core CPU returns a list."""
        cores = get_cpu_per_core()
        assert isinstance(cores, list)
        assert len(cores) > 0
        for core in cores:
            assert isinstance(core, (int, float))


class TestMemoryUsage:
    """Tests for memory usage functions."""

    def test_get_memory_percent_returns_float(self):
        """Test that memory usage returns a float."""
        usage = get_memory_percent()
        assert isinstance(usage, (int, float))
        assert 0 <= usage <= 100

    def test_get_memory_details_returns_dict(self):
        """Test that memory details returns a dict."""
        details = get_memory_details()
        assert isinstance(details, dict)
        assert "total" in details
        assert "used" in details
        assert "free" in details
        assert "cached" in details


class TestGPUInfo:
    """Tests for GPU info functions."""

    def test_get_gpu_info_returns_dict_or_none(self):
        """Test that GPU info returns a dict or None."""
        info = get_gpu_info()
        assert info is None or isinstance(info, dict)

    def test_get_gpu_info_structure(self):
        """Test GPU info structure when available."""
        info = get_gpu_info()
        if info is not None:
            assert "name" in info
            assert "usage" in info


class TestTopProcesses:
    """Tests for top processes function."""

    def test_get_top_processes_returns_list(self):
        """Test that top processes returns a list."""
        processes = get_top_processes()
        assert isinstance(processes, list)

    def test_get_top_processes_limit(self):
        """Test that top processes respects limit."""
        processes = get_top_processes(limit=3)
        assert len(processes) <= 3

    def test_get_top_processes_structure(self):
        """Test process info structure."""
        processes = get_top_processes(limit=5)
        if processes:
            proc = processes[0]
            assert "name" in proc
            assert "cpu" in proc
            assert "mem" in proc


class TestSystemStats:
    """Tests for system stats function."""

    def test_get_system_stats_returns_dict(self):
        """Test that system stats returns a dict."""
        stats = get_system_stats()
        assert isinstance(stats, dict)

    def test_get_system_stats_contains_cpu(self):
        """Test that system stats contains CPU info."""
        stats = get_system_stats()
        assert "cpu" in stats

    def test_get_system_stats_contains_memory(self):
        """Test that system stats contains memory info."""
        stats = get_system_stats()
        assert "memory" in stats

    def test_get_system_stats_detailed_contains_more(self):
        """Test that detailed stats contains additional info."""
        stats = get_system_stats(detailed=True)
        assert "cpu_cores" in stats
        assert "mem_total" in stats
        assert "processes" in stats
        assert isinstance(stats["processes"], list)


class TestFormatBytes:
    """Tests for format_bytes function."""

    def test_format_bytes_kb(self):
        """Test formatting KB values."""
        assert "KB" in format_bytes(2048)

    def test_format_bytes_mb(self):
        """Test formatting MB values."""
        assert "MB" in format_bytes(2 * 1024 * 1024)

    def test_format_bytes_gb(self):
        """Test formatting GB values."""
        assert "GB" in format_bytes(2 * 1024 * 1024 * 1024)

    def test_format_bytes_zero(self):
        """Test formatting zero."""
        result = format_bytes(0)
        assert "0" in result
