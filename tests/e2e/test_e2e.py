from pathlib import Path

import pytest
import yaml

from mau import Mau
from mau.test_helpers import NullMessageHandler
from mau.visitors.yaml_visitor import YamlVisitor

# End-to-end tests that exercise the full Mau
# pipeline (lexer -> parser -> YAML visitor)
# on real `.mau` source files stored in `cases/`.
#
# Each `.mau` file has a companion `.yaml`
# reference. The test processes the source,
# strips non-deterministic keys, and asserts
# that the output matches the reference.
#
# Run with `--update-e2e-refs` to regenerate
# every reference file from the current output.

CASES_DIR = Path(__file__).parent / "cases"

# Keys produced by the visitor that must be
# excluded from comparison. The key `_context`
# contains line/column positions that shift
# when whitespace changes, and `parent` holds
# a recursive copy of the parent node that
# makes the comparison order-sensitive and
# bloated.
UNSTABLE_KEYS = {"_context", "parent"}


# The YAML output contains keys that are either
# non-deterministic across runs (like `_context`)
# or redundant for comparison purposes (like
# `parent`). This function walks the nested
# structure and drops them so that the golden-file
# comparison only covers semantically meaningful
# data.
def strip_unstable_keys(obj):
    if isinstance(obj, dict):
        return {
            k: strip_unstable_keys(v) for k, v in obj.items() if k not in UNSTABLE_KEYS
        }

    if isinstance(obj, list):
        return [strip_unstable_keys(item) for item in obj]

    return obj


# Build the parametrized case list by scanning
# `cases/` for `.mau` files. Each case is a pair
# of (mau_path, yaml_path) where `yaml_path` may
# or may not exist yet. Whether the missing
# reference causes a failure or a regeneration
# is decided by `test_e2e` at runtime.
def discover_cases():
    cases = []
    for mau_path in sorted(CASES_DIR.glob("*.mau")):
        yaml_path = mau_path.with_suffix(".yaml")
        cases.append(pytest.param(mau_path, yaml_path, id=mau_path.stem))
    return cases


@pytest.mark.parametrize("mau_path,yaml_path", discover_cases())
def test_e2e(mau_path, yaml_path, request):
    # Run the full Mau pipeline on the
    # source file and strip non-deterministic
    # keys from the result.
    source = mau_path.read_text()

    mau = Mau(NullMessageHandler())
    raw_yaml = mau.process(YamlVisitor, source, str(mau_path))

    actual = strip_unstable_keys(yaml.safe_load(raw_yaml))

    # When `--update-e2e-refs` is active,
    # overwrite (or create) the reference
    # file and skip the assertion.
    if request.config.getoption("--update-e2e-refs"):
        yaml_path.write_text(yaml.dump(actual, default_flow_style=False))
        pytest.skip("reference updated")

    # Fail explicitly when the reference
    # does not exist rather than raising
    # a confusing `FileNotFoundError`.
    if not yaml_path.exists():
        pytest.fail(
            f"Reference file {yaml_path.name} not found. "
            f"Run with --update-e2e-refs to generate it."
        )

    # Load the golden reference and compare.
    expected = strip_unstable_keys(yaml.safe_load(yaml_path.read_text()))

    assert actual == expected
