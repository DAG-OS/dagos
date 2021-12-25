# Use Vale to lint documentation

* Status: :accepted:
* Date: 2021-12-25

## Context and Problem Statement

Documentation is an integral part of any software project made for a group of people.
Creating succint and consistent documentation is non-trivial.
Is it possible to support developers in creating such documentation?

## Decision Drivers <!-- optional -->

* Tool maturity
* Extensibility
* Configuration cost
* Ease of use

## Considered Options

* [Vale](https://github.com/errata-ai/vale)
* Other linters mentioned in this [blog post](https://earthly.dev/blog/markdown-lint/)

## Decision Outcome

Chosen option: "Vale", because

* it's a mature and extendable documentation linter.
* through existing style guides most of the rules from other linters are already implemented.
* it integrates well with common IDEs such as Visual Studio Code.
* the cost of configuring the linter is low.
* it's fast.

### Compliance

For now a pre-commit hook runs on every commit to check for any extreme violations of the chosen style guides.
