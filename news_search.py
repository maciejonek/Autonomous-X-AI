import worldnewsapi
from worldnewsapi.models.search_news200_response import SearchNews200Response
from worldnewsapi.rest import ApiException
from pprint import pprint
import json


class Search():
    def __init__(self, api_key):
        self.api_key = api_key
        self.configuration = worldnewsapi.Configuration(host="https://api.worldnewsapi.com")
        self.configuration.api_key['apiKey'] = api_key
        self.configuration.api_key['headerApiKey'] = api_key

    def search_news(self, query):
        
        conf = self.configuration
        with worldnewsapi.ApiClient(self.configuration) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            text = query
            language = 'en'
            number = 1

            try:
                api_response = api_instance.search_news(text=text, language=language, number=number)
                response = api_response.to_json()
                return json.loads(response)
            except Exception as e:
                print("Exception when calling NewsApi->search_news: %s\n" % e)