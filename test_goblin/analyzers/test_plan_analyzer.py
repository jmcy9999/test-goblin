"""Test Plan Analyzer for iOS XCTest projects.

This module analyzes .xctestplan files to extract test selection strategies,
calculate test counts, identify overlaps between plans, and detect orphaned tests.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional


class TestPlanAnalyzer:
    """Analyzes Xcode test plans (.xctestplan files)."""

    def __init__(self, project_path: Path):
        """Initialize the analyzer.

        Args:
            project_path: Path to the iOS project root directory
        """
        self.project_path = Path(project_path)
        self.test_plans: List[Dict[str, Any]] = []
        self.all_tests_in_plans: Set[str] = set()
        self.test_to_plans_map: Dict[str, List[str]] = {}

    def analyze(
        self, test_inventory: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze all test plans in the project.

        Args:
            test_inventory: Optional test inventory data to detect orphaned tests.
                Expected format: {"test_files": [{"test_classes": [...]}]}

        Returns:
            Dictionary containing test plan analysis results matching the schema
        """
        # Find all .xctestplan files
        test_plan_files = self._find_test_plans()

        if not test_plan_files:
            return self._empty_result()

        # Parse each test plan
        for plan_file in test_plan_files:
            plan_data = self._parse_test_plan(plan_file)
            if plan_data:
                self.test_plans.append(plan_data)

        # Calculate overlap and statistics
        result = self._build_analysis_result(test_inventory)
        return result

    def _find_test_plans(self) -> List[Path]:
        """Find all .xctestplan files in the project.

        Returns:
            List of Path objects for .xctestplan files
        """
        return sorted(self.project_path.rglob("*.xctestplan"))

    def _parse_test_plan(self, plan_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single .xctestplan file.

        Args:
            plan_path: Path to the .xctestplan file

        Returns:
            Dictionary with plan data or None if parsing fails
        """
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_json = json.load(f)

            plan_name = plan_path.stem
            test_targets = plan_json.get("testTargets", [])

            # Collect all tests mentioned in this plan
            included_tests = set()
            skipped_tests = set()

            for target in test_targets:
                # Check for selectedTests (positive selection)
                selected = target.get("selectedTests", [])
                if selected:
                    for test in selected:
                        test_id = self._normalize_test_identifier(test)
                        included_tests.add(test_id)

                # Check for skippedTests (negative selection)
                skipped = target.get("skippedTests", [])
                if skipped:
                    for test in skipped:
                        test_id = self._normalize_test_identifier(test)
                        skipped_tests.add(test_id)

            # Determine selection strategy
            if included_tests:
                strategy = "positive_selection"
                tests_run = len(included_tests)
                tests_skipped = 0
            elif skipped_tests:
                strategy = "negative_selection"
                tests_run = 0  # Unknown without full inventory
                tests_skipped = len(skipped_tests)
            else:
                strategy = "negative_selection"
                tests_run = 0
                tests_skipped = 0

            # Infer purpose from plan name
            purpose = self._infer_purpose(plan_name)

            # Track tests in this plan
            plan_tests = included_tests if included_tests else skipped_tests
            for test in plan_tests:
                self.all_tests_in_plans.add(test)
                if test not in self.test_to_plans_map:
                    self.test_to_plans_map[test] = []
                self.test_to_plans_map[test].append(plan_name)

            return {
                "name": plan_name,
                "file_path": str(plan_path),
                "strategy": strategy,
                "tests_skipped": tests_skipped,
                "tests_run": tests_run,
                "purpose": purpose,
                "_included_tests": list(included_tests),
                "_skipped_tests": list(skipped_tests),
            }

        except Exception as e:
            print(f"Warning: Failed to parse {plan_path}: {e}")
            return None

    def _normalize_test_identifier(self, test_identifier: str) -> str:
        """Normalize a test identifier to consistent format.

        Handles formats like:
        - "ClassName/testMethod()"
        - "ClassName"
        - "testMethod()"

        Args:
            test_identifier: Raw test identifier from test plan

        Returns:
            Normalized test identifier
        """
        # Remove trailing slashes or whitespace
        test_identifier = test_identifier.strip().rstrip("/")
        return test_identifier

    def _infer_purpose(self, plan_name: str) -> str:
        """Infer the purpose of a test plan from its name.

        Args:
            plan_name: Name of the test plan

        Returns:
            Inferred purpose string
        """
        name_lower = plan_name.lower()

        if "smoke" in name_lower or "pr" in name_lower:
            return "smoke"
        elif "full" in name_lower or "functional" in name_lower:
            return "full"
        elif "performance" in name_lower or "perf" in name_lower:
            return "performance"
        elif "accessibility" in name_lower or "a11y" in name_lower:
            return "accessibility"
        elif "integration" in name_lower:
            return "integration"
        elif "unit" in name_lower:
            return "unit"
        elif "snapshot" in name_lower or "l10n" in name_lower:
            return "snapshot"
        elif "sync" in name_lower:
            return "sync"
        else:
            return "general"

    def _build_analysis_result(
        self, test_inventory: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the final analysis result.

        Args:
            test_inventory: Optional test inventory to detect orphaned tests

        Returns:
            Complete analysis result matching the schema
        """
        # Calculate total unique tests across all plans
        total_unique_tests = len(self.all_tests_in_plans)

        # Find tests that appear in multiple plans (with details)
        tests_in_multiple_details: List[Dict[str, Any]] = []
        for test_name, plans in self.test_to_plans_map.items():
            if len(plans) > 1:
                tests_in_multiple_details.append(
                    {
                        "test": test_name,
                        "plan_count": len(plans),
                        "plans": sorted(plans),
                    }
                )

        # Sort by plan_count descending, then by test name
        def sort_key(x: Dict[str, Any]) -> tuple:
            return (-x["plan_count"], x["test"])

        tests_in_multiple_details.sort(key=sort_key)

        tests_in_multiple_count = len(tests_in_multiple_details)

        # Calculate overlap percentage
        overlap_percentage = (
            (tests_in_multiple_count / total_unique_tests * 100)
            if total_unique_tests > 0
            else 0.0
        )

        # Detect orphaned tests
        orphaned_tests, orphaned_count = self._detect_orphaned_tests(test_inventory)

        # Collect all skipped tests across all plans
        all_skipped_tests: Set[str] = set()
        for plan in self.test_plans:
            skipped = plan.get("_skipped_tests", [])
            all_skipped_tests.update(skipped)

        # Build plan summaries (remove internal fields)
        plan_summaries = []
        for plan in self.test_plans:
            plan_summary = {
                "name": plan["name"],
                "file_path": plan["file_path"],
                "strategy": plan["strategy"],
                "tests_skipped": plan["tests_skipped"],
                "tests_run": plan["tests_run"],
                "purpose": plan["purpose"],
            }
            plan_summaries.append(plan_summary)

        return {
            "test_plans": plan_summaries,
            "total_unique_tests": total_unique_tests,
            "tests_in_multiple_plans_count": tests_in_multiple_count,
            "tests_in_multiple_plans": tests_in_multiple_details,
            "overlap_percentage": round(overlap_percentage, 2),
            "orphaned_tests": orphaned_tests,
            "orphaned_count": orphaned_count,
            "skipped_tests": sorted(all_skipped_tests),
            "skipped_tests_count": len(all_skipped_tests),
        }

    def _detect_orphaned_tests(
        self, test_inventory: Optional[Dict[str, Any]]
    ) -> tuple[List[str], int]:
        """Detect tests that exist in test files but not in any test plan.

        Args:
            test_inventory: Test inventory data with structure:
                {"test_files": [{"test_classes": [...], "test_methods": [...]}]}

        Returns:
            Tuple of (list of orphaned test identifiers, count)
        """
        if not test_inventory:
            return [], 0

        # Build set of all tests from inventory
        all_inventory_tests = set()

        for file_data in test_inventory.get("test_files", []):
            classes = file_data.get("test_classes", [])
            tests = file_data.get("test_methods", [])

            # Generate test identifiers in format "ClassName/testMethod()"
            for class_name in classes:
                for test_name in tests:
                    # Handle test names with or without parentheses
                    if not test_name.endswith("()"):
                        test_name = f"{test_name}()"
                    test_id = f"{class_name}/{test_name}"
                    all_inventory_tests.add(test_id)

                    # Also add class-level identifier
                    all_inventory_tests.add(class_name)

                    # Also add test method alone (some plans use this format)
                    all_inventory_tests.add(test_name)

        # Find orphaned tests
        orphaned = sorted(all_inventory_tests - self.all_tests_in_plans)

        # Filter to only include full test identifiers (ClassName/testMethod)
        # to avoid noise from partial matches
        orphaned_full = [test for test in orphaned if "/" in test and "(" in test]

        return orphaned_full, len(orphaned_full)

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result when no test plans found.

        Returns:
            Empty analysis result
        """
        return {
            "test_plans": [],
            "total_unique_tests": 0,
            "tests_in_multiple_plans_count": 0,
            "tests_in_multiple_plans": [],
            "overlap_percentage": 0.0,
            "orphaned_tests": [],
            "orphaned_count": 0,
            "skipped_tests": [],
            "skipped_tests_count": 0,
        }


def analyze_test_plans(
    project_path: Path, test_inventory: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to analyze test plans.

    Args:
        project_path: Path to the iOS project root
        test_inventory: Optional test inventory for orphaned test detection

    Returns:
        Test plan analysis results
    """
    analyzer = TestPlanAnalyzer(project_path)
    return analyzer.analyze(test_inventory)
