import requests

from .types import ConfigDict, HTTPMethods


class Requester(object):
    def __init__(self, api_key: str) -> None:
        self.headers = {"Authorization": f"Api-Key {api_key}"}

    def post(self, url: str, data: ConfigDict):
        return self._factory("post", url, data)

    def get(self, url: str, data: ConfigDict | None = None):
        return self._factory("get", url, data)

    def delete(self, url: str, data: ConfigDict | None = None):
        return self._factory("delete", url, data)

    def _factory(self, method: HTTPMethods, url: str, data: ConfigDict):
        if method.lower() == "post":
            request = requests.post
        elif method.lower() == "get":
            request = requests.get
        elif method.lower() == "delete":
            request = requests.delete
        else:
            raise ValueError(f"Unrecognized HTTPMethod {method}.")

        response = request(url, json=data or {}, headers=self.headers)
        self._catch_status(response)
        return response

    @staticmethod
    def _catch_status(response: requests.Response) -> requests.HTTPError:
        status = response.status_code
        try:
            message = response.json()
        except requests.exceptions.JSONDecodeError:
            message = response.text
        match status:
            case 400:
                raise requests.HTTPError(f"400: Bad request, {message}.")
            case 404:
                raise requests.HTTPError(
                    f"404: Cannot find the given endpoint, {message}."
                )
            case 403:
                raise requests.HTTPError(
                    f"403: You do not have permissions to perform this action, {message}"
                )
            case 500:
                raise requests.HTTPError(f"500: Internal server error, {message}")
            case _:
                pass
