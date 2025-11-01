from datetime import datetime, timedelta, timezone

from domain.model import ActivationCode


def test_activation_new_code_generation():
    code = ActivationCode.generate_activation_code()
    assert len(code.value) == 4
    assert code.value.isdigit()
    assert not code.has_code_expired()


def test_activation_new_code_expiration():
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    expired_code = ActivationCode(value="1234", expires_at=past)
    assert expired_code.has_code_expired()
