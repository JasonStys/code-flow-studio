# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: _source(text)@L25; practical_project(language)@L477
# variables: PROGRAMS@L30; CASES@L321; SYNTAX_FAILURES@L437; RUNTIME_FAILURES@L458; content@L486; entry@L486; exit_code@L494; name@L494; stdin@L494; stdout@L494
# parameters: text@L25; language@L477
# </code-map>

"""Jason Stys: independent, realistic CLI cases for every supported worker adapter.

Only the restricted worker may compile or execute the embedded source strings.
``practical_project`` returns a fresh flat project; it never runs target code.
``PROGRAMS`` stores entry names/source, and ``CASES`` stores separately authored
input/output/exit oracles. ``SYNTAX_FAILURES`` binds deliberate compiler/parser
errors to exact authored lines. ``RUNTIME_FAILURES`` contains valid programs
which fail during execution. SQLite has no separate compilation phase.
Definition/variable line locations are maintained in docs/code-index.md.
"""

from textwrap import dedent

from studio.models import Project


def _source(text: str) -> str:
    """Remove fixture indentation while preserving predictable one-based source lines."""
    return dedent(text).lstrip("\n")


PROGRAMS: dict[str, tuple[str, str]] = {
    "python": (
        "main.py",
        _source('''
            """Summarize at most 64 comma-separated, bounded integer telemetry samples."""
            import sys

            def summarize(text):
                """Return count/sum/min/max; reject malformed or out-of-range samples."""
                if not text.strip():
                    return "0|0|NA|NA"
                values = [int(part.strip()) for part in text.strip().split(",")]
                if len(values) > 64 or any(value < -1000 or value > 1000 for value in values):
                    raise ValueError("Invalid telemetry range")
                return f"{len(values)}|{sum(values)}|{min(values)}|{max(values)}"

            try:
                print(summarize(sys.stdin.read()))
            except ValueError:
                raise SystemExit(2) from None
        '''),
    ),
    "javascript": (
        "main.js",
        _source("""
            // Integer-cent invoice; half-up discount rounding avoids binary currency arithmetic.
            const fields = require("node:fs").readFileSync(0, "utf8").trim().split(/\\s+/);
            if (fields.length !== 3 || fields.some((field) => !/^[0-9]+$/.test(field))) {
              process.exit(2);
            }
            const [quantity, unitCents, discountBps] = fields.map(Number);
            if (quantity > 1000 || unitCents > 1000000 || discountBps > 10000) {
              process.exit(2);
            }
            const subtotal = quantity * unitCents;
            const discount = Math.floor((subtotal * discountBps + 5000) / 10000);
            console.log(`${subtotal}|${discount}|${subtotal - discount}`);
        """),
    ),
    "typescript": (
        "main.ts",
        _source("""
            // Classify bounded temperature/vibration telemetry; this is an illustrative policy.
            declare function require(name: "node:fs"): {
              readFileSync(fd: number, encoding: "utf8"): string;
            };
            declare const process: { exit(code: number): never };
            const fields = require("node:fs").readFileSync(0, "utf8").trim().split(/\\s+/);
            if (fields.length !== 2 || fields.some((field) => !/^-?[0-9]+$/.test(field))) {
              process.exit(2);
            }
            const temperature = Number(fields[0]);
            const vibration = Number(fields[1]);
            if (temperature < -100 || temperature > 200 || vibration < 0 || vibration > 100) {
              process.exit(2);
            }
            const severity: "normal" | "warning" | "critical" =
              temperature >= 80 || vibration >= 70 ? "critical" :
              temperature >= 60 || vibration >= 40 ? "warning" : "normal";
            console.log(severity);
        """),
    ),
    "cpp": (
        "main.cpp",
        _source("""
            // Convert bounded sensor ticks using an explicit integer offset and gain.
            #include <iostream>
            #include <string>
            int main() {
              long long reading{}, offset{}, gain{};
              std::string extra;
              if (!(std::cin >> reading >> offset >> gain) || (std::cin >> extra)) return 2;
              if (reading < -10000 || reading > 10000 || offset < -10000 ||
                  offset > 10000 || gain < 1 || gain > 100) return 2;
              std::cout << (reading - offset) * gain << "\\n";
              return 0;
            }
        """),
    ),
    "c": (
        "main.c",
        _source("""
            // XOR checksum for a bounded count followed by unsigned byte values.
            #include <ctype.h>
            #include <errno.h>
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>
            static int next_value(char **cursor, long *value) {
              char *end;
              errno = 0;
              *value = strtol(*cursor, &end, 10);
              if (end == *cursor || errno == ERANGE) return 0;
              *cursor = end;
              return 1;
            }
            int main(void) {
              char buffer[8193];
              size_t length = fread(buffer, 1, sizeof(buffer) - 1, stdin);
              if (ferror(stdin) || !feof(stdin) || memchr(buffer, 0, length)) return 2;
              buffer[length] = 0;
              char *cursor = buffer;
              long count, value;
              unsigned checksum = 0;
              if (!next_value(&cursor, &count) || count < 0 || count > 16) return 2;
              for (long index = 0; index < count; ++index) {
                if (!next_value(&cursor, &value) || value < 0 || value > 255) return 2;
                checksum ^= (unsigned)value;
              }
              while (isspace((unsigned char)*cursor)) ++cursor;
              if (*cursor) return 2;
              printf("%u\\n", checksum);
              return 0;
            }
        """),
    ),
    "java": (
        "Main.java",
        _source("""
            // Allocate a bounded capacity after reserving slots; reject invalid requests.
            import java.util.Scanner;
            public class Main {
              private static long next(Scanner input) {
                if (!input.hasNextLong()) throw new IllegalArgumentException();
                return input.nextLong();
              }
              public static void main(String[] args) {
                try (Scanner input = new Scanner(System.in)) {
                  long capacity = next(input), reserved = next(input), requested = next(input);
                  if (input.hasNext() || capacity < 0 || capacity > 1000000 ||
                      reserved < 0 || reserved > capacity || requested < 0 || requested > 1000000) {
                    throw new IllegalArgumentException();
                  }
                  long available = capacity - reserved;
                  long accepted = Math.min(available, requested);
                  System.out.println(accepted + "|" + (available - accepted));
                } catch (IllegalArgumentException error) {
                  System.exit(2);
                }
              }
            }
        """),
    ),
    "csharp": (
        "Program.cs",
        _source("""
            // Decimal invoice; invariant formatting and explicit half-away-from-zero currency rounding.
            using System.Globalization;
            var fields = Console.In.ReadToEnd().Split((char[])null, StringSplitOptions.RemoveEmptyEntries);
            var culture = CultureInfo.InvariantCulture;
            if (fields.Length != 3 ||
                !int.TryParse(fields[0], NumberStyles.None, culture, out var quantity) ||
                !decimal.TryParse(fields[1], NumberStyles.AllowDecimalPoint, culture, out var unitPrice) ||
                !decimal.TryParse(fields[2], NumberStyles.AllowDecimalPoint, culture, out var taxPercent) ||
                quantity > 1000 || unitPrice > 1000000m || taxPercent > 100m) return 2;
            var subtotal = decimal.Round(quantity * unitPrice, 2, MidpointRounding.AwayFromZero);
            var tax = decimal.Round(subtotal * taxPercent / 100m, 2, MidpointRounding.AwayFromZero);
            Console.WriteLine(subtotal.ToString("F2", culture) + "|" + tax.ToString("F2", culture) +
                              "|" + (subtotal + tax).ToString("F2", culture));
            return 0;
        """),
    ),
    "rust": (
        "main.rs",
        _source("""
            // Apply a bounded inventory adjustment; never permit negative resulting stock.
            use std::io::{self, Read};
            fn adjust(text: &str) -> Result<String, ()> {
                let fields: Vec<i64> = text.split_whitespace()
                    .map(str::parse).collect::<Result<_, _>>().map_err(|_| ())?;
                if fields.len() != 2 || !(0..=1000000).contains(&fields[0]) ||
                    !(-1000000..=1000000).contains(&fields[1]) { return Err(()); }
                let balance = fields[0] + fields[1];
                if !(0..=1000000).contains(&balance) { return Err(()); }
                let state = if balance < 10 { "reorder" } else { "ok" };
                Ok(format!("{}|{}", balance, state))
            }
            fn main() {
                let mut input = String::new();
                if io::stdin().read_to_string(&mut input).is_err() { std::process::exit(2); }
                match adjust(&input) {
                    Ok(output) => println!("{}", output),
                    Err(()) => std::process::exit(2),
                }
            }
        """),
    ),
    "php": (
        "main.php",
        _source("""
            <?php
            // Integer-cent quote: ten or more units receive a rounded five-percent discount.
            $fields = preg_split('/\\s+/', trim(stream_get_contents(STDIN)));
            if (count($fields) !== 3) { exit(2); }
            foreach ($fields as $field) {
                if (!preg_match('/\\A[0-9]+\\z/', $field)) { exit(2); }
            }
            [$quantity, $unitCents, $shippingCents] = array_map('intval', $fields);
            if ($quantity > 1000 || $unitCents > 100000 || $shippingCents > 100000) { exit(2); }
            $subtotal = $quantity * $unitCents;
            $discount = $quantity >= 10 ? intdiv($subtotal * 5 + 50, 100) : 0;
            $total = $subtotal - $discount + ($quantity > 0 ? $shippingCents : 0);
            echo $subtotal . '|' . $discount . '|' . $total . "\\n";
        """),
    ),
    "bash": (
        "main.sh",
        _source("""
            # Count exact log severities; blank lines are ignored, unknown values are rejected.
            ok=0
            warning=0
            error=0
            while IFS= read -r severity || [[ -n "$severity" ]]; do
              case "$severity" in
                OK) ((ok += 1)) ;;
                WARN) ((warning += 1)) ;;
                ERROR) ((error += 1)) ;;
                '') continue ;;
                *) exit 2 ;;
              esac
            done
            printf '%s|%s|%s\\n' "$ok" "$warning" "$error"
        """),
    ),
    "sql": (
        "main.sql",
        _source("""
            -- Fresh in-memory order schema; test queries supply independently reviewed reports.
            PRAGMA foreign_keys = ON;
            CREATE TABLE products (
              sku TEXT PRIMARY KEY, unit_cents INTEGER NOT NULL CHECK (unit_cents >= 0)
            );
            CREATE TABLE orders (
              id INTEGER PRIMARY KEY,
              sku TEXT NOT NULL REFERENCES products(sku),
              quantity INTEGER NOT NULL CHECK (quantity >= 0)
            );
            INSERT INTO products VALUES ('sensor', 1200), ('cable', 500), ('spare', 0);
            INSERT INTO orders VALUES (1, 'sensor', 2), (2, 'cable', 3),
              (3, 'sensor', 1), (4, 'spare', 0);
        """),
    ),
    "assembly": (
        "main.S",
        _source("""
            # GNU Linux x86-64 C ABI: decode three illustrative alarm bits from a bounded input mask.
            .section .rodata
            scan_format: .string "%1[0-7] %c"
            report_format: .string "%d|%d|%d\\n"
            .text
            .global main
            .type main, @function
            main:
              subq $24, %rsp
              leaq 8(%rsp), %rsi
              leaq 12(%rsp), %rdx
              leaq scan_format(%rip), %rdi
              xorl %eax, %eax
              call scanf@PLT
              cmpl $1, %eax
              jne invalid_input
              movzbl 8(%rsp), %eax
              subl $48, %eax
              cmpl $7, %eax
              ja invalid_input
              movl %eax, %esi
              andl $1, %esi
              movl %eax, %edx
              shrl $1, %edx
              andl $1, %edx
              movl %eax, %ecx
              shrl $2, %ecx
              andl $1, %ecx
              leaq report_format(%rip), %rdi
              xorl %eax, %eax
              call printf@PLT
              xorl %eax, %eax
              jmp finish
            invalid_input:
              movl $2, %eax
            finish:
              addq $24, %rsp
              ret
            .size main, .-main
            .section .note.GNU-stack,"",@progbits
        """),
    ),
}

