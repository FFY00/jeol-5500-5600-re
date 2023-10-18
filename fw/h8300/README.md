# H8/300 firmware

## Entrypoint

- Vector table: 0x0000
- Entrypoint Address: 0x0000 - 0x0001

Entrypoints:
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
