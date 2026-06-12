import random
import re
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

class ECommerceScraper:
    """
    Main scraper class attempting live web queries with high fidelity mock data fallback.
    """
    def __init__(self):
        pass

    def search_all_platforms(self, query):
        """
        Searches Amazon and Flipkart via real-time scraping.
        If blocked or returns no results, falls back to simulated data.
        """
        results = []
        
        # 1. Attempt real scraping
        print(f"[*] Attempting real scrape for: {query}")
        amazon_deals = self._scrape_amazon(query)
        flipkart_deals = self._scrape_flipkart(query)
        
        results.extend(amazon_deals)
        results.extend(flipkart_deals)
        
        # 2. Fallback to simulation if both failed or returned very few results
        if len(results) < 2:
            print("[*] Real scrape failed or blocked. Falling back to simulation...")
            simulated_results = self._generate_simulated_data(query)
            results.extend(simulated_results)
        
        return results

    def _scrape_amazon(self, query):
        deals = []
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        try:
            res = requests.get(url, headers=get_headers(), timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('div[data-component-type="s-search-result"]')
            for item in items[:5]:
                title_elem = item.select_one('h2 a span')
                price_elem = item.select_one('.a-price-whole')
                img_elem = item.select_one('img.s-image')
                link_elem = item.select_one('h2 a') or item.find('a', href=True)
                
                if title_elem and price_elem and img_elem:
                    title = title_elem.text.strip()
                    price_str = price_elem.text.replace(',', '').strip()
                    try:
                        price = float(price_str)
                        href = link_elem['href'] if link_elem else ""
                        product_url = "https://www.amazon.in" + href if href.startswith('/') else (href if href else url)
                        deals.append({
                            "title": title,
                            "price": price,
                            "original_price": price * 1.1,
                            "discount": 10.0,
                            "rating": 4.2,
                            "reviews_count": random.randint(100, 2000),
                            "delivery_fee": 0.0,
                            "delivery_time": "In 2 Days",
                            "platform": "Amazon",
                            "url": product_url,
                            "image_url": img_elem.get('src', '')
                        })
                    except ValueError:
                        pass
        except Exception as e:
            print("Amazon scrape error:", e)
        return deals

    def _scrape_flipkart(self, query):
        deals = []
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        try:
            res = requests.get(url, headers=get_headers(), timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Flipkart layout classes change frequently. We look for common patterns.
            items = soup.find_all('div', {'class': '_1AtVbE'})
            if not items:
                items = soup.find_all('div', {'class': 'cPHDOP'})
            if not items:
                items = soup.find_all('div', {'class': 'slAVV4'})
            if not items:
                # Fallback to general listing container
                items = soup.find_all('div', {'data-id': True})
            
            for item in items:
                title_elem = item.find('div', {'class': '_4rR01T'}) or item.find('a', {'class': 'IRpwTa'}) or item.find('a', {'class': 's1Q9rs'}) or item.find('div', {'class': 'KzDlHZ'})
                price_elem = item.find('div', {'class': '_30jeq3'}) or item.find('div', {'class': 'Nx9bqj'})
                img_elem = item.find('img', {'class': '_396cs4'}) or item.find('img', {'class': '_2r_T1I'}) or item.find('img', {'class': 'DByuf4'}) or item.find('img')
                link_elem = item.find('a', {'class': '_1fQZEK'}) or item.find('a', {'class': 'CGtC98'}) or item.find('a', href=True)
                
                if title_elem and price_elem and img_elem:
                    title = title_elem.text.strip()
                    price_str = price_elem.text.replace('₹', '').replace(',', '').strip()
                    try:
                        price = float(price_str)
                        href = link_elem['href'] if link_elem else ""
                        product_url = "https://www.flipkart.com" + href if href.startswith('/') else (href if href else url)
                        deals.append({
                            "title": title,
                            "price": price,
                            "original_price": price * 1.1,
                            "discount": 10.0,
                            "rating": 4.1,
                            "reviews_count": random.randint(50, 1500),
                            "delivery_fee": random.choice([0.0, 40.0]),
                            "delivery_time": "In 3 Days",
                            "platform": "Flipkart",
                            "url": product_url,
                            "image_url": img_elem.get('src', '')
                        })
                        if len(deals) >= 5:
                            break
                    except ValueError:
                        pass
        except Exception as e:
            print("Flipkart scrape error:", e)
        return deals

    def _generate_simulated_data(self, query):
        """
        Generates highly realistic and clustered product deals for Amazon, Flipkart, Myntra, Ajio, and Meesho.
        """
        query_lower = query.lower()
        deals = []
        
        # Categorize query
        is_electronics = any(x in query_lower for x in ["phone", "iphone", "samsung", "oneplus", "pixel", "laptop", "macbook", "ipad", "tablet", "tv", "earbuds", "headphones", "watch", "smartwatch", "charger"])
        is_fashion = any(x in query_lower for x in ["tshirt", "shirt", "jeans", "dress", "kurta", "jacket", "hoodie", "top", "saree", "clothing", "wear", "suit"])
        is_footwear = any(x in query_lower for x in ["shoes", "sneakers", "boots", "sandals", "slippers", "crocs", "footwear"])
        
        # Base templates for realistic products
        if is_electronics:
            category = "Electronics"
            # Define 3 distinct matching models matching the query
            if "iphone" in query_lower:
                base_models = [
                    {"name": "Apple iPhone 15 (128 GB)", "base_price": 69900, "specs": ["Blue", "Black", "Green"], "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Apple iPhone 15 Plus (128 GB)", "base_price": 79900, "specs": ["Black", "Blue", "Yellow"], "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Apple iPhone 15 Pro (256 GB)", "base_price": 129900, "specs": ["Natural Titanium", "Blue Titanium", "Black Titanium"], "img": "https://images.unsplash.com/photo-1695048065216-34b16f64db5e?w=500&auto=format&fit=crop&q=60"}
                ]
            elif "samsung" in query_lower or "galaxy" in query_lower:
                base_models = [
                    {"name": "Samsung Galaxy S24 Ultra (5G, 256GB)", "base_price": 129999, "specs": ["Titanium Gray", "Titanium Yellow", "Titanium Black"], "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Samsung Galaxy S24 (5G, 256GB)", "base_price": 79999, "specs": ["Onyx Black", "Amber Yellow"], "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Samsung Galaxy A55 (5G, 128GB)", "base_price": 39999, "specs": ["Awesome Iceblue", "Awesome Navy"], "img": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop&q=60"}
                ]
            elif "laptop" in query_lower or "macbook" in query_lower or "asus" in query_lower or "hp" in query_lower or "dell" in query_lower:
                base_models = [
                    {"name": "Apple MacBook Air M3 (8GB/256GB SSD)", "base_price": 114900, "specs": ["Space Grey", "Silver", "Midnight"], "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=60"},
                    {"name": "ASUS Vivobook 15 (Intel i5 12th Gen, 16GB/512GB SSD)", "base_price": 49990, "specs": ["Quiet Blue", "Icelight Silver"], "img": "https://images.unsplash.com/photo-1496181130204-7552cc145cdb?w=500&auto=format&fit=crop&q=60"},
                    {"name": "HP Pavilion 14 (Intel i7 13th Gen, 16GB/1TB SSD)", "base_price": 78990, "specs": ["Natural Silver", "Warm Gold"], "img": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&auto=format&fit=crop&q=60"}
                ]
            else:
                # General electronics template
                clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).title()
                base_models = [
                    {"name": f"{clean_query} Premium Edition", "base_price": 12999, "specs": ["Black", "Platinum White"], "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Lite Pro", "base_price": 6499, "specs": ["Navy Blue", "Space Grey"], "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Classic", "base_price": 2999, "specs": ["Stealth Black"], "img": "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&auto=format&fit=crop&q=60"}
                ]
            platforms = ["Amazon", "Flipkart", "Meesho"]  # Typical tech platforms in India
            
        elif is_fashion:
            category = "Fashion"
            if "tshirt" in query_lower or "shirt" in query_lower:
                base_models = [
                    {"name": "Puma Men's Regular Fit Cotton T-Shirt", "base_price": 1499, "specs": ["Red", "Navy Blue", "Black"], "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Levi's Solid Regular Fit Cotton Shirt", "base_price": 2499, "specs": ["White", "Olive Green", "Light Blue"], "img": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Roadster Striped Crew Neck T-Shirt", "base_price": 799, "specs": ["Black/Grey", "Navy/White"], "img": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=500&auto=format&fit=crop&q=60"}
                ]
            elif "jeans" in query_lower:
                base_models = [
                    {"name": "Levi's 511 Slim Fit Men's Jeans", "base_price": 3899, "specs": ["Dark Indigo", "Light Wash"], "img": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Pepe Jeans Men Regular Fit Mid-Rise Jeans", "base_price": 2999, "specs": ["Mid Blue", "Stone Wash"], "img": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Highlander Men Slim Fit Clean Jeans", "base_price": 1499, "specs": ["Black", "Navy Blue"], "img": "https://images.unsplash.com/photo-1582552938357-32b906df43cd?w=500&auto=format&fit=crop&q=60"}
                ]
            else:
                clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).title()
                base_models = [
                    {"name": f"{clean_query} Designer Printed Wear", "base_price": 1899, "specs": ["Red Multi", "Blue Flora"], "img": "https://images.unsplash.com/photo-1618244972963-dbee1a7edc95?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Casual Comfort Fit", "base_price": 999, "specs": ["Charcoal Grey", "Beige"], "img": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Premium Slim Fit", "base_price": 2799, "specs": ["Burgundy", "Emerald Green"], "img": "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=500&auto=format&fit=crop&q=60"}
                ]
            platforms = ["Amazon", "Flipkart", "Myntra", "Ajio", "Meesho"]
            
        elif is_footwear:
            category = "Footwear"
            if "nike" in query_lower or "sneakers" in query_lower:
                base_models = [
                    {"name": "Nike Air Max Solo Sneakers", "base_price": 8995, "specs": ["White/Red", "Full Black"], "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Nike Court Vision Low Next Nature", "base_price": 5995, "specs": ["White/Black", "White/Blue"], "img": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Nike Revolution 7 Running Shoes", "base_price": 3695, "specs": ["Grey/Neon", "Black/White"], "img": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=500&auto=format&fit=crop&q=60"}
                ]
            elif "adidas" in query_lower or "puma" in query_lower:
                base_models = [
                    {"name": "Puma Smashic Unisex Sneakers", "base_price": 3999, "specs": ["Black/White", "Navy/White"], "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Adidas Ultrabounce Running Shoes", "base_price": 6599, "specs": ["Core Black", "Cloud White"], "img": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500&auto=format&fit=crop&q=60"},
                    {"name": "Adidas Advantage Base Tennis Sneakers", "base_price": 4599, "specs": ["White/Green", "All Black"], "img": "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=500&auto=format&fit=crop&q=60"}
                ]
            else:
                clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).title()
                base_models = [
                    {"name": f"{clean_query} Sports Training Shoes", "base_price": 3299, "specs": ["Grey/Orange", "Navy Blue"], "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Casual Loafer Shoes", "base_price": 1999, "specs": ["Tan Brown", "Suede Black"], "img": "https://images.unsplash.com/photo-1531310197839-ccf54664f2d5?w=500&auto=format&fit=crop&q=60"},
                    {"name": f"{clean_query} Retro Leather Sneakers", "base_price": 4999, "specs": ["Vintage White", "Black Gum"], "img": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&auto=format&fit=crop&q=60"}
                ]
            platforms = ["Amazon", "Flipkart", "Myntra", "Ajio"]
            
        else:
            category = "General"
            clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query).title()
            base_models = [
                {"name": f"Premium {clean_query} Combo Set", "base_price": 1999, "specs": ["Standard Edition"], "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"},
                {"name": f"Universal {clean_query} Utility Pack", "base_price": 899, "specs": ["Multipack"], "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"},
                {"name": f"Compact {clean_query} Smart Gadget", "base_price": 3499, "specs": ["Classic Edition", "Mini Edition"], "img": "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?w=500&auto=format&fit=crop&q=60"}
            ]
            platforms = ["Amazon", "Flipkart", "Meesho"]

        # Generate deals for each platform
        for model in base_models:
            for spec in model["specs"]:
                for plat in platforms:
                    # Introduce random variation per platform but centered around base_price
                    # Meesho is usually cheapest but higher delivery time/lower rating
                    # Amazon is standard price, free/cheap delivery, high ratings, fast delivery
                    # Flipkart is competitive, medium delivery, solid reviews
                    # Myntra/Ajio are premium fashion, medium price, good returns/packaging
                    
                    price_modifier = 1.0
                    rating_modifier = 0.0
                    delivery_time = "In 2-3 Days"
                    delivery_fee = 40.0
                    discount_pct = random.randint(5, 30)
                    
                    if plat == "Amazon":
                        price_modifier = random.uniform(0.96, 1.03)
                        rating_modifier = random.uniform(0.1, 0.4)
                        delivery_time = random.choice(["Tomorrow", "In 1 Day", "In 2 Days"])
                        delivery_fee = random.choice([0.0, 0.0, 40.0])
                    elif plat == "Flipkart":
                        price_modifier = random.uniform(0.94, 1.01)
                        rating_modifier = random.uniform(0.0, 0.3)
                        delivery_time = random.choice(["In 2 Days", "In 3 Days"])
                        delivery_fee = random.choice([0.0, 40.0, 40.0])
                    elif plat == "Meesho":
                        price_modifier = random.uniform(0.85, 0.93) # Cheapest
                        rating_modifier = random.uniform(-0.6, -0.1) # Lower quality/rating
                        delivery_time = random.choice(["In 5 Days", "In 7 Days"]) # Slower
                        delivery_fee = 0.0 # Often free shipping
                        discount_pct = random.randint(15, 45) # Higher discounts
                    elif plat == "Myntra":
                        price_modifier = random.uniform(0.98, 1.05)
                        rating_modifier = random.uniform(0.1, 0.5)
                        delivery_time = random.choice(["In 2 Days", "In 4 Days"])
                        delivery_fee = 49.0
                    elif plat == "Ajio":
                        price_modifier = random.uniform(0.95, 1.02)
                        rating_modifier = random.uniform(-0.1, 0.3)
                        delivery_time = random.choice(["In 3 Days", "In 5 Days"])
                        delivery_fee = 50.0

                    price = round(model["base_price"] * price_modifier)
                    original_price = round(price / (1 - (discount_pct / 100)))
                    rating = round(min(5.0, max(2.5, 4.2 + rating_modifier)), 1)
                    reviews_count = random.randint(50, 15000)
                    
                    # Generate a realistic platform-specific product title representation
                    title_variations = [
                        f"{model['name']} ({spec})",
                        f"{model['name']} - {spec}",
                    ]
                    if plat == "Amazon":
                        title = f"{model['name']} ({spec}, Ultra Pack)" if random.choice([True, False]) else f"Apple {model['name']}" if "Apple" not in model['name'] and "iphone" in query_lower else f"{model['name']} ({spec})"
                    elif plat == "Flipkart":
                        title = f"{model['name']} ({spec} Color, {random.choice(['128 GB', '8 GB RAM'])} Edition)" if is_electronics else f"{model['name']} ({spec})"
                    else:
                        title = f"{model['name']} - {spec}"
                        
                    # Add mockup platform link
                    plat_lower = plat.lower()
                    if plat_lower == "amazon":
                        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
                    elif plat_lower == "flipkart":
                        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
                    elif plat_lower == "ajio":
                        url = f"https://www.ajio.com/search/?text={query.replace(' ', '+')}"
                    elif plat_lower == "myntra":
                        url = f"https://www.myntra.com/search?q={query.replace(' ', '+')}"
                    elif plat_lower == "meesho":
                        url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
                    else:
                        url = f"https://www.{plat_lower}.com/search?q={query.replace(' ', '+')}"

                    deals.append({
                        "title": title,
                        "price": float(price),
                        "original_price": float(original_price),
                        "discount": float(discount_pct),
                        "rating": float(rating),
                        "reviews_count": reviews_count,
                        "delivery_fee": float(delivery_fee),
                        "delivery_time": delivery_time,
                        "platform": plat,
                        "url": url,
                        "image_url": model["img"]
                    })
                    
        return deals
