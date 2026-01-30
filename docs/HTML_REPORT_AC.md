# HTML Report Acceptance Criteria

Based on the current dummy project analysis output.

**STATUS: ✅ ALL CRITERIA MET**

---

## Visual Design & Layout

### Theme (Apple-inspired)
- [x] Clean sans-serif font (SF Pro Text / system font stack)
- [x] Light gray background (`#f5f5f7`)
- [x] White card backgrounds with subtle shadows
- [x] Primary color: Blue (`#007AFF`)
- [x] Success: Green (`#34C759`)
- [x] Warning: Orange (`#FF9500`)
- [x] Danger: Red (`#FF3B30`)

### Section Dividers
- [x] Short horizontal line (80px) centered between subsections
- [x] Provides visual separation for easier scanning
- [x] Applied between all h3 subsections within each main section

### Spacing
- [x] Extra margin (2rem) above each h3 subsection heading
- [x] Padding (1.5rem) at top of subsections
- [x] Consistent gap between cards and tables

### Tables
- [x] Full-width tables with header row
- [x] Alternating row hover effect
- [x] Uppercase, smaller header text
- [x] Each table followed by JSON reference link

### Badges
- [x] Rounded pill-style badges for counts
- [x] Color-coded: success (green), warning (orange), danger (red), info (blue)

### Progress Bars
- [x] Used for consistency percentages
- [x] Color changes based on threshold (good/warning/danger)

---

## Header
- [x] Title: "iOS Test Suite Analysis Report"
- [x] Generated timestamp in UTC format
- [x] Project name displayed (not full path)

## Executive Summary
Top row (issue cards with color-coded severity):
- [x] Naming Issues count (16) - if test file naming configured
- [x] Orphaned Tests count (431)
- [x] Large Files count (3)

Bottom row (informational):
- [x] Total Tests: 505
- [x] Test Files: 58
- [x] Test Plans: 15

## Table of Contents
- [x] Link to Test Inventory
- [x] Link to Accessibility Identifiers
- [x] Link to Test Plans
- [x] Link to Recommendations
- [x] All links work (anchor navigation)

## Test Inventory Section
### Overview
- [x] Total Test Files: 58
- [x] Total Test Methods: 505
- [x] Tests per File stats (min, max, avg, median)
- [x] JSON reference link: `test_inventory.json`

### Test File Naming (if configured)
- [x] Expected Pattern: `[Feature]Tests.swift`
- [x] Consistency percentage with progress bar
- [x] Files Not Following Convention count
- [x] Categorized non-compliant files (Snake case, Flow, Validation, Scenario, Other)

### Test Method Naming (if configured)
- [x] Expected Style: `camelCase`
- [x] Consistency: 99.0%
- [x] Progress bar
- [x] Style breakdown: camelCase: 500 | snake_case: 3 | BDD: 2
- [x] Non-compliant methods table with columns: Method, Detected Style
- [x] Badge showing non-compliant count
- [x] JSON reference link: `test_inventory.json` → `method_naming_patterns.non_compliant_methods`

### Largest Test Files
- [x] Table with columns: File, Tests, Classes
- [x] Top 20 files shown
- [x] SearchTests.swift with 80 tests at top
- [x] "Showing top 20 of X files" note
- [x] JSON reference link: `test_inventory.json` → `test_files`

## Accessibility Identifiers Section
### Overview
- [x] Total Unique IDs: 84
- [x] Total Usage Count: 274
- [x] Average Usage per ID
- [x] JSON reference link: `accessibility_ids.json`

### Naming Conventions
- [x] Table with columns: Convention, Count, Examples
- [x] PascalCase count with 3 sample identifiers
- [x] dotted.notation count with 3 sample identifiers
- [x] lowercase count with 3 sample identifiers (or "—" if none)
- [x] JSON reference link: `accessibility_ids.json` → `identifiers` for complete list

