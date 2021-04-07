# DRF_API_Consumer
Django REST Framework API Consumer

This basic API consumer was originally created to easily consume a Django REST Framework API from a PyQT application on a Raspberry Pi.

To use it :
```py
class User:
  pass

user = User(url="https://example.org/api", token="")
user.from_db(id=5) # GET https://example.org/api/user/5 and hydrate instance
print(user.first_name) # Give you the first name of this user id 5
```

Unit tests are coming soon...
