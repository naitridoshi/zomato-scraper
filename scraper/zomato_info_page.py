from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from vars.xpaths import XPATHS
from logger import get_logger

logger, listener = get_logger('zomato_info_page')
listener.start()

def get_more_info(driver, more_info_url):
    logger.info(f'Called get_more_info for URL: {more_info_url}')
    driver.get(more_info_url)
    raw_text = r''
    phone_xpath = '//*[@id="root"]/div/main/div/section[2]/section/section/div/div/section[2]/div/div[2]/div/a'
    try:
        element = WebDriverWait(driver=driver, timeout=1).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='More Info']"))
                )
        xpath_more_info = get_xpath(element)
        more_info_content_element =  WebDriverWait(driver=driver, timeout=5).until(
                    EC.presence_of_element_located((By.XPATH, f'{xpath_more_info}/following-sibling::div'))
                )
        raw_text += more_info_content_element.text
        logger.debug(f'More info content: {raw_text}')
        try:
            phone_element = WebDriverWait(driver=driver, timeout=1).until(
                EC.presence_of_element_located((By.XPATH, phone_xpath))
            )
            phone_number = phone_element.text
            logger.debug(f'Phone number found: {phone_number}')
            raw_text += f'\nPhone: {phone_number}'
        except Exception as e:
            logger.warning(f'Phone number not found: {e}')
        return raw_text.split('\n')
    except Exception as e:
        logger.error(f'Error in get_more_info: {e}')
        return  raw_text.split('\n') if raw_text else ['None']
    

def get_xpath(element: WebElement) -> str:
    logger.debug('Called get_xpath')
    n = len(element.find_elements(By.XPATH, "./ancestor::*"))
    path = ""
    current = element
    for _ in range(n):
        tag = current.tag_name
        lvl = len(current.find_elements(By.XPATH, f"./preceding-sibling::{tag}")) + 1
        path = f"/{tag}[{lvl}]" + path
        current = current.find_element(By.XPATH, "./parent::*")
    logger.debug(f'XPath generated: /{current.tag_name}{path}')
    return f"/{current.tag_name}{path}"


def get_images(driver, more_info_url):
    logger.info(f'Called get_images for URL: {more_info_url}')
    driver.get(more_info_url)
    images = []

    xpath_array = [XPATHS.image_1, XPATHS.image_2, XPATHS.image_3, XPATHS.image_4]

    for xpath in xpath_array:
        return_value = get_an_image(driver=driver, timeout=10, image_xpath=xpath)

        if return_value == -1:
            logger.warning(f'Image not found for xpath: {xpath}, retrying...')
            attempt = get_an_image(driver=driver, timeout=10, image_xpath=xpath)
        
        images.append(return_value)
    
    
    logger.debug(f'Images collected: {images}')
    return images

    
def get_an_image(driver, timeout, image_xpath):
    logger.debug(f'Called get_an_image for xpath: {image_xpath}')
    try:
        image = WebDriverWait(driver = driver, timeout= timeout).until(
            EC.presence_of_element_located((By.XPATH, image_xpath))
        )
        href = image.get_attribute('src')
        if len(href) != 0:
            output_index = href.find('?output')
            href = href[:output_index]
            logger.debug(f'Image src found: {href}')
            return href
        
        logger.warning('Image src empty')
        return -1
            
    except Exception as e:
        logger.error(f'Error in get_an_image: {e}')
        pass