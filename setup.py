from distutils.core import setup

setup(
    name = "iron_celery",
    packages = ["iron_celery"],
    install_requires = ["iron_mq", "iron_cache", "celery"],
    version = "0.4.0",
    description = "IronMQ transport and IronCache backend for Celery",
    author = "Iron.io",
    author_email = "info@iron.io",
    url = "https://github.com/iron-io/iron_celery"
)
