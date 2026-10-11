# Admin guide

Open `https://<your-site>/admin/` (there is an "Admin" link in the site footer).

## One-time: create a sign-in token

1. Sign in to GitHub as the repository owner.
2. Go to <https://github.com/settings/personal-access-tokens/new>.
3. Name: "Kontagious admin". Expiration: up to 1 year.
4. Repository access: **Only select repositories** > `kontagious-website`.
5. Permissions > Repository permissions > **Contents: Read and write**.
6. Generate, copy, and paste it into the admin page. Treat it like a password.

Tick "Keep me signed in" only on your own computer; use **Sign out** on shared ones.

## Using it

- **Events**: New event (title, picture, dates, details, sign-up button), Edit, Delete, Shown/Hidden switch, and order with ⠿ drag or ↑ ↓. "Sort by date" puts the soonest first and ended events last. An event disappears from the site after its *Last day*.
- **Blog posts**: write stories from blocks (heading, paragraph, photo, list, quote, video, button). Reorder, hide or delete posts. The first 3 shown posts appear on the home page.
- **Gallery**: Add photos (several at once), caption them, ★ to feature on the home page, Show/hide, reorder, delete.
- **Preview** in the editors shows roughly how it will look. Nothing is live until **Publish changes**.
- Photos are shrunk automatically before upload.

## Publishing

Publish makes a single commit; the site updates in about a minute (watch the Actions tab). To undo, revert that commit on GitHub (History of `content/*.json`).

If someone else changed the content in the meantime, the admin refuses to overwrite it: reload and redo your edit.

## Text formatting

`**bold**`, `*italic*`, `[link text](https://example.com)`; a blank line starts a new paragraph. Links to other sites open in a new tab.
