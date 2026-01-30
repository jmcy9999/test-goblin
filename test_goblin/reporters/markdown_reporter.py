"""Markdown Reporter for iOS Test Optimizer.

Generates comprehensive markdown reports from analyzer results.
Includes test inventory, accessibility IDs, test plans, screen graphs,
and actionable recommendations.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from test_goblin.config import get_threshold


class MarkdownReporter:
    """Generates markdown analysis reports from analyzer results."""

    def __init__(self, project_path: Path):
        """Initialize the markdown reporter.

        Args:
            project_path: Path to the iOS project root
        """
        self.project_path = Path(project_path)
        self.report_sections: List[str] = []
        # Instance variables for cross-section data sharing
        self._naming_issues: Dict[str, Any] = {}
        self._test_plan_info: Dict[str, Any] = {}

    def generate_report(
        self,
        test_inventory: Optional[Dict[str, Any]] = None,
        accessibility_data: Optional[Dict[str, Any]] = None,
        test_plans: Optional[Dict[str, Any]] = None,
        screen_graph: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate complete markdown report from analyzer results.

        Args:
            test_inventory: Results from TestInventoryAnalyzer
            accessibility_data: Results from AccessibilityAnalyzer
            test_plans: Results from TestPlanAnalyzer
            screen_graph: Results from ScreenGraphAnalyzer

        Returns:
            Complete markdown report as string
        """
        self.report_sections = []

        # Header and executive summary
        self._add_header()
        self._add_executive_summary(
            test_inventory, accessibility_data, test_plans, screen_graph
        )

        # Table of contents
        self._add_table_of_contents(
            test_inventory, accessibility_data, test_plans, screen_graph
        )

        # Main sections
        if test_inventory:
            self._add_test_inventory_section(test_inventory)

        if accessibility_data:
            self._add_accessibility_section(accessibility_data)

        if test_plans:
            self._add_test_plans_section(test_plans)

        if screen_graph and screen_graph.get("has_screen_graph"):
            self._add_screen_graph_section(screen_graph)

        # Recommendations
        self._add_recommendations(
            test_inventory, accessibility_data, test_plans, screen_graph
        )

        return "\n\n".join(self.report_sections)

    def _add_header(self) -> None:
        """Add report header with metadata."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        header = f"""# iOS Test Suite Analysis Report

**Generated:** {timestamp}
**Project:** `{self.project_path}`

