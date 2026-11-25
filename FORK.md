# This fork

`qwqqvq123456/totk-pc-recomp` follows [`valentderah/totk-pc-recomp`](https://github.com/valentderah/totk-pc-recomp) and
adds nothing to the code. Three workflows keep it level and make a release out of every sync; this page says what they do
and what they need.

| Workflow | Runs | What it does |
| --- | --- | --- |
| [`sync-upstream.yml`](.github/workflows/sync-upstream.yml) | every 6 hours, or on demand | Merges the upstream branch, adds the sync's section to [CHANGELOG.md](CHANGELOG.md), pushes the tag `v<version>-sync.<n>` |
| [`release.yml`](.github/workflows/release.yml) | on a `v*` tag, or on demand | Runs the checks, packs the tag's sources, publishes the release with the tag's changelog section as its notes |
| [`build-installer.yml`](.github/workflows/build-installer.yml) | on demand, self-hosted runner only | Builds `TotK-Setup.zip` on a machine that has the game files and attaches it to the release |

## Versions

`VERSION` stays upstream's file, so a sync never edits it: the release number is the tag, `v0.5.1-sync.2` — upstream's
`VERSION` at that commit, then the number of syncs made since that version changed. The changelog section of a tag and the
release notes of that tag are the same text.

## Setup, once

1. Add the token the sync pushes with. It must belong to an account that can push to `main` and create tags, and it needs
   the `repo` scope; the workflow uses it instead of `GITHUB_TOKEN` because a push made with `GITHUB_TOKEN` starts no
   workflow, so the release would never run.

   ```sh
   gh secret set SYNC_TOKEN --repo qwqqvq123456/totk-pc-recomp
   ```

2. Nothing else: Actions are on, and each workflow asks for the permissions it uses (`contents: write` to push and
   release, `issues: write` for the conflict issue).

## When a merge conflicts

The fork's own files are `.github/` and `CHANGELOG.md`. A conflict means upstream changed something the fork also holds,
so the run stops, `main` is left untouched, no tag is pushed, and an issue lists the files. Merge it by hand, or dispatch
the sync again with `merge_strategy` set to `prefer-ours` to keep the fork's side of the conflicting hunks.

## The setup archives

GitHub's runners cannot build `TotK-Setup-*`: `tools/make_release.py` needs `build/xlate` and a game version extracted
into `generated/`, which the repository never holds ([CONTRIBUTING.md](CONTRIBUTING.md)). The releases here therefore carry
the sources of the tag; building the setup from them is [docs/installer.md](docs/installer.md) on a machine with your own
game files. If such a machine also runs a self-hosted runner, set two repository variables and `build-installer.yml` does
it for you:

```sh
gh variable set TOTK_RUNNER --repo qwqqvq123456/totk-pc-recomp --body '["self-hosted","Windows","X64"]'
gh variable set TOTK_WORKDIR --repo qwqqvq123456/totk-pc-recomp --body 'D:\totk'
```

`TOTK_WORKDIR` is the folder that holds `generated/`, `toolchain/`, `build/` and `.venv-py314` on that machine. Until
`TOTK_RUNNER` is set the job skips itself instead of waiting for a runner that does not exist.

## Limits worth knowing

- GitHub pauses scheduled workflows in a repository with no activity for 60 days; a sync pushes a commit, which counts.
- Upstream's tags are not mirrored here, and nothing about the game is: the content guard in
  [`content-guard.yml`](.github/workflows/content-guard.yml) runs on every push as before.
- The schedule is GitHub's: loads delay a run by minutes, and a fork's schedules can be turned off in the repository's
  Actions settings.
