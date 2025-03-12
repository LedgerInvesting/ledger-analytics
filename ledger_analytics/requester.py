import requests

from .types import HTTPMethods, JSONData


class Requester(object):
    def __init__(self, api_key: str) -> None:
        self.headers = {"Authorization": f"Api-Key {api_key}"}

    @property
    def post(self, url: str, data: JSONData):
        return self._factory("post", url, data)

    @property
    def get(self, url: str, data: JSONData):
        return self._factory("get", url, data)

    def _factory(self, method: HTTPMethods, url: str, data: JSONData):
        if method.lower() == "post":
            request = requests.post
        else:
            request = requests.get
        response = request(url, data=data, format="json", headers=self.headers)
        self._catch_status(response.status_code)
        return response

    @staticmethod
    def _catch_status(status: requests.Response) -> requests.HTTPError:
        match status:
            case 404:
                raise requests.HTTPError("404: Cannot find the given endpoint.")
            case 403:
                raise requests.HTTPError(
                    "403: You do not have permissions to perform this action."
                )
            case 500:
                raise requests.HTTPError("500: Internal server error.")
            case _:
                pass
