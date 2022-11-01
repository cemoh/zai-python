from typing import Any, AnyStr
import requests
import resources


TEST_TOKEN_ENDPOINT = 'https://au-0000.sandbox.auth.assemblypay.com/tokens'
TEST_ENDPOINT = "https://test.api.promisepay.com/"


class ZaiTooManyRetriesException(Exception): 
    def __init__(self):
        message = "Too many retries"
        super().__init__(message)


class ZaiClient:
    access_token: str|None = None
    _max_retries: int = 3
    _retries: int = 0

    
    def __init__(self, client_id: str, client_secret: str, scope: str, token_endpoint: str = None, endpoint: str = None) -> None:
        self._client_id: str = client_id
        self._client_secret: str = client_secret 
        self._scope: str = scope
        self._token_endpoint = token_endpoint or TEST_TOKEN_ENDPOINT
        self._endpoint = endpoint or TEST_ENDPOINT
       
        self.companies = resources.Companies(self)
        self.users = resources.Users(self)

    def get_access_token(self) -> str:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self._scope
        }
        
        response = self._post(self._token_endpoint, json=payload)
        self.access_token = response.json().get('access_token')
        
        return self.access_token
       
    def get_headers(self) -> dict[str, str]:
        headers =  {
            "accept": "application/json",
            "content-type": "application/json"
        }
 
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            
        return headers

    def request(self, method, url, **kwargs) -> requests.Response:
        response = requests.request(method, url, headers=self.get_headers(), **kwargs)
 
        if self._retries > self._max_retries:
            raise ZaiTooManyRetriesException()

        if response.status_code == 401:
            self._retries += 1
            self.get_access_token()
            response = self.request(method, url, **kwargs)

        return response

    def _get(self, url: str) -> requests.Response:
        return self.request('GET', url)

    def _delete(self, url: str) -> requests.Response:
        return self.request('DELETE', url)

    def _post(self, url: str, json: dict) -> requests.Response:
        return self.request('POST', url, json=json)

    def _patch(self, url: str, json: dict) -> requests.Response:
        return self.request('PATCH', url, json=json)

    def get(self, path: str) -> requests.Response:
        url = self._endpoint + path
        return self._get(url)

    def delete(self, path: str) -> requests.Response:
        url = self._endpoint + path
        return self._delete(url)

    def post(self, path: str, json: dict) -> requests.Response:
        url = self._endpoint + path
        return self._post(url, json=json)

    def patch(self, path: str, json: dict) -> requests.Response:
        url = self._endpoint + path
        return self._patch(url, json=json)
