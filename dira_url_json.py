from requests import get


def dira_url_json(url):
    """
    This function receives an url of API and import it as json
    """
    url = url + "limit=1000000"
    global table_data
    response = get(url)
    table_data = response.json()
    return table_data