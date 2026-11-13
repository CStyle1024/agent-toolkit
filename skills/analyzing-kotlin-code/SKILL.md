---
name: analyzing-kotlin-code
description: Analyze specified Kotlin files or code snippets in Android, Android Framework, JVM, and mixed Kotlin-Java projects. Use when a developer needs to understand business responsibilities, execution paths, state, risks, Kotlin language features in real code, or Kotlin-Java/JVM interoperability; especially for maintainers learning Kotlin from Java, C++, or Android Framework backgrounds.
---

# Kotlin Code Analysis

Produce an evidence-based analysis of the supplied Kotlin code. Explain the business path before language syntax, and teach only the Kotlin features that affect the code being analyzed.

## Analyze

1. Define the boundary: supplied files, visible imports and types, likely entries, external symbols, and missing context.
2. Map the business: inputs, outputs, state, dependencies, success, failure, cancellation, and cleanup paths.
3. Select only components on the core path; do not turn utility types into architecture.
4. Trace the primary execution path in runtime order. Cite names and line numbers when available.
5. Explain Kotlin constructs that occur on, or materially affect, that path. Connect each one to its business purpose and Java mental model.
6. Inspect Java/JVM interoperability whenever Kotlin crosses a Java boundary or its declarations are consumed from Java.
7. Inspect Android, Framework, Binder, coroutine, Flow, lifecycle, threading, performance, permission, and multi-user concerns only when the visible code warrants it.
8. Separate confirmed defects, conditional risks, maintainability concerns, compatible improvements, and required follow-up context.

Use the detailed rules, diagram templates, report format, and final checklist in [references/analysis-guide.md](references/analysis-guide.md). Read the relevant sections before producing a detailed report; for Android Framework, coroutines, Flow, interoperability, diagrams, or large files, read the corresponding section rather than relying on general Kotlin knowledge.

## Evidence Rules

Label material conclusions as one of:

- **代码可确认** — directly visible in the provided code.
- **合理推断** — supported by the visible call site but needs surrounding context.
- **需要更多上下文** — cannot be established without callers, implementations, configuration, generated code, or runtime evidence.

Do not invent implementations, ownership, threading, process boundaries, lifecycle behavior, inheritance, or dispatcher changes. In particular, `suspend` does not imply background execution and a `Flow` does not necessarily run until collected.

## Diagrams

For non-trivial code, generate Mermaid diagrams that answer a concrete question and add a prose explanation after each diagram:

- Create a compact class diagram for two or more related core types.
- Create a sequence diagram for the primary path when meaningful calls are visible.
- Create a flowchart for important validation, state, branch, retry, or error logic.
- Add a specialized diagram only when concurrency, Flow, Binder, lifecycle, state, or data transformation makes it clearer.

Mark inferred nodes and relationships explicitly. Omit any diagram only when it cannot express a meaningful visible relationship, and explain why.

## Kotlin and Java

For every important Kotlin feature, show the smallest useful source excerpt; explain its semantics, business role, Java equivalent or mental model, JVM/Java-call impact where relevant, and maintenance risk. Cover only features actually present or required to safely modify the code.

At Kotlin-Java boundaries, check applicable property accessors, nullability/platform types, function types and SAM conversion, default parameters and `@Jvm*` annotations, companion/top-level declarations, generic wildcards, checked exceptions, `internal`, `suspend` continuations, generated data-class methods, and source/binary compatibility.

## Report

Use the fixed report structure in the reference. At minimum include the analysis scope, conclusion summary, business responsibility, component table, applicable diagrams, runtime paths, Kotlin features, interoperability, applicable Android/Framework concerns, risks categorized by confidence, learning priorities, and recommended next files.

For a small snippet, retain the same evidence discipline but omit inapplicable sections and explain omitted diagrams. For a large file, identify public entry points and state first, group functions by business responsibility, and prioritize the main path over helper-by-helper narration.

## Final Check

Before responding, verify that business behavior precedes syntax, all non-obvious conclusions are labeled by confidence, diagrams describe real relationships, Kotlin teaching is code-derived, Java compatibility is considered where relevant, and unresolved dependencies are listed with the source needed to resolve them.
