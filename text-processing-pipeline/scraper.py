import re, time, random
import pandas as pd
from playwright.sync_api import sync_playwright


def scrape_flipkart_reviews(product_url, max_reviews=1500):
    """
    Scrape Flipkart reviews using Playwright (non-headless browser)
    Flipkart uses React Native Web with generated class names that change often
    This scraper finds review containers by their TEXT STRUCTURE instead of CSS classes
    """
    # Ensure URL points to product-reviews page
    if '/p/' in product_url and '/product-reviews/' not in product_url:
        product_url = product_url.replace('/p/', '/product-reviews/')

    reviews = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        empty_pages = 0
        pg = 1

        while len(reviews) < max_reviews:
            sep = '&' if '?' in product_url else '?'
            page_url = f"{product_url}{sep}page={pg}"

            try:
                page.goto(page_url, timeout=60000)
                page.wait_for_load_state("networkidle")
                time.sleep(3)
            except Exception as e:
                print(f"[!] Page {pg} error: {e}")
                empty_pages += 1
                if empty_pages >= 3:
                    break
                pg += 1
                continue

            # Extract reviews from rendered DOM using structural text parsing
            page_reviews = page.evaluate("""() => {
                const results = [];
                const allDivs = document.querySelectorAll('div');
                
                for (const div of allDivs) {
                    const text = div.innerText.trim();
                    // Look for rating pattern: "X.0" where X is 1-5
                    if (!/^[1-5]\.0$/.test(text)) continue;
                    
                    // Walk up the DOM to find the review container
                    let container = div;
                    for (let i = 0; i < 10; i++) {
                        if (!container.parentElement) break;
                        container = container.parentElement;
                        const ct = container.innerText;
                        if (ct.includes('Verified Purchase') || ct.includes('Certified Buyer')) {
                            const lines = ct.split('\\n').map(l => l.trim()).filter(l => l);
                            results.push({
                                rating: parseInt(text.charAt(0)),
                                lines: lines
                            });
                            break;
                        }
                    }
                }
                
                // Deduplicate by joining first few lines
                const seen = new Set();
                return results.filter(r => {
                    const key = r.lines.slice(0, 5).join('|');
                    if (seen.has(key)) return false;
                    seen.add(key);
                    return true;
                });
            }""")

            found = 0
            for rv in page_reviews:
                lines = rv["lines"]
                rating = rv["rating"]

                # Parse structured lines:
                # [0] "5.0", [1] "•", [2] title, [3] "Review for:...", [4] body, ...
                title = ""
                body = ""
                for i, line in enumerate(lines):
                    if line == "•" and i + 1 < len(lines):
                        title = lines[i + 1]
                    if line.startswith("Review for:") and i + 1 < len(lines):
                        # Body is the next line (before reviewer name line)
                        body = lines[i + 1]
                        break

                text = f"{title} {body}".strip()
                if len(text) < 5 or text in seen:
                    continue
                seen.add(text)
                reviews.append({"review_text": text, "rating": rating})
                found += 1

            if found == 0:
                empty_pages += 1
                if empty_pages >= 3:
                    print(f"[!] No reviews on {empty_pages} consecutive pages. Stopping.")
                    break
            else:
                empty_pages = 0
                print(f"  Page {pg}: +{found} (Total: {len(reviews)})")

            if len(reviews) >= max_reviews:
                break

            pg += 1
            time.sleep(random.uniform(1, 2))

        browser.close()

    print(f"\n[OK] Scraped {len(reviews)} reviews from Flipkart")
    return pd.DataFrame(reviews[:max_reviews])


# ─── CLI interface (used by notebook via subprocess) ────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <flipkart_url> [max_reviews] [output_csv]")
        sys.exit(1)

    url = sys.argv[1]
    max_rev = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
    out_csv = sys.argv[3] if len(sys.argv) > 3 else "flipkart_reviews.csv"

    df = scrape_flipkart_reviews(url, max_reviews=max_rev)
    if not df.empty:
        df.to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"[OK] Saved to {out_csv}")
    else:
        print("[!] No reviews scraped")