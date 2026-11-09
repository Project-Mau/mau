from pathlib import Path

import pytest
import yaml

from mau import BASE_NAMESPACE, Mau
from mau.environment.environment import Environment
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
#
# A case can have an optional configuration file
# `CASE.config.yaml`, loaded under the namespace
# `mau` like the CLI does with `mau -c`.
#
# Cases are processed from the directory `cases/`,
# so paths in includes like `<< mau:` are relative
# to it. Files that are only included by other cases
# must be stored in a subdirectory, otherwise they
# would be collected as cases themselves.

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


# Build the environment of a case. If the case
# has a configuration file, its content is loaded
# under the base namespace, as the CLI does with
# the option `-c`. Otherwise the environment
# is empty.
def load_environment(mau_path):
    config_path = mau_path.with_suffix(".config.yaml")

    if not config_path.exists():
        return Environment()

    config = yaml.safe_load(config_path.read_text())

    return Environment.from_dict(config, BASE_NAMESPACE)


@pytest.mark.parametrize("mau_path,yaml_path", discover_cases())
def test_e2e(mau_path, yaml_path, request, monkeypatch):
    # Process the case from the directory `cases/`
    # so that included files can be referenced with
    # paths relative to it, wherever pytest runs.
    monkeypatch.chdir(CASES_DIR)

    # Run the full Mau pipeline on the
    # source file and strip non-deterministic
    # keys from the result.
    source = mau_path.read_text()

    mau = Mau(NullMessageHandler(), environment=load_environment(mau_path))
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
