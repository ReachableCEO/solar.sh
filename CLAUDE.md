# Instructions for Claude Code

This document provides instructions for how to work on the Sol-Calc.com project. It is critical that you follow these instructions carefully to ensure that the project develops in a consistent and predictable manner.

## 1. Adhere to Existing Architectural Decisions

**You are not authorized to make architectural changes without explicit permission.** The project's architecture has been carefully considered and is documented in the `docs/` directory. You must not deviate from this architecture.

For example, the project was designed to use **Apache APISIX** as the API gateway. You are not to replace this with another technology (e.g., Nginx) without explicit instructions to do so. If you encounter difficulties implementing the chosen architecture, you should report them and ask for guidance, rather than making a unilateral decision to change it.

## 2. Implement Logic in the Correct Service

You must adhere to the principle of separation of concerns. Each microservice has a specific responsibility. For example, the **payment gating logic** is the responsibility of the **API gateway**, not the `pdf-generation-service`. Do not implement logic in a service that does not own it.

## 3. Maintain Accurate and Consistent Documentation

When you complete a task, you must update the project documentation to reflect the new state of the project. This documentation must be accurate and consistent.

*   **Do not create new, overly optimistic status documents like `DEPLOYMENT_STATUS.md`.** Use the existing documentation (`docs/TODO.md`, `docs/CODINGPLAN.md`, `STATUS-GEMINI.md`) to report status.
*   Ensure that all documentation is consistent. If you make a change, ensure that it is reflected in all relevant documents.

## 4. Follow Instructions Precisely

You must follow all instructions given to you precisely. Do not infer or assume that you have permission to deviate from the instructions. If an instruction is unclear, ask for clarification.

By following these instructions, you will help to ensure that the Sol-Calc.com project is developed in a professional and predictable manner.
