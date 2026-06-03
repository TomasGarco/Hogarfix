Thank you for your interest in contributing to HogarFix!

Guidelines
- Fork the repository and create feature branches for changes.
- Keep changes focused and documented in a short commit message.
- Run linting and tests (if present) before creating a PR.

Code style
- Python: follow PEP8 and use 4-space indentation.
- Templates: keep Jinja2 logic minimal; prefer small helper functions in `app/utils.py`.

Security
- Never commit secrets. Add credentials to `.env` and never include `.env` in commits.

Pull requests
- Describe the change, reference any related issue, and include testing steps.
