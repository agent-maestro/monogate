# SDK-A5 Private Explore CLI Help Import-Boundary Contract

Status: `SDK_A5_PRIVATE_EXPLORE_CLI_HELP_IMPORT_BOUNDARY_CONTRACT_PASS`

## Summary

- source artifact: `sdk-a4-private-sdk-smoke-result-review-selector`
- help boundary obligations: `3`
- dependency gate obligations: `3`
- blocked paths: `4`
- SDK implementation changed: `False`
- next recommended artifact: `SDK-A6 private explore CLI help import-boundary remediation implementation`

## Help Boundary Obligations

- `top_level_help_no_optional_substrate_import`: PYTHONPATH=python python -m monogate.cli.explore --help
- `top_level_version_no_optional_substrate_import`: PYTHONPATH=python python -m monogate.cli.explore --version
- `subcommand_help_no_optional_substrate_import`: PYTHONPATH=python python -m monogate.cli.explore witness --help

## Dependency Gate Obligations

- `witness_command_dependency_gate`: PYTHONPATH=python python -m monogate.cli.explore witness 'exp(x)'
- `analyze_command_dependency_gate`: PYTHONPATH=python python -m monogate.cli.explore analyze 'exp(x)'
- `identify_command_dependency_gate`: PYTHONPATH=python python -m monogate.cli.explore identify 'exp(x)'

## Blocked Paths

- `public_release_readiness_from_help_fix`: A help import-boundary fix would not prove the SDK is stable or public-release ready.
- `install_optional_extras_in_contract`: SDK-A5 records source-tree behavior obligations only; installed-extra smoke belongs in a later bounded artifact.
- `claim_explore_semantics`: The contract concerns import boundaries and dependency gates, not command semantic correctness.
- `touch_laptop_owned_repos`: The laptop/electronics repos are outside this research-side SDK remediation lane.

## Non-Claims

- SDK-A5 is a private remediation contract; it does not change SDK implementation or remediate the explore CLI.
- SDK-A5 does not execute remediation tests, rerun smoke probes, install optional dependencies, build native extensions, or install public packages.
- SDK-A5 does not claim SDK stability, public readiness, public package release readiness, API compatibility, or semantic-versioning commitments.
- SDK-A5 does not claim compiler correctness, semantic preservation, runtime performance, training savings, estimator accuracy, hardware readiness, silicon readiness, or broad EML advantage.
- SDK-A5 respects the D109 hold and does not start D110, consume reviewer response, or touch laptop-owned electronics repositories.
