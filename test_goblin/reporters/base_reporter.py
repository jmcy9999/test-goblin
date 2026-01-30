"""Base reporter class for all reporter implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseReporter(ABC):
    """Abstract base class for all reporters.

    Reporters take analyzer results and generate output files in various formats.
    Each reporter focuses on a specific output format (JSON, Markdown, HTML, etc.).
    """

    def __init__(self, output_dir: Path):
        """Initialize the reporter.

        Args:
            output_dir: Path to the directory where output files will be written
        """
        self.output_dir = Path(output_dir)

    @abstractmethod
    def generate(
        self,
        test_inventory: Optional[Dict[str, Any]] = None,
        accessibility_ids: Optional[Dict[str, Any]] = None,
        test_plans: Optional[Dict[str, Any]] = None,
        screen_graph: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate reports from analyzer results.

        Args:
            test_inventory: Test inventory analyzer results
            accessibility_ids: Accessibility analyzer results
            test_plans: Test plan analyzer results
            screen_graph: Screen graph analyzer results (optional)
            metadata: Analysis metadata (timestamp, version, etc.)

        Returns:
            Dictionary with:
                - success: bool
                - files_written: List[str] - paths of files successfully written
                - errors: List[str] - any errors encountered
        """
        pass

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
