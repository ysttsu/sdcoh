"""CLI entry point."""

import click


@click.group()
@click.version_option()
def cli() -> None:
    """sdcoh — Story Design Coherence."""
