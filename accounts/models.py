from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from babasika.base_models import TimeStampedModel, UUIDPrimaryKeyModel

from .managers import UserManager

phone_validator = RegexValidator(
    regex=r"^\+[1-9]\d{7,14}$",
    message="Phone number must be in E.164 format, e.g. +2348012345678",
)

PIN_MAX_ATTEMPTS = 3
PIN_LOCKOUT_MINUTES = 30


class OccupationType(models.TextChoices):
    TRADER = "trader", "Trader"
    ARTISAN = "artisan", "Artisan"
    POS_AGENT = "pos_agent", "POS Agent"
    TAILOR = "tailor", "Tailor"
    MECHANIC = "mechanic", "Mechanic"
    MARKET_WOMAN = "market_woman", "Market Woman"
    OTHER = "other", "Other"


class OnboardingState(models.TextChoices):
    STARTED = "started", "Started"
    OCCUPATION_SELECTED = "occupation_selected", "Occupation selected"
    BANK_LINKED = "bank_linked", "Bank linked"
    CONSENT_GIVEN = "consent_given", "Consent given"
    PIN_SET = "pin_set", "PIN set"
    COMPLETED = "completed", "Completed"


class User(AbstractBaseUser, PermissionsMixin, UUIDPrimaryKeyModel, TimeStampedModel):
    """
    Phone-first user. End users never have a usable login password (see
    UserManager) - WhatsApp phone number ownership is the identity, and a
    separate transaction PIN (hashed, independent of `password`) gates any
    money movement. Staff/admin accounts are created via createsuperuser and
    do use `password` normally, through the regular Django admin login.
    """

    phone_number = models.CharField(
        max_length=20, unique=True, validators=[phone_validator], db_index=True
    )
    full_name = models.CharField(max_length=150, blank=True)
    occupation_type = models.CharField(
        max_length=20, choices=OccupationType.choices, blank=True
    )
    onboarding_state = models.CharField(
        max_length=25, choices=OnboardingState.choices, default=OnboardingState.STARTED
    )

    # Transaction PIN - independent of the (normally unusable) login password.
    transaction_pin_hash = models.CharField(max_length=128, blank=True)
    pin_attempt_count = models.PositiveSmallIntegerField(default=0)
    pin_locked_until = models.DateTimeField(null=True, blank=True)

    # Stub only for now - no translation logic wired up (out of scope).
    preferred_language = models.CharField(max_length=10, default="en")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone_number

    # -- transaction PIN helpers -------------------------------------------------
    def set_transaction_pin(self, raw_pin: str) -> None:
        self.transaction_pin_hash = make_password(raw_pin)
        self.pin_attempt_count = 0
        self.pin_locked_until = None

    def has_transaction_pin(self) -> bool:
        return bool(self.transaction_pin_hash)

    def is_pin_locked(self) -> bool:
        return bool(self.pin_locked_until and self.pin_locked_until > timezone.now())

    def check_transaction_pin(self, raw_pin: str) -> bool:
        """
        Verifies the PIN and updates the attempt/lockout counters. Returns
        False both when the PIN is wrong AND when the account is currently
        locked out - callers should check is_pin_locked() first to give the
        right message.
        """
        if self.is_pin_locked():
            return False
        valid = bool(self.transaction_pin_hash) and check_password(
            raw_pin, self.transaction_pin_hash
        )
        if valid:
            self.pin_attempt_count = 0
            self.pin_locked_until = None
        else:
            self.pin_attempt_count += 1
            if self.pin_attempt_count >= PIN_MAX_ATTEMPTS:
                self.pin_locked_until = timezone.now() + timezone.timedelta(
                    minutes=PIN_LOCKOUT_MINUTES
                )
        self.save(update_fields=["pin_attempt_count", "pin_locked_until"])
        return valid


class ConsentType(models.TextChoices):
    DATA_PROCESSING = "data_processing", "Data processing"
    TERMS_OF_SERVICE = "terms_of_service", "Terms of service"
    PIN_SETUP = "pin_setup", "PIN setup"


class ConsentRecord(UUIDPrimaryKeyModel, TimeStampedModel):
    """Explicit, timestamped consent capture - never inferred."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents")
    consent_type = models.CharField(max_length=25, choices=ConsentType.choices)
    consent_text_version = models.CharField(max_length=20)
    accepted_at = models.DateTimeField()
    channel = models.CharField(max_length=20, default="whatsapp")
    source_message_sid = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-accepted_at"]

    def __str__(self):
        return f"{self.user} - {self.consent_type} @ {self.accepted_at}"
