from inspect import getmembers, ismethod
from typing import Tuple, Type, TypeVar, Any, Optional

from .api import Api
from .exceptions import ModelConsumerException


T = TypeVar("T", bound="Model")


class Model(Api):
    _item = None
    id = 0

    def __new__(cls, url: str, item: str = "", verbose: bool = False):
        if cls._item is None:
            cls._item = cls.__name__.lower()

        if item:
            cls._item = item

        return super().__new__(cls)

    def __init__(self, url: str, item: str = "", verbose: bool = False):
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
        dictionary = {}
        for member in getmembers(self):
            if self._is_public_attribute(member):
                dictionary[member[0]] = member[1]
            elif self._is_object(member):
                dictionary[member[0]] = member[1].id
        return dictionary

    def get_url(self):
        return self._url

    def save(self, log: bool = False) -> dict:
        """CREATE - Save the instance in the API"""
        if self.id == 0:
            response = self.post_instance(self._item, payload=self._build_dictionary())
        else:
            response = self.update()

        if response:
            self.from_json(response)

        if log:
            self.log()
        return response

    def from_db(self, id_instance: int = 0) -> bool:
        """READ - Load the instance from the API"""
        if not id_instance and not self.id:
            raise ModelConsumerException(f"ID required for item {self._item}")
        elif not id_instance:
            id_instance = self.id

        datas = self.get_instance(self._item, id_instance)
        if not datas:
            raise ModelConsumerException(
                f"Error retriving item {self._item}({id_instance}) from API"
            )
        return self.from_json(datas)

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

        item = self._define_item(model_class)
        items: list = self._paginated_results(item, limit, options)

        if model_class and items:
            if limit == 1:
                return self.factory(model_class, items[0])
            else:
                return self.factory_list(model_class, items)
        else:
            return items

    def from_json(self, datas: dict):
        """Load an instance from a dict"""
        for k, v in datas.items():
            self.__setattr__(k, self.auto_typing(k, v))
        return self.control(datas)

    def auto_typing(self, key: str, value: Any) -> Any:
        """Convert to a type defined in class Model attribute if exist"""
        try:
            return type(getattr(self, key))(value)
        except Exception:
            return value

    def factory(self, model_class, dictionary: dict):
        """Return a new instance of the same type with attributes in dictionary"""
        if not issubclass(model_class, Model):
            raise ModelConsumerException(
                "The class supplied to the factory must be a "
                f"Model type class (inheritance) and not a {type(model_class)}"
            )

        instance = model_class(self._url) if model_class else self.__class__(self._url)
        instance.from_json(dictionary)
        return instance

    def factory_list(self, model_class, dict_list: list):
        """
        Convert a list of dict to a list of instance
        Class must be an uninstantiated class and not a class name
        ex: class = Model
        """
        if not issubclass(model_class, Model):
            raise ModelConsumerException(
                "The class supplied to the factory must be a "
                f"Model type class (inheritance) and not a {type(model_class)}"
            )

        instances_list = []
        for e in dict_list:
            instance = model_class(self._url)
            instance.from_json(e)
            instances_list.append(instance)
        return instances_list

    def update(self):
        """UPDATE - Update instance from API"""
        return self.patch_instance(self._item, payload=self._build_dictionary())

    def delete(self):
        """ " DELETE - Delete instance in the API"""
        return self.delete_instance(self._item, payload={"id": self.id})

    def control(self, dictionary: dict):
        """Control datas"""
        # TODO: Manage lists and lists of id / instances (M2M & O2M)
        for k, _ in dictionary.items():
            if not getattr(self, k) == dictionary[k]:
                return False
            elif (
                self._is_object((0, getattr(self, k)))
                and not getattr(self, k).id == dictionary[k]
            ):
                return False
        return True

    def id_to_object(self, attribute: str, instance):
        """Composition from ids"""
        id_instance = getattr(self, attribute)
        if isinstance(id_instance, int) and isinstance(instance, Model):
            self.__setattr__(attribute, instance.from_db(id_instance))
        else:
            raise ModelConsumerException(
                f"Convert id to instance (attribute {attribute})"
                f" impossible in {self._item}"
            )

    def object_to_id(self, attribute: str):
        """Decomposition from instance"""
        instance = getattr(self, attribute)
        if isinstance(instance, Model):
            self.__setattr__(attribute, instance.id)
        else:
            raise ModelConsumerException(
                f"Convert id to instance (attribute {attribute})"
                f" impossible in {self._item}"
            )

    def log(self):
        # TODO: use logging instead of this
        import json
        from datetime import date

        try:
            fichier = f"logs/{date.today()}-{self._item}.log"
            with open(fichier, "a+") as f:
                f.write(json.dumps(self._build_dictionary()))
        except ModelConsumerException as e:
            print("Model.log Exception :", e)
