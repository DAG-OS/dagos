import typing as t
from io import StringIO
from pathlib import Path

import yamale
from loguru import logger

from dagos.exceptions import DagosException, ValidationException


class Validator:

    schema_dir = Path(__file__).parent / "schemas"
    schemas = {
        "configuration": schema_dir / "configuration.schema.yml",
        "environment": schema_dir / "environment.schema.yml",
    }

    def validate_configuration(self, path: Path) -> t.Dict:
        return self._validate_with_schema("configuration", path)

    def validate_environment(self, path: Path) -> t.Dict:
        return self._validate_with_schema("environment", path)

    def _validate_with_schema(self, schema_key: str, path: Path) -> t.Dict:
        if not path.exists():
            raise ValidationException(f"The file '{path}' does not exist!")
        if not path.is_file():
            raise ValidationException(
                f"Unable to validate path '{path}'. Expected a file!"
            )
        try:
            data = yamale.make_data(path)
        except Exception as e:
            raise ValidationException(f"Unable to parse '{path}'", e)

        schema = yamale.make_schema(self.schemas[schema_key])

        try:
            yamale.validate(schema, data)
        except yamale.YamaleError as e:
            errors = StringIO()
            for result in e.results:
                errors.writelines([f"{x}\n\t" for x in result.errors])
            raise ValidationException(
                f"The {schema_key} at '{path}' is invalid:\n\t{errors.getvalue()}"
            )

        logger.trace("The {} at '{}' is valid", schema_key, path)
        return data[0][0]
