"""Tests for Pydantic request/response schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.check import FreeCheckRequest


class TestFreeCheckRequest:
    def test_valid_registration(self):
        req = FreeCheckRequest(registration="AB12CDE")
        assert req.registration == "AB12CDE"

    def test_lowercase_uppercased(self):
        req = FreeCheckRequest(registration="ab12cde")
        assert req.registration == "AB12CDE"

    def test_spaces_stripped(self):
        req = FreeCheckRequest(registration="AB12 CDE")
        assert req.registration == "AB12CDE"

    def test_dashes_rejected_if_over_max_length(self):
        """Pydantic validates max_length before field_validator runs."""
        with pytest.raises(ValidationError):
            FreeCheckRequest(registration="AB-12-CDE")  # 9 chars with dashes

    def test_too_short_raises(self):
        with pytest.raises(ValidationError):
            FreeCheckRequest(registration="A")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            FreeCheckRequest(registration="ABCDEFGHIJ")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            FreeCheckRequest(registration="")

    def test_missing_raises(self):
        with pytest.raises(ValidationError):
            FreeCheckRequest()
