# STM32F2 RDP1 — odzyskiwanie fabrycznego firmware M300 Dual (2026-11-09)

## Co wykazano na oryginalnej płycie

- Dual Motherboard V3.4 (2019-04-02); MCU STM32F2, Device ID **0x411**.
- STLINK-V3SET: SRAM i rejestry dostępne, odczyt Flash 0x08000000 nieudany nawet dla 4 B, zarówno SWD 200 kHz, jak i 8000 kHz.
- FLASH_OPTCR przy 0x40023C14 = **0x0FFF00ED** (RDP = 0x00 ⇒ Level 1).
- Fabryczny UART diagnostyczny MCU: **115200, 8N1**, logi ZOS, zcmd, COMMAND_GUI_INIT (23), COMMAND_REQUIRE_MODEL_SYNC (32), Extruder not connected.
- Nie odnaleziono aktywnej fabrycznej funkcji eksportowania Flash. Konsole UART nie stanowią dowodu na dostęp do funkcji odczytu pamięci.

## Wniosek o loaderze SRAM przez ST-Link

Oficjalny dokument **PM0059**, sekcja 2.6.3 i tabela 8, jednoznacznie opisuje zachowanie:

| Tryb | Odczyt Main Flash przy RDP1 |
| --- | --- |
| Debugowanie SWD/JTAG | Niedozwolony |
| Własny program startujący z SRAM | Niedozwolony |
| Rozruch z systemowego bootloadera ROM | Niedozwolony |
| Normalny kod wykonujący się z fabrycznej Flash, bez aktywnego debuggera | Dozwolony |

Zatem sam zapis programu odczytującego Flash do SRAM przez ST-Link **nie ominie RDP1**. Próba odczytu generuje bus error i może zatrzymać procesor. Powrót RDP1→RDP0 (Read Unprotect) **masowo kasuje Flash**, a ustawienie RDP2 jest nieodwracalne. Nie wykonywać obu operacji.

Źródła: [ST PM0059](https://www.st.com/resource/en/programming_manual/pm0059-stm32f205215-stm32f207217-flash-programming-manual-stmicroelectronics.pdf), [ST AN5156](https://www.st.com/content/st_com/en/technical-documents/an5156-introduction-to-security-for-stm32-mcus-stmicroelectronics_asset/chunk-006-topic-an5156-sec-feat-read-out-protection-rdp-.html).

## Potencjalne obejścia wymagające badań na innym MCU

1. **SRAM + FPB + kontrolowany restart**: opisany [atak STM32F1](https://github.com/CTXz/stm32f1-picopwner) wykorzystuje rezydujące dane SRAM i FPB. STM32F2 ma jednostkę FPB (ST RM0033), ale **nie potwierdzono** tego samego zachowania ochrony, zatrzasków i resetu na F2. Nie uruchamiać binariów STM32F1 na M300 Dual.
2. **Voltage glitching / fault injection**: [SEC Consult](https://sec-consult.com/blog/detail/secglitcher-part-1-reproducible-voltage-glitching-on-stm32-microcontrollers/) opisał odczyt RDP1 z wykorzystaniem ChipWhisperer; badany egzemplarz to STM32F429ZI, nie STM32F207. Wyniki ani parametry nie są przenośne na tę płytę.
3. **Oryginalny kod użytkownika**: aplikacja uruchomiona z Flash może czytać Flash. Potrzebna byłaby legalnie dostępna funkcja serwisowa eksportu lub odrębne, zweryfikowane wykonanie kodu z kontekstu fabrycznego rozruchu; **niczego takiego obecnie nie znaleziono**.

Do eksperymentów nad metodami 1–2 potrzebny jest **oddzielny STM32F2 tej samej rewizji**, program testowy z nieistotnymi danymi i dokumentacja wyników; nie używać jedynego oryginalnego MCU.

## Realna ścieżka odzyskania firmware aktualizacyjnego

Najpierw odzyskać zawartość **eMMC systemu Android Allwinner A33-Core3**, niezależnego od chronionego STM32, metodą tylko do odczytu. Następnie przeanalizować pliki APK/DEX/biblioteki natywne odpowiedzialne za format aktualizacji **update.zar2** i wydzielić ewentualne aktualizacje STM32. [mandraga/klipper4m200](https://github.com/mandraga/klipper4m200) dokumentuje UART0 J5/FEL oraz kopię eMMC dla pokrewnego A33; nie należy bez sprawdzenia przenosić pinoutów ani sekwencji z M200 Plus na Dual.

Wyniki wcześniejszej pracy: 14/14 oryginalnych kontenerów ZRTX Inventure/klasycznych M200/M300 zostało poprawnie odszyfrowanych i zweryfikowanych HMAC. W **ZAR2** Plus/Dual nagłówek 8192 B pod XOR 0xAA jest rozpoznany, lecz zewnętrzny korpus nadal nieodkodowany. Testy na Plus z historycznym AES nie ujawniły jawnego obrazu STM32. Nie zakładać, że te same klucze obowiązują Dual.

**Ważne rozróżnienie:** firmware z pakietu aktualizacji może nie zawierać **oryginalnego bootloadera Zortrax** z początkowych sektorów Flash. Systemowy bootloader ST w ROM to odrębny komponent. Pełny dump zainstalowanego bootloadera MCU pozostaje osobnym zadaniem.

## Decyzja na 9 listopada 2026

- **Nie**: zwykły SRAM-loader przez SWD, Read Unprotect, programowanie przypadkowego firmware, wymuszona aktualizacja przed kopią systemu.
- **Tak, priorytet**: read-only obraz eMMC A33 → odzyskanie aplikacji aktualizatora → odtworzenie ZAR2 → wyizolowanie aplikacji MCU.
- **Eksperymentalnie**: porównanie ataków FPB/fault injection na zapasowym STM32F207, bez ingerencji w oryginalną płytę.

Status: badanie dokumentacyjne, **nie wykonano w tej turze żadnych operacji elektrycznych ani odczytu fabrycznej Flash**.