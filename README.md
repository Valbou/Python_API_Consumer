# DRF_API_Consumer
Django REST Framework API Consumer

![License LGPLv3](https://img.shields.io/badge/license-LGPLv3-blue "License LGPLv3")
![Python v3.7](https://img.shields.io/badge/python-v3.7-blue "Python v3.7")

This API consumer was originally created to easily consume a Django REST Framework API from a PyQT application on a Raspberry Pi.
This, with the goal to achieve this in a similar way to Django ORM use.

## Dependencies
* asyncio
* requests
* functools
* inspect

## Get started:

### GET Retrieve
```py
class User(Model):
  pass

user = User(url="https://example.org/api/user")

# GET https://example.org/api/user/5?format=json and hydrate instance
user.from_db(id=5)

# Give you the first name of this user id 5
print(user.first_name)
```

### GET List
```py
class Foo(Model):
  item = "bar"

foo = Foo("ttps://example.org/api/bar")
limit = 10

# GET https://example.org/api/bar?format=json&limit=10 and create 10 hydrated instances of Foo from api/bar/
many_foo = foo.from_query(
  options=[f"limit={limit}"],
  limit=limit,
  model_class=Foo
  )
# The use of limit=limit parameter is used to add instances beyond the DRF page_size configuration.
# model_class=Foo is optional because foo is an instance of Foo
# many_foo is a list of 10 instances of Foo class
```

### PUT/PATCH update
```py
user.fisrt_name = "Alice"
user.save()
```

### POST Create
```py
account = User("https://example.org/api/user")
account.fisrt_name = "Bob"
account.email = "bob@example.org"
account.save()
```

### DELETE Destroy
```py
account.delete()
```

You need any development, please create an issue or submit a pull request :)
Enjoy !
