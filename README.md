## How to Scrape Amazon Prices with Python (Step-by-Step)

This repository is a **minimal, practical tutorial** that shows you how to:

- **Open an Amazon search / category page**
- **Collect product titles, URLs, prices and currencies**
- **Save everything into a CSV file (`amazon_prices.csv`)**

You can follow this guide line by line on a fresh machine and get a working result.

> **Educational use only**: Always respect Amazon's terms of service, robots rules, and local laws. Only scrape public pages you are allowed to access, and never overload any website.

---

## 1. What You Will Build

By the end of this tutorial you will have:

- A simple script `main.py` that:
  - Opens an Amazon search / category page in a headless browser
  - Finds products on the page
  - Extracts: **title, product URL, price, currency**
  - Saves the results into `amazon_prices.csv` in the project folder

You will run it like this:

```bash
python main.py --url "https://www.amazon.com/s?k=wireless+mouse"
```

---

## 2. Prerequisites

- **Operating system**: Windows, macOS or Linux
- **Python**: 3.10 or newer (3.11 recommended)
- **Google Chrome** browser installed

You do **not** need to know Selenium in advance — we will go through it step by step.

---

## 3. Project Structure

After you finish this tutorial, your folder will look like this:

```text
how-to-scrape-amazon-prices-with-python/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
└── amazon_prices.csv      # created after you run the script
```

Everything is concentrated into **one Python file** to keep it easy to read and modify.

---

## 4. Step 1 – Download or Clone This Repository

You can **either** clone via Git:

```bash
git clone https://github.com/Thordata/how-to-scrape-amazon-prices-with-python.git
cd how-to-scrape-amazon-prices-with-python
```

Or **download as ZIP** from your Git hosting platform, unzip it, and open the folder in your editor (VS Code / Cursor / PyCharm, etc.).

All commands below are assumed to be run **inside this project folder**.

---

## 5. Step 2 – Create and Activate a Virtual Environment

### 5.1 Create virtual environment

```bash
python -m venv .venv
```

This creates a `.venv` folder with an isolated Python environment.

### 5.2 Activate the environment

- **Windows (PowerShell)**:

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- **Windows (Git Bash)**:

  ```bash
  source .venv/Scripts/activate
  ```

- **macOS / Linux (bash / zsh)**:

  ```bash
  source .venv/bin/activate
  ```

After activation, your terminal prompt should show something like:

```text
(.venv) C:\path\to\how-to-scrape-amazon-prices-with-python>
```

---

## 6. Step 3 – Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:

- `selenium` – browser automation (Selenium Manager will automatically download the correct ChromeDriver)

---

## 7. Step 4 – Pick an Amazon Page to Scrape

1. Open your browser and go to Amazon for your region, for example:
   - `https://www.amazon.com` (US)
   - `https://www.amazon.de` (Germany)
   - `https://www.amazon.co.uk` (UK)
2. Use the search box or choose a department. Example:
   - Search for **"wireless mouse"**
   - Or open a department like **Electronics → Headphones**
3. Wait for the page to load, then **copy the full URL** from the address bar.

Example URL:

```text
https://www.amazon.com/s?k=wireless+mouse
```

We will pass this URL to the script in the next step.

---

## 8. Step 5 – Run the Scraper

Run the Python script and pass your Amazon URL via the `--url` argument:

```bash
python main.py --url "https://www.amazon.com/s?k=wireless+mouse"
```

What happens:

- The script starts a **headless Chrome** window
- It loads the page you provided
- It finds each product block on the page
- For each product, it tries to extract:
  - Title
  - Product URL
  - Price (e.g. `19.99`)
  - Currency symbol (e.g. `$`)
- Finally, it writes everything into `amazon_prices.csv`

You should see log output similar to:

```text
[INFO] Opening Amazon page...
[INFO] Found 48 product elements on the page
[INFO] Parsed 32 products with prices
[INFO] Saved 32 products to amazon_prices.csv
```

If a product is missing a price (for example, currently unavailable), the script will simply skip it and continue.

---

## 9. Step 6 – Inspect the CSV File

In the project folder, you should now see:

- `amazon_prices.csv`

Open it with:

- Excel
- LibreOffice Calc
- Numbers (macOS)
- Or any editor that can read CSV files

You should see columns similar to:

- `title`
- `url`
- `price`
- `currency`
- `page` – which result page the product came from (1 = first page)
- `position` – position of the product on that page (1 = first result)

Each row represents one product found on the Amazon page.

---

## 10. How the Code Works (High-Level Overview)

You can open `main.py` and follow along. The flow is:

- Define a small `Product` data class to hold one product's data
- Initialize a headless Chrome browser using Selenium (Selenium Manager will download ChromeDriver automatically)
- Visit the Amazon page URL
- Find product containers using an XPath that targets search results
- For each container:
  - Extract the **title** from the product heading
  - Extract the **product URL** from the link
- Extract the **price** and **currency symbol**
- Collect all valid products into a list (optionally filtered by price range / title text)
- Save the list as `amazon_prices.csv` using Python's built-in `csv` module

The code is intentionally compact and focused on **a small number of pages** (controlled by `--max-pages` and `--max-products`) to make it easy to understand and extend.

---

## 11. Common Issues & Troubleshooting

**1. ChromeDriver / browser errors**

