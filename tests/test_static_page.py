from pathlib import Path

from main import Product, scrape_amazon_prices


def test_scrape_sample_static_page() -> None:
    """Scrape the bundled static HTML page and verify parsed products."""
    sample_file = Path(__file__).parent / "sample_page.html"
    file_url = sample_file.resolve().as_uri()

    products = scrape_amazon_prices(file_url)

    # We expect exactly two products with prices (third has no price and is skipped)
    assert len(products) == 2

    first, second = products

    assert isinstance(first, Product)
    assert first.title == "Sample Product 1"
    assert first.url == "https://www.example.com/product-1"
    assert first.price == "19.99"
    assert first.currency == "$"
    assert first.page == 1
    assert first.position == 1

    assert isinstance(second, Product)
    assert second.title == "Sample Product 2"
    assert second.url == "https://www.example.com/product-2"
    assert second.price == "42.50"
    assert second.currency == "$"
    assert second.page == 1
    assert second.position == 2

