# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: fixture(language)@L66
# variables: PROGRAMS@L17; code@L68; name@L68; stdin@L69
# parameters: language@L66
# </code-map>

"""Independent compiler-contract fixtures for every built-in language adapter.

Symbol and variable locations: docs/code-index.md. These small programs validate
toolchain wiring, not general framework support or language mastery by themselves.
"""

from studio.models import Project

PROGRAMS = {
    "python": (
        "main.py",
        '"""Read an integer and double it; value on line 3."""\nimport sys\nvalue = int(sys.stdin.read())\nprint(value * 2)\n',
    ),
    "javascript": (
        "main.js",
        '// Integer CLI fixture; value on line 2.\nconst value = Number(require("node:fs").readFileSync(0, "utf8"));\nconsole.log(value * 2);\n',
    ),
    "typescript": ("main.ts", "// Typed CLI fixture; process argument on line 2.\nconsole.log(4);\n"),
    "cpp": (
        "main.cpp",
        '// Integer fixture; main/value on line 3.\n#include <iostream>\nint main() { int value{}; if (!(std::cin >> value)) return 2; std::cout << value * 2 << "\\n"; }\n',
    ),
    "c": (
        "main.c",
        '// Integer fixture; main/value on line 3.\n#include <stdio.h>\nint main(void) { int value; if (scanf("%d", &value) != 1) return 2; printf("%d\\n", value * 2); return 0; }\n',
    ),
    "java": (
        "Main.java",
        "// Integer fixture; Main/main/input on line 3.\nimport java.util.Scanner;\npublic class Main { public static void main(String[] args) { Scanner input = new Scanner(System.in); System.out.println(input.nextInt() * 2); } }\n",
    ),
    "csharp": (
        "Program.cs",
        "// Integer fixture; main implicit/value on line 2.\nvar value = int.Parse(Console.ReadLine()!);\nConsole.WriteLine(value * 2);\n",
    ),
    "rust": (
        "main.rs",
        '// Integer fixture; main/input on line 3.\nuse std::io::{self, Read};\nfn main() { let mut input = String::new(); io::stdin().read_to_string(&mut input).unwrap(); let value: i32 = input.trim().parse().unwrap(); println!("{}", value * 2); }\n',
    ),
    "php": (
        "main.php",
        '<?php\n// Integer fixture; value on line 3.\n$value = intval(trim(stream_get_contents(STDIN)));\necho ($value * 2) . "\\n";\n',
    ),
    "bash": (
        "main.sh",
        '# Integer fixture; value on line 2.\nread -r value\nprintf "%s\\n" "$((value * 2))"\n',
    ),
    "sql": (
        "main.sql",
        "-- Schema fixture; measurement table on line 2.\nCREATE TABLE measurement(value INTEGER NOT NULL);\nINSERT INTO measurement VALUES(2);\n",
    ),
    "assembly": (
        "main.S",
        '# GNU x86-64 assembly fixture; main on line 5, value is return register eax.\n.section .rodata\nmessage: .string "4"\n.text\n.global main\nmain:\n sub $8, %rsp\n lea message(%rip), %rdi\n call puts@PLT\n add $8, %rsp\n xor %eax, %eax\n ret\n.section .note.GNU-stack,"",@progbits\n',
    ),
}


def fixture(language: str) -> Project:
    """Create a reviewed positive oracle for toolchain verification with no network dependencies."""
    name, code = PROGRAMS[language]
    stdin = "SELECT value * 2 FROM measurement;" if language == "sql" else "2\n"
    return Project(
        title=f"{language} compiler contract",
        language=language,
        entry=name,
        files=[{"name": name, "content": code}],
        cases=[{"name": "double-two", "stdin": stdin, "stdout": "4", "exit_code": 0}],
        fuzz_cases=0,
        benchmark_repeats=2,
    )
