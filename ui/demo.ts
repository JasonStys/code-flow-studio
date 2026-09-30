/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: demo@L10
 * </code-map> */

/** Independent synthetic demo with approved oracles. No capstone code copied. Symbols: docs/code-index.md. */
import type { Project } from "./types";

export const demo: Project = {
  title: "CSV sensor normalizer",
  language: "python",
  entry: "main.py",
  files: [
    {
      name: "main.py",
      encoding: "text",
      content:
        '# CSV millimetre conversion demo; strict, finite numeric inputs.\nimport csv\nimport io\nimport math\nimport sys\n\ndef normalize(text):\n    """Convert explicit inch/cm/mm measurements to millimetres."""\n    factors = {"in": 25.4, "cm": 10.0, "mm": 1.0}\n    output = []\n    for row in csv.DictReader(io.StringIO(text)):\n        value = float(row["value"])\n        if not math.isfinite(value) or row["unit"] not in factors:\n            raise ValueError("Invalid measurement")\n        output.append(f"{row[\"id\"]},{value * factors[row[\"unit\"]]:.2f}")\n    return "\\n".join(output)\n\nif __name__ == "__main__":\n    try:\n        print(normalize(sys.stdin.read()))\n    except (ValueError, KeyError, TypeError):\n        print("Invalid input", file=sys.stderr)\n        sys.exit(2)\n',
    },
  ],
  cases: [
    {
      name: "inch",
      stdin: "id,value,unit\na,1,in\n",
      stdout: "a,25.40",
      exit_code: 0,
    },
    {
      name: "centimetre",
      stdin: "id,value,unit\nb,2,cm\n",
      stdout: "b,20.00",
      exit_code: 0,
    },
    {
      name: "nonfinite",
      stdin: "id,value,unit\nx,NaN,mm\n",
      stdout: "",
      exit_code: 2,
    },
  ],
  requirements:
    "Read CSV rows with id, value, unit. Convert finite in/cm/mm values to mm. Reject unsupported units and non-finite numbers with exit 2.",
  tests:
    'from main import normalize\nimport pytest\nfrom hypothesis import given, strategies as st\n\ndef test_empty():\n    assert normalize("id,value,unit\\n") == ""\n\n@given(st.integers(min_value=-10000,max_value=10000))\ndef test_mm_identity(value):\n    assert normalize(f"id,value,unit\\nx,{value},mm\\n") == f"x,{value:.2f}"\n\ndef test_unknown_unit():\n    with pytest.raises(ValueError):\n        normalize("id,value,unit\\nx,1,unknown\\n")\n',
  fuzz_methods: ["boundary", "mutation", "grammar", "dictionary", "generation"],
  fuzz_cases: 24,
  seed: 42,
  benchmark_repeats: 3,
  mutation: true,
  fuzz_engine: "blackbox",
  fuzz_harness: "",
  priorities: {
    runtime: 0.4,
    memory: 0.2,
    readability: 0.25,
    footprint: 0.15,
    scrutiny: "strict",
  },
};
