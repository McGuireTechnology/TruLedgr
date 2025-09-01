# Security Policy

This document describes how to report security vulnerabilities in TruLedgr and what to expect after reporting.

## Reporting

Preferred methods (in order):

- Open a GitHub Security Advisory for the repository: use the GitHub "Security" tab and select **Report a vulnerability**.
- If you cannot use the GitHub advisory flow, email a report to: <security@mcguire.technology>.

## What to include

Provide as much of the following as you can:

- A clear summary of the issue and affected component(s) (repo/subproject/file).
- Steps to reproduce, minimal proof-of-concept (PoC) code or commands.
- Expected vs actual behaviour and impact (data exposure, code execution, privilege escalation, etc.).
- Environment details: TruLedgr version / commit SHA, OS, browser, dependencies, configuration.
- Any relevant logs, stack traces, or network captures.

Do not include sensitive data (passwords, private keys) in public reports. Use the secure channels above.

## Response and timeline

- Acknowledgement: within 3 business days (we will confirm receipt and next steps).
- Triage: initial assessment within 7 calendar days.
- Fix and coordinated disclosure: we aim for coordinated disclosure within 90 days, depending on severity and complexity. Critical issues may be accelerated; some fixes may take longer and will be communicated.

We will provide periodic updates and credit reporters unless you request anonymity.

## Supported releases

We support and provide fixes for the `main` branch and published releases from the last 12 months. If a vulnerability affects older releases, we will evaluate backporting on a case-by-case basis.

## Disclosure policy

We follow coordinated disclosure. Reporters should avoid public disclosure until the issue is fixed and a release or advisory is published. If you believe public disclosure is necessary (for legal/safety reasons), contact us and we will work with you to coordinate.

## CVE & reporting to third parties

If a CVE is appropriate, we will request it and coordinate assignment. For vulnerabilities in third-party dependencies, please report to the upstream maintainers as well and follow their disclosure channels.

## Safe harbor

We welcome good-faith security research. Reporters who follow this policy and act in good faith will not be subject to legal action by the project for their security research.

## After a fix

- We will publish a security advisory / release notes describing the issue, affected versions, and upgrade instructions.
- Follow the instructions in the advisory to upgrade and run any required migrations.

---
If you need help identifying the correct contact or have questions about this policy, open an issue or discussion on GitHub and tag it `security` (do not include exploit details in public issues).
