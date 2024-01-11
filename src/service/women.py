import requests

from time import time
from datetime import datetime
from icecream import ic
from fake_useragent import FakeUserAgent

from src.utils.fileIO import File
from src.utils.corrector import vname


class Women:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent()

        self.DOMAIN = 'data.ipu.org'
        self.MAIN_URL = 'https://data.ipu.org/women-speakers'
        self.PIE_RIGHT_API = 'https://data.ipu.org/api/comparison.json?load-entity-refs=taxonomy_term%2Cfield_collection_item&max-depth=2&langcode=en&field=chamber%3Afield_chamber_speakers%3Afield_sex&structure=any__upper_chamber&chart_only=0'
        self.PIE_LEFT_API = 'https://data.ipu.org/api/comparison.json?load-entity-refs=taxonomy_term%2Cfield_collection_item&max-depth=2&langcode=en&field=chamber%3Afield_chamber_speakers%3Afield_sex&structure=any__lower_chamber&chart_only=0'



        self.__header = {
            "User-Agent": self.__faker.random
        }
        ...



    def main(self):
        response = requests.get(self.PIE_LEFT_API+'&year='+'1993', headers=self.__header)

        ic(response)
        years = [year for year in response.json()["payload"]["visualization"]["map"]["settings"]["range"]]

        for year in years:
            ic(year)

            ic(self.PIE_LEFT_API+'&year='+year)


            if year != '2024': 
                left = requests.get(self.PIE_LEFT_API+'&year='+year, headers=self.__header)
                right = requests.get(self.PIE_RIGHT_API+'&year='+year, headers=self.__header)
            else: 
                left = requests.get(self.PIE_LEFT_API, headers=self.__header)
                right = requests.get(self.PIE_RIGHT_API, headers=self.__header)

            ic(left)
            ic(right)

            self.__file.write_json('data/left.json', left.json())
            self.__file.write_json('data/right.json', right.json())
            
            results = {
                "year": year,
                "domain": self.DOMAIN,
                "url": self.MAIN_URL,
                "crawler_time": str(datetime.now()),
                "crawler_time_epoch": int(time()),
                "path_data_row": "",
                "chart": {
                    "lower_and_unicameral_chambers": {
                        "total_speakers": "",
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
                        "total_speakers": "",
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

            left_speakers = left.json()["payload"]["aggregations"]["chamber:field_chamber_speakers:field_sex"]["map"]
            ic(len(left_speakers))
            
            right_speakers = right.json()["payload"]["aggregations"]["chamber:field_chamber_speakers:field_sex"]["map"]
            ic(len(right_speakers))

            for speakers in left_speakers:
                if speakers["value"] == "Male":
                    results["chart"]["lower_and_unicameral_chambers"]["male"]["speakers"] += 1
                else:
                    results["chart"]["lower_and_unicameral_chambers"]["female"]["speakers"] += 1

            results["chart"]["lower_and_unicameral_chambers"]["male"]["percent"] = \
                str((results["chart"]["lower_and_unicameral_chambers"]["male"]["speakers"] / len(left_speakers) * 100))+'%'
            results["chart"]["lower_and_unicameral_chambers"]["female"]["percent"] = \
                str((results["chart"]["lower_and_unicameral_chambers"]["female"]["speakers"] / len(left_speakers) * 100))+'%'
            
            for speakers in right_speakers:
                if speakers["value"] == "Male":
                    results["chart"]["upper_chambers"]["male"]["speakers"] += 1
                else:
                    results["chart"]["upper_chambers"]["female"]["speakers"] += 1

            results["chart"]["upper_chambers"]["male"]["percent"] = \
                str((results["chart"]["upper_chambers"]["male"]["speakers"] / len(left_speakers) * 100))+'%'
            results["chart"]["upper_chambers"]["female"]["percent"] = \
                str((results["chart"]["upper_chambers"]["female"]["speakers"] / len(left_speakers) * 100))+'%'

            ic(results)

            break


        ...
