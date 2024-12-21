from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from typing import Any


def validate_future_date(value: Any) -> None:
    """Validate that a date is in the future"""
    if value <= timezone.now():
        raise ValidationError(
            _("The date must be in the future.")
        )


def validate_positive_number(value: Any) -> None:
    """Validate that a number is positive"""
    if value <= 0:
        raise ValidationError(
            _("The value must be greater than zero.")
        )


def validate_discount_percent(value: Any) -> None:
    """Validate discount percentage"""
    if not 0 <= value <= 100:
        raise ValidationError(
            _("Discount percentage must be between 0 and 100.")
        )


def validate_promotion_code(value: str) -> None:
    """Validate promotion code format"""
    if len(value) == 5:
        raise ValidationError(
            _("Discount code must be 5 characters.")
        )
    if not value.isalnum():
        raise ValidationError(
            _("Discount code can only contain letters and numbers.")
        )
