"""Validated API and execution contracts; inputs never become host commands.

Classes, functions, and module variables are indexed in docs/code-index.md.
This generated index is checked in CI to keep exact line locations current.
"""

import base64
import binascii
import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LANGUAGES = (
    "python",
    "javascript",
    "typescript",
    "cpp",
    "c",
    "java",
    "csharp",
    "rust",
    "php",
    "bash",
    "sql",
    "assembly",
)
Language = Literal[
    "python",
    "javascript",
    "typescript",
    "cpp",
    "c",
    "java",
    "csharp",
    "rust",
    "php",
    "bash",
    "sql",
    "assembly",
]
FUZZ_METHODS = (
    "generation",
    "mutation",
    "grammar",
    "dictionary",
    "boundary",
    "stateful",
    "differential",
    "metamorphic",
)


class Contract(BaseModel):
    """Forbid unknown properties across every public request and stored result."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SourceFile(Contract):
    """One flat, bounded file; content is UTF-8 text or an explicitly encoded attachment."""

    name: str = Field(min_length=1, max_length=80)
    content: str = Field(max_length=262144)
    encoding: Literal["text", "base64"] = "text"

    @field_validator("name")
    @classmethod
    def safe_name(cls, value: str) -> str:
        """Reject traversal, hidden files, command switches, and Windows device names."""
        stem = value.split(".", 1)[0].upper()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]*", value) or ".." in value:
            raise ValueError("Use a flat filename beginning with a letter")
        if stem in {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10)),
        }:
            raise ValueError("Reserved filename")
        return value

    def bytes(self) -> bytes:
        """Return bounded decoded bytes without interpreting or executing their format."""
        try:
            return (
                self.content.encode("utf-8")
                if self.encoding == "text"
                else base64.b64decode(self.content, validate=True)
            )
        except (ValueError, binascii.Error) as error:
            raise ValueError("Invalid base64 attachment") from error


class TestCase(Contract):
    """Developer-approved input/output oracle, immutable during candidate evaluation."""

    name: str = Field(min_length=1, max_length=80)
    stdin: str = Field(default="", max_length=8192)
    stdout: str = Field(max_length=8192)
    exit_code: int = Field(default=0, ge=0, le=255)


class Priorities(Contract):
    """Soft preferences only; correctness and verification are non-negotiable gates."""

    runtime: float = Field(default=0.4, ge=0, le=1)
    memory: float = Field(default=0.2, ge=0, le=1)
    readability: float = Field(default=0.25, ge=0, le=1)
    footprint: float = Field(default=0.15, ge=0, le=1)
    scrutiny: Literal["standard", "strict"] = "strict"

    @model_validator(mode="after")
    def nonzero(self) -> "Priorities":
        """Require at least one meaningful finite preference."""
        if (
            not math.isfinite(self.runtime + self.memory + self.readability + self.footprint)
            or self.runtime + self.memory + self.readability + self.footprint <= 0
        ):
            raise ValueError("Set at least one positive weight")
        return self


class Project(Contract):
    """Executable manifest; sources remain distinct from tests and supporting data."""

    title: str = Field(min_length=1, max_length=100)
    language: Language
    entry: str
    files: list[SourceFile] = Field(min_length=1, max_length=20)
    cases: list[TestCase] = Field(default_factory=list, max_length=64)
    requirements: str = Field(default="", max_length=16000)
    tests: str = Field(default="", max_length=64000)
    fuzz_methods: list[str] = Field(default_factory=lambda: ["boundary", "mutation"], max_length=8)
    fuzz_cases: int = Field(default=24, ge=0, le=128)
    seed: int = Field(default=42, ge=0, le=2147483647)
    benchmark_repeats: int = Field(default=3, ge=1, le=10)
    mutation: bool = False
    fuzz_engine: Literal["blackbox", "libfuzzer", "aflplusplus", "atheris"] = "blackbox"
    fuzz_harness: str = Field(default="", max_length=64000)
    priorities: Priorities = Field(default_factory=Priorities)

    @model_validator(mode="after")
    def coherent(self) -> "Project":
        """Validate unique names, entry text, total budget, and recognized fuzz strategies."""
        names = [file.name.casefold() for file in self.files]
        if len(set(names)) != len(names) or self.entry not in [file.name for file in self.files]:
            raise ValueError("Unique files and an existing entry are required")
        if next(file for file in self.files if file.name == self.entry).encoding != "text":
            raise ValueError("Entry must be text source")
        if sum(len(file.bytes()) for file in self.files) > 1048576:
            raise ValueError("Project exceeds one MiB")
        if any(method not in FUZZ_METHODS for method in self.fuzz_methods):
            raise ValueError("Unknown fuzz method")
        if len(set(self.fuzz_methods)) != len(self.fuzz_methods):
            raise ValueError("Duplicate fuzz methods")
        return self


class AIRequest(Contract):
    """Explicit transmission consent for a single bounded AI task."""

    task: Literal["generate", "tests", "improve", "suggest"]
    project: Project
    prompt: str = Field(default="", max_length=12000)
    consent: bool = False


class Proposal(Contract):
    """Untrusted model output awaiting validation and developer approval."""

    explanation: str = Field(max_length=8000)
    files: list[SourceFile] = Field(default_factory=list, max_length=20)
    tests: str = Field(default="", max_length=64000)
    suggestions: list[str] = Field(default_factory=list, max_length=20)
