# Kontagious website

Lightweight, self-contained static website for [Kontagious](https://www.kontagious.org), a Silicon Valley nonprofit that welcomes international students. Plain HTML, CSS and a little JavaScript. No build step, no dependencies, nothing that sends visitors to the old Wix site.

## Pages

| Page | File |
| --- | --- |
| Home | `index.html` |
| About + team | `about.html` |
| High-impact initiatives | `initiatives.html` |
| Student chapters | `chapters.html` |
| Alumni | `alumni.html` |
| Events (all details + sign-ups) | `events.html` |
| Airport pickup | `airport-pickup.html` |
| Get involved | `get-involved.html` |
| Gallery | `gallery.html` |
| Blog + 3 posts | `blog.html`, `post-*.html` |
| Donate (GoFundMe, Zelle, check, stock, corporate match) | `donate.html` |
| Privacy, Terms, 404 | `privacy.html`, `terms.html`, `404.html` |

Shared files: `style.css` (colors live in `:root`), `script.js` (mobile menu, hides past events, fade-in).

Links to other websites (Google Forms, GoFundMe, Facebook, Instagram, YouTube) open in a new tab. Everything else stays on this site.

## First-time setup: download the photos

The photos are not stored in the repo yet. Run this once on your computer (needs internet):

```bash
bash scripts/download-images.sh
```

It downloads about 70 resized photos from the old Wix site into `images/`. Then commit them:

```bash
git add images && git commit -m "Add photos" && git push
```

Do this **before** the old Wix site is taken down.

## Preview locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Common edits

**Add an event.** In `events.html`, copy an `<article class="event-full card" ...>` block and edit it. Set `data-end="YYYY-MM-DD"`; the event hides itself after that date. Do the same for the small card in `index.html`.

**Change colors.** Edit `--navy` and `--accent` at the top of `style.css`.

**Update stats, address, phone or email.** Search for the value across the `.html` files and edit it.

**Menu or footer changes.** These appear in every page, so change them in each `.html` file (search for `class="nav"` or `site-footer`).

## Deploy

Pushing to `main` publishes the site with GitHub Pages (`.github/workflows/pages.yml`). In the GitHub repo set Settings > Pages > Source to "GitHub Actions". For `kontagious.org`, add the custom domain there and point DNS at GitHub Pages.

## Before replacing the old site

- [ ] Run `scripts/download-images.sh` and commit the photos.
- [ ] Confirm the blog posts: they were rewritten from summaries of the originals. Paste in the original text if wanted.
- [ ] Add a card/PayPal giving link on `donate.html` (the old site mentions credit card and PayPal but the provider is unknown).
- [ ] Confirm the Zelle email (`admin@kontagious.org` on the old donate page).
- [ ] Confirm the Thanksgiving host sign-up link (`tiny.cc/kontagiousthanksgiving25` ends in "25") and event times/location.
- [ ] Have someone review the Privacy Policy and Terms (the old pages were empty templates).
- [ ] Replace the contact form's `mailto:` with a form service (Formspree, etc.).
- [ ] Add the real logo and match brand colors.
- [ ] Point the `kontagious.org` domain at the new site, then take down Wix.
