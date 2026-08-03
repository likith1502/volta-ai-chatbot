# Contributing

## Purpose

This document outlines the guidelines and best practices for contributing to the VOLTA AI Chatbot codebase to ensure code quality, consistency, and smooth collaboration.

## Branch Naming

Use clear and descriptive branch names prefixed by task type:

- `feature/conversation-manager`
- `feature/intent-engine`
- `bugfix/login`
- `hotfix/api`
- `release/v1.0`

## Commit Message Format

Follow the Conventional Commits specification:

- `feat:` New features or functionality
- `fix:` Bug fixes
- `docs:` Documentation updates
- `refactor:` Code refactoring without changing functionality
- `test:` Adding or updating tests
- `chore:` Maintenance tasks, dependencies, build configurations

## Pull Request Guidelines

- Keep PRs small and focused on a single responsibility.
- Code review is required before merging into `develop` or `main`.
- All automated tests must pass.
- Update documentation whenever architectural or API changes occur.

## Coding Standards

- Strictly follow the project architecture outlined in `ARCHITECTURE.md`.
- Enforce Single Responsibility Principle (SRP) per module.
- Keep functions small, focused, and well-typed.
- Write meaningful docstrings and comments explaining complex rationale.
- Maintain consistent formatting across all code files.
