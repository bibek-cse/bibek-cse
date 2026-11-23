# Profile card: setup & editing

The card at the top of the profile is generated: **don't hand-edit the SVGs**, since every build overwrites them.

## Edit the content
- `build_svg.py` holds everything in the config block at the top: `SUBJECT`, `SIGNALS` (bar lengths),
  `STACK`, `CONTACT`, `VERIFY_LINE`, the colour `THEMES`, and the hidden `WATERMARK` (exactly 5 ASCII chars).
- `BIRTHDAY` is defined in both `build_svg.py` and `today.py`; keep them the same.
- New portrait: `python ascii_art.py photo.jpg` writes `cache/ascii.txt` (36 x 25 max).
- Run `python build_svg.py`. It stops with an error if the right column overflows.
- Preview locally by opening `dark_mode.svg` in a browser (the animations run there too).

## Live stats (GitHub Action)
`.github/workflows/build.yaml` runs on every push, daily, and on demand (Actions → *README build* → *Run workflow*).
It rebuilds the layout, then `today.py` writes repos/stars/commits/followers/LOC into the elements with ids
`repo_data, contrib_data, star_data, commit_data, follower_data, loc_data, loc_add, loc_del, age_data`.

It needs a repo secret **`ACCESS_TOKEN`**, a fine-grained PAT with:
- Repository access: **All repositories**
- Repository permissions (read-only): Contents, Metadata, Commit statuses, Issues, Pull requests
- Account permissions (read-only): Followers, Starring, Watching

If the push step fails with 403: Settings → Actions → General → Workflow permissions → **Read and write**.