# Oracles are literal reviewed expectations, not values calculated by the target programs.
# Tuple fields: descriptive case name, standard input, expected standard output, expected exit code.
CASES: dict[str, tuple[tuple[str, str, str, int], ...]] = {
    "python": (
        ("telemetry-window", "20,30,10\n", "3|60|10|30", 0),
        ("zero-readings", "0,0\n", "2|0|0|0", 0),
        ("signed-readings", "-5,5\n", "2|0|-5|5", 0),
        ("empty-window", "", "0|0|NA|NA", 0),
        ("range-boundaries", "-1000,1000\n", "2|0|-1000|1000", 0),
        ("malformed-reading", "12,bad\n", "", 2),
    ),
    "javascript": (
        ("discounted-invoice", "3 1999 1000\n", "5997|600|5397", 0),
        ("zero-quantity", "0 1999 1000\n", "0|0|0", 0),
        ("full-discount", "2 2500 10000\n", "5000|5000|0", 0),
        ("half-cent-rounding", "1 1 5000\n", "1|1|0", 0),
        ("malformed-price", "2 nope 0\n", "", 2),
        ("negative-quantity", "-1 100 0\n", "", 2),
    ),
    "typescript": (
        ("normal-sample", "25 10\n", "normal", 0),
        ("warning-boundary", "60 0\n", "warning", 0),
        ("critical-boundary", "20 70\n", "critical", 0),
        ("zero-sample", "0 0\n", "normal", 0),
        ("maximum-sample", "200 100\n", "critical", 0),
        ("malformed-sample", "x 10\n", "", 2),
    ),
    "cpp": (
        ("calibrated-reading", "1200 200 2\n", "2000", 0),
        ("zero-adjustment", "200 200 3\n", "0", 0),
        ("negative-adjustment", "-100 100 2\n", "-400", 0),
        ("bounded-maximum", "10000 -10000 100\n", "2000000", 0),
        ("malformed-reading", "x 0 1\n", "", 2),
        ("invalid-gain", "100 0 0\n", "", 2),
    ),
    "c": (
        ("packet-checksum", "3 16 32 255\n", "207", 0),
        ("empty-packet", "0\n", "0", 0),
        ("maximum-byte", "1 255\n", "255", 0),
        ("cancelling-bytes", "4 12 12 0 0\n", "0", 0),
        ("malformed-byte", "2 1 bad\n", "", 2),
        ("out-of-range-byte", "1 256\n", "", 2),
    ),
    "java": (
        ("capacity-allocation", "100 20 50\n", "50|30", 0),
        ("zero-capacity", "0 0 0\n", "0|0", 0),
        ("malformed-capacity", "many 0 1\n", "", 2),
        ("exact-capacity", "100 0 100\n", "100|0", 0),
        ("demand-over-capacity", "100 20 120\n", "80|0", 0),
        ("invalid-reservation", "100 101 1\n", "", 2),
    ),
    "csharp": (
        ("taxed-invoice", "3 19.99 8.25\n", "59.97|4.95|64.92", 0),
        ("zero-quantity", "0 19.99 8.25\n", "0.00|0.00|0.00", 0),
        ("half-cent-tax", "1 0.05 10\n", "0.05|0.01|0.06", 0),
        ("tax-free-invoice", "2 7.50 0\n", "15.00|0.00|15.00", 0),
        ("bounded-maximum", "1 1000000 100\n", "1000000.00|1000000.00|2000000.00", 0),
        ("malformed-price", "1 money 8\n", "", 2),
    ),
    "rust": (
        ("inventory-withdrawal", "20 -5\n", "15|ok", 0),
        ("zero-inventory", "0 0\n", "0|reorder", 0),
        ("reorder-boundary", "9 1\n", "10|ok", 0),
        ("empty-inventory", "10 -10\n", "0|reorder", 0),
        ("reject-overdraft", "5 -6\n", "", 2),
        ("malformed-adjustment", "bad 1\n", "", 2),
    ),
    "php": (
        ("ordinary-quote", "3 1200 500\n", "3600|0|4100", 0),
        ("bulk-discount", "10 1000 500\n", "10000|500|10000", 0),
        ("zero-order", "0 1000 500\n", "0|0|0", 0),
        ("half-cent-discount", "10 1 0\n", "10|1|9", 0),
        ("bounded-maximum", "1000 100000 100000\n", "100000000|5000000|95100000", 0),
        ("malformed-price", "2 nope 1\n", "", 2),
    ),
    "bash": (
        ("mixed-log", "OK\nWARN\nERROR\nWARN\n", "1|2|1", 0),
        ("empty-log", "", "0|0|0", 0),
        ("blank-lines", "\n\n", "0|0|0", 0),
        ("missing-final-newline", "ERROR", "0|0|1", 0),
        ("all-ok", "OK\nOK\n", "2|0|0", 0),
        ("unknown-severity", "OK\nMAYBE\n", "", 2),
    ),
    "sql": (
        (
            "joined-revenue",
            "SELECT SUM(o.quantity * p.unit_cents) FROM orders o JOIN products p USING (sku);",
            "5100",
            0,
        ),
        (
            "ordered-product-report",
            "SELECT p.sku, COALESCE(SUM(o.quantity * p.unit_cents), 0) "
            "FROM products p LEFT JOIN orders o USING (sku) GROUP BY p.sku ORDER BY p.sku;",
            "cable|1500\nsensor|3600\nspare|0",
            0,
        ),
        (
            "missing-product-zero",
            "SELECT COALESCE(SUM(quantity), 0) FROM orders WHERE sku = 'missing';",
            "0",
            0,
        ),
        ("zero-quantity-order", "SELECT COUNT(*) FROM orders WHERE quantity = 0;", "1", 0),
        ("reject-negative-quantity", "INSERT INTO orders VALUES (5, 'sensor', -1);", "", 1),
        ("malformed-query", "SELECT FROM orders;", "", 1),
    ),
    "assembly": (
        ("no-alarm", "0\n", "0|0|0", 0),
        ("first-alarm", "1\n", "1|0|0", 0),
        ("third-alarm", "4\n", "0|0|1", 0),
        ("all-alarm-bits", "7\n", "1|1|1", 0),
        ("out-of-range-mask", "8\n", "", 2),
        ("malformed-mask", "bad\n", "", 2),
    ),
}


