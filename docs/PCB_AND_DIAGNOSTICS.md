# Zortrax M300 Dual — PCB identification and diagnostic notes

## Motion-control motherboard

- Photos show **Dual Motherboard V3.4**, PCB date **2019/04/02**.
- STM32 SWD device ID reported by STM32CubeProgrammer: **0x411** (STM32F2 family).
- Measured/debug supply voltage approximately **3.31–3.32 V**.
- STLINK-V3SET over SWD is usable at 200 kHz and 8 MHz for identification, Option Bytes and peripheral/SRAM readout.
- Factory protection: `FLASH_OPTCR` read at `0x40023C14`: **`0x0FFF00ED`**, RDP byte `0x00` => **RDP Level 1**.
- STM32 Flash read at `0x08000000` fails even for 4-byte reads. **Do not perform Read Unprotect / RDP1→RDP0** (mass erase).
- The MCU outputs factory diagnostic logs on the debug UART at **115200, 8N1**. Observed startup and command entries:

```text
Initializing zos...
Reset caused by power on power down
Reset caused by external reset pin
Procedures task created!
Failsafe loop. Source : 15, Reason : 8, Locked : false, Message : Extruder not connected.
[zcmd] executing COMMAND_GUI_INIT (23), active: COMMAND_NONE (0)
[zcmd] Tried to execute command, but we're in failsafe!
[zcmd] executing COMMAND_REQUIRE_MODEL_SYNC (32), active: COMMAND_NONE (0)
```

The debug log also showed `[Nozzle z offset] init`, signal tower modes, homing procedure entries, and HOTEND API pointer warnings. These logs reflect the observed bench-test configuration; they are **not** proof of any interactive firmware-export command.

## Android and display electronics

- White PCB marked **Zortrax Rev. 2.1**, and date **2019-05-30**.
- System-on-module: **Allwinner A33 (A33-Core3)**, **AXP223** PMIC, Toshiba eMMC chip marked **THGBMFG6C1LBAIL** (nominal 8 GB).
- `J5` labeled `UART0`, two signal pins `RX` and `TX`; ground must be supplied separately from a verified common ground.
- `P3` is a separate 10-way inter-board connection to the MCU and carries UART, reset/sleep and other signals; it **is not** the Android UART0 console.
- `Home` button enters the observed eXdroid4 Android Recovery UI when used during boot. Recovery showed `apply update from ADB`, but sideload does **not** imply read access to eMMC.
- USB0/OTG/FEL is a potential avenue for *read-only* system backup, but board-specific pinout and voltage must be confirmed; no FEL dump has been achieved.
- Original Android UI reported errors including `Cannot connect to motherboard`; diagnostics should distinguish physical P3 communication from MCU failsafe caused by a disconnected extruder.

## Objective

Recover the Android updater application/libraries, determine how `update.zar2` is unpacked, and locate the encrypted or signed STM32 update. Preservation of factory MCU Flash and the original eMMC is mandatory. No flashing or destructive protection changes.

## Related public research

- [zharijs/zmxxxp-re](https://github.com/zharijs/zmxxxp-re) — Zortrax Plus hardware research.
- [mandraga/klipper4m200](https://github.com/mandraga/klipper4m200) — related A33-Core3 board, UART0 J5 and eMMC research; **not** a guaranteed pin-for-pin equivalent of M300 Dual.

All facts above are based on the supplied board photographs, CubeProgrammer logs and reported bench diagnostics, unless linked to a separate public research project.
