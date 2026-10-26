"""deploy/README.md's App YAML must give the container a CA store.

debian:bookworm-slim ships none, and Python's urllib (the Slack post, the feed
fetch) reads the OS store: the first tick, 2026-10-26, recorded
CERTIFICATE_VERIFY_FAILED on the post and 0 articles while arXiv (requests,
certifi) fetched 84. SSL_CERT_FILE naming the venv's certifi bundle recovers
both; proved on the server with the host's store hidden.
"""

import re
from pathlib import Path

import yaml

README = Path(__file__).resolve().parents[1] / "deploy" / "README.md"


def _app_yaml() -> dict:
    match = re.search(r"```yaml\n(services:\n.*?)```", README.read_text(), re.DOTALL)
    assert match, "no services: YAML block in deploy/README.md"
    return yaml.safe_load(match.group(1))


def test_app_yaml_points_ssl_cert_file_at_the_venv_certifi_bundle():
    env = _app_yaml()["services"]["paperboy"]["environment"]
    cert = env.get("SSL_CERT_FILE", "")
    assert cert.startswith("<home>/paperboy/.venv/"), f"SSL_CERT_FILE={cert!r}: the slim image has no CA store"
    assert cert.endswith("certifi/cacert.pem"), cert
