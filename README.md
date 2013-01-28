## An [IronMQ](http://www.iron.io) transport for Celery

- Cloud message queue service
- No servers
- No maintenance
- Scales effortlessly
- Get 10M requests/month absolutely free


## How to use

1. `pip install iron_celery`
2. in the place (tasks file) you have `from celery import Celery` add `import iron_celery`
3. use broker url `ironmq://`
