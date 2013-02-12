## [IronMQ](http://iron.io/mq) broker and [IronCache](http://iron.io/cache) result store for [Celery](http://celeryproject.org/)

- Cloud message queue and caching services
- No servers
- No maintenance
- Scales effortlessly

Installation
============

Note: We recommend using [virtualenv](http://www.virtualenv.org/) to avoid any dependency issues.

For IronMQ support, you'll need the [iron_celery](http://github.com/iron-io/iron_celery) library:

.. code-block:: bash

    $ pip install iron_celery

As well as an [Iron.io account](http://www.iron.io). Sign up for free at [iron.io](http://www.iron.io).

.. _broker-ironmq-configuration:

Configuration
=============

First, you'll need to import the iron_celery library right after you import Celery, for example:

    from celery import Celery
    import iron_celery

    celery = Celery('mytasks', broker='ironmq://', backend='ironcache://')

To use IronMQ, the broker URL should be in this format:

    BROKER_URL = 'ironmq://ABCDEFGHIJKLMNOPQRST:ZYXK7NiynGlTogH8Nj+P9nlE73sq3@'

where the URL format is:

    ironmq://project_id:token@

The project_id and token are for your Iron.io account, you can find these in the [Iron.io HUD](http://hud.iron.io).
You must *remember to include the "@" at the end*.

The login credentials can also be set using the environment variables
:envvar:`IRON_TOKEN` and :envvar:`IRON_PROJECT_ID`, which are set automatically if you use the IronMQ Heroku add-on.
And in this case the broker url may only be:

    ironmq://

Clouds
-----

The default cloud/region is `AWS us-east-1`. You can choose the IronMQ Rackspace cloud by changing the URL to::

    ironmq://project_id:token@mq-rackspace-dfw.iron.io

Results
======

You can store results in IronCache with the same Iron.io credentials, just set the results URL with the same syntax
as the broker URL, but changing the start to `ironcache`:

    ironcache:://project_id:token@

This will default to a cache named "Celery", if you want to change that:

    ironcache:://project_id:token@/awesomecache

Django - Using iron_celery with [Django](https://www.djangoproject.com/)
======

Setup celery with Django as you [normally would](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html),
but add `import iron_celery` and set the BROKER_URL to the URL's above. For example, at the top of your Django `settings.py` file:

```python
# NOTE: these must go before djcelery.setup_loader() line
BROKER_URL = 'ironmq://project_id:token@'
CELERY_RESULT_BACKEND = 'ironcache://project_id:token@'

import djcelery
import iron_celery
from celerytest.tasks import add

djcelery.setup_loader()
```

You can test it by going through the [First Steps with Django](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html)
guide in the Celery documentation.
