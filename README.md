# Kontagious website

Lightweight static website for [Kontagious](https://www.kontagious.org), a Silicon Valley nonprofit that welcomes international students. Plain HTML, CSS and a little JavaScript. No build step, no dependencies, about 26 KB in total.

## Files

| File | What it does |
| --- | --- |
| `index.html` | All page content: Home, About, Events, Get Involved, Gallery, Blog, Donate, Contact |
| `style.css` | Colors, fonts and layout (colors live in `:root` at the top) |
| `script.js` | Mobile menu, hides past events, fade-in on scroll |

## Preview locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Common edits

**Add an event.** In `index.html`, copy one `<article class="event card" ...>` block inside the Events section, then change the text, image, link and `data-end="YYYY-MM-DD"`. The event hides itself automatically the day after `data-end`.

**Change colors.** Edit `--navy` and `--accent` at the top of `style.css`.

**Update stats, address, phone or email.** Search for the value in `index.html` and edit it in place.

## Deploy

Pushing to `main` publishes the site with GitHub Pages (see `.github/workflows/pages.yml`). In the GitHub repo go to Settings > Pages and set Source to "GitHub Actions". Then point the `kontagious.org` domain at it under Settings > Pages > Custom domain.

Any static host (Netlify, Cloudflare Pages, etc.) also works by uploading these files as they are.

## Known to-dos before replacing the old site

- [ ] Images are still loaded from the old Wix site. Download them into an `images/` folder and update the `src` links.
- [ ] Blog and event "Learn more" links still point to kontagious.org. Replace them with pages on the new site.
- [ ] Donate buttons point to the existing donate page. Replace with a donation service link (Zeffy, Givebutter, etc.).
- [ ] Contact form uses `mailto:`. Swap in a form service (Formspree, etc.) so messages arrive directly.
- [ ] Recreate the Privacy Policy and Terms pages.
- [ ] Add the real logo and match brand colors.

## Working on issues

Open a GitHub Issue for each change, work on a branch, and merge through a pull request so changes are easy to review and undo.
