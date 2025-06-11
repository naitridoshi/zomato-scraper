from flask import Blueprint, render_template, request, make_response, redirect, url_for
import io
import pandas as pd
from export.export import SCRAPE_ZOMATO_DINEOUT_FLASK
from xlsxwriter import Workbook
from logger import get_logger
import json

view = Blueprint("view", __name__)
RESULT_DICT = {}
CITY_NAME = ''
logger, listener = get_logger('website.views')
listener.start()

@view.route("/", methods=["get", "post"])
def homepage():
    logger.info('Rendering homepage')
    return render_template("zs-webpage.html")


@view.route("/submit", methods=["get", "post"])
def formsubmitted():
    logger.info('Form submitted')
    form_data = request.form.to_dict()
    error_city, error_scroll, more_info, images, city, scroll = form_values(form_data=form_data)

    city_name = request.form.get("city") 

    global CITY_NAME
    CITY_NAME = city_name
   
    action = request.form.get('action')
    logger.debug(f'Form data: {form_data}, action: {action}')
    
    if error_city == False and error_scroll == False:
        try:
            initiate_scrape = SCRAPE_ZOMATO_DINEOUT_FLASK(city=city_name, 
                scroll_count = scroll,
                more_info = more_info,
                images = images,
                action=action
            )
            logger.info('Initiating scrape')
            results = initiate_scrape.scrape()

            global RESULT_DICT
            RESULT_DICT = results

        except Exception as e:
            logger.error(f'Error during scrape: {e}')

        logger.info('Rendering export page')

        logger.info("Saving results to local file")
        with open(f'{city_name}_results.json', 'w') as f:
            json.dump(results, f)

        return render_template(
            "zs-export.html",

            results = results,
            action = action,
            city = city_name,
            num_of_records = len(results)
        )
    else:
        logger.warning(f'Form validation failed: error_city={error_city}, error_scroll={error_scroll}')
        return render_template(
            "zs-webpage.html",

            city=city_name,
            scroll=scroll,
            error_city = error_city,
            error_scroll = error_scroll
        )


@view.route("/download", methods = ["post", "get"])
def file_export():
    logger.info('File export requested')
    action = request.form.get('action')
    

    global RESULT_DICT
    if action == 'csv':
        logger.info('Redirecting to download_csv')
        return redirect(url_for('view.download_csv',))
    elif action == 'xlsx':
        logger.info('Redirecting to download_excel')
        return redirect(url_for('view.download_excel',))
    elif action == 'json':
        logger.info('Redirecting to download_json')
        return redirect(url_for('view.download_json',))
        
    logger.warning('Unknown export action')
    return f'{RESULT_DICT}, '

@view.route('/download/csv/')
def download_csv():
    logger.info('CSV download requested')
    global RESULT_DICT
    global CITY_NAME

    df = pd.DataFrame(RESULT_DICT).T
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    response = make_response(csv_buffer.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={CITY_NAME}_data.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@view.route('/download/excel/')
def download_excel():
    logger.info('Excel download requested')
    global RESULT_DICT
    global CITY_NAME

    df = pd.DataFrame(RESULT_DICT).T
    # Convert DataFrame to Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Sheet1')
    excel_buffer.seek(0)

    response = make_response(excel_buffer.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={CITY_NAME}_data.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

@view.route('/download/json/')
def download_json():
    logger.info('JSON download requested')
    global RESULT_DICT
    global CITY_NAME

    df = pd.DataFrame(RESULT_DICT).T
    
    json_buffer = io.StringIO()
    df.to_json(json_buffer, orient='records')
    json_buffer.seek(0)

    response = make_response(json_buffer.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={CITY_NAME}_data.json'
    response.headers['Content-Type'] = 'text/csv'
    return response


def form_values(form_data):
    logger.debug(f'Validating form data: {form_data}')
    error_city = False
    error_scroll = False
    more_info = False
    images = False
    city = form_data['city']
    scroll = form_data["scroll"]

    if len(form_data["city"].strip()) == 0:
        error_city= True

    try:
        scroll = int(
            form_data["scroll"],
        )
    except:
        error_scroll = True

    if "more-info" in list(form_data.keys()):
        more_info = True

    if "images" in list(form_data.keys()):
        images = True
    
    logger.debug(f'Validation results: error_city={error_city}, error_scroll={error_scroll}, more_info={more_info}, images={images}, city={city}, scroll={scroll}')
    return error_city, error_scroll, more_info, images, city, scroll