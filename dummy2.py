import asyncio
import csv
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import requests
from lxml import html
from telegram import Bot
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass

class RateLimitError(ScrapingError):
    """Exception for rate limiting"""
    pass

class BlockedError(ScrapingError):
    """Exception for being blocked"""
    pass

class ProductScraper:
    def __init__(self, bot_token: str, channel_id: str, csv_filename: str = 'products.csv'):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.csv_filename = csv_filename
        self.session = requests.Session()
        self.bot = None
        
        # Rate limiting configuration
        self.min_delay = 2.0  # Minimum delay between requests
        self.max_delay = 5.0  # Maximum delay between requests
        self.retry_delays = [10, 30, 60, 180, 300]  # Exponential backoff delays
        self.max_retries = 5
        
        # Request headers rotation
        self.headers_pool = [
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "referer": "https://themes.woocommerce.com/"
            },
            {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
                "referer": "https://themes.woocommerce.com/"
            },
            {
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "referer": "https://themes.woocommerce.com/"
            }
        ]
        
        # XPath selectors
        self.xpaths = {
            'electronics_list': "//ul[@class='products columns-4']/li[contains(@class, 'purchasable')]",
            "image": ".//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']/img/@src",
            "name": ".//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']/h2/text()",
            "price": ".//span[@class='woocommerce-Price-amount amount']/bdi/text()",
            "next_page": "(//a[@class='next page-numbers'])[1]/@href"
        }
        
        self.scraped_products = []
        self.total_scraped = 0
        
    async def initialize_bot(self) -> None:
        """Initialize Telegram bot"""
        try:
            self.bot = Bot(token=self.bot_token)
            # Test bot connection
            await self.bot.get_me()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise
    
    def get_random_headers(self) -> Dict[str, str]:
        """Get random headers from the pool"""
        return random.choice(self.headers_pool).copy()
    
    def random_delay(self) -> None:
        """Add random delay between requests"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def make_request(self, url: str, retry_count: int = 0) -> Tuple[str, html.HtmlElement]:
        """Make HTTP request with error handling and retries"""
        if retry_count >= self.max_retries:
            raise ScrapingError(f"Max retries exceeded for URL: {url}")
        
        headers = self.get_random_headers()
        
        try:
            logger.info(f"Requesting URL: {url} (attempt {retry_count + 1})")
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=30,
                allow_redirects=True
            )
            
            # Check for rate limiting or blocking
            if response.status_code == 429:
                raise RateLimitError("Rate limited by server")
            elif response.status_code == 403:
                raise BlockedError("Access forbidden - possibly blocked")
            elif response.status_code == 404:
                raise ScrapingError(f"Page not found: {url}")
            elif not response.ok:
                raise ScrapingError(f"HTTP {response.status_code}: {response.reason}")
            
            # Check for common blocking indicators in content
            content_lower = response.text.lower()
            blocking_indicators = [
                "access denied", "blocked", "captcha", "cloudflare",
                "please verify you are human", "security check"
            ]
            
            if any(indicator in content_lower for indicator in blocking_indicators):
                raise BlockedError("Detected blocking mechanism in response")
            
            tree = html.fromstring(response.text)
            logger.info(f"Successfully parsed HTML for: {url}")
            return url, tree
            
        except (RateLimitError, BlockedError) as e:
            delay = self.retry_delays[min(retry_count, len(self.retry_delays) - 1)]
            logger.warning(f"{e} - Waiting {delay} seconds before retry...")
            time.sleep(delay)
            return self.make_request(url, retry_count + 1)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            if retry_count < self.max_retries:
                delay = self.retry_delays[min(retry_count, len(self.retry_delays) - 1)]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                return self.make_request(url, retry_count + 1)
            raise ScrapingError(f"Request failed after {self.max_retries} retries: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise ScrapingError(f"Unexpected error: {e}")
    
    def extract_product_data(self, product_element) -> Optional[Dict[str, str]]:
        """Extract product data from HTML element with error handling"""
        try:
            # Extract name
            name_elements = product_element.xpath(self.xpaths['name'])
            name = name_elements[0].strip() if name_elements else "Unknown Product"
            
            # Extract price
            price_elements = product_element.xpath(self.xpaths['price'])
            price = price_elements[0].strip() if price_elements else "Price not available"
            
            # Extract image
            image_elements = product_element.xpath(self.xpaths['image'])
            image = image_elements[0].strip() if image_elements else "No image"
            
            # Validate extracted data
            if not name or name == "Unknown Product":
                logger.warning("Product name not found, skipping...")
                return None
                
            product_data = {
                'name': name,
                'price': price,
                'image': image
            }
            
            logger.debug(f"Extracted product: {product_data}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    def get_next_page_url(self, tree: html.HtmlElement) -> Optional[str]:
        """Get next page URL"""
        try:
            next_page_elements = tree.xpath(self.xpaths['next_page'])
            return next_page_elements[0] if next_page_elements else None
        except Exception as e:
            logger.error(f"Error getting next page URL: {e}")
            return None
    
    def save_to_csv(self, products: List[Dict[str, str]]) -> None:
        """Save products to CSV file"""
        try:
            file_exists = Path(self.csv_filename).exists()
            
            with open(self.csv_filename, mode='a' if file_exists else 'w', 
                     newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                if not file_exists:
                    writer.writerow(['Name', 'Price', 'Image'])  # Header
                
                for product in products:
                    writer.writerow([product['name'], product['price'], product['image']])
            
            logger.info(f"Saved {len(products)} products to {self.csv_filename}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    async def send_telegram_notification(self, products: List[Dict[str, str]], 
                                       start_index: int = 0) -> None:
        """Send product notification to Telegram channel"""
        try:
            if not self.bot:
                await self.initialize_bot()
            
            if not products:
                logger.warning("No products to send to Telegram")
                return
            
            # Create message
            message = f"🔥 New Products Alert! ({len(products)} items)\n\n"
            
            for i, product in enumerate(products[:10], start_index + 1):  # Limit to 10 products per message
                message += f"{i}. {product['name']} - {product['price']}\n"
                if product['image'] != "No image":
                    message += f"Image: {product['image']}\n"
                message += "\n"
            
            # Add timestamp
            message += f"📅 Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send message
            await self.bot.send_message(chat_id=self.channel_id, text=message)
            logger.info(f"Successfully sent Telegram notification with {len(products)} products")
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            raise
    
    def scrape_page(self, url: str) -> List[Dict[str, str]]:
        """Scrape a single page"""
        try:
            url, tree = self.make_request(url)
            
            # Get product elements
            product_elements = tree.xpath(self.xpaths['electronics_list'])
            
            if not product_elements:
                logger.warning(f"No products found on page: {url}")
                return []
            
            logger.info(f"Found {len(product_elements)} products on page")
            
            # Extract product data
            products = []
            for element in product_elements:
                product_data = self.extract_product_data(element)
                if product_data:
                    products.append(product_data)
            
            logger.info(f"Successfully extracted {len(products)} products from page")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            raise
    
    async def scrape_all_pages(self, start_url: str, max_pages: int = 50, 
                              telegram_batch_size: int = 20) -> None:
        """Scrape all pages starting from start_url"""
        current_url = start_url
        page_count = 0
        all_products = []
        
        try:
            while current_url and page_count < max_pages:
                page_count += 1
                logger.info(f"\n====== Scraping Page {page_count}: {current_url} ======")
                
                # Scrape current page
                products = self.scrape_page(current_url)
                
                if products:
                    all_products.extend(products)
                    self.total_scraped += len(products)
                    
                    # Save to CSV periodically
                    self.save_to_csv(products)
                    
                    # Send Telegram notification in batches
                    if len(all_products) >= telegram_batch_size:
                        await self.send_telegram_notification(
                            all_products[-telegram_batch_size:], 
                            self.total_scraped - telegram_batch_size
                        )
                
                # Get next page URL
                _, tree = self.make_request(current_url)
                next_url = self.get_next_page_url(tree)
                
                if not next_url:
                    logger.info("No more pages found")
                    break
                
                current_url = next_url
                
                # Add delay between pages
                self.random_delay()
            
            # Send final notification for remaining products
            remaining_products = len(all_products) % telegram_batch_size
            if remaining_products > 0:
                await self.send_telegram_notification(
                    all_products[-remaining_products:], 
                    self.total_scraped - remaining_products
                )
            
            logger.info(f"\n====== Scraping Complete ======")
            logger.info(f"Total pages scraped: {page_count}")
            logger.info(f"Total products scraped: {self.total_scraped}")
            logger.info(f"Products saved to: {self.csv_filename}")
            
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        finally:
            # Close session
            self.session.close()
            if self.bot:
                await self.bot.close()

async def main():
    """Main function"""
    # Configuration
    BOT_TOKEN = '8331772051:AAG5KbiP05GIBsxs98yYG851rkN7Tz3aOc4'
    CHANNEL_ID = '-1002797016897'
    START_URL = "http://themes.woocommerce.com/storefront/product-category/electronics/"
    CSV_FILENAME = 'products.csv'
    MAX_PAGES = 10  # Adjust as needed
    TELEGRAM_BATCH_SIZE = 10  # Products per Telegram message
    
    # Initialize scraper
    scraper = ProductScraper(
        bot_token=BOT_TOKEN,
        channel_id=CHANNEL_ID,
        csv_filename=CSV_FILENAME
    )
    
    try:
        # Start scraping
        await scraper.scrape_all_pages(
            start_url=START_URL,
            max_pages=MAX_PAGES,
            telegram_batch_size=TELEGRAM_BATCH_SIZE
        )
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)