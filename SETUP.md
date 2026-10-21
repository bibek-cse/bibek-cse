# Setting up the profile card

## 1. Edit your details
- `build_svg.py` → the `PROFILE` and `CONTACT` lists. Replace the two lines marked `EDIT ME`
  (academic email, LinkedIn) and correct anything else (OS, languages, etc.).
- `today.py` → set `BIRTHDAY = datetime.datetime(YYYY, M, D)` (drives the "Uptime" line).
- Optional: your own face as ASCII art: `python ascii_art.py photo.jpg` (add `--invert` if it looks negative).
- Run `python build_svg.py`. It warns you if any line is too long.

## 2. Create the profile repository
On GitHub create a **public** repo named exactly **`bibek-cse`** (same as your username).
GitHub shows its README on your profile page.

## 3. Create a token
GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate:
- Repository access: **All repositories**
- Repository permissions: Contents, Metadata, Commit statuses, Issues, Pull requests → **Read-only**
- Account permissions: Followers, Starring, Watching → **Read-only**

Copy the token.

## 4. Add it as a secret
In the `bibek-cse` repo: Settings → Secrets and variables → Actions → **New repository secret**
- Name: `ACCESS_TOKEN`, Value: the token

## 5. Push
```bash
cd bibek-cse
git init && git add . && git commit -m "Profile card"
git branch -M main
git remote add origin https://github.com/bibek-cse/bibek-cse.git
git push -u origin main
```
The Action runs on every push and daily; it fills in repos, stars, commits, followers and
lines of code. Trigger it any time from the **Actions** tab → *README build* → *Run workflow*.

If the push step fails with a 403: repo Settings → Actions → General → Workflow permissions →
**Read and write permissions**.
