"""monogate.frontiers — research experiment scripts."""

from .analog_renaissance import AnalogRenaissance, CrossDomainAnalogy
from .eml_complexity import (
    EML_1, EML_2, EML_3, EML_INF, COMPLEXITY_CLASSES,
    EMLComplexityClass, complexity_certificate, zero_order_lower_bound,
    zero_order_at, classify_function, complexity_table,
)
from .eml_fourier import (
    EMLBasisAtom, EMLFourierResult,
    build_eml_dictionary, eml_fourier_search, fourier_summary_table,
)
from .spatial_eml import (
    SpatialTarget, SpatialSRResult,
    CIRCLE_SDF, ELLIPSE_SDF, GAUSSIAN_2D, RING_SDF, INVERSE_SQ, AXIS_WAVE,
    ALL_TARGETS,
    fit_spatial_eml, eval_on_grid, formula_to_2d, print_results_table,
    radial_reduce, axis_reduce, reconstruct_radial, pareto_analysis,
)

__all__ = [
    "AnalogRenaissance", "CrossDomainAnalogy",
    "EML_1", "EML_2", "EML_3", "EML_INF", "COMPLEXITY_CLASSES",
    "EMLComplexityClass", "complexity_certificate", "zero_order_lower_bound",
    "zero_order_at", "classify_function", "complexity_table",
    "EMLBasisAtom", "EMLFourierResult",
    "build_eml_dictionary", "eml_fourier_search", "fourier_summary_table",
    "SpatialTarget", "SpatialSRResult",
    "CIRCLE_SDF", "ELLIPSE_SDF", "GAUSSIAN_2D", "RING_SDF", "INVERSE_SQ", "AXIS_WAVE",
    "ALL_TARGETS",
    "fit_spatial_eml", "eval_on_grid", "formula_to_2d", "print_results_table",
    "radial_reduce", "axis_reduce", "reconstruct_radial", "pareto_analysis",
]
