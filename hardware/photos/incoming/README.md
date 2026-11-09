# Incoming M300 Dual PCB photographs

This folder is for the **27 additional original photos** from the two batches already supplied for this project.

Expected image identifiers:

- `IMG_8997`, `IMG_8998`, `IMG_8999`;
- `IMG_9001` through `IMG_9024` (24 images).

Total **27**. Filename suffixes such as `(1)` or ` 2` are supported; only one file per image identifier is allowed.

When all 27 originals are present, the workflow automatically:

1. reads the existing 21-photo PNG ZIP;
2. converts the 27 added images to **PNG**, stripping **EXIF, GPS, ICC profiles, comments and other metadata**;
3. produces a downloadable `hardware/photos/M300_Dual_Photos_48_PNG.zip` with 48 numbered PNG files and checksums;
4. replaces the reference contact sheet with a new 48-photo sheet.

If any photo is missing or duplicated, the workflow **fails without publishing** a misleading "complete" archive.

Do not publish factory firmware images or private records in this folder.
