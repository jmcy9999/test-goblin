"""
Screen Graph Analyzer for iOS Test Optimizer.

Analyzes screen navigation graphs and navigator usage patterns in XCUITest suites.
Detects MappaMundi-based navigation systems and calculates adoption metrics.

This analyzer is OPTIONAL - it gracefully handles projects without screen graphs.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter


class ScreenGraphAnalyzer:
    """
    Analyzes screen navigation graphs and navigator.goto() usage patterns.

    Searches for:
    - Screen graph files (FxScreenGraph.swift, *ScreenGraph*.swift, *Navigator*.swift)
    - MappaMundi library imports
    - Screen state definitions (case statements, let constants)
    - navigator.goto() calls in test files

    Returns structured data about screen navigation patterns and adoption rates.
    """

    def __init__(self, project_path: Path):
        """
        Initialize analyzer with project path.

        Args:
            project_path: Root path of iOS project to analyze
        """
        self.project_path = Path(project_path)
        self.screen_graph_file: Optional[Path] = None
        self.screens: List[str] = []
        self.screen_usage: Counter = Counter()
        self.test_files_with_navigator: List[Path] = []
        self.test_files_without_navigator: List[Path] = []
        self.total_goto_calls: int = 0

    def analyze(self, test_files: Optional[List[Path]] = None) -> Dict[str, Any]:
        """
        Perform complete screen graph analysis.

        Args:
            test_files: Optional list of test file paths. If not provided, will
                       search for test files in project.

        Returns:
            Dictionary containing:
            - has_screen_graph: bool
            - screen_graph_file: str or None
            - total_screens: int
            - navigator_adoption: str (e.g., "86%")
            - navigator_usage_count: int
            - top_screens: List of screen usage dicts
        """
        # Step 1: Search for screen graph file
        self._find_screen_graph_file()

        # Step 2: If found, extract screen definitions
        if self.screen_graph_file:
            self._extract_screen_definitions()

        # Step 3: Find test files if not provided
        if test_files is None:
            test_files = self._find_test_files()

        # Step 4: Analyze navigator usage in test files
        if test_files:
            self._analyze_navigator_usage(test_files)

        # Step 5: Calculate metrics and return results
        return self._generate_results()

    def _find_screen_graph_file(self) -> None:
        """
        Search for screen graph definition files.

        Looks for files matching patterns:
        - *ScreenGraph*.swift
        - *Navigator*.swift (but not *NavigatorRegistry*)
        - Files containing MappaMundi imports
        """
        # Search patterns in priority order
        patterns = [
            "**/FxScreenGraph.swift",
            "**/*ScreenGraph*.swift",
            "**/*Navigator.swift",
        ]

        for pattern in patterns:
            matches = list(self.project_path.glob(pattern))
            if matches:
                # Filter out NavigatorRegistry files
                matches = [m for m in matches if "Registry" not in m.name]
                if matches:
                    self.screen_graph_file = matches[0]
                    break

        # If not found by name, search for MappaMundi usage
        if not self.screen_graph_file:
            self._find_by_mappa_mundi_import()

    def _find_by_mappa_mundi_import(self) -> None:
        """
        Search for files containing MappaMundi imports.

        This is a fallback strategy for projects that don't follow
        standard naming conventions.
        """
        swift_files = list(self.project_path.glob("**/*.swift"))

        for swift_file in swift_files:
            try:
                content = swift_file.read_text(encoding="utf-8")
                if "import MappaMundi" in content or "MMScreenGraph" in content:
                    # Check if it looks like a screen graph definition
                    if self._is_screen_graph_file(content):
                        self.screen_graph_file = swift_file
                        break
            except (UnicodeDecodeError, IOError):
                continue

    def _is_screen_graph_file(self, content: str) -> bool:
        """
        Heuristic to determine if file content represents a screen graph.

        Args:
            content: Swift file content

        Returns:
            True if file appears to be a screen graph definition
        """
        # Look for screen state enum or multiple case statements
        indicators = [
            r"enum\s+\w+State",
            r"case\s+\w+Screen",
            r"MMScreenGraph",
            r"createScreenGraph",
        ]

        matches = sum(1 for pattern in indicators if re.search(pattern, content))
        return matches >= 2

    def _extract_screen_definitions(self) -> None:
        """
        Extract screen state definitions from screen graph file.

        Looks for patterns like:
        - case ScreenName
        - let ScreenName = "..."
        - .ScreenName

        Handles Swift enum cases and constants.
        """
        if not self.screen_graph_file:
            return

        try:
            content = self.screen_graph_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IOError):
            return

        # Pattern 1: enum case statements
        # Matches: case SettingsScreen, case BrowserTab, etc.
        case_pattern = r"case\s+([A-Z][A-Za-z0-9_]+)"
        case_matches = re.findall(case_pattern, content)

        # Pattern 2: let constants (screen state strings)
        # Matches: let SettingsScreen = "..."
        let_pattern = r"let\s+([A-Z][A-Za-z0-9_]+)\s*="
        let_matches = re.findall(let_pattern, content)

        # Pattern 3: Screen references in navigator.goto() definitions
        # Matches: navigator.goto(.SettingsScreen)
        goto_pattern = r"\.goto\(\s*\.?([A-Z][A-Za-z0-9_]+)\s*\)"
        goto_matches = re.findall(goto_pattern, content)

        # Combine and deduplicate
        all_screens = set(case_matches + let_matches + goto_matches)

        # Filter out common false positives
        excluded_keywords = {
            "UserState",
            "Action",
            "Navigator",
            "Screen",
            "State",
            "Graph",
            "String",
            "Bool",
            "Int",
            "Optional",
            "Array",
        }

        self.screens = sorted(
            [
                screen
                for screen in all_screens
                if screen not in excluded_keywords and not screen.startswith("_")
            ]
        )

    def _find_test_files(self) -> List[Path]:
        """
        Find XCUITest files in project.

        Returns:
            List of test file paths
        """
        # Search for test files in common locations
        test_patterns = [
            "**/XCUITests/**/*Tests.swift",
            "**/XCUITests/**/*Test.swift",
            "**/UITests/**/*Tests.swift",
            "**/UITests/**/*Test.swift",
            "**/*Tests.swift",
        ]

        test_files = []
        seen = set()

        for pattern in test_patterns:
            for test_file in self.project_path.glob(pattern):
                if test_file not in seen:
                    test_files.append(test_file)
                    seen.add(test_file)

        return test_files

    def _analyze_navigator_usage(self, test_files: List[Path]) -> None:
        """
        Analyze navigator.goto() usage across test files.

        Args:
            test_files: List of test file paths to analyze
        """
        # Pattern to match navigator.goto() calls
        # Matches: navigator.goto(Screen), navigator.goto(.Screen), etc.
        goto_pattern = r"navigator\.goto\(\s*\.?([A-Z][A-Za-z0-9_]+)\s*\)"

        for test_file in test_files:
            try:
                content = test_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, IOError):
                continue

            # Find all goto calls
            goto_matches = re.findall(goto_pattern, content)

            if goto_matches:
                self.test_files_with_navigator.append(test_file)
                self.total_goto_calls += len(goto_matches)

                # Count screen usage
                for screen in goto_matches:
                    self.screen_usage[screen] += 1
            else:
                self.test_files_without_navigator.append(test_file)

    def _calculate_adoption_rate(self) -> str:
        """
        Calculate navigator adoption rate as percentage.

        Returns:
            Formatted percentage string (e.g., "86%")
        """
        total_files = len(self.test_files_with_navigator) + len(
            self.test_files_without_navigator
        )

        if total_files == 0:
            return "0%"

        adoption = (len(self.test_files_with_navigator) / total_files) * 100
        return f"{adoption:.0f}%"

    def _generate_top_screens(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Generate list of most-used screens with usage statistics.

        Args:
            limit: Maximum number of screens to return

        Returns:
            List of dicts with screen, usage_count, and percentage
        """
        if self.total_goto_calls == 0:
            return []

        top_screens = []
        for screen, count in self.screen_usage.most_common(limit):
            percentage = (count / self.total_goto_calls) * 100
            top_screens.append(
                {
                    "screen": screen,
                    "usage_count": count,
                    "percentage": round(percentage, 1),
                }
            )

        return top_screens

    def _generate_results(self) -> Dict[str, Any]:
        """
        Generate final analysis results.

        Returns:
            Dictionary matching the JSON schema from ANALYSIS_TOOL_REQUIREMENTS.md
        """
        has_screen_graph = self.screen_graph_file is not None

        results = {
            "has_screen_graph": has_screen_graph,
            "screen_graph_file": (
                str(self.screen_graph_file.relative_to(self.project_path))
                if self.screen_graph_file
                else None
            ),
            "total_screens": len(self.screens),
            "navigator_adoption": self._calculate_adoption_rate(),
            "navigator_usage_count": self.total_goto_calls,
            "top_screens": self._generate_top_screens(),
        }

        return results


def analyze_screen_graph(
    project_path: Path, test_files: Optional[List[Path]] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze screen graph in one call.

    Args:
        project_path: Root path of iOS project
        test_files: Optional list of test files (will auto-detect if not provided)

    Returns:
        Analysis results dictionary

    Example:
        >>> results = analyze_screen_graph(Path("/path/to/ios-project"))
        >>> print(f"Navigator adoption: {results['navigator_adoption']}")
        Navigator adoption: 86%
    """
    analyzer = ScreenGraphAnalyzer(project_path)
    return analyzer.analyze(test_files)
