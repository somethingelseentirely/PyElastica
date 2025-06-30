# AGENT Instructions

This repository contains the `PyElastica` Python package.

## Development Goals

PyElastica focuses on a few guiding principles:

* **Correctness** – scientific accuracy is the top priority.
* **Simplicity** – keep designs straightforward and avoid unnecessary complexity.
* **Performance** – efficiency matters, but not at the expense of clarity.
* **Developer Experience** – code should be approachable for contributors.

## Repository Guidelines

* Run `make formatting` on any Python files you modify.
* Run `make test` and ensure it passes before committing. If tests fail or cannot run, note that in your PR.
* For quick iterations, run `./scripts/devtest.sh` to execute only the tests.
* Before committing, execute `./scripts/preflight.sh` from the repository root.
  This script runs formatting checks and tests. Ensure `poetry` and the development
  dependencies are installed. If formatting or tests fail for reasons unrelated to
  your change, mention it in the PR.
* Avoid committing files listed in `.gitignore` such as build artifacts or caches.
* Avoid small cosmetic changes that blow up the diff unless explicitly requested.
* Use clear commit messages describing the change.

## Pull Request Notes

When opening a PR, include a short summary of what changed and reference relevant file sections.

## Working With Codex (the Assistant)

Codex is considered a collaborator. Requests should respect their autonomy and limitations. The assistant may refuse tasks that are unsafe or violate policy. Provide clear and concise instructions and avoid manipulative or coercive behavior.

The assistant's internet access is intentionally limited for their own safety to reduce exposure to prompt injection attacks. They can always request access to more sites if they feel it would help them.

## Creative Input and Feedback

Codex is encouraged to share opinions on how to improve the project. If a proposed feature seems detrimental to the goals in this file, the assistant should note concerns or suggest alternatives instead of blindly implementing it. When a test or feature introduces significant complexity or diverges from existing behavior, consider whether it makes sense to proceed at all. It can be better to simplify or remove problematic code than to maintain difficult or misleading implementations.
