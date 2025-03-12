import requests

from .types import HTTPMethods, JSONData


class Requester(object):
    def __init__(self, api_key: str) -> None:
        self.headers = {"Authorization": f"Api-Key {api_key}"}

    def post(self, url: str, data: JSONData):
        return self._factory("post", url, data)

    def get(self, url: str, data: JSONData | None = None):
        return self._factory("get", url, data)

    def delete(self, url: str, data: JSONData | None = None):
        return self._factory("delete", url, data)

    def _factory(self, method: HTTPMethods, url: str, data: JSONData):
        if method.lower() == "post":
            request = requests.post
        elif method.lower() == "get":
            request = requests.get
        elif method.lower() == "delete":
            request = requests.delete
        else:
            raise ValueError(f"Unrecognized HTTPMethod {method}.")

        response = request(url, json=data or {}, headers=self.headers)
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
