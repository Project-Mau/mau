# Register the `--update-e2e-refs` CLI flag so that
# E2E tests can regenerate their reference files
# instead of asserting against them.
def pytest_addoption(parser):
    parser.addoption(
        "--update-e2e-refs",
        action="store_true",
        default=False,
        help="Regenerate E2E reference YAML files from current output.",
    )
