import requests
from lxml import html
from urllib.parse import urljoin
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from queue import Queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OnedocScraper:
    def __init__(self, max_workers=10, request_timeout=20):
        self.max_workers = max_workers
        self.request_timeout = request_timeout
        self.csv_lock = threading.Lock()
        self.field_names = [
            "fullName",
            "gender", 
            "title",
            "website",
            "bookable",
            "acceptedVideoConsultations",
            "professionalId",
            "doctorUrl",
            "entityName",
            "entityPhoneNumber",
            "entityAddress",
            "entityLat",
            "entityLng",
            "entityId"
        ]
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "authority": "www.onedoc.ch",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": "LANG=de; didomi_token=eyJ1c2VyX2lkIjoiMTk5MDU0ZmEtYWI2ZC02NjVkLTliMWItZjY4YmMyYjVlYTIyIiwiY3JlYXRlZCI6IjIwMjUtMDktMDFUMTI6NDU6MzEuMTkwWiIsInVwZGF0ZWQiOiIyMDI1LTA5LTAxVDEyOjUzOjU0LjM5M1oiLCJ2ZXJzaW9uIjoyLCJwdXJwb3NlcyI6eyJlbmFibGVkIjpbInBlcmZvcm1pbi04ZTNRZWlodyIsImdvb2dsZW1hcC03YWF0ekZXUSJdfSwidmVuZG9ycyI6eyJlbmFibGVkIjpbImM6Z29vZ2xlYW5hLWNYd0RVSzlnIiwiYzpvbmVkb2MtQTlHUTg5UlEiLCJjOmdvb2dsZW1hcC00NFhhaEZwYSJdfX0=; euconsent-v2=CQXENQAQXENQAAHABBENB6FgAAAAAAAAAAQ4AAAAAAAA.YAAAAAAAAAAA; ANONYMOUS_ID=4a913f07fa38eab9bec415e4a5c7211f3c37552e80b917aee19247e38c759083-anonymousId=c6a93be7-4b8b-4a1b-bb61-f3730a0108ab; _gid=GA1.2.1382792710.1756731257; _ga_R69GP3TF3E=GS2.1.s1756742809$o2$g1$t1756743902$j58$l0$h0; _ga=GA1.1.1486939226.1756731235",
            "Priority": "u=1, i",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 CrKey/1.54.250320",
            "X-Requested-With": "XMLHttpRequest"
        })

    def get_city_links(self):
        """Get all city links for dermatologists"""
        try:
            r = self.session.get("https://www.onedoc.ch/de/hautarzt-dermatologe/stadte", timeout=self.request_timeout)
            tree = html.fromstring(r.content)
            directory_columns = tree.xpath("//ul[@class='directory-column']")
            
            site_links = []
            for col in directory_columns:
                col_links = col.xpath(".//li[contains(@class, 'directory-column-group')]/a/@href")
                col_full_links = [urljoin(r.url, link) for link in col_links]
                site_links.extend(col_full_links)
            
            logger.info(f"Found {len(site_links)} city links")
            return site_links
        except Exception as e:
            logger.error(f"Error getting city links: {e}")
            return []

    def get_professional_ids_from_link(self, link):
        """Get professional IDs from a single city link"""
        try:
            logger.info(f"Processing link: {link}")
            r = self.session.get(link, timeout=self.request_timeout)
            tree = html.fromstring(r.content)
            bookable_professional_ids = tree.xpath(
                "//div[@class='od-search-results-list']/div[contains(@class, 'od-search-result od-search-result-bookable')]/@data-professional-id"
            )
            logger.info(f"Found {len(bookable_professional_ids)} professionals in {link}")
            return bookable_professional_ids
        except Exception as e:
            logger.error(f"Error processing link {link}: {e}")
            return []

    def collect_professional_ids(self, site_links):
        """Collect all professional IDs using multi-threading"""
        all_professional_ids = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_link = {
                executor.submit(self.get_professional_ids_from_link, link): link 
                for link in site_links
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    professional_ids = future.result()
                    all_professional_ids.extend(professional_ids)
                except Exception as e:
                    logger.error(f"Error collecting IDs from {link}: {e}")
        
        logger.info(f"Total professional IDs collected: {len(all_professional_ids)}")
        return all_professional_ids

    def scrape_professional_data(self, pid, csv_writer):
        """Scrape data for a single professional ID"""
        try:
            url = f"https://www.onedoc.ch/api/professionals/{pid}"
            
            # Add some headers specific to this request
            headers = {
                "method": "GET",
                "path": f"/api/professionals/{pid}",
                "Referer": "https://www.onedoc.ch/de/hautarztin-dermatologin/bulach/pcvfd/dr-ephsona-shencoru"
            }
            
            r = self.session.get(url, headers=headers, timeout=self.request_timeout)
            res_data = r.json()
            
            data = res_data.get("data", {})
            profile_url = data.get("profileUrl", {})
            
            # Safely get entity details
            entity_urls = profile_url.get("entityUrls", [])
            if not entity_urls:
                logger.warning(f"No entity URLs for professional {pid}")
                return False
                
            entity_id = entity_urls[0].get("entityId", "")
            if not entity_id:
                logger.warning(f"No entity ID for professional {pid}")
                return False
                
            entity_details = res_data.get("relations", {}).get("entities", {}).get(f"{entity_id}", {})
            addresses = entity_details.get("addresses", [])
            
            if not addresses:
                logger.warning(f"No addresses for professional {pid}")
                entity_address = {}
            else:
                entity_address = addresses[0]

            # Extract all data
            row_data = {
                "fullName": data.get("fullName", ""),
                "gender": data.get("gender", ""),
                "title": data.get("title", ""),
                "website": data.get("website", ""),
                "bookable": data.get("bookable", False),
                "acceptedVideoConsultations": data.get("acceptedVideoConsultations", False),
                "professionalId": profile_url.get("professionalId", ""),
                "doctorUrl": profile_url.get("url", ""),
                "entityName": entity_details.get("name", ""),
                "entityPhoneNumber": entity_details.get("phoneNumber", ""),
                "entityAddress": entity_address.get("formattedAddress", ""),
                "entityLat": entity_address.get("lat", ""),
                "entityLng": entity_address.get("lng", ""),
                "entityId": entity_details.get("id", "")
            }
            
            # Thread-safe CSV writing
            with self.csv_lock:
                csv_writer.writerow(row_data)
            
            logger.info(f"🎉 {pid} Completed")
            return True
            
        except Exception as e:
            logger.error(f"Error scraping professional {pid}: {e}")
            return False

    def run_scraper(self, csv_filename='onedoc_dermatologists_switzerland.csv'):
        """Main scraper function"""
        start_time = time.time()
        
        # Initialize CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.field_names)
            writer.writeheader()
            
            # Step 1: Get all city links
            logger.info("Getting city links...")
            site_links = self.get_city_links()
            if not site_links:
                logger.error("No city links found. Exiting.")
                return
            
            # Step 2: Collect professional IDs (multi-threaded)
            logger.info("Collecting professional IDs...")
            professional_ids = self.collect_professional_ids(site_links)
            if not professional_ids:
                logger.error("No professional IDs found. Exiting.")
                return
            
            # Step 3: Scrape professional data (multi-threaded)
            logger.info(f"Scraping data for {len(professional_ids)} professionals...")
            successful_scrapes = 0
            failed_scrapes = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all scraping tasks
                future_to_pid = {
                    executor.submit(self.scrape_professional_data, pid, writer): pid 
                    for pid in professional_ids
                }
                
                # Process completed tasks
                for future in as_completed(future_to_pid):
                    pid = future_to_pid[future]
                    try:
                        success = future.result()
                        if success:
                            successful_scrapes += 1
                        else:
                            failed_scrapes += 1
                    except Exception as e:
                        logger.error(f"Exception for professional {pid}: {e}")
                        failed_scrapes += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Scraping completed in {duration:.2f} seconds")
        logger.info(f"Successful scrapes: {successful_scrapes}")
        logger.info(f"Failed scrapes: {failed_scrapes}")
        logger.info(f"Total professionals processed: {len(professional_ids)}")

# Usage
if __name__ == "__main__":
    # Initialize scraper with custom settings
    scraper = OnedocScraper(
        max_workers=10,  # Adjust based on your system and rate limiting
        request_timeout=20
    )
    
    # Run the scraper
    scraper.run_scraper('onedoc_dermatologists_switzerland.csv')