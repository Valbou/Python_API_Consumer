
# Project Improvements

### API
- [ ] Change API.async_req() to permit to add more requests to executor with a pending status of queries flushed on demand
- [ ] Update API.get_list() to permit to override paginator querystring names
- [ ] Update API._gen_url() to permit to add an URL formatter object to get more flexibility

### Model
- [ ] In Model.__init__(), add config to permit auto composition from attribute name, ex: "object_id" add an "object" attribute that contain an Object(Model) instance
- [ ] In Model.is_up_to_date(), manage lists, and lists of id / instances (M2M & O2M)
