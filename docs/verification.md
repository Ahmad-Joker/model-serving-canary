# Verification and publication

Original build: Python 3.13, 2026-11-13. Initial isolated editable install failed because setuptools download was blocked by DNS/network access; installing with --no-build-isolation using local build tooling succeeded. Python compileall passed, 15 unittest cases passed and synthetic CLI smoke returned PASS.

Recovery: 2026-11-19, Python unittest: 15/15 passed; CLI --help executed successfully. GitHub publication is via branch feat/model-serving-canary-mvp; GitHub CI status is separate and must not be presumed passing. All metrics from generated fixture, not real deployed models.