SYNTAX_FAILURES: dict[str, dict[str, str | int]] = {
    "python": {"content": "def broken(:\n    pass\n", "line": 1},
    "javascript": {"content": "const broken = ;\n", "line": 1},
    "typescript": {"content": "const broken: number = ;\n", "line": 1},
    "cpp": {"content": "int main() {\n    int value = ;\n}\n", "line": 2},
    "c": {"content": "int main(void) {\n    int value = ;\n}\n", "line": 2},
    "java": {
        "content": "public class Main {\n  public static void main(String[] args) {\n    int value = ;\n  }\n}\n",
        "line": 3,
    },
    "csharp": {"content": "using System;\nConsole.WriteLine(;\n", "line": 2},
    "rust": {"content": "fn main() {\n    let value = ;\n}\n", "line": 2},
    "php": {"content": "<?php\n$value = ;\n", "line": 2},
    "bash": {"content": "if then\n  :\nfi\n", "line": 1},
    "assembly": {
        "content": '.text\n.global main\nmain:\n this_is_not_an_instruction\n.section .note.GNU-stack,"",@progbits\n',
        "line": 4,
    },
}


RUNTIME_FAILURES: dict[str, str] = {
    "python": "def fail():\n    raise RuntimeError('Synthetic runtime failure')\nfail()\n",
    "javascript": "throw new Error('Synthetic runtime failure');\n",
    "typescript": "throw new Error('Synthetic runtime failure');\n",
    "cpp": "int main() { return 7; }\n",
    "c": "int main(void) { return 7; }\n",
    "java": "public class Main { public static void main(String[] args) { System.exit(7); } }\n",
    "csharp": "return 7;\n",
    "rust": "fn main() { std::process::exit(7); }\n",
    "php": "<?php\nexit(7);\n",
    "bash": "exit 7\n",
    "sql": "CREATE TABLE present(value INTEGER);\nINSERT INTO missing_table VALUES (7);\n",
    "assembly": (
        ".text\n.global main\n.type main, @function\nmain:\n movl $7, %eax\n ret\n"
        '.section .note.GNU-stack,"",@progbits\n'
    ),
}


def practical_project(language: str) -> Project:
    """Build one fresh approved project; unknown languages fail without choosing a fallback.

    ``language`` selects a fixed worker adapter. Returned sources and six literal
    cases are independent copies; callers may replace them for negative tests
    without changing another scenario. Benchmarks repeat once and fuzzing is
    disabled here, keeping these deterministic CLI oracles distinct from the
    existing dedicated fuzz/mutation/location suites.
    """
    entry, content = PROGRAMS[language]
    return Project(
        title=f"Practical {language} standard-library CLI validation",
        language=language,
        entry=entry,
        files=[{"name": entry, "content": content}],
        cases=[
            {"name": name, "stdin": stdin, "stdout": stdout, "exit_code": exit_code}
            for name, stdin, stdout, exit_code in CASES[language]
        ],
        requirements=(
            "Synthetic bounded CLI demonstration. Preserve the approved stdout and exit-code "
            "oracles, reject invalid input explicitly, and use no network or external packages."
        ),
        benchmark_repeats=1,
        fuzz_cases=0,
        mutation=False,
    )
