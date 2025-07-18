import requests
from bs4 import BeautifulSoup
import csv
import time
from fake_useragent import UserAgent


def scrape_ebay_products(search_query, max_products=5):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}"

    try:
        time.sleep(2)  # Avoid rate limiting
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        items = soup.select('.s-item__wrapper')[:max_products]

        for item in items:
            try:
                name = item.select_one('.s-item__title').get_text(strip=True)
                price = item.select_one('.s-item__price').get_text(strip=True)
                rating_tag = item.select_one('.s-item__reviews-count')
                rating = rating_tag.get_text(strip=True).split()[
                    0] if rating_tag else "N/A"

                products.append({
                    'Name': name,
                    'Price': price,
                    'Rating': rating,
                    'Source': 'eBay'
                })
            except Exception as e:
                print(f"Error parsing eBay product: {e}")
                continue

        return products

    except Exception as e:
        print(f"eBay request failed: {e}")
        return None


def scrape_walmart_products(search_query, max_products=5):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    url = f"https://www.walmart.com/search?q={search_query.replace(' ', '+')}"

    try:
        time.sleep(2)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        items = soup.select('[data-item-id]')[:max_products]

        for item in items:
            try:
                name = item.select_one(
                    '[data-automation-id="product-title"]').get_text(strip=True)
                price = item.select_one(
                    '[data-automation-id="product-price"]').get_text(strip=True)
                rating_tag = item.select_one('.stars-container')
                rating = rating_tag['aria-label'].split()[0] if rating_tag else "N/A"

                products.append({
                    'Name': name,
                    'Price': price,
                    'Rating': rating,
                    'Source': 'Walmart'
                })
            except Exception as e:
                print(f"Error parsing Walmart product: {e}")
                continue

        return products

    except Exception as e:
        print(f"Walmart request failed: {e}")
        return None


def save_to_csv(data, filename):
    if not data:
        return
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(
            file, fieldnames=['Name', 'Price', 'Rating', 'Source'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    search_term = input("Enter product to search: ").strip()
    if not search_term:
        print("Error: Please enter a valid search term.")
    else:
        # Scrape both sites
        ebay_products = scrape_ebay_products(search_term)
        walmart_products = scrape_walmart_products(search_term)

        combined_products = []
        if ebay_products:
            combined_products.extend(ebay_products)
        if walmart_products:
            combined_products.extend(walmart_products)

        if combined_products:
            print(f"\nFound {len(combined_products)} products:")
            for idx, product in enumerate(combined_products, 1):
                print(
                    f"{idx}. [{product['Source']}] {product['Name']} | {product['Price']} | Rating: {product['Rating']}")

            csv_file = f"{search_term.replace(' ', '_')}_products.csv"
            save_to_csv(combined_products, csv_file)
        else:
            print("No products found from any source.")
