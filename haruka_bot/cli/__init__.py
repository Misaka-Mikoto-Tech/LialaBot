import click

from .utils import create_env
from .custom_event import GroupMessageSentEvent


@click.group()
def main():
    pass


@click.command()
def run():
    create_env()
    from .bot import run

    run()


main.add_command(run)
