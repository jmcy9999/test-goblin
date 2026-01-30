"""Base class for all analyzers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseAnalyzer(ABC):
    """Abstract base class for all analyzers.

    Analyzers scan iOS test projects and extract structured data.
    Each analyzer focuses on a specific aspect (test inventory, accessibility IDs).
    """

    def __init__(self, project_path: Path):
        """Initialize the analyzer.

        Args:
            project_path: Path to the iOS project directory
        """
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Run the analysis and return structured data.

        Returns:
            Dictionary containing analysis results in a structured format
        """
        pass

    def _find_test_files(self, pattern: str = "*Tests.swift") -> list[Path]:
        """Find test files matching the given pattern.

        Args:
            pattern: Glob pattern for test files (default: *Tests.swift)

        Returns:
            List of paths to test files
        """
        # Search recursively for test files, focusing on XCUITest directories
        test_files = []

        # Directories to EXCLUDE (unit tests, integration tests, KIF tests, etc.)
        exclude_dirs = {
            "ClientTests",
            "StorageTests",
            "SyncTests",
            "AccountTests",
            "SharedTests",
            "ExperimentIntegrationTests",
            "SyncIntegrationTests",
            "SyncTelemetryTests",
            "StoragePerfTests",
            "L10nSnapshotTests",
            "DeferredTests",
            "BrowserKitTests",
            "CommonTests",
            "ActionExtensionKitTests",
            "WebEngineTests",
            "ComponentLibraryTests",
            "Tests/UITests",  # Exclude nested UITests
        }

        # Primary pattern: look for XCUITests directories specifically
        xcui_test_patterns = [
            "**/XCUITests/**",
            "**/*UITests/**",  # Catches MockShopAppUITests, AppNameUITests, etc.
        ]

        for test_dir_pattern in xcui_test_patterns:
            found_files = self.project_path.glob(f"{test_dir_pattern}/{pattern}")
            for file_path in found_files:
                # Check if path contains "Tests/UITests" (nested - likely KIF tests)
                path_str = str(file_path)
                if "Tests/UITests" in path_str:
                    continue

                # Check if file is in an excluded directory
                if not any(excluded in file_path.parts for excluded in exclude_dirs):
                    test_files.append(file_path)

        # If no files found with XCUITests patterns, search more broadly
        # but still exclude unit test directories
        if not test_files:
            all_files = self.project_path.glob(f"**/{pattern}")
            for file_path in all_files:
                path_str = str(file_path)

                # Skip if in Tests/UITests (nested pattern)
                if "Tests/UITests" in path_str:
                    continue

                # Exclude hidden directories and known non-UI test directories
                is_hidden = any(part.startswith(".") for part in file_path.parts)
                is_excluded = any(
                    excluded in file_path.parts for excluded in exclude_dirs
                )
                if not is_hidden and not is_excluded:
                    test_files.append(file_path)

        # Remove duplicates and sort
        return sorted(set(test_files))
