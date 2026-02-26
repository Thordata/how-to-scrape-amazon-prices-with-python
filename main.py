"""
Simple Amazon price scraper tutorial.

This script:
- Opens an Amazon search / category page in a headless Chrome browser
- Extracts product title, URL, price and currency
- Saves the results into amazon_prices.csv in the current folder

Usage:
    python main.py --url "https://www.amazon.com/s?k=wireless+mouse"
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class Product:
    title: str
    url: str
    price: str
    currency: str
    page: int
    position: int


def _create_driver() -> webdriver.Chrome:
    """Create a headless Chrome WebDriver.

    Selenium 4+ includes Selenium Manager, which can automatically
    download and manage the appropriate ChromeDriver binary, so we
    do not need an extra driver manager dependency here.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Let Selenium Manager handle the driver binary automatically
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def _parse_price_block(product_element) -> tuple[str | None, str | None]:
    """Extract price and currency from one product container.

    We first try to parse from the dedicated price container (current price),
    and only if that fails fall back to a text-based regex.
    """
    try:
        price_container = product_element.find_element(
            By.XPATH, ".//span[contains(@class, 'a-price')]"
        )
    except NoSuchElementException:
        return None, None

    # Many Amazon layouts include a fully formatted price in an "a-offscreen" span.
    try:
        offscreen_text = price_container.find_element(
            By.CLASS_NAME, "a-offscreen"
        ).text.strip()
    except NoSuchElementException:
        offscreen_text = ""

    if offscreen_text:
        # Example: "$19.99" or "€19,99"
        currency_char = offscreen_text[0]
        numeric_part = offscreen_text[1:].strip().replace(",", "")
        return numeric_part, currency_char

    # Fallback to whole + fraction structure
    try:
        whole = price_container.find_element(
            By.CLASS_NAME, "a-price-whole"
        ).text.replace(",", "").strip()
        fraction = price_container.find_element(
            By.CLASS_NAME, "a-price-fraction"
        ).text.strip()
        price_value = f"{whole}.{fraction}"
    except NoSuchElementException:
        # If either part is missing, treat price as unavailable
        return None, None

    try:
        currency = price_container.find_element(
            By.CLASS_NAME, "a-price-symbol"
        ).text.strip()
    except NoSuchElementException:
        currency = ""

    if price_value and currency:
        return price_value, currency

    # Final fallback: look for a pattern like "$19.99" anywhere in the product text
    text = product_element.text
    match = re.search(r"([€$£])\s?(\d[\d,]*\.\d{2})", text)
    if match:
        currency_char, numeric = match.groups()
        numeric = numeric.replace(",", "")
        return numeric, currency_char

    return None, None


