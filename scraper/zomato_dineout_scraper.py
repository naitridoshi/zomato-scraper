import sys
sys.path.append('.')
from logger import get_logger

import driver.driver_setup as driver_setup
import scraper.zomato_dinout_scrape_parameters as parameters
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from vars.xpaths import XPATHS
from vars.globals import OUTPUT

import time

logger, listener = get_logger('zomato_dineout_scraper')
listener.start()

def zomato_dine_out_scrape(city, more_info, images, scroll_count):
    logger.info(f'Function zomato_dine_out_scrape called with city={city}, more_info={more_info}, images={images}, scroll_count={scroll_count}')
    print(f'zomato_dine_out_scrape: {city} ')
    driver = driver_setup.prepare_driver()
    logger.debug('Driver prepared')
    driver.get(f'https://www.zomato.com/{city}/dine-out')
    logger.info(f'Navigated to https://www.zomato.com/{city}/dine-out')
    output = [OUTPUT.output_ff]
    seen_links = set()  # Track unique restaurant links
    restaurant_rows = []  # Temporarily store restaurant data before more_info
    times_scroll = 0

    try:
        while times_scroll <= scroll_count :
            logger.debug(f'Scrolling: {times_scroll}/{scroll_count}')
            driver.execute_script(f'scrollBy(0, 1500)')
            time.sleep(0.5)
            
            try:
                elements = WebDriverWait(driver=driver, timeout=5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'jumbo-tracker'))
                )
                logger.info(f'Found {len(elements)} restaurant elements')
            except Exception as e:
                logger.error(f'Error finding elements: {e}')
                break

            for element in elements:
                try:
                    restaurant_name = element.find_element(By.XPATH, XPATHS.name).text
                    restaurant_cuisines = element.find_element(By.XPATH, XPATHS.cuisines).text
                    restaurant_prices = element.find_element(By.XPATH, XPATHS.prices).text
                    restaurant_address = element.find_element(By.XPATH, XPATHS.address).text
                    restaurant_link = element.find_element(By.XPATH, XPATHS.zomato_link).get_attribute('href')
                    if restaurant_link in seen_links:
                        logger.warning(f'Duplicate restaurant found: {restaurant_link}, skipping.')
                        continue
                    seen_links.add(restaurant_link)
                    logger.debug(f'Parsed restaurant: {restaurant_name}')
                    restaurant_rows.append([restaurant_name, restaurant_address, restaurant_prices, restaurant_cuisines, restaurant_link])
                except Exception as e:
                    logger.error(f'Error parsing restaurant element: {e}')

            times_scroll += 1

    finally:
        logger.info('Finalizing scrape, handling images/more_info if needed')
        driver.close()
        logger.info('Driver closed')

    # Add all collected rows to output
    output.extend(restaurant_rows)

    # Parallelize only more_info step after all links are collected
    if more_info:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import scraper.zomato_info_page as zomato_info_page
        def fetch_more_info(row):
            driver = driver_setup.prepare_driver()
            try:
                link = row[4]
                info = zomato_info_page.get_more_info(driver, link)
                return info
            except Exception as e:
                logger.error(f'Error fetching more info for {row[4]}: {e}')
                return ["None"]
            finally:
                driver.quit()
        logger.info('Fetching more info in parallel for all restaurants')
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_idx = {executor.submit(fetch_more_info, row): idx for idx, row in enumerate(output[1:])}
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    info = future.result()
                    output[idx+1].append(info)
                except Exception as e:
                    logger.error(f'Error in future for row {idx}: {e}')
        output[0] = OUTPUT.output_tf if not images else OUTPUT.output_tt
    # Images logic remains sequential
    if images:
        output[0] = OUTPUT.output_ft if not more_info else OUTPUT.output_tt
        parameters.images_form_links(driver_setup.prepare_driver(), output)
    logger.info('Scrape complete')
    return output

