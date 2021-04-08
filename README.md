# DRF_API_Consumer
Django REST Framework API Consumer

This basic API consumer was originally created to easily consume a Django REST Framework API from a PyQT application on a Raspberry Pi.

To use it :

# GET Retrieve
```py
class User(Model):
  pass

user = User(url="https://example.org/api", token="")

# GET https://example.org/api/user/5?token=&format=json and hydrate instance
user.from_db(id=5)

# Give you the first name of this user id 5
print(user.first_name)
```

# GET List
```py
class PublicQuestion(Model):
  item = "question"

question = PublicQuestion(*user.args_api)
limit = 10

# GET https://example.org/api/question/?limit=10&token=&format=json and create 10 hydrated instances
top_questions = question.from_query(
  options=['limit={}'.format(limit)],
  limit=limit,
  classe=PublicQuestion
  )
# The use of limit=limit parameter is used to add instances beyond the DRF page_size configuration.
# top_question is a list of 10 instances of PublicQuestion class
```

# PUT/PATCH update
```py
user.fisrt_name = "Alice"
user.save()
```

# POST Create
```py
account = User(*question.args_api)
account.fisrt_name = "Bob"
account.email = "bob@example.org"
account.save()
```

# DELETE Destroy
```py
account.delete()
```

Unit tests are coming soon...