def _wait_for_product_elements(driver: webdriver.Chrome, timeout: int = 10) -> None:
    """Wait until at least one product result element is present on the page."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@data-component-type='s-search-result']")
            )
        )
    except TimeoutException:
        print(
            "[WARN] Timed out waiting for product elements. "
            "Continuing with whatever is currently loaded."
        )


def _scrape_products_on_current_page(
    driver: webdriver.Chrome,
    page_number: int,
) -> List[Product]:
    """Scrape all products with prices on the currently loaded page."""
    product_elements = driver.find_elements(
        By.XPATH, "//div[@data-component-type='s-search-result']"
    )
    print(f"[INFO] Found {len(product_elements)} product elements on the page")

    products: List[Product] = []
    skipped_due_to_errors = 0

    for index, element in enumerate(product_elements, start=1):
        # Title and URL can have slightly different structures on different locales.
        # We use CSS selectors that match the current Amazon layout and fall back
        # to simpler ones if needed.
        try:
            try:
                # Typical desktop search result: <a class="... s-link-style ..."><h2><span>Title</span></h2></a>
                title_element = element.find_element(By.CSS_SELECTOR, "h2 span")
            except NoSuchElementException:
                title_element = element.find_element(By.CSS_SELECTOR, "h2")

            try:
                link_element = element.find_element(
                    By.CSS_SELECTOR, "a.a-link-normal.s-link-style"
                )
            except NoSuchElementException:
                link_element = element.find_element(By.CSS_SELECTOR, "a.a-link-normal")

            title = title_element.text.strip()
            product_url = link_element.get_attribute("href")

            if not title or not product_url:
                continue

            # Price and currency
            price, currency = _parse_price_block(element)
            if not price:
                # Skip products without visible price (e.g. unavailable)
                continue

            products.append(
                Product(
                    title=title,
                    url=product_url,
                    price=price,
                    currency=currency,
                    page=page_number,
                    position=index,
                )
            )
        except Exception:
            skipped_due_to_errors += 1
            continue

    print(f"[INFO] Parsed {len(products)} products with prices on this page")
    if skipped_due_to_errors:
        print(
            f"[INFO] Skipped {skipped_due_to_errors} products due to unexpected structure."
        )
    return products


def _go_to_next_page(driver: webdriver.Chrome) -> bool:
    """Click the 'Next' pagination button if it exists and is enabled."""
    try:
        next_button = driver.find_element(
            By.XPATH,
            "//a[contains(@class, 's-pagination-next') and not(contains(@class, 's-pagination-disabled'))]",
        )
    except NoSuchElementException:
        print("[INFO] No next page button found; stopping pagination.")
        return False

    try:
        driver.execute_script("arguments[0].click();", next_button)
    except Exception:
        next_button.click()

    # Wait for the next page to load some results
    _wait_for_product_elements(driver)
    return True


def _apply_filters(
    products: List[Product],
    min_price: float | None,
    max_price: float | None,
    title_contains: str | None,
) -> List[Product]:
    """Filter products by numeric price range and optional title substring."""
    if min_price is None and max_price is None and not title_contains:
        return products

    filtered: List[Product] = []
    query = title_contains.lower() if title_contains else None

    for product in products:
        # Title filter
        if query and query not in product.title.lower():
            continue

        # Price range filter
        try:
            value = float(product.price)
        except ValueError:
            continue

        if min_price is not None and value < min_price:
            continue
        if max_price is not None and value > max_price:
            continue

        filtered.append(product)

    return filtered


def scrape_amazon_prices(
    url: str,
    max_pages: int = 1,
    max_products: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    title_contains: str | None = None,
) -> List[Product]:
    """Scrape one or more Amazon pages and return a list of products."""
    print("[INFO] Opening Amazon page...")
    driver = _create_driver()

    try:
        driver.get(url)
        # Wait for content to load
        _wait_for_product_elements(driver)

        # Optional: dump the first loaded page to an HTML file for debugging.
        # This can help you inspect the structure if selectors ever stop working.
        try:
            debug_path = Path("debug_last_page.html")
            debug_path.write_text(driver.page_source, encoding="utf-8")
            print(f"[INFO] Saved a copy of the first page HTML to {debug_path.name}")
        except Exception:
            print("[WARN] Failed to save debug HTML copy.", file=sys.stderr)

        all_products: List[Product] = []
        current_page = 1

        while True:
            page_products = _scrape_products_on_current_page(
                driver,
                page_number=current_page,
            )
            page_products = _apply_filters(
                page_products,
                min_price=min_price,
                max_price=max_price,
                title_contains=title_contains,
            )
            all_products.extend(page_products)

            if max_products is not None and len(all_products) >= max_products:
                all_products = all_products[:max_products]
                break

            if current_page >= max_pages:
                break

            print(f"[INFO] Moving to page {current_page + 1}...")
            if not _go_to_next_page(driver):
                break

            current_page += 1

        print(f"[INFO] Total products collected after pagination: {len(all_products)}")
        return all_products
    finally:
        driver.quit()


def save_products_to_csv(products: List[Product], output_path: Path) -> None:
    """Save product list to a CSV file."""
    if not products:
        print("[INFO] No products to save; CSV will not be created.")
        return

    fieldnames = ["title", "url", "price", "currency", "page", "position"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            writer.writerow(asdict(product))

    print(f"[INFO] Saved {len(products)} products to {output_path.name}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape product prices from an Amazon search or category page."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Full URL of the Amazon search or category page to scrape.",
    )
    parser.add_argument(
        "--output",
        default="amazon_prices.csv",
        help="Output CSV file name (default: amazon_prices.csv).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum number of result pages to scrape (default: 1).",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=None,
        help="Maximum number of products to collect in total (default: no limit).",
    )
    parser.add_argument(
        "--min-price",
        type=float,
        default=None,
        help="Minimum price filter (e.g. 10.0).",
    )
    parser.add_argument(
        "--max-price",
        type=float,
        default=None,
        help="Maximum price filter (e.g. 50.0).",
    )
    parser.add_argument(
        "--title-contains",
        type=str,
        default=None,
        help="Only keep products whose title contains this text (case-insensitive).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    products = scrape_amazon_prices(
        args.url,
        max_pages=args.max_pages,
        max_products=args.max_products,
        min_price=args.min_price,
        max_price=args.max_price,
        title_contains=args.title_contains,
    )
    output_path = Path(args.output).resolve()
    save_products_to_csv(products, output_path)


if __name__ == "__main__":
    main()

