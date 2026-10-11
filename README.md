# Kontagious website

Lightweight static website for [Kontagious](https://www.kontagious.org), a Silicon Valley nonprofit that welcomes international students. Everything lives on this site; nothing sends visitors to the old Wix site.

## How it works

Content is stored as data, and a small script builds the pages:

| Edit this | To change |
| --- | --- |
| `content/events.json` | Events (home cards + Events page) |
| `content/posts.json` | Blog posts |
| `content/gallery.json` | Gallery photos (first 3 starred = home page) |
| `scripts/build.py` | Page layouts and fixed pages (About, Donate, Privacy…) |
| `style.css` | Colors (`:root`) and styling |

`python3 scripts/build.py` writes the finished site to `dist/`. GitHub Actions does this on every push to `main` and publishes `dist/` with GitHub Pages (Settings > Pages > Source = "GitHub Actions").

## Admin page (no coding)

`/admin/` lets the site owner add/reorder/hide/delete events, blog posts and gallery photos, and publish with one button. See [ADMIN.md](ADMIN.md).

## Preview locally

```bash
python3 scripts/build.py && python3 -m http.server -d dist 8000
# open http://localhost:8000  (admin at /admin/)
```

## Photos

Photos live in `images/`. After importing new content run once, then commit:

```bash
bash scripts/download-images.sh
git add images && git commit -m "Add photos" && git push
```

Photos uploaded through the admin page go to `images/uploads/` automatically.

## Before replacing the old site

- [ ] Full human testing of every page, the admin, and mobile.
- [ ] Add a card/PayPal giving link on the Donate page (provider unknown).
- [ ] Confirm the Zelle email (`admin@kontagious.org` on the old donate page).
- [ ] Confirm the Thanksgiving host sign-up link (`tiny.cc/kontagiousthanksgiving25` ends in "25").
- [ ] Have someone review Privacy and Terms (drafts).
- [ ] Replace the contact form's `mailto:` with a form service.
- [ ] Point the `kontagious.org` domain at the new site, then take down Wix.
