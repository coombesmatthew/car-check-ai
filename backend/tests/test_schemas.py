"""Tests for Pydantic request/response schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.check import FreeCheckRequest, BasicCheckRequest


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


class TestBasicCheckRequest:
    def test_valid_basic_request(self):
        req = BasicCheckRequest(
            registration="AB12CDE",
            email="test@example.com",
            listing_url="https://autotrader.co.uk/listing/123",
            listing_price=899900,
        )
        assert req.registration == "AB12CDE"
        assert req.email == "test@example.com"
        assert req.listing_price == 899900

    def test_email_required(self):
        with pytest.raises(ValidationError):
            BasicCheckRequest(registration="AB12CDE")

    def test_optional_fields(self):
        req = BasicCheckRequest(
            registration="AB12CDE",
            email="test@example.com",
        )
        assert req.listing_url is None
        assert req.listing_price is None

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            BasicCheckRequest(
                registration="AB12CDE",
                email="test@example.com",
                listing_price=-100,
            )
