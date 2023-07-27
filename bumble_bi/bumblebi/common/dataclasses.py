from dataclasses import dataclass

from bumblebi.common.enums import ColumnTypes


@dataclass(eq=False, order=False, frozen=True)
class CsvColumn:
    name: str
    type: ColumnTypes = ColumnTypes.STRING
