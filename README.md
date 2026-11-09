# Zortrax M300 Dual — hardware reverse engineering and Klipper research

Independent research project for **Zortrax M300 Dual**. Not the classic M300 Klipper project.

## Hardware identified from photographs

| Subsystem | Observation |
| --- | --- |
| Motion-control board | **Zortrax Dual Motherboard V3.4**, PCB silkscreen **2019/04/02** |
| Motion-control MCU | STM32F2 family, SWD Device ID `0x411`; exact chip marking not reliably legible in the photos |
| Factory MCU protection | RDP **Level 1**, verified via STM32F2 `FLASH_OPTCR=0x0FFF00ED` (RDP field `0x00`); stock Flash read via ST-Link fails |
| STM32 debugging | STLINK-V3SET and 3.3 V SWD connection established; SRAM/registers readable, stock Flash not readable |
| STM32 diagnostics | Debug serial output at **115200, 8N1**, including `Initializing zos...` and `[zcmd]` messages |
| Android / user-interface board | Zortrax PCB **Rev. 2.1**, A33-Core3 module with Allwinner A33 and Toshiba eMMC |
| Android recovery | eXdroid 4 recovery UI observed; `Home` button on Android board enters recovery mode |
| Android debug | `J5 UART0` with TX/RX markings; `P3` is a separate inter-board MCU interface |
| USB/power daughterboards | Photographed and identified, including M200P_Power Button Rev 1.3 and USB board Rev 4.0 |

## Important precautions

- **Never switch RDP Level 1 to Level 0 in order to read the original MCU firmware.** On STM32F2 the transition performs a mass erase.
- The Android eMMC has not been dumped in this project. No proprietary firmware binaries or secrets are distributed here.
- Exact UART pin directions and signal voltages must be verified before wiring test equipment.

## Photo archive

See [`hardware/photos/`](hardware/photos/) for the photo archive, contact sheet and hardware notes.

The first 21 photographs are available as PNG images in a downloadable ZIP. A further 27 original photographs were supplied in two batches (IMG_8997–IMG_9024, excluding IMG_9000), but must be verified as files before publishing a complete 48-photo archive.

## Goals

1. Preserve the hardware documentation and identify MCU, Android, inter-board connectors and signals.
2. Investigate the manufacturer update format `update.zar2`, and recover the stock update mechanism from the Android side without destroying the protected MCU firmware.
3. Port Klipper to M300 Dual, leveraging previously recovered knowledge from Zortrax Inventure (motion, thermal management and endstops).
4. Compare engineering notes with [zharijs/zmxxxp-re](https://github.com/zharijs/zmxxxp-re).

Research and photos contributed by Marcin Kowalik.
