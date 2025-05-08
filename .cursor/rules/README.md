# Cursor Rules for DCS Model Replication

## Purpose
These rules are designed to ensure that all work on this project strictly follows the mathematical models and theory described in each folder's documentation. The goal is to produce Python code that is mathematically faithful, well-documented, and robust, using best practices in scientific programming.

---

## General Principles
1. **Mathematical Fidelity**
   - Always replicate models exactly as described in the markdown theory files in each folder.
   - Do not make assumptions or shortcuts; if a step is unclear, reference the documentation or request clarification.
   - All mathematical derivations, equations, and logic must be explicitly implemented and commented.

2. **Documentation-Driven Development**
   - Each folder contains a markdown file (e.g., `3RUT_Theory.md`) with the theoretical background and equations.
   - Before coding, read and understand the relevant markdown file(s).
   - Reference the specific section/equation in the markdown when implementing each part of the model.

3. **Multi-Step Planning and Implementation**
   - For each model, plan the implementation in multiple prompts:
     1. **Theory Extraction:** Summarize the model, equations, and steps from the markdown file.
     2. **Design:** Outline the Python classes/functions needed, with clear mapping to the theory.
     3. **Implementation:** Write code in small, testable units, referencing the theory at each step.
     4. **Testing:** Write unit tests for all mathematical/model functions.
     5. **Validation:** Compare results to reference data or expected outputs if available.

4. **Best Practices in Python**
   - Use type hints, docstrings, and comments for all functions and classes.
   - Follow PEP8 and use strict linting/formatting (see workspace settings).
   - Prefer explicit, readable code over cleverness.
   - Use numpy, scipy, and other scientific libraries as appropriate, but always document how they map to the theory.
   - All code must be version controlled and reviewed before merging.

5. **Strict Review and Reasoning**
   - Every implementation step must be justified with reference to the theory.
   - If a mathematical step is ambiguous, document the reasoning and assumptions made.
   - All code must be reviewed for mathematical and computational correctness.

---

## Workflow for Each Model Folder
1. **Identify the Theory File:**
   - Locate the markdown file (e.g., `3RUT_Theory.md`) in the folder.
2. **Extract and Summarize:**
   - Summarize the model, equations, and steps to be implemented.
3. **Plan the Code:**
   - Outline the structure of the Python code, mapping each part to the theory.
4. **Implement in Steps:**
   - Write code for each part, referencing the theory and documenting thoroughly.
5. **Test and Validate:**
   - Write and run tests to ensure correctness.
6. **Document and Review:**
   - Ensure all code is documented, reviewed, and justified with reference to the theory.

---

## Example Prompt Sequence
1. "Summarize the model and equations in `BU_3RUT/3RUT_MBe1/3RUT_Theory.md`."
2. "Design Python classes/functions to implement the model, mapping each to the theory."
3. "Implement the first component (e.g., tissue compartment model) with reference to Section 2.1 of the markdown."
4. "Write unit tests for the tissue compartment model."
5. "Validate the model against provided data."

---

## Final Notes
- Be rigorous, methodical, and transparent in all work.
- The goal is to produce models that are both mathematically correct and maintainable for future research and development. 