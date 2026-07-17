import os
import pytest
from pdf_gen import generate_nota

def test_generate_nota():
    items = [
        {"name": "Nasi Uduk", "qty": 3, "subtotal": 30000},
        {"name": "Kopi Susu", "qty": 2, "subtotal": 10000}
    ]

    file_path = generate_nota(
        warung_name="Warung Makmur",
        items=items,
        total=40000,
        transaction_id="tx-123456789"
    )

    assert os.path.exists(file_path)
    assert os.path.isfile(file_path)
    assert os.path.getsize(file_path) > 0

    # Clean up
    os.remove(file_path)
