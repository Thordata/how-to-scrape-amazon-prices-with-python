import csv
import subprocess
import sys
from pathlib import Path

from main import Product, scrape_amazon_prices


def _sample_file_url() -> str:
    sample_file = Path(__file__).parent / "sample_page.html"
    return sample_file.resolve().as_uri()


def test_price_range_filter() -> None:
    """min_price / max_price should correctly filter products."""
    url = _sample_file_url()

    # Only keep products priced >= 20
    products = scrape_amazon_prices(url, min_price=20.0)

    assert len(products) == 1
    item = products[0]
    assert isinstance(item, Product)
    assert item.title == "Sample Product 2"
    assert float(item.price) >= 20.0


def test_title_contains_filter() -> None:
    """title_contains should match case-insensitively."""
    url = _sample_file_url()

    products = scrape_amazon_prices(url, title_contains="product 1")

    assert len(products) == 1
    item = products[0]
    assert "sample product 1".lower() in item.title.lower()


def test_max_products_limit(tmp_path: Path) -> None:
    """CLI: --max-products should limit number of saved rows."""
    url = _sample_file_url()
    output_csv = tmp_path / "out.csv"

    completed = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--url",
            url,
            "--output",
            str(output_csv),
            "--max-pages",
            "1",
            "--max-products",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert output_csv.exists()

    with output_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # One data row plus header means len(rows) == 1
    assert len(rows) == 1
    row = rows[0]
    # Basic sanity checks on CSV columns
    assert row["title"]
    assert row["url"]
    assert row["price"]
    assert row["currency"] == "$"
    assert row["page"] == "1"
    assert row["position"] == "1"