### Top 20 Most Used Identifiers
- [x] Table with columns: Rank, Identifier, Usage Count
- [x] Badges for overused/high usage IDs
- [x] "Showing top 20 of X identifiers" note
- [x] JSON reference link: `accessibility_ids.json` → `identifiers`

### Generic IDs Warning
- [x] Warning about Done (150 uses)
- [x] Warning about Cancel (58 uses)

### Unused Identifiers
- [x] Header shows count with badge (61)
- [x] Table with columns: Identifier, Defined In
- [x] Shows where each unused ID is defined
- [x] "Showing X of Y unused identifiers" note for long lists
- [x] JSON reference link: `accessibility_ids.json` → `unused_identifiers`

## Test Plans Section
### Overview
- [x] Total Test Plans: 15
- [x] Unique Tests in Plans: 380
- [x] Tests in Multiple Plans: 380
- [x] Orphaned Tests: 431
- [x] JSON reference link: `test_plans.json`

### Test Plan Details Table
- [x] Columns: Plan Name, Tests
- [x] All 15 plans listed with test counts
- [x] JSON reference link: `test_plans.json` → `test_plans`

### Tests in Multiple Plans
- [x] Header shows count with badge
- [x] Sample tests listed with plan count
- [x] Shows which plans (e.g., "+12 more")
- [x] "Showing X of Y" note
- [x] JSON reference link

### Orphaned Tests
- [x] Header shows count with badge (431)
- [x] Explanation that these won't run in CI
- [x] Table by file showing orphaned count
- [x] JSON reference link

### Skipped Tests
- [x] Header shows count with badge
- [x] Table with columns: Test Class, Skipped, Sample Tests
- [x] "Showing X of Y files" note
- [x] JSON reference link

## Recommendations Section
Dynamic recommendations based on thresholds:

### Split Large Test Files
- [x] Shows files exceeding threshold (30 tests)
- [x] Lists affected files with test counts

### Standardize File Naming (if configured)
- [x] Shows consistency percentage
- [x] Shows non-compliant file count
- [x] Sample files listed
- [x] JSON reference link

### Standardize Method Naming (if below threshold)
- [x] Shows consistency percentage
- [x] Shows expected style
- [x] Non-compliant examples listed

### Refine Generic Accessibility IDs
- [x] Lists IDs exceeding usage threshold
- [x] Shows usage counts

### Remove Unused Accessibility IDs
- [x] Shows count of unused identifiers (61)
- [x] Lists sample unused IDs
- [x] Suggestion to remove or add coverage

### Add Orphaned Tests to Plans
- [x] Shows orphaned test count
- [x] Top affected files with counts
- [x] "...and X more files" note

### Review Tests in Multiple Plans
- [x] Shows count
- [x] Sample tests with plan counts
- [x] JSON reference link

### Review Skipped Tests
- [x] Shows count
- [x] Sample test names
- [x] Explains what skipped tests may indicate
- [x] JSON reference link

---

## Configuration (thresholds.json)

Default thresholds that trigger recommendations:

```json
{
  "test_inventory": {
    "large_file_threshold": 30
  },
  "test_file_naming": {
    "pattern": "[Feature]Tests.swift",
    "consistency_threshold": 90.0
  },
  "test_method_naming": {
    "pattern": "camelCase",
    "consistency_threshold": 85.0
  },
  "accessibility_ids": {
    "generic_id_usage_threshold": 50,
    "unused_ids_threshold": 0
  },
  "test_plans": {
    "orphaned_tests_threshold": 0
  }
}
```

---

## Output Files Generated

| File | Description |
|------|-------------|
| `ANALYSIS_REPORT.html` | Interactive HTML report (this spec) |
| `test_inventory.json` | All test files, classes, methods, naming patterns |
| `accessibility_ids.json` | ID usage patterns, naming conventions, unused IDs |
| `test_plans.json` | Plan analysis, orphaned tests, overlaps, skipped tests |
| `screen_graph.json` | Navigation patterns (if FxScreenGraph detected) |
| `metadata.json` | Analysis timestamp and project info |
