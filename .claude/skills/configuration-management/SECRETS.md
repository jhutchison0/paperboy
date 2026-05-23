# SECRETS — .env Management, Rotation, and Production Stores

Sidecar to `SKILL.md`. How to keep secrets out of git, rotate them safely, and use production secret stores when local `.env` is no longer enough.

## .env Files: Local Pattern

Two files, one committed, one ignored.

`.env.example` (committed — see `STRUCTURE-AND-FILES.md` for full template):

```bash
# Template. Copy to .env and fill in real values.
# NEVER commit .env to git.

DB_HOST=localhost
DB_PASSWORD=your_secure_password_here
API_KEY=your_api_key_here
SECRET_KEY=generate_a_random_secret_key_here
```

`.env` (gitignored, real values):

```bash
DB_HOST=localhost
DB_PASSWORD=MySecureP@ssw0rd123
API_KEY=sk_live_abc123def456
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

## .gitignore for Secrets

```gitignore
# Environment variables (secrets)
.env
.env.local
.env.*.local
.env.production
.env.staging

# Exception: keep the template
!.env.example

# Local config overrides
config/local/
config/*.local.yaml

# Secret files (any extension that suggests a secret)
secrets/
*.secret
*.key
*.pem
*.p12
api_key.txt
token.txt
```

The `!.env.example` line is critical — without it, the `.env*` glob would also block the template. Order matters in `.gitignore`; the negation must come after the broader rule.

## Best Practices

**Do** ✅:
- Use `.env` files for local secrets (gitignored).
- Provide `.env.example` as the canonical template (committed).
- Use environment variables for all secrets; never hardcode.
- Rotate secrets on a schedule (quarterly at minimum).
- Use strong random secrets (not `"secret123"`).
- Use a managed secret store in production — AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, GCP Secret Manager.
- Encrypt secrets at rest.
- Audit who can access which secrets.

**Don't** ❌:
- Never commit `.env` to git.
- Never hardcode secrets in config files or code.
- Never log secrets (see "Sanitization" below).
- Never expose secrets in error messages or stack traces.
- Never use the same secret across environments.
- Never share secrets via Slack, email, or other insecure channels — use a password manager or secret-sharing tool.

## Secret Rotation

When rotating a secret:

1. **Generate the new secret.**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update `.env`.**

   ```bash
   # Old (commented for handover, deleted after deploy)
   # API_KEY=old_key_abc123

   # New
   API_KEY=new_key_xyz789
   ```

3. **Rolling deployment.**
   - Deploy version that accepts both old and new (a `try new, fallback old` pattern).
   - Verify the new secret works in all environments.
   - Remove the old-secret fallback in the next deploy.
   - Revoke the old secret at the source (API provider, key store).

4. **Audit.**
   - Log the rotation event (without logging the secret itself).
   - Track secret age in a manifest or vault.
   - Alert when a secret exceeds its rotation interval.

## Sanitization for Logging

Logging the full config dict will leak secrets. Always sanitize before logging.

```python
def sanitize_config(config: dict) -> dict:
    """Return a copy of config with secrets masked. For logging only."""
    sanitized = config.copy()
    if 'database' in sanitized:
        sanitized['database'] = {**sanitized['database'], 'password': '***'}
    if 'api_client' in sanitized:
        sanitized['api_client'] = {
            **sanitized['api_client'],
            'api_key': '***',
            'api_secret': '***',
        }
    return sanitized


# Bad
logger.debug(f"Config: {config}")

# Good
logger.debug(f"Database host: {config['database']['host']}")

# Also good
logger.debug(f"Config: {sanitize_config(config)}")
```

For a more general approach, walk the config dict and mask any key whose name matches a sensitive pattern (`password`, `secret`, `key`, `token`, `credential`).

## Production Secret Stores

For production deployments, `.env` files become insufficient — they don't support rotation without redeployment, they don't audit access, and they aren't easy to share between many machines.

Switch to a managed store when **any** of these become true:

- You have more than one production host.
- You have a compliance requirement (SOC 2, HIPAA, PCI-DSS).
- Secrets change more often than quarterly.
- Multiple people need access on a least-privilege basis.

Recommended stores by environment:

| Environment | Tool |
|---|---|
| AWS | AWS Secrets Manager or AWS Systems Manager Parameter Store |
| GCP | Google Secret Manager |
| Azure | Azure Key Vault |
| Multi-cloud / on-prem | HashiCorp Vault |
| Kubernetes | External Secrets Operator with one of the above as the backend |

The `ConfigLoader` (see `LOADER.md`) doesn't need to change — it still reads environment variables. The deployment system fetches secrets from the store and injects them as env vars at process start.

## See Also

- `STRUCTURE-AND-FILES.md` — the `.env.example` template.
- `LOADER.md` — how `${VAR}` values get expanded from env into config.
- `VALIDATION.md` — schema validation that ensures required secrets are present at startup.
