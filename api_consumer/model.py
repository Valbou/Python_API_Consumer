import logging
from inspect import getmembers, ismethod
from typing import Any, List, Optional, Tuple, Type, TypeVar, Union

from .api import Api
from .exceptions import ModelConsumerException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound="Model")


class Model(Api):
    _item = None
    id = 0

    def __new__(cls, url: str, item: str = "", verbose: bool = False):
        if not item or cls._item is None:
            cls._item = item or cls.__name__.lower()

        return super().__new__(cls)

    def __init__(self, url: str, item: str = "", verbose: bool = False):
        # TODO: add config to permit auto composition from attribute name
        # ex: object_id add a object attribute that contain an Object(Model) instance
        self.config(url, verbose=verbose)

    def _is_public_attribute(self, member: Tuple[str, any]) -> bool:
        return (
            not ismethod(member[1])
            and not isinstance(member[1], Model)
            and member[0][0] != "_"
        )

    def _is_object(self, member: Tuple[str, any]) -> bool:
        return isinstance(member[1], Model)

    def _build_dictionary(self) -> dict:
        data = {}
        for member in getmembers(self):
            if self._is_public_attribute(member):
                data[member[0]] = member[1]
            elif self._is_object(member):
                data[member[0]] = member[1].id
        return data

    def get_url(self):
        return self._url

    def save(self) -> dict:
        """CREATE - Save the instance in the API"""
        if self.id == 0:
            response = self.post_instance(self._item, payload=self._build_dictionary())
            self.from_json(response)
        else:
            response = self.update()
        return response

    def get(self, id_instance: Optional[Union[int, str]] = None) -> bool:
        """READ - Load the instance from the API"""
        if not id_instance and not self.id:
            err = f"ID required for item {self._item}"
            logger.error(err)
            raise ModelConsumerException(err)
        elif not id_instance:
            id_instance = self.id

        data = self.get_instance(self._item, id_instance)
        if not data:
            err = f"Error retriving item {self._item}({id_instance}) from API"
            logger.error(err)
            raise ModelConsumerException(err)
        return self.from_json(data)

    def _paginated_results(self, item: str, limit: int, options: list) -> list:
        """Build a list with the expected number of elements"""
        items = []
        if limit:
            items = self.get_list(item, options=options)
            while self._next and len(items) < limit:
                items += self.get_list(item, page="next")
            items = items[:limit]
        else:
            items = self.get_list(item, options=options)
        return items

    def _define_item(self, model_class: Optional[Type[T]] = None):
        """We need an item set to continue"""
        if model_class:
            item = model_class._item or model_class.__name__.lower()
        else:
            item = self._item or self.__name__.lower()
        return item

    def from_query(
        self,
        options: list = None,
        limit: int = 0,
        model_class: Optional[Type[T]] = None,
    ):
        """Return a list of dict items or an instance list of items if a class is specified"""
        options = options or []

        model_class = self._check_model_class(model_class)
        item = self._define_item(model_class)
        items: list = self._paginated_results(item, limit, options)

        if model_class and items:
            if limit == 1:
                return self.factory(items[0], model_class)
            else:
                return self.factory_list(items, model_class)
        else:
            return items

    def from_json(self, data: dict):
        """Load an instance from a dict"""
        for k, v in data.items():
            self.__setattr__(k, self._auto_typing(k, v))
        return self.is_up_to_date(data)

    def _auto_typing(self, key: str, value: Any) -> Any:
        """Convert to a type defined in class Model attribute if exist"""
        try:
            # if self.__annotations__.get(key) in [int, float, str, bytes, list, tuple, set, dict]:
            #     return self.__annotations__.get(key)(value)
            return type(getattr(self, key))(value)
        except Exception:
            return value

    def _check_model_class(self, model_class: Optional[Type[T]] = None) -> Type[T]:
        if not model_class:
            model_class = self.__class__

        if not issubclass(model_class, Model):
            err = (
                "The class supplied to the factory must be a "
                f"Model type class (inheritance) and not a {type(model_class)}"
            )
            logger.error(err)
            raise ModelConsumerException(err)
        return model_class

    def factory(self, data: dict, model_class: Optional[Type[T]] = None):
        """Return a new instance of the same type with attributes in dictionary"""
        model_class = self._check_model_class(model_class)

        instance = model_class(self._url)
        instance.from_json(data)
        return instance

    def factory_list(
        self, data_list: list, model_class: Optional[Type[T]] = None
    ) -> List[Type[T]]:
        """
        Convert a list of dict to a list of instances
        Class must be an uninstantiated class and not a class name
        ex: class = Model
        """
        model_class = self._check_model_class(model_class)
        return [self.factory(data, model_class) for data in data_list]

    def update(self):
        """UPDATE - Update instance from API"""
        data = self.patch_instance(self._item, payload=self._build_dictionary())
        self.from_json(data)
        return data

    def delete(self):
        """ " DELETE - Delete instance in the API"""
        return self.delete_instance(self._item, payload={"id": self.id})

    def is_up_to_date(self, data: dict):
        """Control data is up to date"""
        # TODO: Manage lists and lists of id / instances (M2M & O2M)
        for k, _ in data.items():
            if getattr(self, k) != data[k] or (
                self._is_object((0, getattr(self, k)))
                and getattr(self, k).id != data[k]
            ):
                return False
        return True

    def id_to_object(self, attribute: str, instance: T):
        """Composition from ids"""
        id_instance = getattr(self, attribute)
        if isinstance(instance, Model):
            instance.get(id_instance)
            self.__setattr__(attribute, instance)
        else:
            err = (
                f"Convert id to instance (attribute {attribute})"
                f" impossible in {self._item}"
            )
            logger.error(err)
            raise ModelConsumerException(err)

    def object_to_id(self, attribute: str):
        """Decomposition from instance"""
        instance = getattr(self, attribute)
        if isinstance(instance, Model):
            self.__setattr__(attribute, instance.id)
        else:
            err = (
                f"Convert instance to id (attribute {attribute})"
                f" impossible in {self._item}"
            )
            logger.error(err)
            raise ModelConsumerException(err)
