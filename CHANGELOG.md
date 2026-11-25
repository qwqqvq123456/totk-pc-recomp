# Changelog

This fork follows [`valentderah/totk-pc-recomp`](https://github.com/valentderah/totk-pc-recomp) and adds nothing of its own to the code.
Whenever the upstream branch moves, [`.github/workflows/sync-upstream.yml`](.github/workflows/sync-upstream.yml) merges it,
writes the section below and pushes the tag `v<version>-sync.<n>`, where `<version>` is upstream's `VERSION` file at that
commit and `<n>` counts the syncs since that version changed. The tag's release notes are the section itself, published by
[`.github/workflows/release.yml`](.github/workflows/release.yml).

Upstream writes plain-sentence commit subjects, so a section is the list of commits the sync brought in, oldest first, with
the pull requests they came from. Upstream's own releases are on
[its releases page](https://github.com/valentderah/totk-pc-recomp/releases).

## 0.3.1-sync.1 (2026-11-26)

Upstream `valentderah/totk-pc-recomp` moved from [`7ec95ea`](https://github.com/valentderah/totk-pc-recomp/commit/7ec95ea) to [`ab1dee5`](https://github.com/valentderah/totk-pc-recomp/commit/ab1dee5): 9 commits.

- Cache the thread id per thread on Linux ([ff5706c](https://github.com/valentderah/totk-pc-recomp/commit/ff5706c28bd6efb1a258ef5150647b93c6815f99))
- Stop the Windows release on a translator older than its sources. ([33c2a1a](https://github.com/valentderah/totk-pc-recomp/commit/33c2a1ac63085371c3ae7a310d789f4a3bdd2969))
- Stage large CPU texture uploads in parts of at most 32 MiB ([da94604](https://github.com/valentderah/totk-pc-recomp/commit/da9460457e7fd5f318d11e0b2d349f584d6ff99b))
- Build the runtime library without the generated chunk lists ([cc4572b](https://github.com/valentderah/totk-pc-recomp/commit/cc4572b244b3615ff49aab0b1c4dcf5f9b3ca9eb))
- Name the 1.1.0 update 1.1.0 instead of 1.1.1 ([a7b988b](https://github.com/valentderah/totk-pc-recomp/commit/a7b988b417e89757850c3750e3624d46c08751f3))
- Report a busy totk_xlate.exe in the prepare step the way the compile step reports a busy game exe ([72dcdc0](https://github.com/valentderah/totk-pc-recomp/commit/72dcdc0534415d6360cda6c60d944116a4cfced2))
- Extract the RomFS again when its index on disk cannot be read ([2125ad6](https://github.com/valentderah/totk-pc-recomp/commit/2125ad6eead5c3d2177f250e6ba2c248233f30db))
- Use plat_setenv and strcasecmp where the stick dead zone code called Windows-only functions ([2af42cc](https://github.com/valentderah/totk-pc-recomp/commit/2af42ccf0d85e789afbf4e145d7800857066e7dd))
- Close the spawned child's descriptors only where glibc has posix_spawn_file_actions_addclosefrom_np ([ab1dee5](https://github.com/valentderah/totk-pc-recomp/commit/ab1dee5bdb9089399b2000880eaa8f702a846f89))

Pull requests merged: [#358](https://github.com/valentderah/totk-pc-recomp/pull/358), [#365](https://github.com/valentderah/totk-pc-recomp/pull/365), [#375](https://github.com/valentderah/totk-pc-recomp/pull/375), [#354](https://github.com/valentderah/totk-pc-recomp/pull/354), [#246](https://github.com/valentderah/totk-pc-recomp/pull/246), [#371](https://github.com/valentderah/totk-pc-recomp/pull/371)

[Compare 7ec95ea...ab1dee5](https://github.com/valentderah/totk-pc-recomp/compare/7ec95ea...ab1dee5)