- Make sure **Google Chrome** is installed.
- If the script fails to start the browser, make sure your Python version is 3.10 or newer (as specified in this README) and try reinstalling the dependencies with `pip install -r requirements.txt`.

**2. Empty `amazon_prices.csv`**

- Check that the URL you passed is a **search / category** page with visible products and prices (try opening it in your normal browser first).
- The script saves the first loaded page HTML into `debug_last_page.html` in the project folder. If the CSV is empty:
  - Open `debug_last_page.html` in your browser.
  - Use the browser's "Find" (`Ctrl+F` / `Cmd+F`) to look for `$` and confirm that prices such as `$12.99` actually appear in the HTML.
  - If you cannot find any prices, Amazon may be hiding them for your region or requiring you to sign in.
- Some country-specific versions of Amazon use slightly different layouts; selectors in `main.py` can be adjusted if needed.
- Occasionally Amazon may respond with a CAPTCHA or an "unusual traffic" page; in that case, reduce request frequency and avoid running the script too often and avoid running many different keywords in a short time.

**3. Encoding issues when opening CSV**

- When opening in Excel, make sure you import as **UTF-8** if product titles show strange characters.

---

## 12. Next Steps – Ideas to Extend This Tutorial

Once you understand the core flow, here are some ideas:

- Paginate:
  - Click the "Next" button and collect products from multiple pages
- Filter:
  - Only keep products cheaper than a certain price
- Enrich:
  - Add rating, number of reviews, prime badge, etc.
- Export:
  - Save to a database or a dashboard instead of a CSV file

This tutorial aims to give you a **solid starting point**; from here you can adapt it to your own product tracking or market research needs.

---

## 13. (Optional) Advanced CLI Options

The basic example only uses `--url`. For more control, you can use additional options:

- **Paginate across multiple pages**:

  ```bash
  python main.py --url "https://www.amazon.com/s?k=wireless+mouse" --max-pages 3
  ```

  This will:

  - Scrape the first page
  - Click the "Next" button (if available)
  - Scrape up to 3 pages (or stop earlier if there is no next page)

- **Filter by price range**:

  ```bash
  # Only keep products between $10 and $50
  python main.py --url "https://www.amazon.com/s?k=wireless+mouse" --min-price 10 --max-price 50
  ```

- **Filter by words in the title**:

  ```bash
  # Only keep products whose title contains the word "ergonomic"
  python main.py --url "https://www.amazon.com/s?k=wireless+mouse" --title-contains "ergonomic"
  ```

- **Combine them**:

  ```bash
  python main.py \
    --url "https://www.amazon.com/s?k=wireless+mouse" \
    --max-pages 2 \
    --min-price 15 \
    --max-price 60 \
    --title-contains "silent" \
    --max-products 100
  ```

These options let you stay in the "single-file script" world while still gaining some of the power you would normally need a larger project for.

---

## 14. (Optional) Run the Automated Tests

If you are curious about how this repository is tested:

- There is a small **static HTML page** in `tests/sample_page.html` that mimics an Amazon search result.
- The test `tests/test_static_page.py` opens this file in a headless browser and checks that:
  - Two products with prices are parsed correctly
  - A product without price is skipped

To run the tests (with the virtual environment activated):

```bash
pytest
```

This is mainly useful if you change the selectors in `main.py` and want to verify you did not break the parsing logic.

---

## 15. From Tutorial Script to Production-Grade Crawling

The script in this repository is intentionally simple:

- It focuses on **one page at a time**
- It assumes a relatively stable HTML structure
- It does not include large-scale scheduling, rotating IPs, or monitoring

For internal tools, weekend projects, or learning, this is often enough.

However, if you need to:

- Monitor **thousands of products** across multiple Amazon locales
- Run crawlers on a **schedule** (e.g. hourly/daily) without babysitting scripts
- Store historical data and visualize **price changes over time** in dashboards
- Add alerting (for example, when a competitor drops a price below your threshold)

then you will quickly outgrow a single local script.

---

## 16. Thordata – Professional Crawlers + Dashboard (Free Trial)

Thordata provides:

- Managed crawlers for Amazon and other major marketplaces
- Built-in handling for:
  - IP rotation and bans
  - Basic anti-bot defenses
  - Scaling up and down without changing your code
- A Dashboard where you can:
  - Browse collected product data
  - Track price and availability over time
  - Export to your own tools (BI, spreadsheets, APIs)

If this tutorial was useful and you want to **skip the infrastructure work**, you can:

- Start with this script to prototype your data needs
- Then request a **free trial** of Thordata's crawler + dashboard to see how a managed setup feels

To learn more or request access, visit [Thordata on GitHub](https://github.com/Thordata) or contact the Thordata team through your usual channel.

The goal is simple: let you focus on **questions and decisions**, not on keeping scrapers alive.

---

### Final word

- Check the Thordata Dashboard for managed crawlers, data views, and exports: [dashboard.thordata.com](https://dashboard.thordata.com/).
- For more information about Thordata, product updates, and examples, start from the GitHub organization page: [github.com/Thordata](https://github.com/Thordata).
- If you have questions or want to discuss a larger-scale use case, reach out to the Thordata team through your usual contact channel.

---

**⭐ If this tutorial helped you, please consider giving this repository a star!**

