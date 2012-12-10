from distutils.core import setup

setup(
    name = "iron_mq_celery",
    packages = ["iron_mq_celery"],
    install_requires = ["iron_mq", "celery"],
    version = "0.0.1",
    description = "IronMQ transport for Celery",
    author = "Iron.io",
    author_email = "info@iron.io",
    url = "https://github.com/iron-io/iron_mq_python_celery"
)
