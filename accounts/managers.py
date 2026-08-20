from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager for the phone-first custom User model.

    End users never set a Django login password - they authenticate inside
    WhatsApp (their phone number identifies them) and confirm transfers with
    a separate transaction PIN (see User.set_transaction_pin). Only staff
    accounts created via create_superuser use the normal password field, for
    Django admin access.
    """

    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("A phone_number is required")
        phone_number = self.normalize_phone(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not password:
            raise ValueError("Superusers must have a usable password")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(phone_number, password, **extra_fields)

    @staticmethod
    def normalize_phone(phone_number):
        """
        Minimal E.164-ish normalization: strip whitespace, collapse a
        leading '00' to '+'. Real validation happens in the serializer via
        a regex/phonenumbers-style check - this just keeps lookups
        consistent (WhatsApp numbers arrive from Twilio as 'whatsapp:+234...').
        """
        phone_number = phone_number.strip().replace(" ", "")
        if phone_number.startswith("whatsapp:"):
            phone_number = phone_number[len("whatsapp:"):]
        if phone_number.startswith("00"):
            phone_number = "+" + phone_number[2:]
        return phone_number
