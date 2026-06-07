# PINN-A1 Private PINN Advisor Brief

Status: `PINN_A1_PRIVATE_PINN_ADVISOR_BRIEF_PASS`

## Summary

- source artifacts: `prod-a8-private-product-roadmap-post-cpg-selector, prod-a2-training-cost-estimator-private-spec`
- selected lane: `pinn_advisor`
- brief scope: `private_diagnostic_brief_only`
- supported inputs: `5`
- diagnostics: `5`
- caveats: `5`
- example boundaries: `3`
- dependencies: `4`
- blocked claims: `15`
- next recommended artifact: `PINN-A2 private PINN advisor fixture packet or hold selector`
- advisor implemented: `False`
- advisor executed: `False`
- scientific correctness claim: `False`
- public readiness claim: `False`

## Supported Inputs

- `pde_problem_summary`: `supported_for_private_advisory_shape` - Problem-shape context only; no claim that the PDE is correctly solved or fully specified.
- `training_loop_metadata`: `supported_for_training_context_advice` - Training-context metadata only; no convergence, stability, or cost-savings claim.
- `loss_component_history_summary`: `supported_for_balance_warning_advice` - Loss-shape summary only; no guarantee that loss trends diagnose the true physical error.
- `residual_sampling_summary`: `supported_for_sampling_gap_advice` - Sampling-context advice only; no coverage or solution-quality guarantee.
- `cost_estimator_packet_summary`: `supported_for_cost_context_advice` - Consumes cost context as caveated advice, not as runtime truth or savings proof.

## Advisory Diagnostics

- `loss_balance_warning`: Flag large imbalance or unexplained drift between data, physics, and boundary loss summaries. Boundary: Warning only; not evidence of correct or incorrect PDE solution.
- `residual_sampling_gap`: Point out sparse, static, or poorly described collocation sampling relative to the domain summary. Boundary: Review prompt only; not a coverage guarantee.
- `boundary_condition_visibility`: Check whether boundary/initial conditions are explicit enough for review. Boundary: Completeness prompt only; not formal problem validation.
- `cost_context_caveat_check`: Require calibration caveats and blocked claims to remain attached to any cost-context note. Boundary: Evidence hygiene only; not estimator accuracy.
- `reproducibility_packet_prompt`: Suggest private capture of seeds, package versions, device label, and training metadata before comparing runs. Boundary: Reviewer next step only; not a reproducibility guarantee.

## Dependencies

- `prod_a8_selector`: `required_and_consumed` - PROD-A8 selected PINN-A1 after SDK and compiler-plugin lanes were paused.
- `prod_a2_training_cost_caveats`: `required_and_consumed` - PINN advisor cost context must inherit training-cost estimator caveats and blocked claims.
- `private_pinn_example_inventory`: `future_private_review_needed` - Concrete example packets should be reviewed before any advisor implementation.
- `human_implementation_gate`: `blocked_pending_review` - Implementation, execution, public docs, and claims require explicit approval.

## Reviewer Questions

- `diagnostics_useful_without_science_claims`: Which diagnostics are genuinely useful as review prompts without implying PDE solution quality?
- `minimum_example_packet`: What is the smallest private example packet that can test the advisor language safely?
- `implementation_gate_condition`: What must be true before a PINN advisor implementation is worth building?

## Blocked Claims

- PINN solver correctness
- scientific correctness
- PDE solution validity
- training improvement
- training cost savings
- estimator accuracy
- model quality improvement
- wall-clock runtime performance
- compiler correctness
- semantic preservation
- SDK stability
- public product readiness
- hardware readiness
- silicon readiness
- broad EML advantage

## Non-Claims

- PINN-A1 is a private brief for a possible PINN advisor; it does not implement or execute an advisor.
- PINN-A1 records advisory inputs, diagnostics, caveats, examples, dependencies, blocked claims, and reviewer questions only.
- PINN-A1 does not run training, invoke a PINN solver, benchmark runtime, or evaluate scientific correctness.
- PINN-A1 does not claim training improvement, training savings, estimator accuracy, model quality, public readiness, SDK stability, compiler correctness, hardware readiness, silicon readiness, or broad EML advantage.
- PINN-A1 does not touch laptop-owned electronics repositories, start D110, or consume reviewer response.
