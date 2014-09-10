from distutils.core import setup

setup(
    name = "iron-celery-v3",
    packages = ["iron_celery"],
    install_requires = ["iron-mq-v3", "iron_cache", "celery"],
    version = "0.4.1",
    description = "IronMQ transport and IronCache backend for Celery",
    author = "Iron.io",
    author_email = "info@iron.io",
    url = "https://github.com/iron-io/iron_celery/tree/v3"
)