---"""
        self.report_sections.append(header)

    def _add_executive_summary(
        self,
        test_inventory: Optional[Dict[str, Any]],
        accessibility_data: Optional[Dict[str, Any]],
        test_plans: Optional[Dict[str, Any]],
        screen_graph: Optional[Dict[str, Any]],
    ) -> None:
        """Add executive summary with key metrics."""
        summary = ["## Executive Summary"]

        metrics = []

        if test_inventory:
            total_tests = test_inventory.get("total_test_methods", 0)
            total_files = test_inventory.get("total_test_files", 0)
            metrics.append(f"- **Total Tests:** {total_tests}")
            metrics.append(f"- **Test Files:** {total_files}")

        if accessibility_data:
            total_ids = accessibility_data.get("total_unique_ids", 0)
            metrics.append(f"- **Accessibility IDs:** {total_ids}")

        if test_plans:
            plans = test_plans.get("test_plans", [])
            metrics.append(f"- **Test Plans:** {len(plans)}")

        if screen_graph and screen_graph.get("has_screen_graph"):
            total_screens = screen_graph.get("total_screens", 0)
            adoption = screen_graph.get("navigator_adoption", "0%")
            metrics.append(f"- **Screens:** {total_screens}")
            metrics.append(f"- **Navigator Adoption:** {adoption}")

        if not metrics:
            metrics.append("- No analysis data available")

        summary.extend(metrics)
        self.report_sections.append("\n".join(summary))

    def _add_table_of_contents(
        self,
        test_inventory: Optional[Dict[str, Any]],
        accessibility_data: Optional[Dict[str, Any]],
        test_plans: Optional[Dict[str, Any]],
        screen_graph: Optional[Dict[str, Any]],
    ) -> None:
        """Add table of contents for navigation."""
        toc = ["## Table of Contents"]
        toc_items = []

        if test_inventory:
            toc_items.append("1. [Test Inventory](#test-inventory)")

        if accessibility_data:
            toc_items.append(
                "2. [Accessibility Identifiers](#accessibility-identifiers)"
            )

        if test_plans:
            toc_items.append("3. [Test Plans](#test-plans)")

        if screen_graph and screen_graph.get("has_screen_graph"):
            toc_items.append("4. [Screen Graph](#screen-graph)")

        toc_items.append(f"{len(toc_items) + 1}. [Recommendations](#recommendations)")

        toc.extend(toc_items)
        self.report_sections.append("\n".join(toc))

    def _add_test_inventory_section(self, test_inventory: Dict[str, Any]) -> None:
        """Add test inventory section with statistics and tables."""
        section = ["## Test Inventory"]

        # Overview statistics
        total_tests = test_inventory.get("total_test_methods", 0)
        total_files = test_inventory.get("total_test_files", 0)
        stats = test_inventory.get("tests_per_file", {})

        section.append("### Overview")
        section.append("")
        section.append(f"- **Total Test Files:** {total_files}")
        section.append(f"- **Total Test Methods:** {total_tests}")
        section.append(
            f"- **Tests per File:** {stats.get('min', 0)} min, "
            f"{stats.get('max', 0)} max, "
            f"{stats.get('avg', 0):.1f} avg, "
            f"{stats.get('median', 0)} median"
        )
        section.append("")
        section.append(
            "> **Complete data:** See `test_inventory.json` for full file list "
            "with all test methods"
        )

        # Naming patterns
        naming = test_inventory.get("naming_patterns", {})
        expected_pattern = naming.get("pattern", "[Feature]Tests.swift")
        consistency_str = naming.get("consistency", "0%")

        section.append("")
        section.append("### Naming Convention")
        section.append("")
        section.append(f"- **Expected Pattern:** `{expected_pattern}`")
        section.append(f"- **Consistency:** {consistency_str}")

        # Find and categorize files not following convention
        test_files = test_inventory.get("test_files", [])

        # Categorize non-compliant files by their naming issues
        snake_case_files = []  # e.g., login_tests.swift
        flow_files = []  # e.g., LoginFlow.swift, CheckoutFlows.swift
        validation_files = []  # e.g., LoginValidation.swift
        scenario_files = []  # e.g., TestScenarios.swift
        other_files = []  # Other non-standard patterns

        for file_data in test_files:
            file_name = file_data.get("file_name", "")
            # Check if follows *Tests.swift or *Test.swift pattern
            if file_name.endswith("Tests.swift") or file_name.endswith("Test.swift"):
                continue  # Compliant

            # Categorize non-compliant files
            lower_name = file_name.lower()
            if "_test" in lower_name or "_tests" in lower_name:
                snake_case_files.append(file_name)
            elif "flow" in lower_name:
                flow_files.append(file_name)
            elif "validation" in lower_name:
                validation_files.append(file_name)
            elif "scenario" in lower_name:
                scenario_files.append(file_name)
            else:
                other_files.append(file_name)

        total_non_compliant = (
            len(snake_case_files)
            + len(flow_files)
            + len(validation_files)
            + len(scenario_files)
            + len(other_files)
        )

        if total_non_compliant > 0:
            section.append("")
            section.append(
                f"**Files Not Following Convention ({total_non_compliant}):**"
            )

            if snake_case_files:
                section.append("")
                section.append(
                    f"*Snake case naming* ({len(snake_case_files)} files) - "
                    f"should use PascalCase `[Feature]Tests.swift`:"
                )
                for f in sorted(snake_case_files)[:5]:
                    section.append(f"- `{f}`")
                if len(snake_case_files) > 5:
                    section.append(f"- *...and {len(snake_case_files) - 5} more*")

            if flow_files:
                section.append("")
                section.append(
                    f"*Flow-based naming* ({len(flow_files)} files) - "
                    f"consider renaming to `[Feature]FlowTests.swift`:"
                )
                for f in sorted(flow_files)[:5]:
                    section.append(f"- `{f}`")
                if len(flow_files) > 5:
                    section.append(f"- *...and {len(flow_files) - 5} more*")

            if validation_files:
                section.append("")
                section.append(
                    f"*Validation-based naming* ({len(validation_files)} files) - "
                    f"consider renaming to `[Feature]ValidationTests.swift`:"
                )
                for f in sorted(validation_files)[:5]:
                    section.append(f"- `{f}`")
                if len(validation_files) > 5:
                    section.append(f"- *...and {len(validation_files) - 5} more*")

            if scenario_files:
                section.append("")
                section.append(
                    f"*Scenario-based naming* ({len(scenario_files)} files) - "
                    f"consider renaming to `[Feature]ScenarioTests.swift`:"
                )
                for f in sorted(scenario_files)[:5]:
                    section.append(f"- `{f}`")
                if len(scenario_files) > 5:
                    section.append(f"- *...and {len(scenario_files) - 5} more*")

            if other_files:
                section.append("")
                section.append(
                    f"*Other non-standard naming* ({len(other_files)} files):"
                )
                for f in sorted(other_files)[:5]:
                    section.append(f"- `{f}`")
                if len(other_files) > 5:
                    section.append(f"- *...and {len(other_files) - 5} more*")

            section.append("")
            section.append(
                "> See `test_inventory.json` → `test_files` for complete file list"
            )

        # Store non-compliant info for recommendations
        self._naming_issues = {
            "snake_case": snake_case_files,
            "flow": flow_files,
            "validation": validation_files,
            "scenario": scenario_files,
            "other": other_files,
            "total": total_non_compliant,
        }

        # Largest test files table
        section.append("")
        section.append("### Largest Test Files")
        section.append("")

        # Sort by test count descending and take top 20
        sorted_files = sorted(
            test_files, key=lambda x: x.get("test_count", 0), reverse=True
        )[:20]

        if sorted_files:
            section.append("| File | Tests | Classes |")
            section.append("|------|------:|---------|")

            for file_data in sorted_files:
                file_name = file_data.get("file_name", "Unknown")
                test_count = file_data.get("test_count", 0)
                classes = file_data.get("test_classes", [])
                class_list = ", ".join(classes) if classes else "N/A"

                section.append(f"| {file_name} | {test_count} | {class_list} |")

            if len(test_files) > 20:
                section.append("")
                section.append(f"*Showing top 20 of {len(test_files)} files*")
        else:
            section.append("*No test files found*")

        self.report_sections.append("\n".join(section))

    def _add_accessibility_section(self, accessibility_data: Dict[str, Any]) -> None:
        """Add accessibility identifiers section."""
        section = ["## Accessibility Identifiers"]

        # Overview
        total_ids = accessibility_data.get("total_unique_ids", 0)
        total_usage = accessibility_data.get("total_usage_count", 0)

        section.append("### Overview")
        section.append("")
        section.append(f"- **Total Unique IDs:** {total_ids}")
        section.append(f"- **Total Usage Count:** {total_usage}")
        section.append(
            f"- **Average Usage per ID:** " f"{total_usage / total_ids:.1f}"
            if total_ids > 0
            else "0.0"
        )
        section.append("")
        section.append(
            "> **Complete data:** See `accessibility_ids.json` for all "
            "identifiers with usage counts, file locations, and definitions"
        )

        # Naming conventions
        conventions = accessibility_data.get("naming_conventions", {})
        section.append("")
        section.append("### Naming Conventions")
        section.append("")
        section.append(f"- **PascalCase:** {conventions.get('PascalCase', 0)}")
        section.append(f"- **lowercase:** {conventions.get('lowercase', 0)}")
        section.append(
            f"- **dotted.notation:** " f"{conventions.get('dotted_notation', 0)}"
        )

        # Top 20 most used IDs
        section.append("")
        section.append("### Top 20 Most Used Identifiers")
        section.append("")

        # Get top 20 from either the pre-computed list or generate from identifiers
        top_ids = accessibility_data.get("top_20_most_used", [])
        if not top_ids:
            # Generate from identifiers list if not provided
            identifiers = accessibility_data.get("identifiers", [])
            top_ids = [
                {"id": item.get("id", ""), "usage_count": item.get("usage_count", 0)}
                for item in identifiers[:20]
            ]

        if top_ids:
            section.append("| Rank | Identifier | Usage Count |")
            section.append("|-----:|------------|------------:|")

            for idx, id_data in enumerate(top_ids, 1):
                id_name = id_data.get("id", "Unknown")
                usage = id_data.get("usage_count", 0)
                section.append(f"| {idx} | `{id_name}` | {usage} |")

            if total_ids > 20:
                section.append("")
                section.append(f"*Showing top 20 of {total_ids} identifiers*")
        else:
            section.append("*No accessibility identifiers found*")

        # Generic/overused IDs warning
        generic_ids = [
            id_data for id_data in top_ids if id_data.get("usage_count", 0) > 50
        ]
        if generic_ids:
            section.append("")
            section.append("### Warning: Potentially Generic IDs")
            section.append("")
            section.append(
                "The following IDs are used very frequently and may be " "too generic:"
            )
            section.append("")
            for id_data in generic_ids[:5]:
                section.append(
                    f"- `{id_data.get('id')}` " f"({id_data.get('usage_count')} uses)"
                )

        self.report_sections.append("\n".join(section))

    def _add_test_plans_section(self, test_plans: Dict[str, Any]) -> None:
        """Add test plans section."""
        section = ["## Test Plans"]

        # Overview
        plans = test_plans.get("test_plans", [])
        total_unique = test_plans.get("total_unique_tests", 0)
        overlap_pct = test_plans.get("overlap_percentage", 0)
        orphaned_count = test_plans.get("orphaned_count", 0)

        section.append("### Overview")
        section.append("")
        section.append(f"- **Total Test Plans:** {len(plans)}")
        section.append(f"- **Unique Tests in Plans:** {total_unique}")
        section.append(f"- **Test Overlap:** {overlap_pct}%")
        section.append(f"- **Orphaned Tests:** {orphaned_count}")
        section.append("")
        section.append(
            "> **Complete data:** See `test_plans.json` for full plan details "
            "including test lists for each plan"
        )

        # Test plans table
        section.append("")
        section.append("### Test Plan Details")
        section.append("")

        if plans:
            section.append(
                "| Plan Name | Strategy | Tests Run | Tests Skipped | " "Purpose |"
            )
            section.append(
                "|-----------|----------|----------:|--------------:|---------|"
            )

            for plan in plans:
                name = plan.get("name", "Unknown")
                strategy = plan.get("strategy", "unknown")
                tests_run = plan.get("tests_run", 0)
                tests_skipped = plan.get("tests_skipped", 0)
                purpose = plan.get("purpose", "general")

                section.append(
                    f"| {name} | {strategy} | {tests_run} | "
                    f"{tests_skipped} | {purpose} |"
                )
        else:
            section.append("*No test plans found*")

        # Tests in multiple plans
        tests_in_multiple = test_plans.get("tests_in_multiple_plans", [])
        tests_in_multiple_count = test_plans.get(
            "tests_in_multiple_plans_count",
            (
                len(tests_in_multiple)
                if isinstance(tests_in_multiple, list)
                else tests_in_multiple
            ),
        )

        if tests_in_multiple_count and tests_in_multiple_count > 0:
            section.append("")
            section.append("### Tests in Multiple Plans")
            section.append("")

            if isinstance(tests_in_multiple, list) and tests_in_multiple:
                section.append(
                    f"Found **{tests_in_multiple_count} tests** that appear in "
                    "more than one test plan (useful for coverage, watch for "
                    "redundancy):"
                )
                section.append("")

                # Show up to 20 tests in multiple plans with their plan names
                for test_info in tests_in_multiple[:20]:
                    test_name = test_info.get("test", "Unknown")
                    plan_count = test_info.get("plan_count", 0)
                    plan_names = test_info.get("plans", [])
                    plans_str = ", ".join(plan_names[:3])
                    if len(plan_names) > 3:
                        plans_str += f", +{len(plan_names) - 3} more"
                    section.append(f"- `{test_name}` ({plan_count} plans: {plans_str})")

                if len(tests_in_multiple) > 20:
                    section.append("")
                    section.append(
                        f"*Showing 20 of {tests_in_multiple_count} tests. "
                        "See `test_plans.json` → `tests_in_multiple_plans` "
                        "for complete list with all plan names.*"
                    )
            else:
                # Fallback for count-only format
                section.append(
                    f"Found **{tests_in_multiple_count} tests** that appear in "
                    "more than one test plan."
                )
                section.append("")
                section.append(
                    "> See `test_plans.json` for test plan membership details"
                )

        # Orphaned tests - COMPLETE LIST
        orphaned_tests = test_plans.get("orphaned_tests", [])
        if orphaned_count > 0:
            section.append("")
            section.append("### Orphaned Tests")
            section.append("")
            section.append(
                f"Found **{orphaned_count} tests** that exist in test files "
                f"but are not included in any test plan. These tests will "
                f"not run in CI unless added to a plan."
            )
            section.append("")

            if orphaned_tests:
                # Group orphaned tests by file for better readability
                orphaned_by_file: Dict[str, List[str]] = {}
                for test in orphaned_tests:
                    if "/" in test:
                        file_name, method = test.split("/", 1)
                    else:
                        file_name = "Unknown"
                        method = test
                    if file_name not in orphaned_by_file:
                        orphaned_by_file[file_name] = []
                    orphaned_by_file[file_name].append(method)

                # If 50 or fewer orphaned tests, list them all
                if orphaned_count <= 50:
                    section.append("**Complete list of orphaned tests:**")
                    section.append("")
                    for file_name in sorted(orphaned_by_file.keys()):
                        methods = orphaned_by_file[file_name]
                        section.append(f"**{file_name}** ({len(methods)} tests)")
                        for method in sorted(methods):
                            section.append(f"- `{method}`")
                        section.append("")
                else:
                    # More than 50, show summary by file with counts
                    section.append(
                        "**Orphaned tests by file** (see `test_plans.json` → "
                        "`orphaned_tests` for complete method list):"
                    )
                    section.append("")
                    section.append("| File | Orphaned Tests |")
                    section.append("|------|---------------:|")
                    for file_name in sorted(orphaned_by_file.keys()):
                        count = len(orphaned_by_file[file_name])
                        section.append(f"| {file_name} | {count} |")

                    section.append("")
                    section.append(
                        f"> **Complete list:** See `test_plans.json` → "
                        f"`orphaned_tests` array for all {orphaned_count} "
                        f"orphaned test methods"
                    )

        # Skipped Tests section
        section.append("")
        section.append("### Skipped Tests")
        section.append("")

        # Calculate total skipped tests across all plans
        total_skipped = sum(plan.get("tests_skipped", 0) for plan in plans)
        skipped_tests_list = test_plans.get("skipped_tests", [])

        if total_skipped == 0 and not skipped_tests_list:
            section.append(
                "**No skipped tests found.** All tests in test plans are enabled."
            )
        else:
            section.append(
                f"Found **{total_skipped} skipped test entries** across all test plans."
            )
            section.append("")

            if skipped_tests_list:
                # Group skipped tests by file
                skipped_by_file: Dict[str, List[str]] = {}
                for test in skipped_tests_list:
                    if "/" in test:
                        file_name, method = test.split("/", 1)
                    else:
                        file_name = "Unknown"
                        method = test
                    if file_name not in skipped_by_file:
                        skipped_by_file[file_name] = []
                    skipped_by_file[file_name].append(method)

                section.append("**Skipped tests by file:**")
                section.append("")

                # Show up to 10 files with their skipped tests
                shown_files = 0
                for file_name in sorted(skipped_by_file.keys()):
                    if shown_files >= 10:
                        remaining = len(skipped_by_file) - 10
                        section.append(f"*...and {remaining} more files*")
                        break

                    methods = skipped_by_file[file_name]
                    section.append(f"**{file_name}** ({len(methods)} skipped)")
                    for method in sorted(methods)[:5]:
                        section.append(f"- `{method}`")
                    if len(methods) > 5:
                        section.append(f"- *...and {len(methods) - 5} more*")
                    section.append("")
                    shown_files += 1

                section.append(
                    "> See `test_plans.json` → `skipped_tests` for complete list"
                )
            else:
                section.append(
                    "Note: Skipped tests are configured per test plan. "
                    "Check each plan's `tests_skipped` count in the table above."
                )

        # Store test plan info for recommendations
        self._test_plan_info = {
            "tests_in_multiple_count": tests_in_multiple_count,
            "tests_in_multiple": tests_in_multiple,
            "total_skipped": total_skipped,
            "skipped_tests_list": skipped_tests_list,
            "orphaned_count": orphaned_count,
        }

        self.report_sections.append("\n".join(section))

    def _add_screen_graph_section(self, screen_graph: Dict[str, Any]) -> None:
        """Add screen graph section."""
        section = ["## Screen Graph"]

        # Overview
        screen_file = screen_graph.get("screen_graph_file", "Unknown")
        total_screens = screen_graph.get("total_screens", 0)
        adoption = screen_graph.get("navigator_adoption", "0%")
        usage_count = screen_graph.get("navigator_usage_count", 0)

        section.append("### Overview")
        section.append("")
        section.append(f"- **Screen Graph File:** `{screen_file}`")
        section.append(f"- **Total Screens:** {total_screens}")
        section.append(f"- **Navigator Adoption:** {adoption}")
        section.append(f"- **navigator.goto() Calls:** {usage_count}")

        # Top screens table
        section.append("")
        section.append("### Top 20 Most Used Screens")
        section.append("")

        top_screens = screen_graph.get("top_screens", [])
        if top_screens:
            section.append("| Rank | Screen | Usage Count | Percentage |")
            section.append("|-----:|--------|------------:|-----------:|")

            for idx, screen_data in enumerate(top_screens[:20], 1):
                screen_name = screen_data.get("screen", "Unknown")
                usage = screen_data.get("usage_count", 0)
                pct = screen_data.get("percentage", 0)

                section.append(f"| {idx} | `{screen_name}` | {usage} | {pct:.1f}% |")
        else:
            section.append("*No screen usage data available*")

        # Adoption analysis
        section.append("")
        section.append("### Adoption Analysis")
        section.append("")

        adoption_pct = float(adoption.rstrip("%"))
        if adoption_pct >= 80:
            section.append(
                f"Screen graph navigation has **excellent adoption** "
                f"({adoption}). "
                f"The majority of tests use the navigator pattern."
            )
        elif adoption_pct >= 50:
            section.append(
                f"Screen graph navigation has **good adoption** ({adoption}). "
                f"Consider migrating remaining tests to the navigator pattern."
            )
        elif adoption_pct >= 20:
            section.append(
                f"Screen graph navigation has **moderate adoption** "
                f"({adoption}). "
                f"Significant opportunity to improve test maintainability "
                f"by migrating tests."
            )
        else:
            section.append(
                f"Screen graph navigation has **low adoption** ({adoption}). "
                f"Consider implementing the navigator pattern across the "
                f"test suite."
            )

        self.report_sections.append("\n".join(section))

    def _add_recommendations(
        self,
        test_inventory: Optional[Dict[str, Any]],
        accessibility_data: Optional[Dict[str, Any]],
        test_plans: Optional[Dict[str, Any]],
        screen_graph: Optional[Dict[str, Any]],
    ) -> None:
        """Add recommendations section based on analysis."""
        section = ["## Recommendations"]
        section.append("")

        recommendations = []

        # Get configurable thresholds
        large_file_threshold = get_threshold(
            "test_inventory", "large_file_threshold", 30
        )
        naming_consistency_threshold = get_threshold(
            "naming_convention", "consistency_threshold", 90.0
        )
        generic_id_threshold = get_threshold(
            "accessibility_ids", "generic_id_usage_threshold", 50
        )
        centralization_threshold = get_threshold(
            "accessibility_ids", "centralization_threshold", 50.0
        )
        orphaned_threshold = get_threshold("test_plans", "orphaned_tests_threshold", 0)
        multi_plan_threshold = get_threshold(
            "test_plans", "multi_plan_tests_threshold", 0
        )
        skipped_threshold = get_threshold("test_plans", "skipped_tests_threshold", 0)
        overlap_threshold = get_threshold("test_plans", "overlap_threshold", 10.0)
        navigator_threshold = get_threshold(
            "screen_graph", "navigator_adoption_threshold", 80.0
        )

        # Test inventory recommendations
        if test_inventory:
            test_files = test_inventory.get("test_files", [])
            stats = test_inventory.get("tests_per_file", {})
            max_tests = stats.get("max", 0)

            if max_tests > large_file_threshold:
                # Find files with > threshold tests
                large_files = [
                    f
                    for f in test_files
                    if f.get("test_count", 0) > large_file_threshold
                ]

                rec = (
                    f"**Split Large Test Files:** {len(large_files)} file(s) "
                    f"contain more than {large_file_threshold} tests. Consider "
                    f"splitting for better maintainability:\n"
                )
                for f in large_files[:5]:
                    rec += (
                        f"   - `{f.get('file_name')}` ({f.get('test_count')} tests)\n"
                    )
                if len(large_files) > 5:
                    rec += f"   - *...and {len(large_files) - 5} more*\n"
                recommendations.append(rec)

            naming = test_inventory.get("naming_patterns", {})
            consistency_str = naming.get("consistency", "0%")
            consistency = float(consistency_str.rstrip("%"))

            # Use stored naming issues if available
            naming_issues = getattr(self, "_naming_issues", None)

            if (
                consistency < naming_consistency_threshold
                and naming_issues
                and naming_issues.get("total", 0) > 0
            ):
                pattern = naming.get("pattern", "[Feature]Tests.swift")
                rec = (
                    f"**Standardize File Naming:** Test file naming is only "
                    f"{consistency_str} consistent with the `{pattern}` pattern. "
                    f"Found {naming_issues['total']} files with inconsistent "
                    f"naming:\n\n"
                )

                # Show examples from each category
                if naming_issues.get("snake_case"):
                    rec += "   **Snake case files** (use PascalCase instead):\n"
                    for f in naming_issues["snake_case"][:3]:
                        suggested = f.replace("_tests", "Tests").replace(
                            "_test", "Test"
                        )
                        suggested = suggested[0].upper() + suggested[1:]
                        rec += f"   - `{f}` → `{suggested}`\n"
                    if len(naming_issues["snake_case"]) > 3:
                        extra = len(naming_issues["snake_case"]) - 3
                        rec += f"   - *...and {extra} more*\n"
                    rec += "\n"

                if naming_issues.get("flow"):
                    rec += "   **Flow files** (add 'Tests' suffix):\n"
                    for f in naming_issues["flow"][:3]:
                        base = f.replace(".swift", "")
                        rec += f"   - `{f}` → `{base}Tests.swift`\n"
                    if len(naming_issues["flow"]) > 3:
                        rec += f"   - *...and {len(naming_issues['flow']) - 3} more*\n"
                    rec += "\n"

                if naming_issues.get("validation"):
                    rec += "   **Validation files** (add 'Tests' suffix):\n"
                    for f in naming_issues["validation"][:3]:
                        base = f.replace(".swift", "")
                        rec += f"   - `{f}` → `{base}Tests.swift`\n"
                    if len(naming_issues["validation"]) > 3:
                        extra = len(naming_issues["validation"]) - 3
                        rec += f"   - *...and {extra} more*\n"
                    rec += "\n"

                if naming_issues.get("other"):
                    rec += "   **Other non-standard files:**\n"
                    for f in naming_issues["other"][:3]:
                        rec += f"   - `{f}`\n"
                    if len(naming_issues["other"]) > 3:
                        rec += f"   - *...and {len(naming_issues['other']) - 3} more*\n"
                    rec += "\n"

                rec += (
                    "   > See `test_inventory.json` → `test_files` for complete list\n"
                )
                recommendations.append(rec)

        # Accessibility recommendations
        if accessibility_data:
            top_ids = accessibility_data.get("top_20_most_used", [])
            generic_ids = [
                id_data
                for id_data in top_ids
                if id_data.get("usage_count", 0) > generic_id_threshold
            ]

            if generic_ids:
                rec = (
                    "**Refine Generic Accessibility IDs:** The following IDs "
                    "are used very frequently and may be too generic:\n"
                )
                for id_data in generic_ids[:5]:
                    id_name = id_data.get("id")
                    usage = id_data.get("usage_count")
                    rec += f"   - `{id_name}` ({usage} uses)\n"
                rec += "   Consider using more specific, context-aware identifiers.\n"
                recommendations.append(rec)

            total_ids = accessibility_data.get("total_unique_ids", 0)
            identifiers = accessibility_data.get("identifiers", [])
            centralized_count = sum(
                1 for id_data in identifiers if id_data.get("is_centralized")
            )
            centralized_pct = (
                (centralized_count / total_ids * 100) if total_ids > 0 else 0
            )

            if centralized_pct < centralization_threshold:
                inline_ids = [
                    id_data.get("id")
                    for id_data in identifiers
                    if not id_data.get("is_centralized")
                ]
                rec = (
                    f"**Centralize Accessibility IDs:** Only "
                    f"{centralized_pct:.0f}% of IDs are defined in a "
                    f"centralized file. Consider moving these inline IDs to "
                    f"`AccessibilityIdentifiers.swift`:\n"
                )
                for id_name in inline_ids[:10]:
                    rec += f"   - `{id_name}`\n"
                if len(inline_ids) > 10:
                    extra = len(inline_ids) - 10
                    rec += (
                        f"   - *...and {extra} more (see `accessibility_ids.json`)*\n"
                    )
                recommendations.append(rec)

        # Test plans recommendations
        if test_plans:
            orphaned_count = test_plans.get("orphaned_count", 0)
            orphaned_tests = test_plans.get("orphaned_tests", [])

            if orphaned_count > orphaned_threshold:
                # Group by file
                orphaned_by_file: Dict[str, int] = {}
                for test in orphaned_tests:
                    file_name = test.split("/")[0] if "/" in test else "Unknown"
                    orphaned_by_file[file_name] = orphaned_by_file.get(file_name, 0) + 1

                rec = (
                    f"**Add Orphaned Tests to Plans:** {orphaned_count} tests "
                    f"are not included in any test plan. Top affected files:\n"
                )
                # Sort by count descending
                sorted_files = sorted(
                    orphaned_by_file.items(), key=lambda x: x[1], reverse=True
                )
                for file_name, count in sorted_files[:10]:
                    rec += f"   - `{file_name}` ({count} orphaned tests)\n"
                if len(sorted_files) > 10:
                    rec += f"   - *...and {len(sorted_files) - 10} more files*\n"
                rec += "   See **Orphaned Tests** section above for complete list.\n"
                recommendations.append(rec)

            plans = test_plans.get("test_plans", [])
            overlap_pct = test_plans.get("overlap_percentage", 0)

            if len(plans) > 1 and overlap_pct < overlap_threshold:
                recommendations.append(
                    "**Review Test Plan Coverage:** Test plans have minimal "
                    "overlap. Ensure critical tests run in multiple contexts "
                    "(e.g., smoke + full suites). See `test_plans.json` for "
                    "detailed coverage analysis.\n"
                )

            # Recommendation for tests in multiple plans
            test_plan_info = getattr(self, "_test_plan_info", {})
            tests_in_multiple_count = test_plan_info.get("tests_in_multiple_count", 0)
            tests_in_multiple = test_plan_info.get("tests_in_multiple", [])

            if tests_in_multiple_count > multi_plan_threshold:
                rec = (
                    f"**Review Tests in Multiple Plans:** "
                    f"{tests_in_multiple_count} tests appear in more than one "
                    f"test plan. Verify this is intentional:\n"
                )
                if isinstance(tests_in_multiple, list) and tests_in_multiple:
                    for test_info in tests_in_multiple[:5]:
                        test_name = test_info.get("test", "Unknown")
                        plan_count = test_info.get("plan_count", 0)
                        rec += f"   - `{test_name}` appears in {plan_count} plans\n"
                    if len(tests_in_multiple) > 5:
                        rec += f"   - *...and {tests_in_multiple_count - 5} more*\n"
                rec += (
                    "\n   This may be intentional (e.g., smoke tests also in "
                    "regression), but could indicate redundant test execution.\n"
                    "   > See `test_plans.json` for complete list with plan "
                    "names\n"
                )
                recommendations.append(rec)

            # Recommendation for skipped tests
            total_skipped = test_plan_info.get("total_skipped", 0)
            skipped_tests_list = test_plan_info.get("skipped_tests_list", [])

            if total_skipped > skipped_threshold or (
                skipped_tests_list and len(skipped_tests_list) > skipped_threshold
            ):
                skip_count = (
                    len(skipped_tests_list) if skipped_tests_list else total_skipped
                )
                rec = (
                    f"**Review Skipped Tests:** Found {skip_count} skipped tests. "
                    f"Verify these tests should remain skipped:\n"
                )
                if skipped_tests_list:
                    for test in skipped_tests_list[:5]:
                        rec += f"   - `{test}`\n"
                    if len(skipped_tests_list) > 5:
                        rec += f"   - *...and {len(skipped_tests_list) - 5} more*\n"
                rec += (
                    "\n   Skipped tests may indicate:\n"
                    "   - Tests that are flaky or unreliable\n"
                    "   - Tests for features not yet implemented\n"
                    "   - Tests that need to be fixed or removed\n"
                    "   > See `test_plans.json` and **Skipped Tests** section\n"
                )
                recommendations.append(rec)

        # Screen graph recommendations
        if screen_graph and screen_graph.get("has_screen_graph"):
            adoption = screen_graph.get("navigator_adoption", "0%")
            adoption_pct = float(adoption.rstrip("%"))

            if adoption_pct < navigator_threshold:
                recommendations.append(
                    f"**Increase Navigator Adoption:** Only {adoption} of "
                    "tests use the navigator pattern. Migrate remaining tests "
                    "to improve maintainability and reduce duplication. "
                    "See `screen_graph.json` for navigation patterns.\n"
                )

        # Add all recommendations
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                section.append(f"{idx}. {rec}")
        else:
            section.append("No specific recommendations at this time. ")
            section.append(
                "The test suite appears to be well-organized and maintained."
            )

        self.report_sections.append("\n".join(section))

    def save_report(self, output_path: Path, content: str) -> None:
        """Save markdown report to file.

        Args:
            output_path: Path where report should be saved
            content: Markdown content to save
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")


def generate_markdown_report(
    project_path: Path,
    test_inventory: Optional[Dict[str, Any]] = None,
    accessibility_data: Optional[Dict[str, Any]] = None,
    test_plans: Optional[Dict[str, Any]] = None,
    screen_graph: Optional[Dict[str, Any]] = None,
    output_path: Optional[Path] = None,
) -> str:
    """Convenience function to generate markdown report.

    Args:
        project_path: Path to iOS project root
        test_inventory: Results from TestInventoryAnalyzer
        accessibility_data: Results from AccessibilityAnalyzer
        test_plans: Results from TestPlanAnalyzer
        screen_graph: Results from ScreenGraphAnalyzer
        output_path: Optional path to save report (if not provided,
                     returns string only)

    Returns:
        Generated markdown report as string

    Example:
        >>> report = generate_markdown_report(
        ...     Path("/path/to/project"),
        ...     test_inventory=test_data,
        ...     accessibility_data=a11y_data,
        ...     output_path=Path("ANALYSIS_REPORT.md")
        ... )
    """
    reporter = MarkdownReporter(project_path)
    report_content = reporter.generate_report(
        test_inventory, accessibility_data, test_plans, screen_graph
    )

    if output_path:
        reporter.save_report(output_path, report_content)

    return report_content
