import json
import pathlib

import binaryninja as bn
import binaryninja.architecture
import binaryninja.binaryview
import binaryninja.enums
import binaryninja.platform
import binaryninja.types


supported_mcus = [
    'HD6473308',
]
vector_table = {
    0x0000: ('reset', 'entrypoint'),
    #0x0002: ('reserved0', None),
    #0x0004: ('reserved0', None),
    0x0006: ('NMI', None),
    0x0008: ('IRQ0', None),
    0x000A: ('IRQ1', None),
    0x000C: ('IRQ2', None),
    0x000E: ('IRQ3', None),
    0x0010: ('IRQ4', None),
    0x0012: ('IRQ5', None),
    0x0014: ('IRQ6', None),
    0x0016: ('IRQ7', None),
    # 16-bit free-running timer 0
    0x0018: ('ICIA0', 'interrupt capture A'),
    0x001A: ('ICIB0', 'interrupt capture B'),
    0x001C: ('ICIC0', 'interrupt capture C'),
    0x001E: ('ICID0', 'interrupt capture D'),
    0x0020: ('OCIA0', 'output compare A'),
    0x0022: ('OCIB0', 'output compare B'),
    0x0024: ('FOVI0', 'overflow'),
    # 16-bit free-running timer 1
    0x0026: ('ICI1', 'input capture'),
    0x0028: ('OCIA1', 'output compare A'),
    0x002A: ('OCIB1', 'output compare B'),
    0x002C: ('FOVI1', 'overflow'),
    # 8-bit timer 0
    0x002E: ('CMI0A', 'compare match A'),
    0x0030: ('CMI0B', 'compare match B'),
    0x0032: ('OVI0', 'overflow'),
    # 8-bit timer 1
    0x0034: ('CMI1A', 'compare match A'),
    0x0036: ('CMI1B', 'compare match B'),
    0x0038: ('OVI1', 'overflow'),
    # Serial communication interface 0
    0x003A: ('ERI0', 'receive error'),
    0x003C: ('RXI0', 'receive end'),
    0x003E: ('TXI0', 'TDR empty'),
    0x0040: ('TEI0', 'TSR empty'),
    # Serial communication interface 1
    0x0042: ('ERI1', 'receive error'),
    0x0044: ('RXI1', 'receive end'),
    0x0046: ('TXI1', 'TDR empty'),
    0x0048: ('TEI1', 'TSR empty'),
    # A/D converter
    0x004A: ('ADI', 'conversion end'),
    # Data transfer unit
    0x004C: ('MWEI', 'write end'),
    0x004E: ('MREI', 'read end'),
    0x0050: ('DTIA', 'transfer end A'),
    0x0052: ('DTIB', 'transfer end B'),
    0x0054: ('DTIC', 'transfer end C'),
    0x0056: ('CMPI', 'overrun error'),
    # Watchdog timer
    0x0058: ('OVF', 'watchdog overflow'),
}
vector_sections = {
    (0x0000, 0x0016): None,
    (0x0018, 0x0024): '16-bit free-running timer 0',
    (0x0026, 0x002C): '16-bit free-running timer 1',
    (0x002E, 0x0032): '8-bit timer 0',
    (0x0034, 0x0038): '8-bit timer 1',
    (0x003A, 0x0040): 'Serial communication interface 0',
    (0x0042, 0x0048): 'Serial communication interface 1',
    (0x004A, 0x004A): 'A/D converter',
    (0x004C, 0x0056): 'Data transfer unit',
    (0x0058, 0x0058): 'Watchdog timer',
}
memory_sections = {
    # XXX: This is for mode 2 (Expanded mode with on-chip ROM).
    (0x0000, 0x0059): ('vector', bn.enums.SectionSemantics.ReadOnlyDataSectionSemantics),
    (0x005A, 0xE77F): ('ROM', bn.enums.SectionSemantics.ReadOnlyCodeSectionSemantics),
    (0xE780, 0xEF7F): ('external0', bn.enums.SectionSemantics.ExternalSectionSemantics),
    (0xEF80, 0xFF7F): ('RAM', bn.enums.SectionSemantics.ReadWriteDataSectionSemantics),
    (0xFF80, 0xFF87): ('external1', bn.enums.SectionSemantics.ExternalSectionSemantics),
    (0xFF88, 0xFFFF): ('registers', bn.enums.SectionSemantics.ReadWriteDataSectionSemantics),
}


def get_from_range_dict[T](value: int, range_dict: dict[tuple[int, int], T]) -> T | None:
    for addresses, dict_item in range_dict.items():
        start, end = addresses
        if start <= value <= end:
            return dict_item
    return None


class HD6473308View(bn.binaryview.BinaryView):
    name = 'HD6473308 (H8/330)'
    long_name = 'View for HD6473308 firmware (H8/300M, H8/330, H8/3318)'

    def __init__(self, data: bn.binaryview.BinaryView) -> None:
        super().__init__(parent_view=data, file_metadata=data.file, handle=data.handle)

        self.platform = bn.architecture.Architecture['H8/300'].standalone_platform
        self._annotate_vector_table()

    def _read_word(self, address: int) -> int:
        return int.from_bytes(self.read(address, 2), byteorder='big')

    def _annotate_vector_table(self) -> None:
        for addresses, info in memory_sections.items():
            start_address, end_address = addresses
            name, semantics = info
            self.add_auto_section(
                name=name,
                start=start_address,
                length=end_address - start_address + 1,
                semantics=semantics,
            )

        for address, info in vector_table.items():
            name, description = info

            section = get_from_range_dict(address, vector_sections)
            description = ' - '.join(filter(None, (section, description)))

            # define vector data
            self.define_data_var(address, 'uint16_t', f'v_{name.upper()}')
            if description:
                self.set_comment_at(address, description)

            # define vector functions
            function_address = self._read_word(address)
            if function_address != 0xFFFF:
                function = self.add_function(function_address)
                assert function
                function.name = f'f_{name}'
                function.set_comment_at(0, description)

        self.add_entry_point(self._read_word(0x0000))

    @classmethod
    def is_valid_for_data(self, data: bn.binaryview.BinaryView) -> bool:
        # XXX: Use the Binary Ninja settings instead.
        original_file = pathlib.Path(data.file.original_filename)
        config = original_file.parent / 'firmware.config.json'
        if config.is_file():
            config_data = json.loads(config.read_text())
            return config_data.get(original_file.name) in supported_mcus
        return False


HD6473308View.register()
