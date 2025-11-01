import json
import os

import click as click

from erica.worker.pyeric.pyeric_controller import GetTaxOfficesPyericController
from erica.worker.pyeric.eric_errors import EricGlobalError, EricNullReturnedError

_STATIC_FOLDER = "erica/api/static"
_TAX_OFFICES_JSON_FILE_NAME = _STATIC_FOLDER + "/tax_offices.json"


@click.group()
def cli():
    pass


@cli.command()
def create():
    print(f"Creating Json File under {_TAX_OFFICES_JSON_FILE_NAME}")
    try:
        tax_office_list = GetTaxOfficesPyericController().get_eric_response()
    except (EricNullReturnedError, EricGlobalError) as error:
        click.secho(
            f"Skipping tax office list regeneration due to ERiC error: {error}",
            fg="yellow",
            err=True,
        )
        if os.path.exists(_TAX_OFFICES_JSON_FILE_NAME):
            click.echo(
                "Existing tax_offices.json found; keeping current data.",
                err=True,
            )
            return
        raise

    with open(_TAX_OFFICES_JSON_FILE_NAME, 'w') as tax_offices_file:
        json.dump(tax_office_list, tax_offices_file, ensure_ascii=False)


if __name__ == "__main__":
    cli()
