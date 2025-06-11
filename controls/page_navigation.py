import time
from logger import get_logger
logger, listener = get_logger('controls.page_navigation')
listener.start()

def scroller(driver,function, user_set_scroll_number):
    logger.info(f'Called scroller with user_set_scroll_number={user_set_scroll_number}')
    scroll_number = 0
    while scroll_number <= user_set_scroll_number:
        logger.debug(f'Scrolling: {scroll_number}/{user_set_scroll_number}')
        # driver.execute_script('window.scrollTo(0, 1500);')
        driver.execute_script(f'scrollBy(0, 1500)')
        time.sleep(0.5)
        scroll_number += 1
    logger.info('Completed scrolling')