import requests

from time import time
from datetime import datetime
from fake_useragent import FakeUserAgent
from pyquery import PyQuery
from urllib import request

from src.utils.fileIO import File
from src.utils.corrector import vname
from src.utils.logs import logger


class Women:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent()

        self.DOMAIN = 'data.ipu.org'
        self.MAIN_URL = 'https://data.ipu.org/women-speakers'
        self.PIE_RIGHT_API = 'https://data.ipu.org/api/comparison.json?load-entity-refs=taxonomy_term%2Cfield_collection_item&max-depth=2&langcode=en&field=chamber%3Afield_chamber_speakers%3Afield_sex&structure=any__upper_chamber&chart_only=0'
        self.PIE_LEFT_API = 'https://data.ipu.org/api/comparison.json?load-entity-refs=taxonomy_term%2Cfield_collection_item&max-depth=2&langcode=en&field=chamber%3Afield_chamber_speakers%3Afield_sex&structure=any__lower_chamber&chart_only=0'
        self.XLSX = 'https://data.ipu.org/sites/default/files/other-datasets/women_in_parliament-historical_database-1945_to_2018.xlsx'
        self.RAW_PATH = 'data/xlsx/women_in_parliament-historical_database-1945_to_2018.xlsx'

        self.GENDER = ['male', 'female']

        self.__header = {
            "User-Agent": self.__faker.random
        }
        ...

    def __curl(self, path: str, url: str):
        if url:
            opener = request.build_opener()
            opener.addheaders = [("User-Agent", self.__faker.random)]

            request.install_opener(opener)
            request.urlretrieve(url, path)


    def main(self):
        response = requests.get(self.PIE_LEFT_API+'&year='+'1993', headers=self.__header)
        self.__curl(path=self.RAW_PATH, url=self.XLSX)

        logger.info('is downloading...')
        logger.info('please wait..')

        logger.info(f'status: {response.status_code}')
        print()

        years = [year for year in reversed(response.json()["payload"]["visualization"]["map"]["settings"]["range"])]
        for year in years:

            logger.info(f'year: {year}')
            if year != '2024': 
                left = requests.get(self.PIE_LEFT_API+'&year='+year, headers=self.__header)
                right = requests.get(self.PIE_RIGHT_API+'&year='+year, headers=self.__header)
            else: 
                left = requests.get(self.PIE_LEFT_API, headers=self.__header)
                right = requests.get(self.PIE_RIGHT_API, headers=self.__header)
            
            results = {
                "year": year,
                "domain": self.DOMAIN,
                "url": self.MAIN_URL,
                "crawler_time": str(datetime.now()),
                "crawler_time_epoch": int(time()),
                "path_data_row": self.RAW_PATH,
                "chart": {
                    "lower_and_unicameral_chambers": {
                        "total_speakers": 0,
                        "female": {
                            "speakers": 0,
                            "percent": 0
                        },
                        "male": {
                            "speakers": 0,
                            "percent": 0
                        }
                    },
                    "upper_chambers": {
                        "total_speakers": 0,
                        "female": {
                            "speakers": 0,
                            "percent": 0
                        },
                        "male": {
                            "speakers": 0,
                            "percent": 0
                        }
                    }
                }
            }

            left_speakers = PyQuery(left.json().get("payload", {}).get("visualization", {}).get("pie", {}).get("table", {}).get("markup", {})).find('tbody tr')

            speakers = [int(speaker) for speaker in left_speakers.find('td:last-child').text().split(' ')]
            for index, speaker in enumerate(left_speakers):

                results["chart"]["lower_and_unicameral_chambers"]["total_speakers"] = sum(speakers)
                results["chart"]["lower_and_unicameral_chambers"][PyQuery(speaker).find('td:first-child').text().lower()]["speakers"] = speakers[index]
                results["chart"]["lower_and_unicameral_chambers"][PyQuery(speaker).find('td:first-child').text().lower()]["percent"] = format((speakers[index] / sum(speakers) * 100), ".1f")+'%'


            if right.json()["list"]: 

                right_speakers = PyQuery(right.json().get("payload", {}).get("visualization", {}).get("pie", {}).get("table", {}).get("markup", {})).find('tbody tr')
                speakers = [int(speaker) for speaker in right_speakers.find('td:last-child').text().split(' ')]
                for index, speaker in enumerate(right_speakers):

                    results["chart"]["upper_chambers"]["total_speakers"] = sum(speakers)
                    results["chart"]["upper_chambers"][PyQuery(speaker).find('td:first-child').text().lower()]["speakers"] = speakers[index]
                    results["chart"]["upper_chambers"][PyQuery(speaker).find('td:first-child').text().lower()]["percent"] = format((speakers[index] / sum(speakers) * 100), ".1f")+'%'

            self.__file.write_json(path=f'data/json/{year}.json', content=results)

        ...
