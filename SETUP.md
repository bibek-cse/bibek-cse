# Profile card: setup & editing

The card at the top of the profile is generated: **don't hand-edit the SVGs**, since every build overwrites them.

## Edit the content
- `build_svg.py` holds everything in the config block at the top: `SUBJECT`, `SIGNALS` (bar lengths),
  `STACK`, `CONTACT`, `VERIFY_LINE`, the colour `THEMES`, and the hidden `WATERMARK` (exactly 5 ASCII chars).
- `BIRTHDAY` is defined in both `build_svg.py` and `today.py`; keep them the same.
- New portrait: `pip install opencv-python numpy`, then `python binary_portrait.py photo.jpg`. This removes the
  background and writes `cache/portrait.json` (brightness grid + bits). The photo itself is never stored in the repo.
  The text the 0s and 1s spell out is `PAYLOAD` in `binary_portrait.py`.
- Run `python build_svg.py`. It stops with an error if the right column overflows.
- Preview locally by opening `dark_mode.svg` in a browser (the animations run there too).

## Dynamic content (updates itself)
`profile_sync.py` reads all my public repos every day and writes `cache/profile.json`:
- **KEYWORDS** chips: research keywords + repo topics, ranked by recency (half-life 120 days) and stars; ✦ = new since the last sync
- **RESEARCH SIGNALS** bars: scored from those keywords (mapping in `AREAS`)
- **STACK**: top languages by code size + `FRAMEWORKS` from `build_svg.py`
- **CURRENTLY**: latest pushed repos (put fixed lines in `CURRENTLY_PINNED`)
- the **portrait's 0s and 1s**: bio + live keywords + latest repo
- the README block between `<!-- LAB:START -->` and `<!-- LAB:END -->`

To steer it: add **topics** to your repos (repo page → About → ⚙ → Topics) and write good one-line
descriptions. New research words can be added to `VOCAB` in `profile_sync.py`. Repos that look like
teaching material (quiz, lab, GATE…) only count as *teaching*, so they don't inflate research bars.

## Live stats (GitHub Action)
`.github/workflows/build.yaml` runs on every push, daily, and on demand (Actions → *README build* → *Run workflow*).
It syncs `profile_sync.py`, rebuilds the layout, then `today.py` writes repos/stars/commits/followers/LOC into the elements with ids
`repo_data, contrib_data, star_data, commit_data, follower_data, loc_data, loc_add, loc_del, age_data`.

It needs a repo secret **`ACCESS_TOKEN`**, a fine-grained PAT with:
- Repository access: **All repositories**
- Repository permissions (read-only): Contents, Metadata, Commit statuses, Issues, Pull requests
- Account permissions (read-only): Followers, Starring, Watching

If the push step fails with 403: Settings → Actions → General → Workflow permissions → **Read and write**.
