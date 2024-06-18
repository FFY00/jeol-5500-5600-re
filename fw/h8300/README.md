# H8/300 firmware

## Memory layout

### Modes

#### Mode 1

- Name: Expanded mode without on-chip ROM

| Name                   | Start Address | End Address | Size |
| ---------------------- | ------------- | ----------- | ---- |
| Vector table           | `0x0000`      | `0x0059`    | 89B  |
| External address space | `0x005A`      | `0xEF7F`    | 60kB |
| On-chip RAM            | `0xEF80`      | `0xFF7F`    | 4kB  |
| External address space | `0xFF80`      | `0xFF87`    | 7B   |
| On-chip register field | `0xFF88`      | `0xFFFF`    | 120B |

#### Mode 2

- Name: Expanded mode with on-chip ROM

| Name                   | Start Address | End Address | Size |
| ---------------------- | ------------- | ----------- | ---- |
| Vector table           | `0x0000`      | `0x0059`    | 89B  |
| On-chip ROM            | `0x005A`      | `0xE77F`    | 58kB |
| External address space | `0xE780`      | `0xEF7F`    | 2kB  |
| On-chip RAM            | `0xEF80`      | `0xFF7F`    | 4kB  |
| External address space | `0xFF80`      | `0xFF87`    | 7B   |
| On-chip register field | `0xFF88`      | `0xFFFF`    | 120B |

##### Note

In this mode, external memory can be accessed at the "On-chip RAM" addresses
(`0xEF80` to `0xFF7F`) when the `RAME` bit in the system control register
(`SYSCR`) is cleared to `0`.

#### Mode 3

- Name: Single-chip mode

| Name                   | Start Address | End Address | Size |
| ---------------------- | ------------- | ----------- | ---- |
| Vector table           | `0x0000`      | `0x0059`    | 89B  |
| On-chip ROM            | `0x005A`      | `0xE77F`    | 60kB |
| On-chip RAM            | `0xEF80`      | `0xFF7F`    | 4kB  |
| *Unused*               | `0xFF80`      | `0xFF87`    | 7B   |
| On-chip register field | `0xFF88`      | `0xFFFF`    | 120B |

### Vector table

- Entry (vector) size: 2B (word)
- Entries:
  - `0x0000`: reset (entrypoint)
  - `0x0006`: NMI
  - `0x0008`: IRQ0
  - `0x000A`: IRQ1
  - `0x000C`: IRQ2
  - `0x000E`: IRQ3
  - `0x0010`: IRQ4
  - `0x0012`: IRQ5
  - `0x0014`: IRQ6
  - `0x0016`: IRQ7

  (16-bit free-running timer 0)
  - `0x0018`: ICIA0 (interrupt capture A)
  - `0x001A`: ICIB0 (interrupt capture B)
  - `0x001C`: ICIC0 (interrupt capture C)
  - `0x001E`: ICID0 (interrupt capture D)
  - `0x0020`: OCIA0 (output compare A)
  - `0x0022`: OCIB0 (output compare B)
  - `0x0024`: FOVI0 (overflow)

  (16-bit free-running timer 1)
  - `0x0026`: ICI1 (input capture)
  - `0x0028`: OCIA1 (output compare A)
  - `0x002A`: OCIB1 (output compare B)
  - `0x002C`: FOVI1 (overflow)

  (8-bit timer 0)
  - `0x002E`: CMI0A (compare match A)
  - `0x0030`: CMI0B (compare match B)
  - `0x0032`: OVI0 (overflow)

  (8-bit timer 1)
  - `0x0034`: CMI1A (compare match A)
  - `0x0036`: CMI1B (compare match B)
  - `0x0038`: OVI1 (overflow)

  (Serial communication interface 0)
  - `0x003A`: ERI0 (receive error)
  - `0x003C`: RXI0 (receive end)
  - `0x003E`: TXI0 (TDR empty)
  - `0x0040`: TEI0 (TSR empty)

  (Serial communication interface 1)
  - `0x0042`: ERI1 (receive error)
  - `0x0044`: RXI1 (receive end)
  - `0x0046`: TXI1 (TDR empty)
  - `0x0048`: TEI1 (TSR empty)

  (A/D converter)
  - `0x004A`: ADI (conversion end)

  (Data transfer unit)
  - `0x004C`: MWEI (write end)
  - `0x004E`: MREI (read end)
  - `0x0050`: DTIA (transfer end A)
  - `0x0052`: DTIB (transfer end B)
  - `0x0054`: DTIC (transfer end C)
  - `0x0056`: CMPI (overrun error)

  (Watchdog timer)
  - `0x0058`: OVF (watchdog overflow)


#### Entrypoints

- EOS V1.34: 0x0166
- EVAC V2.07: 0x015E
- HT V1.21: 0x01EC
- LV V1.07: 0x0114

## ABI

There are a couple available toolchains with different ABIs:

- [Renessas](https://www.renesas.com/us/en/software-tool/cc-compiler-package-h8sx-h8s-h8-family)
- [GCC up to 3.4](https://gcc.gnu.org/projects/h8300-abi.html)
- [GCC 4.0 and later](https://gcc.gnu.org/projects/h8300-abi.html)

We can rule out GCC 4.0, as version 4.0.0 was only released in 2005, and the SEM
is older. The viable options are the Renessas/Hitachi toolchain or GCC up to 3.4,
but the vendor toolchain seems more likely.
