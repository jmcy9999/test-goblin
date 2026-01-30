# Test Goblin

**Find orphaned tests, inconsistent naming, overused identifiers, bloated test files, and more — in under 1 second.**

A zero-dependency CLI tool that analyzes your iOS XCUITest suite and surfaces actionable recommendations to keep your tests healthy.

## Why Use This?

Your test suite grows organically. Tests get added, renamed, skipped, forgotten. Before you know it:

- **431 tests** aren't in any test plan (they never run in CI)
- **16 files** don't follow your naming convention
- **3 files** have 30+ tests and are impossible to maintain
- **61 accessibility IDs** are defined but never used in tests
- **5 test methods** don't follow your naming convention

This tool finds these issues instantly and tells you exactly what to fix.

## Quick Start

```bash
pip install test-goblin
test-goblin analyze /path/to/your/ios-project
```

That's it. In under a second, you get a full analysis report.

## Example Output

```
✓ Analysis complete!

Results:
  - 58 test files
  - 505 test methods
  - 84 accessibility IDs
  - 15 test plans

Output: ./analysis/
Time: 0.15s
```

### Sample Recommendations

```markdown
## Recommendations

- **Split Large Test Files:** 3 file(s) contain more than 30 tests
- **Standardize File Naming:** 71.9% consistent, 16 non-compliant files
- **Standardize Method Naming:** 99.0% consistent (camelCase expected)
- **Refine Generic Accessibility IDs:** Done (150 uses), Cancel (58 uses)
- **Remove Unused Accessibility IDs:** 61 IDs defined but never used
- **Add Orphaned Tests to Plans:** 431 tests never run in CI
```

## Use in Your PR Workflow

Add to your CI pipeline to catch test hygiene issues before they merge:

```yaml
- name: Analyze Test Suite
  run: |
    test-goblin analyze . --quiet
    # Fails if critical issues found (coming soon)
```

Keep your test suite healthy with every PR.

## Configurable Thresholds

Customize what triggers recommendations via `thresholds.json`:

| Section | Threshold | Default | Triggers When... |
|---------|-----------|---------|------------------|
| `test_inventory` | `large_file_threshold` | 30 | File has more than 30 tests |
| `test_file_naming` | `pattern` | `[Feature]Tests.swift` | Expected naming pattern (null to skip) |
| `test_file_naming` | `consistency_threshold` | 90% | File naming consistency below 90% |
| `test_method_naming` | `pattern` | `camelCase` | Expected style (camelCase/snake_case/BDD) |
| `test_method_naming` | `consistency_threshold` | 85% | Method naming consistency below 85% |
| `accessibility_ids` | `generic_id_usage_threshold` | 50 | ID used 50+ times |
| `accessibility_ids` | `unused_ids_threshold` | 0 | Any ID defined but unused |
| `test_plans` | `orphaned_tests_threshold` | 0 | Any test not in a plan |

```bash
test-goblin analyze /path/to/project --config ./my-thresholds.json
```

See [Configuration Guide](docs/USAGE.md#configuration) for all options.

## Output Files

| File | Contents |
|------|----------|
| `ANALYSIS_REPORT.html` | Interactive HTML report with recommendations |
| `test_inventory.json` | All test files, classes, methods |
| `accessibility_ids.json` | ID usage patterns and definitions |
| `test_plans.json` | Plan analysis, orphaned tests, overlaps |
| `screen_graph.json` | Navigation patterns (if detected) |

## Installation

### From PyPI (recommended)

```bash
pip install test-goblin
```

### From Source

```bash
git clone https://github.com/jmcy9999/test-goblin.git
cd test-goblin
pip install -e .
```

Requires Python 3.10+. No external dependencies.

## Documentation

- [Usage Guide](docs/USAGE.md) — CLI options, examples, configuration
- [HTML Report Spec](docs/HTML_REPORT_AC.md) — Complete HTML report acceptance criteria
- [Sample Report](docs/assets/sample_report.html) — Example analysis output

## License

MIT
