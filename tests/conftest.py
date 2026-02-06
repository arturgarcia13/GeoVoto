import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_settings(monkeypatch):
    """Mocks settings for testing."""
    monkeypatch.setenv("GEOVOTO__DATABASE__HOST", "localhost")
    monkeypatch.setenv("GEOVOTO__DATABASE__PASSWORD", "test")
