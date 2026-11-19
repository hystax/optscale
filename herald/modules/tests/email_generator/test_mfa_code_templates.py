from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from herald.modules.email_generator.generator import does_template_exist, generate_email

CODE = "048213"
# template -> text that tells the purpose of the code, text of the other purpose
TEMPLATES = {
    "mfa_enrollment_code": (
        ["confirm your e-mail address as an authentication method", "If you did not start this setup"],
        ["signing in", "Someone may know your password"],
    ),
    "mfa_login_code": (
        ["finish signing in", "If you did not try to sign in", "Someone may know your password"],
        ["authentication method", "start this setup"],
    ),
}


def _render(config_client: MagicMock, template_type: str) -> str:
    message = generate_email(
        config_client,
        "user@example.com",
        "FinOps for Cloud: code",
        {"texts": {"code": CODE}},
        template_type=template_type,
    )
    body = message.get_payload()[0]
    return body.get_payload(decode=True).decode(body.get_content_charset())


@pytest.mark.parametrize("template_type", TEMPLATES)
def test_mfa_code_template_exists(template_type: str):
    assert does_template_exist(f"{template_type}.html") is True


def test_single_purpose_template_removed():
    # replaced by the enrollment and login templates, which say what the code is for
    assert does_template_exist("mfa_code.html") is False


@pytest.mark.parametrize(("template_type", "expected", "unexpected"), [(k, *v) for k, v in TEMPLATES.items()])
def test_mfa_code_template_renders(
    config_client_factory: Callable[[dict[str, Any]], MagicMock],
    template_type: str,
    expected: list[str],
    unexpected: list[str],
):
    client = config_client_factory(
        {
            "/public_ip": "1.2.3.4",
            "/company_name": "SoftwareOne",
            "/product_name": "FinOps for Cloud",
        },
    )
    html = _render(client, template_type)

    # the code is a string, leading zeros must be kept
    assert f">{CODE}</span>" in html
    assert "expires in 10 minutes" in html
    for text in expected:
        assert text in html
    for text in unexpected:
        assert text not in html
    # unlike password recovery, nothing in the content is clickable
    assert "password-recovery" not in html
    assert "links.restore_button" not in html
    assert "Recover password" not in html
    # every placeholder was rendered
    assert "{{" not in html
    assert "{%" not in html
