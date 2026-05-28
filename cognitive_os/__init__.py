"""Cognitive OS API v0.1.

A small, deterministic prototype of a user-owned policy and judgment layer
above upstream LLM providers.
"""

from .compiler import compile_profile
from .profiles import get_default_profile, list_default_profiles
from .runtime import compare_profiles, run_prompt
from .schemas import CCP, FiveAnchors, GateDecision
from .version import PROTOCOL_VERSION, __version__

__all__ = [
    "CCP",
    "FiveAnchors",
    "GateDecision",
    "PROTOCOL_VERSION",
    "__version__",
    "compile_profile",
    "compare_profiles",
    "get_default_profile",
    "list_default_profiles",
    "run_prompt",
]
