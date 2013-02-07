## [IronMQ](http://iron.io/mq) transport and [IronCache](http://iron.io/cache) backend for Celery

- Cloud message queue and caching services
- No servers
- No maintenance
- Scales effortlessly

## How to use

1. `pip install iron_celery`
2. In the place (tasks file) you have `from celery import Celery` add `import iron_celery`
3. Use broker url `ironmq://` (in this case configuration from iron.json will be used) or `ironmq://project_id:token@` (notice trailing @). For Rackspace use `ironmq://mq-rackspace-dfw.iron.io` or `ironmq://project_id:token@mq-rackspace-dfw.iron.io`.
4. Use backend url `ironcache://` with the same syntax as broker url which also supports changing cache name (defaults to `Celery`) via appending `/cachename` to url (e.g. `ironcache:///coolcache` or `ironcache://project_id:token@/awesomecache`).
