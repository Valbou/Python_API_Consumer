from inspect import getmembers, ismethod

from .api import Api
from .exceptions import ModelConsumerException


class Model(Api):
    item = None
    id = 0

    def __init__(self, url, verbose=False):
        self.__class__.item = self.__class__.__name__.lower()
        self.config(url, verbose=verbose)
        if not self.item:
            raise ModelConsumerException(
                "Item undefined in model {}".format(self.__class__)
            )

    def _is_public_attribute(self, member):
        return (
            not ismethod(member[1])
            and not isinstance(member[1], Model)
            and member[0][0] != "_"
        )

    def _is_object(self, member):
        return isinstance(member[1], Model)

    def _build_dictionary(self):
        dictionary = {}
        for member in getmembers(self):
            if self._is_public_attribute(member):
                dictionary[member[0]] = member[1]
            elif self._is_object(member):
                dictionary[member[0]] = member[1].id
        return dictionary

    @property
    def args_api(self):
        return self.url

    def save(self, log=False):
        """CREATE - Save the instance in the API"""
        if self.id == 0:
            response = self.post_instance(self.item, payload=self._build_dictionary())
            if response:
                self.from_json(response)
        else:
            response = self.update()
        if log:
            self.log()
        return response

    def from_db(self, id_instance: int = 0):
        """READ - Load the instance from the API"""
        if not id_instance and not self.id:
            raise ModelConsumerException("ID required for item {}".format(self.item))
        elif not id_instance:
            id_instance = self.id

        datas = self.get_instance(self.item, id_instance)
        if not datas:
            raise ModelConsumerException(
                "Error retriving item {}({}) from API".format(self.item, id_instance)
            )
        return self.from_json(datas)

    def from_query(self, options=[], limit=0, model_class=None):
        """Return a list of dict items or an instance list of items if a class is specified"""
        if model_class:
            item = model_class.item
            if not item:
                item = model_class.__name__.lower()
        else:
            item = self.item

        if not item:
            raise ModelConsumerException(
                "### Error", model_class.__name__, "no item defined ->", item
            )

        items = []
        if limit:
            items = self.get_list(item, options=options)
            while self.next and len(items) < limit:
                items += self.get_list(item, page="next")
            items = items[:limit]
        else:
            items = self.get_list(item, options=options)

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

    def auto_typing(self, key, value):
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

        instance = (
            model_class(*self.args_api)
            if model_class
            else self.__class__(*self.args_api)
        )
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
            instance = model_class(*self.args_api)
            instance.from_json(e)
            instances_list.append(instance)
        return instances_list

    def update(self):
        """UPDATE - Update instance from API"""
        return self.patch_instance(self.item, payload=self._build_dictionary())

    def delete(self):
        """ " DELETE - Delete instance in the API"""
        return self.delete_instance(self.item, payload={"id": self.id})

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
        id = getattr(self, attribute)
        if isinstance(id, int) and isinstance(instance, Model):
            self.__setattr__(attribute, instance.from_db(id))
        else:
            raise ModelConsumerException(
                "Convert id to instance (attribute {}) impossible in {}".format(
                    attribute, self.item
                )
            )

    def object_to_id(self, attribute: str):
        """Decomposition from instance"""
        instance = getattr(self, attribute)
        if isinstance(instance, Model):
            self.__setattr__(attribute, instance.id)
        else:
            raise ModelConsumerException(
                "Convert id to instance (attribute {}) impossible in {}".format(
                    attribute, self.item
                )
            )

    def log(self):
        import json
        from datetime import date

        try:
            fichier = "logs/{}-{}.log".format(date.today(), self.item)
            with open(fichier, "a+") as f:
                f.write(json.dumps(self._build_dictionary()))
        except ModelConsumerException as e:
            print("Model.log Exception :", e)
