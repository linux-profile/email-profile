# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in **email-profile**, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please send an email to **email@fernandocelmer.com** with:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested fix (optional)

You will receive a response within **72 hours** acknowledging the report. We will work with you to understand the issue and coordinate a fix before any public disclosure.

## Scope

The following are in scope for security reports:

- Credential exposure (passwords, tokens in logs or storage)
- Path traversal in attachment handling
- Injection vulnerabilities in IMAP/SMTP commands
- Insecure defaults in storage or connection handling
- Denial of service via resource exhaustion

## Disclosure Policy

- We will acknowledge receipt within 72 hours
- We will provide an estimated timeline for a fix within 1 week
- We will credit reporters in the release notes (unless anonymity is requested)
- We aim to release a fix within 30 days of a confirmed vulnerability
