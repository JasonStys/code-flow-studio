# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: catalog()@L69
# variables: TEST_NAMES@L14; HUMAN@L64; EXTERNAL@L65; AUTOMATED@L66; rows@L71; name@L72; number@L72; mode@L73; requirement@L82
# </code-map>

"""Explicit capability catalog from the supplied 48-category test reference.

Symbol and variable locations: docs/code-index.md. Categories are not pass results.
Human review and hardware evidence cannot be manufactured by automation.
"""

TEST_NAMES = (
    "Unit/component",
    "Integration",
    "Interface",
    "API",
    "System",
    "End-to-end",
    "Acceptance",
    "Smoke",
    "Sanity",
    "Confirmation/retesting",
    "Regression",
    "Exploratory",
    "Static analysis",
    "Peer review",
    "Walkthrough",
    "Formal inspection",
    "Functional",
    "GUI",
    "CLI",
    "Usability",
    "Accessibility",
    "Cross-browser compatibility",
    "Interoperability",
    "Installability",
    "Portability/configuration",
    "Performance",
    "Load",
    "Stress",
    "Soak/endurance",
    "Scalability/capacity",
    "Resource utilization",
    "Reliability",
    "Recovery/failover",
    "Chaos/fault injection",
    "Security",
    "Penetration",
    "Code/structural coverage",
    "Mutation",
    "Fuzzing",
    "Property-based",
    "Model-based",
    "Differential",
    "Software-in-the-loop",
    "Hardware-in-the-loop",
    "Hardware/software integration",
    "Data-driven",
    "Keyword-driven",
    "Combinatorial/pairwise",
)
HUMAN = {7, 12, 14, 15, 16, 20}
EXTERNAL = {18, 21, 22, 24, 25, 27, 28, 29, 30, 32, 33, 34, 36, 43, 44, 45}
AUTOMATED = {8, 9, 10, 11, 17, 19, 26, 31, 35, 37, 38, 39, 42, 46}


def catalog() -> list[dict]:
    """Expose honest applicability; a selected category still requires a real oracle/harness."""
    rows = []
    for number, name in enumerate(TEST_NAMES, 1):
        mode = (
            "manual"
            if number in HUMAN
            else "external"
            if number in EXTERNAL
            else "built-in"
            if number in AUTOMATED
            else "custom-harness"
        )
        requirement = {
            "manual": "Attach reviewer/participant evidence; never auto-passed.",
            "external": "Provide a scoped environment, tool, fixture or device; not built-in.",
            "built-in": "See language matrix; explicit cases, baseline and method prerequisites apply.",
            "custom-harness": "Supply reviewed pytest harness code for the isolated runner.",
        }[mode]
        rows.append({"id": number, "name": name, "mode": mode, "requirement": requirement})
    return rows
