WEAK_PINS = {"0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999", "1234", "0123"}


def validate_transaction_pin(raw_pin: str) -> str | None:
    """Returns an error message string if invalid, otherwise None."""
    raw_pin = (raw_pin or "").strip()
    if not raw_pin.isdigit() or len(raw_pin) != 4:
        return "Your PIN must be exactly 4 digits."
    if raw_pin in WEAK_PINS:
        return "That PIN is too easy to guess. Please choose a different 4-digit PIN."
    return None
