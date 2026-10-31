"""Input validation and entity extraction."""
from datetime import date

from app.services.validators import (
    extract_entities, valid_date, valid_email, valid_name, valid_number, valid_phone,
)


def test_phone():
    assert valid_phone("012 345 678") == "012345678"
    assert valid_phone("+855 12 345 678") == "012345678"
    assert valid_phone("០១២៣៤៥៦៧៨") == "012345678"  # Khmer digits
    assert valid_phone("12345") is None
    assert valid_phone("hello") is None


def test_email():
    assert valid_email("Dara@Example.com") == "dara@example.com"
    assert valid_email("dara@") is None
    assert valid_email("no spaces@x.com") is None


def test_date():
    assert valid_date("2026-11-02") == date(2026, 11, 2)
    assert valid_date("02/11/2026") == date(2026, 11, 2)
    assert valid_date("31/02/2026") is None  # no 31 February
    assert valid_date("tomorrow") is None


def test_number_and_name():
    assert valid_number("1,200.5") == 1200.5
    assert valid_number("abc") is None
    assert valid_name("Sok Dara") == "Sok Dara"
    assert valid_name("សុខ ដារា") == "សុខ ដារា"
    assert valid_name("R2D2") is None


def test_extract_entities():
    found = extract_entities("Book 3 seats on 2026-11-02, call 012 345 678 or dara@example.com")
    assert found == {"email": "dara@example.com", "phone": "012345678", "date": "2026-11-02", "number": "3"}
    assert extract_entities("no entities here") == {}
    assert extract_entities("on 02/11/2026", ["date"]) == {"date": "2026-11-02"}
