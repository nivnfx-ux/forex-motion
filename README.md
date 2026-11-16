# Forex Motion — repository preparation

This repository is being prepared to document the Forex Motion Android application.

> **Status:** Not an open-source release. The original buildable source code has not been supplied or verified. The supplied APK is a compiled package, and extracted APK contents are not equivalent to original source.

## What this repository contains

- Documentation about licensing and provenance.
- A local-only APK extraction and checksum-inventory script.

**No APK, extracted proprietary code, third-party assets, signing keys, or buildable Android application are published here.** Please do not describe this repository as open source until the code audit and rights review are complete.

## Why the complete APK cannot simply be open-sourced

Android APKs commonly contain compiled DEX bytecode, resources, libraries and third-party dependencies. Extracting these files does not grant copyright or redistribution rights. Software and assets taken from other applications require their respective owners' permission or a license that permits redistribution.

## Local APK inventory (does not upload anything)

Requirements: Python 3.9+.

```bash
python3 tools/extract_apk.py "/absolute/path/to/FOREX-MOTION-564-silver-workspaces.apk"
```

The command extracts every regular APK archive entry to a locally created `local-apk-inspection/` directory and generates `manifest.sha256`. It never executes APK code, decompiles it, or uploads anything.

**Do not publish the extracted directory without a rights review.**

## Conditions for an actual open-source release

1. Obtain the original buildable source code and its dependency information.
2. Identify code, assets, and native libraries owned by third parties.
3. Obtain permission for redistribution or replace components that cannot be redistributed.
4. Add license notices for each component. License your own code only.
5. Remove signing keys, API credentials, personal data, and other secrets.
6. Verify that the published project builds and its behavior matches the claimed release.

See [RIGHTS_AND_PROVENANCE.md](RIGHTS_AND_PROVENANCE.md) and [LICENSE](LICENSE) for current licensing scope.
