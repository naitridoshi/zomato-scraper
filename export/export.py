import pandas as pd
from scraper.zomato_dineout_scraper import zomato_dine_out_scrape
from logger import get_logger

logger, listener = get_logger('export.export')
listener.start()

class SCRAPE_ZOMATO_DINEOUT:

    def __init__(self, city, scroll_count, more_info, images, as_csv, as_json, as_xlsx) -> None:
        logger.info(f'Initializing SCRAPE_ZOMATO_DINEOUT with city={city}, scroll_count={scroll_count}, more_info={more_info}, images={images}, as_csv={as_csv}, as_json={as_json}, as_xlsx={as_xlsx}')
        self.city = city
        self.scroll = scroll_count
        self.more_info = more_info
        self.images = images
        self.csv = as_csv
        self.json = as_json
        self.xslx = as_xlsx
        

    def scrape(self):
        logger.info('Starting scrape in SCRAPE_ZOMATO_DINEOUT')
        results = zomato_dine_out_scrape(
            city= self.city,
            scroll_count= self.scroll,
            more_info=self.more_info,
            images=self.images,
        )

        if self.csv:
            logger.info('Exporting results as CSV')
            df = pd.DataFrame(results[1:]).to_csv(self.city+'.csv', header=results[0])
        if self.json:
            logger.info('Exporting results as JSON')
            df = pd.DataFrame(results[1:], columns=results[0]).T.to_json(self.city+'.json', index=False)
        if self.xslx:
            logger.info('Exporting results as XLSX')
            df = pd.DataFrame(results[1:]).to_excel(self.city+'.xlsx', header=results[0])
        logger.info('Scrape and export complete in SCRAPE_ZOMATO_DINEOUT')

class SCRAPE_ZOMATO_DINEOUT_FLASK:
    

    def __init__(self, city, scroll_count, more_info, images, action) -> None:
        logger.info(f'Initializing SCRAPE_ZOMATO_DINEOUT_FLASK with city={city}, scroll_count={scroll_count}, more_info={more_info}, images={images}, action={action}')
        self.city = city
        self.scroll = scroll_count
        self.more_info = more_info
        self.images = images
        self.action = action


    def scrape(self):
        logger.info('Starting scrape in SCRAPE_ZOMATO_DINEOUT_FLASK')
        results = zomato_dine_out_scrape(
            city= self.city,
            scroll_count= self.scroll,
            more_info=self.more_info,
            images=self.images,
        )
        logger.info('Converting results to DataFrame and dict for Flask')
        df = pd.DataFrame(results[1:], columns=results[0])
        logger.info('Scrape complete in SCRAPE_ZOMATO_DINEOUT_FLASK')
        return df.T.to_dict()

        # if self.action == 'csv':
        #     df = pd.DataFrame(results[1:]).to_csv(self.city+'.csv', header=results[0])
        # if self.action == 'json':
        #     df = pd.DataFrame(results[1:], columns=results[0]).T.to_json(self.city+'.json', index=False)
        # if self.action == 'xlsx':
        #     df = pd.DataFrame(results[1:]).to_excel(self.city+'.xlsx', header=results[0])
