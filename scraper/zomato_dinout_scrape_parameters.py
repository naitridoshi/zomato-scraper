from scraper import zomato_info_page
from logger import get_logger

logger, listener = get_logger('zomato_dinout_scrape_parameters')
listener.start()

def more_info_from_links(driver, output):
    logger.info('Called more_info_from_links')
    for elements in output[1:]:
        element_link = elements[4]
        logger.debug(f'Getting more info for link: {element_link}')
        retrieved_more = zomato_info_page.get_more_info(driver, element_link)
        elements.append(retrieved_more)
    logger.info('Completed more_info_from_links')

def images_form_links(driver, output):
    logger.info('Called images_form_links')
    for elements in output[1:]:
        element_link = elements[4]
        logger.debug(f'Getting images for link: {element_link}')
        images_list = zomato_info_page.get_images(driver, element_link)
        elements.append(images_list)
    logger.info('Completed images_form_links')