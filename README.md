# ClawPort by CodesbyFebin

A device-aware catalog of **126 distinct upstream repositories**: Claw alternatives, coding agents, local LLM tools, agent frameworks and open-weight model projects.

**Website:** https://codesbyfebin.github.io/ClawPort/

## Explore

- [All 126 projects](CATALOG.md)
- [Platform/package matrix](BUILD-MATRIX.csv)
- [Source import manifest](sources/manifest.json)

Every project has an individual installation page for Android, Windows, macOS and Linux. Official package links are displayed where release metadata was retrieved. A missing package is marked **not verified**, and links to upstream setup remain available. Archived projects are labeled.

## What is actually installable?

The catalog links to existing upstream APK, EXE/MSI, DMG/PKG, Linux package, binary and archive assets. A ClawPort Linux script installs a pinned NullClaw binary with SHA-256 verification and refuses to overwrite an existing install.

**ClawPort has not rebuilt all 126 applications.** Some repositories are libraries, server frameworks or model project code rather than end-user applications. Producing native APKs and signed desktop installers for each requires separate ports, interfaces, build adapters, licensing checks and platform validation. No placeholder installer is offered. Download presence does not establish device compatibility.

Model project code is distinct from model weights. Obtain weights and their licenses from upstream sources. Runtime setup, providers and API charges remain upstream concerns. License metadata marked `Unverified` requires review; source availability does not establish an open-source license.

## Run locally

```
python3 -m http.server 8080 --directory dist
npm test
```

No npm dependencies or build step are needed. GitHub Actions runs the tests and publishes `dist/` to GitHub Pages on updates to `main`.

## Extract upstream sources

```
python3 scripts/import-sources.py --limit 54 --jobs 8
# All manifest entries:
python3 scripts/import-sources.py --jobs 6
```

The importer resolves the current Git HEAD, downloads its commit archive, calculates SHA-256, extracts using Python's data filter, and records evidence in `sources/import-results.json`. It does not execute imported code. Sources are kept separately in ignored `imported-sources/`; their licenses, names and attribution remain intact. Per-repository download and extraction bounds report large repositories as blocked rather than filling the disk. Python 3.12+ and Git are required. No proprietary dependencies, credentials or model weights are bundled.

## Research and refresh

The source collection contains only 15 entries despite its introductory claim of 30+ alternatives. Its README and pinned commit are preserved in `vendor/awesome-openclaw-alternatives/`; no license file was present in that collection.

Expanded discovery used https://github.com/machinae/awesome-claws and primary upstream GitHub repository metadata. Redirected repository names are canonicalized and deduplicated. Existing release metadata includes 656 assets; newly researched projects without checked release metadata link to upstream setup instead. The 126 repository links were verified; application functionality and hardware performance were not tested. Metadata is a dated snapshot, not a security or license audit.

```
python3 scripts/sync.py
python3 scripts/expand.py
python3 scripts/generate-project-pages.py
npm test
```

The refresh scripts use public GitHub endpoints and may encounter rate limits; review results before committing. The checked-in catalog remains usable without live API access.

## Verification

Tests cover catalog uniqueness, source metadata, release asset URLs, OS detection, iPad desktop mode, architecture matching and checksum-file rejection. Native installer execution and mobile device testing have not been performed. Every platform's current status is explicit in `BUILD-MATRIX.csv`.
