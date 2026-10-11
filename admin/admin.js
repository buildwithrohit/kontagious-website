/* Kontagious admin: edits content/*.json and uploads photos by committing to GitHub.
   No server needed. The repo's GitHub Action rebuilds the site after each publish. */
(function () {
  'use strict';

  const CFG = { owner: 'buildwithrohit', repo: 'kontagious-website', branch: 'main' };
  const API = 'https://api.github.com';
  const R = `/repos/${CFG.owner}/${CFG.repo}`;
  const FILES = { events: 'content/events.json', posts: 'content/posts.json', gallery: 'content/gallery.json' };
  const SITE_ROOT = new URL('../', location.href).href;
  const URL_OK = /^(https?:\/\/|mailto:|tel:|#|[\w./%-]+(#[\w-]+)?$)/i;

  // ------------------------------------------------------------------ helpers
  const $ = (s, r) => (r || document).querySelector(s);

  function el(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === false || v == null) continue;
      if (k === 'class') e.className = v;
      else if (k === 'on') for (const [ev, fn] of Object.entries(v)) e.addEventListener(ev, fn);
      else if (k === 'value') e.value = v;
      else if (typeof v === 'boolean') { if (k in e) e[k] = v; else e.setAttribute(k, ''); }
      else e.setAttribute(k, v);
    }
    for (const kid of kids.flat()) {
      if (kid == null || kid === false) continue;
      e.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    }
    return e;
  }

  const escH = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const ser = (o) => JSON.stringify(o, null, 2) + '\n';
  const rand = () => Math.random().toString(36).slice(2, 7);
  const today = () => new Date().toLocaleDateString('en-CA');
  const slugify = (s) => (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'item';
  const stamp = () => { const d = new Date(); const p = (n) => String(n).padStart(2, '0'); return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`; };

  let toastTimer;
  function toast(msg, kind) {
    const t = $('#toast');
    t.textContent = msg;
    t.className = 'toast' + (kind === 'err' ? ' err' : '');
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { t.hidden = true; }, kind === 'err' ? 7000 : 3500);
  }

  // ------------------------------------------------------------------ token storage
  const tokenStore = {
    get() { try { return localStorage.getItem('kt_token') || sessionStorage.getItem('kt_token') || ''; } catch (e) { return ''; } },
    set(t, remember) { try { (remember ? localStorage : sessionStorage).setItem('kt_token', t); } catch (e) { /* ignore */ } },
    clear() { try { localStorage.removeItem('kt_token'); sessionStorage.removeItem('kt_token'); } catch (e) { /* ignore */ } },
  };

  // ------------------------------------------------------------------ GitHub API
  let token = '';
  async function gh(path, opts) {
    const o = opts || {};
    const res = await fetch(API + path, {
      method: o.method || 'GET',
      headers: Object.assign({
        Authorization: 'Bearer ' + token,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      }, o.body ? { 'Content-Type': 'application/json' } : {}),
      body: o.body ? JSON.stringify(o.body) : undefined,
    });
    if (!res.ok) {
      let msg = res.status + ' ' + res.statusText;
      try { const j = await res.json(); if (j && j.message) msg = j.message; } catch (e) { /* ignore */ }
      const err = new Error(msg);
      err.status = res.status;
      throw err;
    }
    return res.status === 204 ? null : res.json();
  }

  const b64ToText = (b64) => new TextDecoder().decode(Uint8Array.from(atob(String(b64).replace(/\s/g, '')), (c) => c.charCodeAt(0)));
  const blobToB64 = (blob) => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1]); r.onerror = no; r.readAsDataURL(blob); });

  async function remoteMeta() {
    const ref = await gh(`${R}/git/ref/heads/${CFG.branch}`);
    const head = ref.object.sha;
    const commit = await gh(`${R}/git/commits/${head}`);
    const tree = await gh(`${R}/git/trees/${commit.tree.sha}?recursive=1`);
    const shas = {}; const uploads = [];
    for (const t of tree.tree) {
      if (t.type !== 'blob') continue;
      shas[t.path] = t.sha;
      if (t.path.startsWith('images/uploads/')) uploads.push(t.path);
    }
    return { head, treeSha: commit.tree.sha, shas, uploads };
  }

  async function loadRemote() {
    const meta = await remoteMeta();
    const data = {};
    for (const [k, p] of Object.entries(FILES)) {
      if (meta.shas[p]) {
        const b = await gh(`${R}/git/blobs/${meta.shas[p]}`);
        data[k] = JSON.parse(b64ToText(b.content));
      } else data[k] = [];
    }
    return Object.assign(meta, { data });
  }

  // ------------------------------------------------------------------ state
  const S = { remote: null, data: { events: [], posts: [], gallery: [] }, orig: {}, tab: 'events', user: '' };
  const pending = new Map();   // repo path -> {blob, url} for photos not yet published
  const urlCache = new Map();  // repo path -> blob URL for this session

  const changedKeys = () => Object.keys(FILES).filter((k) => ser(S.data[k]) !== S.orig[k]);
  const isDirty = () => changedKeys().length > 0;
  const imgSrc = (p) => (p ? (urlCache.get(p) || '../' + p) : '');
  const imgAbs = (p) => (pending.has(p) ? pending.get(p).dataUrl : new URL(p, SITE_ROOT).href);

  function referencedPaths() {
    const s = new Set();
    S.data.events.forEach((e) => e.image && s.add(e.image));
    S.data.gallery.forEach((g) => g.src && s.add(g.src));
    S.data.posts.forEach((p) => {
      if (p.cover) s.add(p.cover);
      (p.blocks || []).forEach((b) => b.type === 'image' && b.src && s.add(b.src));
    });
    return s;
  }

  // ------------------------------------------------------------------ images
  async function processImage(file, maxEdge) {
    if (!/^image\//.test(file.type)) throw new Error('Not an image');
    let bmp;
    try { bmp = await createImageBitmap(file, { imageOrientation: 'from-image' }); } catch (e) { bmp = await createImageBitmap(file); }
    const scale = Math.min(1, maxEdge / Math.max(bmp.width, bmp.height));
    const w = Math.max(1, Math.round(bmp.width * scale));
    const h = Math.max(1, Math.round(bmp.height * scale));
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, w, h);
    ctx.drawImage(bmp, 0, 0, w, h);
    const blob = await new Promise((ok) => c.toBlob(ok, 'image/jpeg', 0.82));
    if (!blob) throw new Error('Could not process image');
    const path = `images/uploads/${stamp()}-${rand()}.jpg`;
    const url = URL.createObjectURL(blob);
    const dataUrl = 'data:image/jpeg;base64,' + await blobToB64(blob);  // previews run in a sandboxed frame that cannot read blob: URLs
    pending.set(path, { blob, url, dataUrl });
    urlCache.set(path, url);
    return path;
  }

  // ------------------------------------------------------------------ list helpers
  let drag = null;
  function dragHandle(card, arr, i) {
    const h = el('span', { class: 'handle', draggable: true, title: 'Drag to reorder', 'aria-hidden': 'true' }, '⠿');
    h.addEventListener('dragstart', (e) => {
      drag = { arr, i };
      e.dataTransfer.effectAllowed = 'move';
      try { e.dataTransfer.setData('text/plain', String(i)); e.dataTransfer.setDragImage(card, 12, 12); } catch (er) { /* ignore */ }
      card.classList.add('dragging');
    });
    h.addEventListener('dragend', () => card.classList.remove('dragging'));
    card.addEventListener('dragover', (e) => { if (drag && drag.arr === arr) { e.preventDefault(); card.classList.add('over'); } });
    card.addEventListener('dragleave', () => card.classList.remove('over'));
    card.addEventListener('drop', (e) => {
      e.preventDefault(); card.classList.remove('over');
      if (drag && drag.arr === arr) move(arr, drag.i, i);
      drag = null;
    });
    return h;
  }

  function move(arr, from, to) {
    if (to < 0 || to >= arr.length || from === to) return;
    const [x] = arr.splice(from, 1);
    arr.splice(to, 0, x);
    render();
  }

  function btn(label, fn, cls, aria) {
    return el('button', { type: 'button', class: 'btn sm ' + (cls || 'ghost'), 'aria-label': aria || label, on: { click: fn } }, label);
  }

  function visSwitch(item) {
    const cb = el('input', { type: 'checkbox', checked: item.visible !== false, on: { change: () => { item.visible = cb.checked; render(); } } });
    return el('label', { class: 'switch' }, cb, 'Shown');
  }

  // ------------------------------------------------------------------ dialogs
  const dlg = () => $('#dlg');
  function openDialog(title, body, buttons, wide) {
    const d = dlg();
    d.className = wide ? 'wide' : '';
    d.replaceChildren(
      el('div', { class: 'dhead' }, el('h2', {}, title), el('button', { type: 'button', class: 'btn ghost sm', on: { click: closeDialog } }, 'Close')),
      el('div', { class: 'dbody' }, body),
      el('div', { class: 'dfoot' }, buttons)
    );
    if (!d.open) d.showModal();
  }
  function closeDialog() { const d = dlg(); if (d.open) d.close(); }

  function field(label, input, hint) {
    return el('label', { class: 'field' }, el('span', { class: 'lbl' }, label), input, hint && el('small', { class: 'hint' }, hint));
  }
  function textIn(obj, key, o) {
    o = o || {};
    const i = el(o.area ? 'textarea' : 'input', { type: o.area ? false : (o.type || 'text'), rows: o.rows, placeholder: o.ph || '', value: obj[key] || '', on: { input: () => { obj[key] = i.value; } } });
    return i;
  }
  function checkIn(obj, key, label) {
    const c = el('input', { type: 'checkbox', checked: obj[key] !== false && !!obj[key], on: { change: () => { obj[key] = c.checked; } } });
    return el('label', { class: 'check' }, c, label);
  }

  function imageField(obj, key, maxEdge, label) {
    const wrap = el('div', { class: 'imgfield' });
    function draw() {
      wrap.replaceChildren();
      const p = obj[key];
      wrap.append(p ? el('img', { src: imgSrc(p), alt: '' }) : el('div', { class: 'noimg' }, 'No image'));
      const file = el('input', { type: 'file', accept: 'image/*', hidden: true });
      file.addEventListener('change', async () => {
        if (!file.files[0]) return;
        try { obj[key] = await processImage(file.files[0], maxEdge); draw(); }
        catch (e) { toast('Could not read that image. Please try a JPG or PNG.', 'err'); }
      });
      wrap.append(el('div', { class: 'imgbtns' },
        el('button', { type: 'button', class: 'btn sm', on: { click: () => file.click() } }, p ? 'Replace image' : 'Choose image'),
        p && el('button', { type: 'button', class: 'btn sm ghost', on: { click: () => { obj[key] = ''; draw(); } } }, 'Remove'),
        file));
    }
    draw();
    return el('div', { class: 'field' }, el('span', { class: 'lbl' }, label || 'Image'), wrap);
  }

  // ------------------------------------------------------------------ previews (mirror of scripts/build.py)
  function inlineMd(s) {
    let t = escH(s);
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, txt, url) => { url = url.replace(/&amp;/g, '&'); return URL_OK.test(url) ? `<a href="${escH(url)}">${txt}</a>` : m; });
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
    return t.replace(/\n/g, '<br>');
  }
  const parasH = (txt) => String(txt || '').split(/\n\s*\n/).filter((t) => t.trim()).map((t) => `<p>${inlineMd(t.trim())}</p>`).join('');
  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    if (!m) return iso || '';
    return new Date(+m[1], +m[2] - 1, +m[3]).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }
  function videoH(url) {
    const y = /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/.exec(url || '');
    if (y) return `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${y[1]}" title="Video" allowfullscreen></iframe></div>`;
    const v = /vimeo\.com\/(\d+)/.exec(url || '');
    if (v) return `<div class="video"><iframe src="https://player.vimeo.com/video/${v[1]}" title="Video" allowfullscreen></iframe></div>`;
    return `<p><a href="${escH(url)}">Watch the video</a></p>`;
  }
  function blocksH(blocks) {
    return (blocks || []).map((b) => {
      switch (b.type) {
        case 'heading': return `<h2>${escH(b.text)}</h2>`;
        case 'paragraph': return `<p>${inlineMd(b.text)}</p>`;
        case 'image': return b.src ? `<figure><img src="${escH(imgAbs(b.src))}" alt="${escH(b.alt || b.caption)}">${b.caption ? `<figcaption>${escH(b.caption)}</figcaption>` : ''}</figure>` : '';
        case 'list': { const t = b.ordered ? 'ol' : 'ul'; return `<${t} class="bullets">${(b.items || []).filter((i) => i.trim()).map((i) => `<li>${inlineMd(i)}</li>`).join('')}</${t}>`; }
        case 'quote': return `<blockquote>${inlineMd(b.text)}</blockquote>`;
        case 'video': return videoH(b.url);
        case 'button': return b.url ? `<p><a class="btn btn-accent" href="${escH(b.url)}">${escH(b.text || 'Learn more')}</a></p>` : '';
        default: return '';
      }
    }).join('\n');
  }
  function postPageH(p) {
    const inline = new Set((p.blocks || []).filter((b) => b.type === 'image').map((b) => b.src));
    const cover = p.cover && !inline.has(p.cover) ? `<img class="post-cover" src="${escH(imgAbs(p.cover))}" alt="">` : '';
    return `<article class="post-page"><header class="post-head"><div class="wrap narrow"><h1>${escH(p.title)}</h1><p class="meta">${escH(fmtDate(p.date))} &middot; By ${escH(p.author)}</p></div></header><div class="wrap narrow article">${cover}${blocksH(p.blocks)}</div></article>`;
  }
  function eventPageH(e) {
    const facts = [e.when && `<b>When:</b> ${escH(e.when)}`, e.where && `<b>Where:</b> ${escH(e.where)}`].filter(Boolean).join('<br>');
    const im = e.image ? `<div class="ef-img"><img src="${escH(imgAbs(e.image))}" alt=""></div>` : '';
    return `<section class="section tint"><div class="wrap"><article class="event-full card${e.image ? '' : ' noimg'}">${im}<div class="ef-body"><p class="meta">${escH(e.dateLabel)}</p><h2>${escH(e.title)}</h2>${facts ? `<p class="facts">${facts}</p>` : ''}${parasH(e.details || e.short)}${e.ctaUrl ? `<p><a class="btn btn-accent" href="${escH(e.ctaUrl)}">${escH(e.ctaText || 'Learn more')}</a></p>` : ''}</div></article></div></section>`;
  }
  function openPreview(title, htmlBody, backFn) {
    const doc = `<!doctype html><html><head><meta charset="utf-8"><base href="${SITE_ROOT}"><link rel="stylesheet" href="style.css"></head><body>${htmlBody}</body></html>`;
    const frame = el('iframe', { class: 'preview', title: 'Preview', sandbox: '' });
    frame.srcdoc = doc;
    openDialog('Preview: ' + title, el('div', {}, el('p', { class: 'muted' }, 'This is how it will look (approximately). Nothing is published yet.'), frame),
      [el('button', { type: 'button', class: 'btn primary', on: { click: backFn } }, 'Back to editing')], true);
  }

  // ------------------------------------------------------------------ EVENTS
  const ended = (e) => !!e.endDate && e.endDate < today();
  function newEvent() {
    return { id: '', title: '', image: '', dateLabel: '', startDate: '', endDate: '', when: '', where: '', short: '', details: '', ctaText: '', ctaUrl: '', visible: true, home: true };
  }
  function editEvent(index) {
    const isNew = index < 0;
    const w = isNew ? newEvent() : clone(S.data.events[index]);
    const reopen = () => editEvent2(w, index);
    editEvent2(w, index);
    function editEvent2(w, index) {
      const body = el('div', { class: 'blocks' },
        field('Title *', textIn(w, 'title', { ph: 'e.g. Diwali Dinner' })),
        imageField(w, 'image', 1200, 'Picture'),
        el('div', { class: 'cols' },
          field('Date as shown on the card', textIn(w, 'dateLabel', { ph: 'Sat, Nov 8, 2026' }), 'Plain text, e.g. "Every summer" or "Aug 27–29, 2027".'),
          field('When (full details)', textIn(w, 'when', { ph: 'Saturday, November 8, 2026, 6:00 PM to 9:00 PM' }))),
        el('div', { class: 'cols' },
          field('Start date', textIn(w, 'startDate', { type: 'date' }), 'Used for "Sort by date".'),
          field('Last day (event disappears after this)', textIn(w, 'endDate', { type: 'date' }), 'Leave empty to always show it.')),
        field('Where', textIn(w, 'where', { ph: 'Santa Clara University' })),
        field('Short description (shown on cards)', textIn(w, 'short', { area: true, rows: 2 })),
        field('Full details', textIn(w, 'details', { area: true, rows: 6 }), 'Leave a blank line between paragraphs. Use **bold**, *italic* and [link text](https://example.com).'),
        el('div', { class: 'cols' },
          field('Button text', textIn(w, 'ctaText', { ph: 'Sign up' })),
          field('Button link', textIn(w, 'ctaUrl', { ph: 'https://forms.gle/…' }), 'A web address, or a page on this site like airport-pickup.html')),
        el('div', { class: 'cols' }, checkIn(w, 'visible', 'Show this event on the website'), checkIn(w, 'home', 'Also show it on the home page')));
      const save = () => {
        if (!w.title.trim()) { toast('Please enter a title.', 'err'); return; }
        if (w.ctaUrl && !URL_OK.test(w.ctaUrl.trim())) { toast('The button link does not look right. Use https://… or a page like events.html.', 'err'); return; }
        w.title = w.title.trim(); w.ctaUrl = (w.ctaUrl || '').trim();
        if (isNew) {
          const base = slugify(w.title);
          let id = base, n = 2;
          while (S.data.events.some((e) => e.id === id)) id = base + '-' + n++;
          w.id = id;
          S.data.events.unshift(w);
        } else S.data.events[index] = w;
        closeDialog(); render();
      };
      openDialog(isNew ? 'New event' : 'Edit event', body, [
        el('button', { type: 'button', class: 'btn ghost', on: { click: closeDialog } }, 'Cancel'),
        el('button', { type: 'button', class: 'btn', on: { click: () => openPreview(w.title || 'event', eventPageH(w), reopen) } }, 'Preview'),
        el('button', { type: 'button', class: 'btn primary', on: { click: save } }, 'Save event')], true);
    }
  }

  function viewEvents(root) {
    const arr = S.data.events;
    root.append(el('div', { class: 'toolbar' },
      el('button', { class: 'btn primary', type: 'button', on: { click: () => editEvent(-1) } }, '+ New event'),
      el('button', { class: 'btn', type: 'button', title: 'Soonest first, ended events last', on: { click: () => { arr.sort((a, b) => (ended(a) - ended(b)) || (a.startDate || '9999-12-31').localeCompare(b.startDate || '9999-12-31')); render(); } } }, 'Sort by date'),
      el('span', { class: 'hint' }, 'Drag ⠿ or use the arrows to choose the order events appear in. Hidden events stay saved but are not shown.')));
    if (!arr.length) { root.append(el('p', { class: 'empty' }, 'No events yet. Click "New event" to add one.')); return; }
    const list = el('div', { class: 'list' });
    arr.forEach((e, i) => {
      const row = el('div', { class: 'row' + (e.visible === false ? ' off' : '') });
      row.append(dragHandle(row, arr, i),
        e.image ? el('img', { class: 'thumb', src: imgSrc(e.image), alt: '' }) : el('div', { class: 'thumb' }),
        el('div', {}, el('div', { class: 'rt' }, e.title || '(untitled)',
          e.visible === false && el('span', { class: 'badge' }, 'Hidden'),
          ended(e) && el('span', { class: 'badge warn' }, 'Ended'),
          e.visible !== false && e.home !== false && el('span', { class: 'badge ok' }, 'On home page')),
          el('div', { class: 'rm' }, [e.dateLabel, e.where].filter(Boolean).join(' · '))),
        el('div', { class: 'ractions' }, visSwitch(e),
          btn('↑', () => move(arr, i, i - 1), 'ghost', 'Move up'), btn('↓', () => move(arr, i, i + 1), 'ghost', 'Move down'),
          btn('Edit', () => editEvent(i), ''), btn('Delete', () => { if (confirm(`Delete "${e.title}"?`)) { arr.splice(i, 1); render(); } }, 'danger')));
      list.append(row);
    });
    root.append(list);
  }

  // ------------------------------------------------------------------ BLOG
  const BLOCK_LABEL = { heading: 'Heading', paragraph: 'Paragraph', image: 'Photo', list: 'List', quote: 'Quote', video: 'Video', button: 'Button' };
  function newBlock(type) {
    return { heading: { type, text: '' }, paragraph: { type, text: '' }, image: { type, src: '', caption: '' }, list: { type, ordered: false, items: [''] }, quote: { type, text: '' }, video: { type, url: '' }, button: { type, text: '', url: '' } }[type];
  }
  function blockEditor(b, i, blocks, redraw) {
    const swap = (j) => { if (j < 0 || j >= blocks.length) return; const [x] = blocks.splice(i, 1); blocks.splice(j, 0, x); redraw(); };
    let inner;
    switch (b.type) {
      case 'heading': inner = textIn(b, 'text', { ph: 'Section heading' }); break;
      case 'paragraph': inner = el('div', {}, textIn(b, 'text', { area: true, rows: 5 }), el('small', { class: 'hint' }, 'Use **bold**, *italic* and [link text](https://example.com).')); break;
      case 'image': inner = el('div', { class: 'blocks' }, imageField(b, 'src', 1600, 'Photo'), field('Caption (optional)', textIn(b, 'caption'))); break;
      case 'list': {
        const t = el('textarea', { rows: 4, value: (b.items || []).join('\n'), on: { input: () => { b.items = t.value.split('\n'); } } });
        inner = el('div', { class: 'blocks' }, field('One item per line', t), checkIn({ get ordered() { return b.ordered; }, set ordered(v) { b.ordered = v; } }, 'ordered', 'Numbered list'));
        break;
      }
      case 'quote': inner = textIn(b, 'text', { area: true, rows: 3 }); break;
      case 'video': inner = field('YouTube or Vimeo link', textIn(b, 'url', { ph: 'https://www.youtube.com/watch?v=…' })); break;
      case 'button': inner = el('div', { class: 'cols' }, field('Button text', textIn(b, 'text')), field('Button link', textIn(b, 'url', { ph: 'https://…' }))); break;
      default: inner = el('div', {}, 'Unknown block');
    }
    return el('div', { class: 'block' },
      el('div', { class: 'bhead' }, el('strong', {}, BLOCK_LABEL[b.type] || b.type), el('span', { class: 'sp' }),
        btn('↑', () => swap(i - 1), 'ghost', 'Move block up'), btn('↓', () => swap(i + 1), 'ghost', 'Move block down'),
        btn('Remove', () => { blocks.splice(i, 1); redraw(); }, 'danger')),
      inner);
  }

  function newPost() {
    return { id: '', slug: '', title: '', author: S.data.posts[0] ? S.data.posts[0].author : '', date: today(), cover: '', blurb: '', visible: true, blocks: [newBlock('paragraph')] };
  }
  function cleanBlocks(blocks) {
    return blocks.map((b) => {
      if (b.type === 'list') return Object.assign({}, b, { items: (b.items || []).map((x) => x.trim()).filter(Boolean) });
      return b;
    }).filter((b) => {
      if (b.type === 'heading' || b.type === 'paragraph' || b.type === 'quote') return (b.text || '').trim();
      if (b.type === 'image') return b.src;
      if (b.type === 'list') return b.items.length;
      if (b.type === 'video') return (b.url || '').trim();
      if (b.type === 'button') return (b.url || '').trim();
      return false;
    });
  }

  function editPost(index) {
    const isNew = index < 0;
    const w = isNew ? newPost() : clone(S.data.posts[index]);
    function open() {
      const blocksBox = el('div', { class: 'blocks' });
      const redraw = () => { blocksBox.replaceChildren(...w.blocks.map((b, i) => blockEditor(b, i, w.blocks, redraw))); if (!w.blocks.length) blocksBox.append(el('p', { class: 'hint' }, 'No content yet. Add a paragraph, photo or heading below.')); };
      redraw();
      const add = el('div', { class: 'addbar' }, el('span', {}, 'Add:'),
        ...Object.keys(BLOCK_LABEL).map((t) => btn('+ ' + BLOCK_LABEL[t], () => { w.blocks.push(newBlock(t)); redraw(); }, '', 'Add ' + BLOCK_LABEL[t])));
      const body = el('div', { class: 'blocks' },
        field('Title *', textIn(w, 'title')),
        el('div', { class: 'cols' }, field('Author', textIn(w, 'author')), field('Date', textIn(w, 'date', { type: 'date' }))),
        imageField(w, 'cover', 1200, 'Cover photo (shown on cards and at the top of the story)'),
        field('Short summary (optional)', textIn(w, 'blurb', { area: true, rows: 2 }), 'Shown on cards. Leave empty to use the first paragraph.'),
        checkIn(w, 'visible', 'Show this story on the website'),
        el('div', { class: 'sect' }, 'Story content'), blocksBox, add);
      const prepared = () => Object.assign({}, w, { blocks: cleanBlocks(clone(w.blocks)) });
      const save = () => {
        if (!w.title.trim()) { toast('Please enter a title.', 'err'); return; }
        if (!w.date) { toast('Please choose a date.', 'err'); return; }
        const out = prepared(); out.title = out.title.trim();
        if (isNew) {
          const base = slugify(out.title);
          let slug = base, n = 2;
          while (S.data.posts.some((p) => p.slug === slug)) slug = base + '-' + n++;
          out.slug = slug; out.id = slug;
          S.data.posts.unshift(out);
        } else S.data.posts[index] = out;
        closeDialog(); render();
      };
      openDialog(isNew ? 'New blog post' : 'Edit blog post', body, [
        el('button', { type: 'button', class: 'btn ghost', on: { click: closeDialog } }, 'Cancel'),
        el('button', { type: 'button', class: 'btn', on: { click: () => openPreview(w.title || 'post', postPageH(prepared()), open) } }, 'Preview'),
        el('button', { type: 'button', class: 'btn primary', on: { click: save } }, 'Save post')], true);
    }
    open();
  }

  function viewPosts(root) {
    const arr = S.data.posts;
    root.append(el('div', { class: 'toolbar' },
      el('button', { class: 'btn primary', type: 'button', on: { click: () => editPost(-1) } }, '+ New post'),
      el('button', { class: 'btn', type: 'button', on: { click: () => { arr.sort((a, b) => (b.date || '').localeCompare(a.date || '')); render(); } } }, 'Newest first'),
      el('span', { class: 'hint' }, 'The first 3 shown posts appear on the home page. Drag ⠿ or use the arrows to reorder.')));
    if (!arr.length) { root.append(el('p', { class: 'empty' }, 'No posts yet. Click "New post" to write one.')); return; }
    const list = el('div', { class: 'list' });
    arr.forEach((p, i) => {
      const row = el('div', { class: 'row' + (p.visible === false ? ' off' : '') });
      row.append(dragHandle(row, arr, i),
        p.cover ? el('img', { class: 'thumb', src: imgSrc(p.cover), alt: '' }) : el('div', { class: 'thumb' }),
        el('div', {}, el('div', { class: 'rt' }, p.title || '(untitled)', p.visible === false && el('span', { class: 'badge' }, 'Hidden')),
          el('div', { class: 'rm' }, [fmtDate(p.date), p.author].filter(Boolean).join(' · '))),
        el('div', { class: 'ractions' }, visSwitch(p),
          btn('↑', () => move(arr, i, i - 1), 'ghost', 'Move up'), btn('↓', () => move(arr, i, i + 1), 'ghost', 'Move down'),
          btn('Edit', () => editPost(i), ''), btn('Delete', () => { if (confirm(`Delete "${p.title}"? Its page will be removed from the website.`)) { arr.splice(i, 1); render(); } }, 'danger')));
      list.append(row);
    });
    root.append(list);
  }

  // ------------------------------------------------------------------ GALLERY
  function viewGallery(root) {
    const arr = S.data.gallery;
    const file = el('input', { type: 'file', accept: 'image/*', multiple: true, hidden: true });
    file.addEventListener('change', async () => {
      const files = [...file.files];
      let ok = 0, bad = 0;
      const added = [];
      for (const f of files) {
        try { const path = await processImage(f, 1600); added.push({ id: 'g' + stamp() + rand(), src: path, caption: '', visible: true, featured: false }); ok++; }
        catch (e) { bad++; }
      }
      arr.unshift(...added);
      file.value = '';
      render();
      if (bad) toast(`${ok} added, ${bad} could not be read (try JPG or PNG).`, 'err'); else if (ok) toast(`${ok} photo${ok > 1 ? 's' : ''} added at the top. Add captions, then publish.`);
    });
    root.append(el('div', { class: 'toolbar' },
      el('button', { class: 'btn primary', type: 'button', on: { click: () => file.click() } }, '+ Add photos'), file,
      el('span', { class: 'hint' }, '★ = show on the home page (first 3 starred). "Show" controls whether a photo appears in the gallery. Drag ⠿ or use ← → to reorder.')));
    if (!arr.length) { root.append(el('p', { class: 'empty' }, 'No photos yet. Click "Add photos".')); return; }
    const grid = el('div', { class: 'ggrid' });
    arr.forEach((g, i) => {
      const card = el('div', { class: 'gcard' + (g.visible === false ? ' off' : '') });
      const cap = el('input', { type: 'text', value: g.caption || '', placeholder: 'Caption (optional)', 'aria-label': 'Caption', on: { input: () => { g.caption = cap.value; } } });
      const show = el('input', { type: 'checkbox', checked: g.visible !== false, on: { change: () => { g.visible = show.checked; render(); } } });
      const star = el('input', { type: 'checkbox', checked: !!g.featured, on: { change: () => { g.featured = star.checked; render(); } } });
      card.append(el('img', { src: imgSrc(g.src), alt: g.caption || '', loading: 'lazy' }),
        el('div', { class: 'gbody' }, cap,
          el('div', { class: 'gtools' }, dragHandle(card, arr, i),
            el('label', { class: 'check' }, show, 'Show'), el('label', { class: 'check', title: 'Show on home page' }, star, '★'),
            btn('←', () => move(arr, i, i - 1), 'ghost', 'Move earlier'), btn('→', () => move(arr, i, i + 1), 'ghost', 'Move later'),
            btn('✕', () => { if (confirm('Remove this photo from the gallery?')) { arr.splice(i, 1); render(); } }, 'danger', 'Delete photo'))));
      grid.append(card);
    });
    root.append(grid);
  }

  // ------------------------------------------------------------------ shell
  const TABS = [['events', 'Events', viewEvents], ['posts', 'Blog posts', viewPosts], ['gallery', 'Gallery', viewGallery]];
  function render() {
    const tabs = $('#tabs');
    tabs.replaceChildren(...TABS.map(([k, label]) => el('button', { class: 'tab', role: 'tab', type: 'button', 'aria-selected': String(S.tab === k), on: { click: () => { S.tab = k; render(); } } },
      label, el('span', { class: 'count' }, S.data[k].length))));
    const view = $('#view');
    view.replaceChildren();
    TABS.find((t) => t[0] === S.tab)[2](view);
    const n = changedKeys().length;
    const pub = $('#publish');
    pub.disabled = !(n || orphanPaths().length);
    pub.textContent = n ? `Publish changes (${n})` : 'Publish changes';
    const st = $('#status');
    st.textContent = n ? 'Unsaved changes: not on the website yet' : 'Everything is published';
    st.className = 'status' + (n ? ' dirty' : '');
  }

  function orphanPaths() {
    if (!S.remote) return [];
    const ref = referencedPaths();
    return S.remote.uploads.filter((p) => !ref.has(p));
  }

  // ------------------------------------------------------------------ publish
  function publishDialog() {
    const keys = changedKeys();
    const ref = referencedPaths();
    const newImgs = [...pending.keys()].filter((p) => ref.has(p));
    const orphans = orphanPaths();
    const names = { events: 'Events', posts: 'Blog posts', gallery: 'Gallery' };
    const body = el('div', {}, el('p', {}, 'You are about to update the live website with:'),
      el('ul', { class: 'summary' },
        ...keys.map((k) => el('li', {}, names[k] + ' changes')),
        newImgs.length ? el('li', {}, `${newImgs.length} new photo${newImgs.length > 1 ? 's' : ''}`) : null,
        orphans.length ? el('li', {}, `${orphans.length} unused uploaded photo${orphans.length > 1 ? 's' : ''} will be cleaned up`) : null),
      el('p', { class: 'muted' }, 'It takes about a minute for changes to appear. Every publish is saved in GitHub history, so it can be undone.'));
    openDialog('Publish to the website?', body, [
      el('button', { type: 'button', class: 'btn ghost', on: { click: closeDialog } }, 'Cancel'),
      el('button', { type: 'button', class: 'btn primary', on: { click: () => doPublish(keys, newImgs, orphans) } }, 'Publish now')]);
  }

  async function doPublish(keys, newImgs, orphansIn) {
    const steps = ['Checking the website for other changes', 'Uploading', 'Saving the new version', 'Publishing'];
    const list = el('ul', { class: 'progress' });
    const mark = (n) => list.replaceChildren(...steps.map((s, i) => el('li', { class: i < n ? 'done' : i === n ? 'now' : 'todo' }, s)));
    mark(0);
    openDialog('Publishing…', list, []);
    try {
      const base = await remoteMeta();
      for (const k of Object.keys(FILES)) {
        if ((base.shas[FILES[k]] || '') !== (S.remote.shas[FILES[k]] || '')) {
          throw new Error('The website was changed somewhere else since you opened this page. Please reload the page and make your edits again.');
        }
      }
      const orphans = orphansIn.filter((p) => base.uploads.includes(p));
      mark(1);
      const entries = [];
      for (const k of keys) {
        const b = await gh(`${R}/git/blobs`, { method: 'POST', body: { content: ser(S.data[k]), encoding: 'utf-8' } });
        entries.push({ path: FILES[k], mode: '100644', type: 'blob', sha: b.sha });
      }
      for (const p of newImgs) {
        const b = await gh(`${R}/git/blobs`, { method: 'POST', body: { content: await blobToB64(pending.get(p).blob), encoding: 'base64' } });
        entries.push({ path: p, mode: '100644', type: 'blob', sha: b.sha });
      }
      orphans.forEach((p) => entries.push({ path: p, mode: '100644', type: 'blob', sha: null }));
      mark(2);
      const tree = await gh(`${R}/git/trees`, { method: 'POST', body: { base_tree: base.treeSha, tree: entries } });
      const what = keys.map((k) => ({ events: 'events', posts: 'blog', gallery: 'gallery' }[k]));
      if (newImgs.length && !what.includes('gallery')) what.push('photos');
      const commit = await gh(`${R}/git/commits`, { method: 'POST', body: { message: `Admin: update ${what.join(', ') || 'site'}`, tree: tree.sha, parents: [base.head] } });
      mark(3);
      await gh(`${R}/git/refs/heads/${CFG.branch}`, { method: 'PATCH', body: { sha: commit.sha } });
      S.remote = await loadRemote();
      Object.keys(FILES).forEach((k) => { S.orig[k] = ser(S.data[k]); });
      newImgs.forEach((p) => pending.delete(p));
      render();
      openDialog('Published!', el('div', {},
        el('p', {}, 'Your changes were saved. The website will show them in about a minute.'),
        el('p', { class: 'muted' }, el('a', { href: `https://github.com/${CFG.owner}/${CFG.repo}/actions`, target: '_blank', rel: 'noopener' }, 'Watch the update progress on GitHub'))),
      [el('button', { type: 'button', class: 'btn primary', on: { click: closeDialog } }, 'Done')]);
    } catch (e) {
      if (e.status === 401 || e.status === 403) {
        openDialog('Could not publish', el('p', {}, 'GitHub did not accept your token (' + e.message + '). It may have expired, or it may not have "Contents: Read and write" permission. Sign out and sign in with a new token. Your edits are still on this page.'),
          [el('button', { type: 'button', class: 'btn primary', on: { click: closeDialog } }, 'OK')]);
      } else {
        openDialog('Could not publish', el('div', {}, el('p', {}, e.message || 'Something went wrong.'), el('p', { class: 'muted' }, 'Nothing was changed on the website. Your edits are still on this page.')),
          [el('button', { type: 'button', class: 'btn primary', on: { click: closeDialog } }, 'OK')]);
      }
    }
  }

  // ------------------------------------------------------------------ sign in / out
  function showLogin(msg) {
    $('#app').hidden = true; $('#login').hidden = false;
    const err = $('#login-err');
    err.hidden = !msg; err.textContent = msg || '';
  }

  async function start(t, remember) {
    token = t;
    const repo = await gh(R);
    if (!repo.permissions || !repo.permissions.push) throw new Error('This token can read the website but cannot change it. Create the token again with Contents set to "Read and write".');
    try { S.user = (await gh('/user')).login; } catch (e) { S.user = ''; }
    S.remote = await loadRemote();
    Object.keys(FILES).forEach((k) => { S.data[k] = clone(S.remote.data[k]); S.orig[k] = ser(S.remote.data[k]); });
    if (remember != null) tokenStore.set(t, remember);
    $('#login').hidden = true; $('#app').hidden = false;
    render();
  }

  $('#login-form').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const t = $('#token').value.trim();
    if (!t) return;
    const btnEl = ev.target.querySelector('button[type=submit]');
    btnEl.disabled = true; btnEl.textContent = 'Signing in…';
    try { await start(t, $('#remember').checked); $('#token').value = ''; }
    catch (e) {
      tokenStore.clear();
      showLogin(e.status === 401 ? 'GitHub did not accept that token. Please check it and try again.' : (e.message || 'Could not sign in.'));
    } finally { btnEl.disabled = false; btnEl.textContent = 'Sign in'; }
  });
  $('#signout').addEventListener('click', () => {
    if (isDirty() && !confirm('You have changes that are not published. Sign out and lose them?')) return;
    tokenStore.clear(); token = ''; S.remote = null; pending.clear(); location.reload();
  });
  $('#publish').addEventListener('click', publishDialog);
  window.addEventListener('beforeunload', (e) => { if (isDirty()) { e.preventDefault(); e.returnValue = ''; } });

  (async function init() {
    const saved = tokenStore.get();
    if (!saved) { showLogin(); return; }
    try { await start(saved, null); }
    catch (e) { tokenStore.clear(); showLogin(e.status === 401 ? 'Your saved sign-in expired. Please sign in again.' : (e.message || 'Could not load the website data.')); }
  })();
})();
