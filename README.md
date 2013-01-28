## An [IronMQ](http://www.iron.io) transport for Celery

- Cloud message queue service
- No servers
- No maintenance
- Scales effortlessly
- Get 10M requests/month absolutely free


## How to use

1. `pip install iron_celery`
2. In the place (tasks file) you have `from celery import Celery` add `import iron_celery`
3. Use broker url `ironmq://` (in this case configuration from iron.json will be used) or `ironmq://project_id:token@` (notice trailing @). For Rackspace use `ironmq://mq-rackspace-dfw.iron.io` or `ironmq://project_id:token@mq-rackspace-dfw.iron.io`.
