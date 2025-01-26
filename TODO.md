
# Project development

The project has just one benevolent dev, and not full free time in this project.
Send issues and pull requests according to your needs, to help me to make it even better.

## New Features
- [ ] Add file support, to download or send a file from external API
- [ ] Take in charge composition (objects in object) using a special field in Model like ORM do (myobject_id: str and myobject: Object).
- [ ] Add an URL Formatter to provide some adjustments about API urls (rarely consistent...)
- [ ] Override pagination behavior and querystring names (based on DRF)
- [ ] Change API.async_req() to add more requests to executor with a pending status of queries flushed on demand
- [ ] Manage lists, and lists of id / instances (M2M & O2M) in Model.is_up_to_date()
