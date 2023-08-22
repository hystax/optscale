from dataclasses import dataclass

from bi_exporter.bumblebi.common.enums import ColumnTypes


@dataclass(eq=False, order=False, frozen=True)
class CsvColumn:
    name: str
    type: ColumnTypes = ColumnTypes.STRING
