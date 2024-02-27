import json

import constants
import requests

from card_info import CardInfo
from config import app_config


class TrelloAPI:

    def __init__(self):
        self.board_id = ""
        self.list_info = {}

    def search_keyword(self, keyword):
        search_endpoint = constants.BASE_URL + constants.SEARCH_ENDPOINT
        query = {
            'query': keyword,
            'key': app_config[constants.API_KEY],
            'token': app_config[constants.API_TOKEN],
        }

        response = requests.request(
            "GET",
            search_endpoint,
            params=query
        )

        return json.loads(response.text)

    def get_task_list(self, board_name=constants.DAILY_PLANNER_BOARD):

        search_response = self.search_keyword(keyword=board_name)

        # board_id = ""

        boards_details = search_response.get("boards")
        for board_details in boards_details:
            if board_details.get("name") == board_name:
                self.board_id = board_details.get("id")
                break

        lists_details = self.get_lists_on_board()
        lists_info = {list_detail.get("id"): list_detail.get("name") for list_detail in lists_details}

        list_cards_info = {}

        for list_id in lists_info:
            list_cards_info[lists_info.get(list_id)] = self.get_cards_from_list(id_list=list_id)

        return json.dumps(list_cards_info)

    def create_board(self, board_name):
        board_endpoint = (constants.BASE_URL + constants.BOARD_ENDPOINT).format(board_name)

        query = {
            'name': board_name,
            'key': app_config[constants.API_KEY],
            'token': app_config[constants.API_TOKEN],
            'defaultLists': 'false',
            "background": 'sky'
        }

        response = requests.request(
            "POST",
            board_endpoint,
            params=query
        )

        self.board_id = json.loads(response.text).get("id")
        return self.board_id
        # return response.status_code

    def get_lists_on_board(self):
        lists_endpoint = (constants.BASE_URL + constants.LISTS_ENDPOINT).format(self.board_id)
        query = {
            'key': app_config[constants.API_KEY],
            'token': app_config[constants.API_TOKEN]
        }

        response = requests.request(
            "POST",
            lists_endpoint,
            params=query
        )

        return json.loads(response.text)

    def create_lists_on_board(self, lists_details):
        lists_endpoint = (constants.BASE_URL + constants.LISTS_ENDPOINT).format(self.board_id)
        headers = {
            "Accept": "application/json"
        }

        # list_ids = []
        for list_detail in lists_details:
            query = {
                'name': list_detail,
                'key': app_config[constants.API_KEY],
                'token': app_config[constants.API_TOKEN]
            }

            response = requests.request(
                "POST",
                lists_endpoint,
                headers=headers,
                params=query
            )

            json_response = json.loads(response.text)
            print(response.status_code)
            # TODO Check if response is not 200
            self.list_info[list_detail] = json_response.get("id")

        return "True"

    def create_card_for_list(self, list_name, cards_details):
        cards_endpoint = constants.BASE_URL + constants.CARD_ENDPOINT
        print("List id {} and endpoint {}".format(self.list_info.get(list_name), cards_endpoint))

        headers = {
            "Accept": "application/json"
        }
        for card_details in cards_details:
            query = {
                'idList': self.list_info.get(list_name),
                'key': app_config[constants.API_KEY],
                'token': app_config[constants.API_TOKEN],
                'name': card_details.get("name"),
                'desc': card_details.get("desc"),
                'due': card_details.get("due"),
                'start': card_details.get("start"),
                'id_list': card_details.get("id_list"),
                'url_source': card_details.get("url_source")
            }

            response = requests.request(
                "POST",
                cards_endpoint,
                headers=headers,
                params=query
            )
            print(response.status_code)
        return "True"
        # json.loads(response.text)

    def get_cards_from_list(self, list_name="", id_list=""):

        if list_name != "":
            id_list = self.list_info.get(list_name)

        endpoint = (constants.BASE_URL + "1/lists/{}/cards").format(id_list)
        headers = {
            "Accept": "application/json"
        }

        query = {
            'key': app_config[constants.API_KEY],
            'token': app_config[constants.API_TOKEN],
        }

        response = requests.request(
            "GET",
            endpoint,
            headers=headers,
            params=query
        )

        response_json = json.loads(response.text)
        cards_info = []
        for card_details in response_json:
            cards_info.append(
                {
                    "id": card_details.get("id"),
                    "name": card_details.get("name"),
                    "desc": card_details.get("desc"),
                    "url": card_details.get("url"),
                    "start_time": card_details.get("start"),
                    "due": card_details.get("due"),

                }
            )

        return cards_info
