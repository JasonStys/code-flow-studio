# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: location_fixture(language)@L77; module_fixture(language)@L98
# variables: SAMPLES@L18; data@L79; missing@L80; source@L80; unused@L80; lines@L90; i@L93; line@L93; i@L94; line@L94; typed@L100; suffix@L101; data@L102
# parameters: language@L77; language@L98
# </code-map>

"""Jason Stys: known positive/negative polyglot location oracles, executed only in restricted CI workers.

Each marker occurs once. Expected locations derive from authored source text, never analyzer output.
Symbol/parameter/variable declaration map: docs/code-index.md. These are tool-contract samples, not production apps.
"""

from examples.projects import fixture
from studio.models import Project

SAMPLES = {
    "javascript": (
        "function unused() {\n  return 7; // missed\n}\nconsole.log(4);\n/*# sourceMappingURL=/input/never-follow-uploaded-map.json */\n",
        "function unused",
        "return 7",
    ),
    "typescript": (
        "function unused(): number {\n  return 7; // missed\n}\nconsole.log(4);\n",
        "function unused",
        "return 7",
    ),
    "c": (
        '#include <stdio.h>\nstatic int unused(void) {\n  return 7; // missed\n}\nint main(void) {\n  int leftover = 1;\n  puts("4");\n  return 0;\n}\n',
        "int leftover",
        "return 7",
    ),
    "cpp": (
        '#include <iostream>\nstatic int unused() {\n  return 7; // missed\n}\nint main() {\n  int leftover = 1;\n  std::cout << "4\\n";\n}\n',
        "int leftover",
        "return 7",
    ),
    "rust": (
        'fn unused() -> i32 {\n    return 7; // missed\n}\nfn main() {\n    let leftover = 1;\n    println!("4");\n}\n',
        "let leftover",
        "return 7",
    ),
    "java": (
        "public class Main {\n  private static int unused() {\n    return 7; // missed\n  }\n  public static void main(String[] args) {\n    int leftover = 1;\n    System.out.println(4);\n  }\n}\n",
        "int leftover",
        "return 7",
    ),
    "csharp": (
        "using System;\nclass Program {\n  private static int leftover;\n  private static int Unused() {\n    return 7; // missed\n  }\n  static void Main() {\n    Console.WriteLine(4);\n  }\n}\n",
        "int leftover",
        "return 7",
    ),
    "php": (
        '<?php\nfunction unused() {\n  return 7; // missed\n}\nfunction work() {\n  $leftover = 1;\n  echo "4\\n";\n}\nwork();\n',
        "$leftover",
        "return 7",
    ),
    "bash": (
        '#!/bin/bash\nunused() {\n  printf "7\\n" # missed\n}\nleftover=1\nprintf "4\\n"\n',
        "leftover=1",
        'printf "7',
    ),
    "sql": (
        "WITH unused AS (SELECT 1) SELECT 4;\nSELECT * FROM missing_table;\nSELECT 7; -- missed\n",
        "unused AS",
        "SELECT 7",
    ),
    "assembly": (
        '# GNU x86-64 fixture: named local label is a review candidate, not proof of dead instructions.\n.section .rodata\nmessage: .string "4"\n.text\n.global main\nmain:\n sub $8, %rsp\n lea message(%rip), %rdi\n call puts@PLT\n add $8, %rsp\n xor %eax, %eax\n ret\nunused:\n mov $7, %eax # missed\n ret\n.section .note.GNU-stack,"",@progbits\n',
        "unused:",
        "mov $7",
    ),
}


def location_fixture(language: str) -> tuple[Project, int, int]:
    """Return a reviewed target and independent unused/missing source-line anchors."""
    data = fixture(language).model_dump()
    source, unused, missing = SAMPLES[language]
    data.update(files=[{"name": data["entry"], "content": source, "encoding": "text"}], benchmark_repeats=1)
    data["cases"] = [
        {
            "name": "known-path",
            "stdin": "",
            "stdout": "" if language == "sql" else "4",
            "exit_code": 1 if language == "sql" else 0,
        }
    ]
    lines = source.splitlines()
    return (
        Project.model_validate(data),
        next(i for i, line in enumerate(lines, 1) if unused in line),
        next(i for i, line in enumerate(lines, 1) if missing in line),
    )


def module_fixture(language: str) -> Project:
    """Exercise original auxiliary-module locations and genuinely unloaded files, never entry-only totals."""
    typed = language == "typescript"
    suffix = "ts" if typed else "js"
    data = fixture(language).model_dump()
    data.update(
        files=[
            {
                "name": data["entry"],
                "content": "import { work } from './helper';\nconsole.log(work());\n"
                if typed
                else "const helper = require('./helper.js');\nconsole.log(helper.work());\n",
            },
            {
                "name": f"helper.{suffix}",
                "content": (
                    "function unused(): number {\n  return 7;\n}\nexport function work(): number {\n  return 4;\n}\n"
                    if typed
                    else "function unused() {\n  return 7;\n}\nexports.work = function work() {\n  return 4;\n};\n"
                ),
            },
            {
                "name": f"unloaded.{suffix}",
                "content": "throw new Error('never import this auxiliary source during static analysis');\n",
            },
        ],
        benchmark_repeats=1,
    )
    return Project.model_validate(data)
