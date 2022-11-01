
from urllib.parse import urlencode
import requests
from typing import Any


class ResourceMixin:

    @property
    def _base_path(self) -> str:
        raise NotImplementedError

    def path(self, id: Any|None=None, **parameters) -> str:
        path = f"{self._base_path}/{id}" if id else self._base_path
        return f"{path}?{urlencode(parameters)}" if parameters else path


class ListMixin(ResourceMixin):

    def list(self, **kwargs) -> requests.Response:
        return self.client.get(self.path(**kwargs))

    class Meta:
        abstract = True


class ShowMixin(ResourceMixin):

    def show(self, id: Any) -> requests.Response:
        return self.client.get(self.path(id=id))

    class Meta:
        abstract = True


class CreateMixin(ResourceMixin):

    def create(self, json: dict) -> requests.Response:
        return self.client.post(self.path(), json=json)

    class Meta:
        abstract = True


class UpdateMixin(ResourceMixin):

    def update(self, id: Any, json: dict) -> requests.Response:
        return self.client.patch(self.path(id=id), json=json)

    class Meta:
        abstract = True


class BaseResource(ResourceMixin):
   
    def __init__(self, client):
        self.client = client

    class Meta:
        abstract = True


class Users(BaseResource, ListMixin, CreateMixin, ShowMixin, UpdateMixin):
    _base_path = "users"

    def verify_prelive(self, user_id) -> requests.Response:
        path = f"{self.path(id=user_id)}/identity_verified" 
        return self.client.patch(path, json={})

    def show_wallet_accounts(self, user_id) -> requests.Response:
        path = f"{self.path(id=user_id)}/wallet_accounts" 
        return self.client.get(path)


class Companies(BaseResource, ListMixin, CreateMixin, ShowMixin, UpdateMixin):
    _base_path = "companies"

