# SDK-A2 Private SDK Import And CLI Smoke Contract

Status: `SDK_A2_PRIVATE_SDK_IMPORT_CLI_SMOKE_CONTRACT_PASS`

## Summary

- source artifact: `sdk-a1-private-sdk-surface-inventory`
- import probe contracts: `4`
- CLI probe contracts: `4`
- blocked probe contracts: `4`
- import probes executed: `False`
- CLI probes executed: `False`
- next recommended artifact: `SDK-A3 private SDK import and CLI smoke dry run`

## Import Probe Contracts

- `python_import_monogate`: PYTHONPATH=python python -c "import monogate"
- `python_import_monogate_validate`: PYTHONPATH=python python -c "import monogate.validate"
- `python_import_monogate_core_optional`: python -c "import monogate_core"
- `forge_preview_import_optional`: PYTHONPATH=packages/monogate-forge-preview/src python -c "import monogate_forge_preview"

## CLI Probe Contracts

- `cli_monogate_capability_card_help`: PYTHONPATH=python python -m monogate.cli.capability_card --help
- `cli_monogate_explore_help`: PYTHONPATH=python python -m monogate.cli.explore --help
- `cli_monogate_validate_help`: PYTHONPATH=python python -m monogate.validate --help
- `cli_forge_preview_help_optional`: PYTHONPATH=packages/monogate-forge-preview/src python -m monogate_forge_preview.cli --help

## Blocked Probe Contracts

- `native_benchmark_execution`: Runtime benchmarking would create performance-evidence obligations outside this smoke contract.
- `forge_emit_or_check_execution`: Compiler-preview emit/check execution belongs in a separate bounded Forge artifact.
- `electronics_repo_cli_probe`: Laptop-owned electronics/dev repos remain outside research-side SDK smoke ownership.
- `public_package_install_probe`: Public package release readiness is explicitly not claimed by SDK-A2.

## Non-Claims

- SDK-A2 defines a private smoke contract; it does not execute imports or CLIs.
- SDK-A2 does not change implementation or claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.
- SDK-A2 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.
- SDK-A2 respects the D109 hold and does not start D110, consume reviewer response, or record reviewer approval.
- SDK-A2 does not touch laptop-owned electronics repositories.
