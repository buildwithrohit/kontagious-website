#!/usr/bin/env python3
"""Builds the Kontagious site into dist/ from templates in this file plus content/*.json."""
import os, re, sys, html

SITE = "https://www.kontagious.org"

# ---------------------------------------------------------------- images
IMG = {}
def reg(key, id_, ext, w=1000):
    IMG[key] = (id_, ext, w)

M = "2091bc_"
for k, i, e, w in [
    ("hero", M+"bb8b9b6d4f004130b0e5770d81d7f14f", "jpg", 1400),
    ("ev_thx_host", "a8263f_28b6aaa5fde74ada9d885bdd4f40c0f0", "jpg", 900),
    ("ev_thx_student", "a8263f_b1cc14ed120f42308dd6dcca18bd16ca", "jpeg", 900),
    ("ev_tahoe", M+"ac3826fbc965491aad219c62d0e20bf5", "webp", 900),
    ("ev_rare", "a8263f_72fe25afce744c8ca4da62138eef457a", "webp", 900),
    ("ev_airport", M+"0def467c49ea4818bc105ff6fa5da056", "webp", 900),
    # team
    ("t_john", M+"b052d4b4db884e689d99cd394fae90d8", "webp", 500),
    ("t_carol", "0a5baa_31d7e173fdcb4963b867020d8fa71a23", "jpg", 500),
    ("t_bob", "0a5baa_27c859e0d27c411eb73429e777554ab6", "jpg", 500),
    ("t_ken", "0a5baa_2fcf419009df48018cb18ba12adc6257", "jpg", 500),
    ("t_cathy", M+"09d7f4f58f3c4ed39f999ac64b39e8e4", "jpg", 500),
    ("t_samuel", M+"ceac4e3444154b599fb9f80d329e2e16", "jpg", 500),
    ("t_virendra", "0a5baa_7e0b168562f243708fcdc55598a82a35", "jpg", 500),
    ("t_maxine", "0a5baa_3da9d9972a524030b20db760a6eb6d8e", "jpg", 500),
    # initiatives
    ("i_rare", M+"28fb9b6e9888409ebd9de2f595310883", "webp", 900),
    ("i_rare2", M+"c94a180487d14f40ba7e7fa734c84ec2", "webp", 900),
    ("i_net", M+"5b2ab744bab84e71886fcbfb1322924e", "webp", 900),
    ("i_net2", M+"d275ca8fec174a5097821e8617ad7cee", "webp", 900),
    ("i_int", M+"eecfcb602ff449af8dd5b6301027467e", "webp", 900),
    ("i_int2", M+"e3f291642e8049aaa0f4f26360e5155a", "webp", 900),
    ("i_res", M+"868c6e9734cf4ceb824fc483acfb4d13", "webp", 900),
    ("i_res2", M+"042765c1bd2d4421aa78674b2e3c8daf", "webp", 900),
    # chapters
    ("c_banner", M+"591c72a5c8324232a99cd3d5c4e116b2", "webp", 1000),
    ("c_chat", M+"832b2b316664495f8ff8e5fa235db917", "webp", 900),
    ("c_breakfast", M+"bc393546bdf7497a996662bdaf2dfd0f", "webp", 900),
    ("c_handover", M+"f1a89404dc524f37a1a0ac2572e98d31", "webp", 900),
    ("c_leaders25", M+"d1d42d728ee94fbb97228f1d96084b20", "webp", 900),
    ("c_leaders24", M+"62448b51bed3441bb087a14ebac7d462", "webp", 900),
    # alumni
    ("a_party", M+"dfbdabf9faa144e39d9ffef30d101982", "webp", 900),
    ("a_peak", M+"98998fc907d9415fbcb452f3c10ab137", "webp", 900),
    ("a_monica", M+"a6d341fdf69748abb923a97019d49724", "webp", 900),
    ("a_meeting", M+"b92d19a912ab497d9fb70904045e641e", "webp", 900),
    ("a_bday", M+"124d83ec3cab4af692260150e3fb50f0", "webp", 900),
    # airport
    ("ap_new", M+"0b4229e7e1f44dfb98b7a8ac700f0dc5", "webp", 900),
    ("ap_miles", M+"904aefd13663490dbd534bc6a5c2b08c", "webp", 900),
    ("ap_dinner", M+"ee45fd4807474e0d826e3179522499b8", "webp", 900),
    ("ap_dinner2", M+"b5e96208afb64290a144adf352648e2a", "webp", 900),
    ("ap_team", M+"31f83337cc6646d2a70f37029f78e250", "webp", 900),
    # journey post
    ("j_head", M+"6ce5fb69_PLACEHOLDER", "webp", 1000),
    ("j_founders", M+"47e75058914b4c629e4f341fa4192167", "webp", 900),
    ("j_welcome", M+"d7b8150c270044d993bbe11c1b6606f0", "webp", 900),
    ("j_bags", M+"b44b04abb06545d99b38bb698fba31b4", "webp", 900),
    ("j_dinner", M+"d16b1dc1b10c4500b218ca19c338cf67", "webp", 900),
    ("j_connect", M+"e15721404f784a7e86bf18cb2852fe23", "webp", 900),
    ("j_smiles", M+"83b74e2ebd704f379b0ccb9db7f2c04c", "jpg", 900),
    ("j_class", M+"9d771178d6ac4bf1ba8ad3a522af13cc", "webp", 900),
    ("j_xmas", M+"277c0cb3302042efa400b96e181d019a", "webp", 900),
    ("j_hike", M+"49932b36ff9945f88f0ef8b59dd9824c", "jpg", 900),
    ("j_yosemite", M+"d7182edafbbe42d19d5373bfffd4d849", "jpg", 900),
    ("j_oranges", M+"949fb60cdd2d4998b7c32c328ad4dc1f", "webp", 900),
    ("j_grad", M+"0593581dcf16438db44bd602c411547f", "jpg", 900),
    ("j_music", M+"f9ad9437b78445e3b0d0f961f4d1c948", "jpg", 900),
    # story post
    ("s_head", M+"ff846b6640954b6f91a954172ff5995b", "jpg", 1000),
    ("s_founders", M+"ebb4d73fa23f45c0bb5a97e25b7a265f", "webp", 900),
    ("s_three", M+"d2d55ea3ed164b8fa79b4efdf7d3afc3", "webp", 900),
    ("s_campus", M+"1ce73c917c5d4f8589180d7bc7a8823c", "jpg", 900),
    ("s_covid", M+"cd46eebfb58e408f8d5bfa388762aa0a", "jpeg", 900),
    ("s_sara", M+"4eae4a14845a4f49ba58e59cc7fdda50", "webp", 900),
    ("s_game", M+"beb316e415ce447288f91eeb6653f57c", "webp", 900),
    ("s_fun", M+"1263c112d7d94efa98915205631e5cbc", "webp", 900),
    ("s_tahoe", M+"bfee213621b34e058d03245ca2f3ee53", "webp", 900),
    ("s_stranger", M+"95762ea432024ea28da192d7dc5139d4", "webp", 900),
    # networking post
    ("n_head", M+"5cd453d8c968499eb99b05c2632231d6", "webp", 1000),
    ("n_thumb", M+"eb9111bc34ba4e4ab646ea84daac2737", "webp", 1000),
    ("n_tahoe", M+"6cff9d1c4d034e5eb23437c9e1da9bfc", "webp", 900),
    ("n_mentor", M+"d80ac4cc94a74d5bb60be448fd1bc3f8", "webp", 900),
    ("n_parag", M+"9f958d491db1428885a443b5ff1580dc", "webp", 900),
    ("n_sarang", M+"de20ad2c30da4dd7b55a9494b30e1c39", "webp", 900),
    ("n_recipe", M+"0d37593fda7a4f68a2256c830fb330da", "webp", 900),
    ("n_one", M+"3c19b97c82b04a2182631d7fad9b7af1", "webp", 900),
    ("n_join", M+"9315091d87fc4e62b98c3a8ae977f39f", "webp", 900),
]:
    reg(k, i, e, w)

# journey header image is the same one used as its gallery thumb
IMG["j_head"] = (M+"6ce5fb690f40433784c1449bb5a581ab", "webp", 1000)

used = set()
def img(key, alt="", cls="", eager=False, w=None, h=None):
    used.add(key)
    id_, ext, _ = IMG[key]
    a = f' class="{cls}"' if cls else ""
    load = "" if eager else ' loading="lazy"'
    size = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img{a}{load} src="images/{id_}.{ext}" alt="{html.escape(alt, quote=True)}"{size}>'

def src(key):
    used.add(key)
    id_, ext, _ = IMG[key]
    return f"images/{id_}.{ext}"

# ---------------------------------------------------------------- shared
FORMS = {
    "airport": "https://docs.google.com/forms/d/1bT6y-pO45ZfVgnxeglYFhyEnm365pZKKPWVcGNbHIzs/viewform",
    "thx_host": "http://tiny.cc/kontagiousthanksgiving25",
    "thx_student": "https://forms.gle/DtaZCDbWAbgwv5gF9",
    "tahoe": "https://docs.google.com/forms/d/1H7GLR1oe40DrVWNaQ1uwRykrzk2yDxddsKkvImPqURQ/viewform",
    "rare": "https://docs.google.com/forms/d/e/1FAIpQLSdveQftgNRKNnxo53EuE8DY8KlhbWgimfwmzyJj0T9x_ZoLuw/viewform",
    "interview": "https://docs.google.com/forms/d/1PL9g0et1irnKmoh05A7Far-FkC5frfdPV9JaAaKtu28/viewform",
    "alumni": "https://docs.google.com/forms/d/e/1FAIpQLScR44AByFFgMfHNonVtaWUcBK3tEa7jdz8ZjXElKtYOM8Deuw/viewform",
    "gofundme": "https://gofund.me/02fe35f89",
}
FB = "https://www.facebook.com/groups/4126073314180195"
IG = "https://www.instagram.com/kontagious_community"
YT = "https://www.youtube.com/@kontagiouskindness"

NAV = [
    ("about.html", "About", "about"),
    ("events.html", "Events", "events"),
    ("get-involved.html", "Get involved", "involved"),
    ("gallery.html", "Gallery", "gallery"),
    ("blog.html", "Blog", "blog"),
    ("index.html#contact", "Contact", "contact"),
]

LOGO = ('<svg viewBox="0 0 64 64" width="34" height="34" aria-hidden="true"><rect width="64" height="64" rx="16" fill="currentColor"/>'
        '<path d="M18 38c4 9 24 9 28 0" stroke="#ff7a59" stroke-width="6" fill="none" stroke-linecap="round"/>'
        '<circle cx="23" cy="24" r="4" fill="#fff"/><circle cx="41" cy="24" r="4" fill="#fff"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%2314213d'/%3E"
           "%3Cpath d='M18 38c4 9 24 9 28 0' stroke='%23ff7a59' stroke-width='6' fill='none' stroke-linecap='round'/%3E"
           "%3Ccircle cx='23' cy='24' r='4' fill='%23fff'/%3E%3Ccircle cx='41' cy='24' r='4' fill='%23fff'/%3E%3C/svg%3E")

def page(fname, title, desc, body, active="", og_key="hero", home=False):
    cur = ' aria-current="page"'
    nav = "".join(
        f'<a href="{h}"{cur if a == active else ""}>{t}</a>' for h, t, a in NAV
    )
    full_title = "Kontagious | A home away from home for international students" if home else f"{title} | Kontagious"
    og_path = og_key if "/" in og_key else src(og_key)
    og = f"{SITE}/{og_path}"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="theme-color" content="#14213d">
<meta property="og:title" content="{html.escape(full_title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{og}">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="top">
  <div class="wrap bar">
    <a class="brand" href="index.html" aria-label="Kontagious home">{LOGO}<span>Kontagious</span></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    <nav id="nav" class="nav" aria-label="Main">
      {nav}
      <a class="btn btn-accent btn-sm" href="donate.html">Donate</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap foot">
    <p>&copy; <span id="year">2026</span> Kontagious. A 501(c)(3) nonprofit serving international students in Silicon Valley.</p>
    <p><a href="privacy.html">Privacy Policy</a> &middot; <a href="terms.html">Terms &amp; Conditions</a> &middot; <a href="{FB}">Facebook</a> &middot; <a href="{IG}">Instagram</a> &middot; <a href="{YT}">YouTube</a> &middot; <a href="#top">Back to top</a> &middot; <a href="admin/">Admin</a></p>
  </div>
</footer>
<script src="script.js" defer></script>
</body>
</html>
"""
    # every http(s) link leaves the site in a new tab
    def fix(m):
        tag = m.group(0)
        if "target=" in tag:
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'
    doc = re.sub(r'<a\b[^>]*\bhref="https?://[^"]*"[^>]*>', fix, doc)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(doc)

def hero(eyebrow, title, lead=""):
    l = f'<p class="lead">{lead}</p>' if lead else ""
    return f'''<section class="page-hero"><div class="wrap"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{l}</div></section>'''

def ps(items):
    return "".join(f"<p>{t}</p>" for t in items)

def cta(text, href, kind="accent"):
    return f'<a class="btn btn-{kind}" href="{href}">{text}</a>'

CONTACT_BLOCK = """<address>
  <p><b>Address</b><br>15585 Los Gatos Blvd<br>Los Gatos, CA 95032</p>
  <p><b>Phone</b><br><a href="tel:+14084219631">408.421.9631</a></p>
  <p><b>Email</b><br><a href="mailto:info@kontagious.org">info@kontagious.org</a></p>
</address>"""

def closing_cta():
    return f'''<section class="donate small"><div class="wrap donate-inner">
  <div><h2>Be the reason no student walks alone</h2>
  <p class="lead">Give, volunteer or host a student. Every bit of kindness counts.</p></div>
  <div class="give"><a class="btn btn-accent wide" href="donate.html">Donate</a><a class="btn btn-light wide" style="margin-top:10px" href="get-involved.html">Get involved</a></div>
</div></section>'''

def build_index(events, posts, gallery):
    vis_posts = [p for p in posts if p.get("visible", True)][:3]
    posts_html = "".join(post_card(p) for p in vis_posts)
    vis_g = [g for g in gallery if g.get("visible", True)]
    feat = [g for g in vis_g if g.get("featured")] or vis_g
    gal = "".join(f'<a href="gallery.html">{imgp(g["src"], g.get("caption", ""), w=640, h=360)}</a>' for g in feat[:3])
    body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Silicon Valley nonprofit</p>
      <h1>A home away from home, <em>starting with a smile.</em></h1>
      <p class="lead">Kontagious inspires ordinary people to practice intentional kindness toward international students who are new to our cities.</p>
      <div class="cta-row">{cta("Get involved", "get-involved.html")}{cta("See upcoming events", "events.html", "ghost")}</div>
    </div>
    <figure class="hero-img">{img("hero", "Students and volunteers gathered at a Kontagious event", eager=True, w=980, h=653)}</figure>
  </div>
</section>

<section class="stats" aria-label="Our impact">
  <div class="wrap stat-grid">
    <div class="stat"><b>26,780</b><span>Students touched by a gesture of kindness</span></div>
    <div class="stat"><b>1,245</b><span>Students in our leadership program</span></div>
    <div class="stat"><b>1,150</b><span>Events hosted</span></div>
    <div class="stat"><b>285</b><span>Volunteers</span></div>
    <div class="stat"><b>2</b><span>Campus communities</span></div>
  </div>
</section>

<section id="about" class="section">
  <div class="wrap two-col">
    <div><p class="eyebrow">About us</p><h2>Kindness that opens our communities</h2></div>
    <div class="prose">
      <p>We believe intentional kindness becomes the hope and light that opens our communities to families relocating from across the globe.</p>
      <p>Kontagious uses unconventional, entrepreneurial approaches to help newcomers feel at home in the multicultural mosaic of our cities. We develop technologies, incubate startups, make space for art and music, and enrich marriage and family life.</p>
      <p>Simple acts of love lead our communities toward new waves of inclusion. <strong>This is Kontagious.</strong></p>
      <p><a class="link-arrow" href="about.html">Meet the team and read our story &rarr;</a></p>
    </div>
  </div>
  <div class="wrap cards four" id="programs">
    <a class="card linkcard" href="airport-pickup.html"><span class="icon" aria-hidden="true">✈️</span><h3>Airport Pickup</h3><p>A friendly face meets you on arrival and gets you settled, stress-free.</p></a>
    <a class="card linkcard" href="events.html#thanksgiving-host"><span class="icon" aria-hidden="true">🏡</span><h3>Host Families</h3><p>Share a Thanksgiving table and give a student a taste of American home life.</p></a>
    <a class="card linkcard" href="initiatives.html"><span class="icon" aria-hidden="true">🌲</span><h3>Leadership &amp; Careers</h3><p>Rare Leadership, networking, interview prep and resume workshops.</p></a>
    <a class="card linkcard" href="chapters.html"><span class="icon" aria-hidden="true">🎓</span><h3>Chapters &amp; Alumni</h3><p>Student chapters on campus and an alumni network that keeps the kindness moving.</p></a>
  </div>
</section>

<section id="events" class="section tint">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Events</p><h2>Upcoming events</h2></div><a class="link-arrow" href="events.html">All events &rarr;</a></div>
    <div class="cards three" id="event-list">
{home_event_cards(events)}
    </div>
    <p class="empty" id="no-events" hidden>No events are scheduled right now. Check back soon, or <a href="#contact">get in touch</a>.</p>
  </div>
</section>

<section id="get-involved" class="section">
  <div class="wrap involve">
    <div>
      <p class="eyebrow">Get involved</p>
      <h2>Be the reason no student walks alone</h2>
      <p class="lead dark">Volunteer for an airport pickup, host a meal, mentor a student or help start a chapter. A few hours can change someone's first year in America.</p>
      {cta("See how to help", "get-involved.html")}
    </div>
    <ul class="ticks">
      <li>Pick up students at the airport</li>
      <li>Host a Thanksgiving or weekend meal</li>
      <li>Mentor a student or alum</li>
      <li>Help at events and camps</li>
      <li>Give monthly from $25</li>
    </ul>
  </div>
</section>

<section id="gallery" class="section tint">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Gallery</p><h2>Moments of welcome</h2></div><a class="link-arrow" href="gallery.html">See all photos &rarr;</a></div>
    <div class="gallery">{gal}</div>
  </div>
</section>

<section id="blog" class="section">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Blog</p><h2>Stories &amp; updates</h2></div><a class="link-arrow" href="blog.html">All stories &rarr;</a></div>
    <div class="cards three">{posts_html}</div>
  </div>
</section>

<section id="donate" class="donate">
  <div class="wrap donate-inner">
    <div><p class="eyebrow light">Donate</p><h2>Join the movement</h2>
    <p class="lead">Your gift funds airport rides, welcome meals and leadership programs that make a student's first months in America feel like home.</p></div>
    <div class="give">
      <div class="amounts" role="group" aria-label="Choose a gift amount">
        <a class="btn btn-light" href="donate.html">$25</a><a class="btn btn-light" href="donate.html">$50</a><a class="btn btn-light" href="donate.html">$100</a><a class="btn btn-light" href="donate.html">Other</a>
      </div>
      <a class="btn btn-accent wide" href="donate.html">Ways to give</a>
    </div>
  </div>
</section>

<section id="contact" class="section">
  <div class="wrap two-col">
    <div>
      <p class="eyebrow">Contact</p><h2>Say hello</h2>
      {CONTACT_BLOCK}
      <p class="social"><a href="{FB}">Facebook</a><a href="{IG}">Instagram</a><a href="{YT}">YouTube</a></p>
    </div>
    <form class="form" id="contact-form" action="mailto:info@kontagious.org" method="post" enctype="text/plain">
      <label>Name <input name="name" autocomplete="name" required></label>
      <label>Email <input type="email" name="email" autocomplete="email" required></label>
      <label>I'm interested in
        <select name="topic"><option>Volunteering</option><option>Hosting a student</option><option>Airport pickup</option><option>Starting a chapter</option><option>Something else</option></select>
      </label>
      <label>Message <textarea name="message" rows="4"></textarea></label>
      <button class="btn btn-accent" type="submit">Send message</button>
    </form>
  </div>
</section>'''
    page("index.html", "Home", "Kontagious is a Silicon Valley nonprofit that welcomes international students through airport pickups, host families, leadership programs and everyday acts of kindness.", body, home=True)


# ---------------------------------------------------------------- ABOUT / TEAM
TEAM = [
    ("t_john", "John Christian", "CEO", "A social entrepreneur with more than 30 years of community transformation work in India and the USA. He founded the Unwind Center in Chennai and focuses on developing leaders and building grassroots movements."),
    ("t_carol", "Carol Christian", "Director, Community Development", "American-born with Indian roots, Carol mentors young people by modeling positive behavior and shares practical strategies for developing leaders of character and compassion."),
    ("t_bob", "Bob Thomas", "Board Member", "A former college wrestler and national champion who went on to earn a Master of Divinity. He has spent decades mentoring youth, students and adults and connects Bay Area business leaders with new immigrants."),
    ("t_ken", "Ken Raasch", "Board Member", "About 30 years in art, entertainment, branding, retail and licensing. Ken founded Immersive Artistry, leads Creative Brands Group and founded the nonprofit Mercy Ventures."),
    ("t_cathy", "Cathy Smith", "Board Member", "CEO and President of ELREPCO, which serves technology clients in semiconductors, storage and power solutions. She supports Bay Area organizations including YoungLife and the San Jose Family Shelter."),
    ("t_samuel", "Samuel Chacko", "Board Member", "Raised in the UAE, Samuel learned to adapt across cultures from childhood. He is a Senior Engineering Manager at Apple and has lived in the Bay Area for over a decade."),
    ("t_virendra", "Virendra Vase", "Board Member", "Born and raised in India, with degrees in electrical and computer engineering. He has held technology roles at Yahoo, Experian and Salesforce, most recently as COO of Life360."),
    ("t_maxine", "Maxine Chicoine-Bagoye", "Lead Communications (Volunteer Leader)", "Grew up in California and built cross-cultural skills running an ESL business in Yokohama, Japan. She holds a chemistry degree from UC Santa Cruz and has a technology and marketing background."),
]

def build_about():
    body = hero("About us", "Where strangers become family",
                "Kontagious encourages ordinary people to practice intentional kindness toward those from other cultures, so newcomers to our cities feel at home.") + f'''
<section class="section"><div class="wrap two-col">
  <div><h2>Our mission</h2></div>
  <div class="prose">
    {ps(["Kontagious inspires ordinary people to embrace a lifestyle of intentional kindness toward those outside their own culture, creating a welcoming home away from home for people new to our cities. It all begins with a smile.",
         "We use unconventional and entrepreneurial approaches to help immigrants find their place in the multicultural mosaic of our communities: developing technologies, incubating startups, making space for art and music, and enriching marriage and family life."])}
    <p><a class="link-arrow" href="post-the-kontagious-story.html">Read the Kontagious story &rarr;</a></p>
  </div>
</div></section>

<section class="section tint"><div class="wrap">
  <div class="head"><div><p class="eyebrow">Explore</p><h2>More about Kontagious</h2></div></div>
  <div class="cards four" style="margin-top:0">
    <a class="card linkcard" href="#team"><span class="icon" aria-hidden="true">👋</span><h3>Meet our team</h3><p>The people who lead and serve.</p></a>
    <a class="card linkcard" href="initiatives.html"><span class="icon" aria-hidden="true">🚀</span><h3>High-impact initiatives</h3><p>Leadership, networking, interview prep and resumes.</p></a>
    <a class="card linkcard" href="chapters.html"><span class="icon" aria-hidden="true">🏫</span><h3>Student chapters</h3><p>Student-led communities at SJSU and Santa Clara.</p></a>
    <a class="card linkcard" href="alumni.html"><span class="icon" aria-hidden="true">🎓</span><h3>Alumni</h3><p>Graduates who stay and give back.</p></a>
  </div>
</div></section>

<section class="section" id="team"><div class="wrap">
  <div class="head"><div><p class="eyebrow">Our team</p><h2>Meet our team</h2></div></div>
  <div class="team">
''' + "".join(f'''    <article class="member">{img(k, n, w=294, h=306)}<h3>{n}</h3><p class="role">{r}</p><p>{b}</p></article>
''' for k, n, r, b in TEAM) + '''  </div>
</div></section>''' + closing_cta()
    page("about.html", "About", "Meet the Kontagious team and learn about our mission to welcome international students to Silicon Valley.", body, "about")

# ---------------------------------------------------------------- INITIATIVES
def build_initiatives():
    def block(title, who, paras, imgs, link=None, link_text="Register"):
        l = f'<p>{cta(link_text, link)}</p>' if link else ""
        im = "".join(img(k, a, w=640, h=380) for k, a in imgs)
        return f'''<section class="section {'tint' if block.n % 2 else ''}"><div class="wrap two-col">
  <div><h2>{title}</h2><p class="meta">{who}</p><div class="stack">{im}</div></div>
  <div class="prose">{ps(paras)}{l}</div>
</div></section>'''
    block.n = 0
    out = hero("High-impact initiatives", "Skills that last a career",
               "Peer-led programs that help students lead, connect and land their first roles in America.")
    for args in [
        ("RARE Leadership Program", "Led by Kim and Virendra Vase",
         ["A 6-week leadership course with 2-hour weekly sessions for a small group of 10 to 12 professionals or students, based on the book <em>Rare Leadership</em> by Marcus Warner and Jim Wilder.",
          "Couples lead the sessions and share personal experiences. Topics include leading with joy, staying relational under stress and building emotional maturity. Spots are limited."],
         [("i_rare", "Rare Leadership class"), ("i_rare2", "Diving into leadership with enthusiasm and fun")], FORMS["rare"], "Register for RARE"),
        ("Networking Events", "Led by Cathy Smith",
         ["Professional networking events connect students with seasoned professionals in Silicon Valley, a way to connect, learn and grow.",
          "A separate track on entrepreneurship is led by Julianne and Ken Raasch."],
         [("i_net", "Networking is key to the Kontagious experience"), ("i_net2", "Networking with Silicon Valley professionals")], FORMS["interview"], "Register for networking"),
        ("Interview Prep Program", "Led by alumni mentors Rohan Pandey, Sindhuja Ravi and Muteeb Akram",
         ["A peer-led program with two tracks. Level 1, <strong>Ace Your Internship Hunt</strong>, is for students starting their search, including those new to the U.S. Level 2, <strong>Conquer Full-Time Job Interviews</strong>, covers advanced technical and interview preparation.",
          "Sessions cover networking, handling tough interview questions and staying motivated through a job search."],
         [("i_int", "Interview night with alumni leaders"), ("i_int2", "Interview strategies with a personal touch")], FORMS["interview"], "Register for interview prep"),
        ("Resume Writing Workshop", "Led by Pramod",
         ["A hands-on workshop that helps participants build a resume that tells a compelling story and stands out to recruiters. Hundreds of students have been through it."],
         [("i_res", "Resume workshop led by Pramod"), ("i_res2", "Another resume writing workshop in action")], None),
    ]:
        out += block(*args)
        block.n += 1
    out += closing_cta()
    page("initiatives.html", "High-impact initiatives", "Leadership, networking, interview prep and resume programs for international students from Kontagious.", out, "about")

# ---------------------------------------------------------------- CHAPTERS
def build_chapters():
    body = hero("Student chapters", "Student-led, mentor-backed",
                "Kontagious chapters give international students a community on campus, built and led by students.") + f'''
<section class="section"><div class="wrap two-col">
  <div><h2>San Jos&eacute; State University</h2><div class="stack">{img("c_banner", "Kindness is Kontagious banner", w=640, h=380)}{img("c_leaders25", "SJSU chapter leaders 2025", w=640, h=380)}</div></div>
  <div class="prose">
    {ps(["The SJSU chapter is an officially recognized student organization. Each chapter has a student leadership team (a President, several Vice Presidents, a Treasurer and other members) with mentorship from the senior Kontagious team.",
         "Chapters focus on leadership development, campus culture and kindness toward newcomers, through leadership chats, breakfast meetings and a yearly Celebration of Leadership where presidents hand over their roles."])}
    <h3>Chapter leaders</h3>
    <ul class="plain">
      <li><b>2025:</b> Harshini (President), with Saurav, Mansi, Akshara and Mayuresh</li>
      <li><b>2024&ndash;25:</b> Nikita Sehgal (President), with Sai, Himani and Parag</li>
      <li><b>2023&ndash;24:</b> Sindhuja Ravi (President)</li>
      <li><b>2021&ndash;22:</b> Sparsha Ramakrishna (first Chapter President)</li>
      <li><b>Advisor:</b> Reeba Thomas</li>
    </ul>
  </div>
</div></section>

<section class="section tint"><div class="wrap">
  <div class="gallery">
    {img("c_chat", "Leadership chat with advisor Reeba Thomas", w=640, h=360)}
    {img("c_breakfast", "Chapter leadership meeting over breakfast", w=640, h=360)}
    {img("c_handover", "Presidential handover from Nikita to Harshini", w=640, h=360)}
  </div>
</div></section>

<section class="section"><div class="wrap two-col">
  <div><h2>Santa Clara University</h2></div>
  <div class="prose">{ps(["Our Santa Clara University chapter is growing as a thriving student community. Want to help lead it, or start a chapter at your own campus?"])}<p>{cta("Get in touch", "index.html#contact")}</p></div>
</div></section>''' + closing_cta()
    page("chapters.html", "Student chapters", "Student-led Kontagious chapters at San Jose State University and Santa Clara University.", body, "about")

# ---------------------------------------------------------------- ALUMNI
def build_alumni():
    body = hero("Alumni", "Graduated, not gone",
                "Our alumni network welcomes graduates of San Jos&eacute; State, Santa Clara and other U.S. universities who want a supportive home in the Bay Area.") + f'''
<section class="section"><div class="wrap two-col">
  <div><h2>Join the network</h2></div>
  <div class="prose">
    {ps(["Alumni stay connected through community gatherings, birthday celebrations, our annual Mission Peak trek in Fremont, and by mentoring the next wave of students.",
         "The Bay Area alumni chapter is led by <strong>Sindhuja Ravi</strong> and <strong>Juhi Malkani</strong>."])}
    <p>{cta("Join the alumni network", FORMS["alumni"])}</p>
  </div>
</div></section>
<section class="section tint"><div class="wrap"><div class="gallery">
  {img("a_party", "Alumni community celebration", w=640, h=360)}
  {img("a_peak", "Alumni and students on the Mission Peak trek", w=640, h=360)}
  {img("a_monica", "Monica and Rahul, Northwestern graduates in the alumni community", w=640, h=360)}
  {img("a_meeting", "Alumni meeting", w=640, h=360)}
  {img("a_bday", "Alumni birthday celebration", w=640, h=360)}
</div></div></section>''' + closing_cta()
    page("alumni.html", "Alumni", "Join the Kontagious alumni network for graduates in the San Francisco Bay Area.", body, "about")

# ---------------------------------------------------------------- AIRPORT
def build_airport():
    steps = [
        "Submit your arrival information through the sign-up form.",
        "Receive a confirmation email. There is no need to resubmit.",
        "Join a required Zoom call so we can confirm your identity and share arrival tips on immigration, baggage claim and meeting points.",
        "Get added to a WhatsApp group with others arriving around the same time.",
        "Meet a Kontagious welcomer at the airport. We track your flight, even if it is delayed.",
        "A volunteer drives you to your accommodation. Please confirm your address and tell us right away if it changes.",
    ]
    li = "".join(f"<li>{s}</li>" for s in steps)
    body = hero("Airport pickup", "Your first stop in America should feel welcoming",
                "A free, volunteer-run service for new students at San Jos&eacute; State University and Santa Clara University.") + f'''
<section class="section"><div class="wrap two-col">
  <div><h2>Who it's for</h2>{img("ap_new", "New home, new journey", w=640, h=380)}</div>
  <div class="prose">
    {ps(["Pickup is for <strong>new, incoming students</strong> enrolled at SJSU or Santa Clara University who are flying into SFO or SJC for the first time to begin their studies.",
         "It is not available to continuing students or to students already in the U.S. who are relocating or returning.",
         "Typical pickup windows: SJSU from July 15 to August 15, and SCU in July. Dates are confirmed each year."])}
    <p>{cta("Sign up for pickup", FORMS["airport"])}</p>
  </div>
</div></section>
<section class="section tint"><div class="wrap two-col">
  <div><h2>How it works</h2></div>
  <div class="prose"><ol class="steps">{li}</ol>
  <p>Information is verified, including admission details. If someone intentionally gives false information, they may be responsible for any resulting costs.</p></div>
</div></section>
<section class="section"><div class="wrap two-col">
  <div><h2>Welcome dinners</h2></div>
  <div class="prose">{ps(["Free transportation is included and anyone can attend, even without using airport pickup. Registration is required through a separate link we send after you sign up for pickup."])}</div>
</div></section>
<section class="section tint"><div class="wrap"><div class="gallery">
  {img("ap_miles", "So many miles traveled", w=640, h=360)}
  {img("ap_dinner", "From strangers to family at a welcome dinner", w=640, h=360)}
  {img("ap_team", "The 2025-26 volunteer team", w=640, h=360)}
</div></div></section>''' + closing_cta()
    page("airport-pickup.html", "Airport pickup", "Free airport pickup for new SJSU and Santa Clara University students arriving in San Jose, run by Kontagious volunteers.", body, "events", og_key="ev_airport")

# ---------------------------------------------------------------- GET INVOLVED
def build_involved():
    roles = [
        ("Student Chapter", "A graduate student group that hikes, camps, shares meals and offers academic and professional development."),
        ("Pickleball Club", "A community and leadership program that focuses on character rather than competition."),
        ("Midweek Hiking Initiative", "Weekly hikes that build skills such as pitching ideas, setting boundaries and living by core values."),
        ("Alumni &amp; Volunteer Team", "Volunteers drive, lead seminars and welcome international students at airport pickups."),
        ("Resource &amp; Leadership Team", "Professionals share expertise, such as entrepreneurship and finance, and help organize networking events."),
        ("Donor Partnership", "Monthly gifts starting at $25 support the mission all year."),
        ("Mentoring &amp; Tech Team", "Mentor graduate students and alumni, or contribute your skills to our technology work."),
        ("Community Service", "Trunk-or-treat events and help preparing for university orientations and airport pickups."),
    ]
    cards = "".join(f'<article class="card"><h3>{t}</h3><p>{d}</p></article>' for t, d in roles)
    body = hero("Get involved", "Join the movement",
                "Kontagious is a welcoming community in California for people building friendships and growing together.") + f'''
<section class="section"><div class="wrap">
  <div class="cards three" style="margin-top:0">{cards}</div>
</div></section>
<section class="section tint"><div class="wrap two-col">
  <div><h2>Ready to help?</h2></div>
  <div class="prose">
    {ps(["Tell us which team sounds like you and we will point you to the right person. You can also reach us on Instagram or Facebook."])}
    <p>{cta("Email us", "mailto:info@kontagious.org")} {cta("Donate", "donate.html", "ghost")}</p>
    <p class="social"><a href="{IG}">Instagram</a><a href="{FB}">Facebook</a><a href="{YT}">YouTube</a></p>
  </div>
</div></section>'''
    page("get-involved.html", "Get involved", "Volunteer, mentor, host or give: ways to get involved with Kontagious.", body, "involved")

# ---------------------------------------------------------------- DONATE
def build_donate():
    body = hero("Donate", "Join the movement",
                "Your gift funds airport rides, welcome meals and leadership programs that make a student's first months in America feel like home. Kontagious is a 501(c)(3) tax-exempt organization, so contributions may be tax-deductible.") + f'''
<section class="section" id="give"><div class="wrap">
  <div class="cards three" style="margin-top:0">
    <article class="card"><span class="icon" aria-hidden="true">💙</span><h3>GoFundMe</h3><p>Give online in a few clicks.</p><p>{cta("Give on GoFundMe", FORMS["gofundme"])}</p></article>
    <article class="card"><span class="icon" aria-hidden="true">🏦</span><h3>Zelle</h3><p>One-time or recurring monthly gifts, bank to bank. Send to <b>admin@kontagious.org</b>, then email us so we can send your tax-deduction certificate.</p></article>
    <article class="card"><span class="icon" aria-hidden="true">✉️</span><h3>Check or bill pay</h3><p>Make checks payable to <b>Kontagious</b> and mail to:<br>15585 Los Gatos Blvd<br>Los Gatos, CA 95032</p></article>
    <article class="card"><span class="icon" aria-hidden="true">📈</span><h3>Stock donations</h3><p>Gifts of appreciated stock can offer tax advantages.</p><p><a class="link-arrow" href="#stock">Stock instructions &darr;</a></p></article>
    <article class="card"><span class="icon" aria-hidden="true">🏢</span><h3>Corporate matching</h3><p>Many employers match gifts. We are registered with Benevity, Bright Funds and Network for Good.</p><p><a class="link-arrow" href="#match">Matching details &darr;</a></p></article>
    <article class="card"><span class="icon" aria-hidden="true">📞</span><h3>Questions?</h3><p>Call <a href="tel:+14084219631">408.421.9631</a> or email <a href="mailto:info@kontagious.org">info@kontagious.org</a>.</p></article>
  </div>
</div></section>

<section class="section tint" id="stock"><div class="wrap two-col">
  <div><h2>Donating stock</h2></div>
  <div class="prose">
    <ol class="steps">
      <li>Email <a href="mailto:info@kontagious.org">info@kontagious.org</a> before the transfer so we can track your gift.</li>
      <li>Ask your broker or financial advisor to transfer the shares, using the details below.</li>
      <li>Sign your brokerage's gifting form. We will send an acknowledgement letter once the gift arrives.</li>
    </ol>
    <table class="kv">
      <tr><th>Receiving firm</th><td>LPL Financial, 3941 Park Drive, Suite 20, #138, El Dorado Hills, CA 95762</td></tr>
      <tr><th>DTC number</th><td>0075</td></tr>
      <tr><th>Account number</th><td>3669-7570</td></tr>
      <tr><th>Account title</th><td>Kontagious</td></tr>
    </table>
    <p class="note">You and your tax advisor determine the gift's value for tax purposes. See IRS Publications 526 and 561.</p>
  </div>
</div></section>

<section class="section" id="match"><div class="wrap two-col">
  <div><h2>Corporate matching</h2></div>
  <div class="prose">
    {ps(["Check your employer's giving portal first: Kontagious is already registered with Benevity, Bright Funds and Network for Good. Your company may also offer volunteer grants.",
         "If we are not listed, use these details to register us with your company's matching program."])}
    <table class="kv">
      <tr><th>Status</th><td>501(c)(3) nonprofit</td></tr>
      <tr><th>EIN</th><td>81-3433550</td></tr>
      <tr><th>Mailing address</th><td>Kontagious, 15585 Los Gatos Blvd, Los Gatos, CA 95032</td></tr>
      <tr><th>Contact</th><td>info@kontagious.org &middot; 408.421.9631</td></tr>
    </table>
  </div>
</div></section>
'''
    page("donate.html", "Donate", "Give to Kontagious by GoFundMe, Zelle, check, stock or corporate match. Kontagious is a 501(c)(3) nonprofit.", body, "donate")

# ---------------------------------------------------------------- LEGAL
def build_legal():
    priv = f'''{hero("Legal", "Privacy Policy", "Last updated: October 2026")}
<section class="section"><div class="wrap narrow prose legal">
{ps(["Kontagious (&ldquo;we&rdquo;, &ldquo;us&rdquo;) respects your privacy. This policy explains what information we collect through this website and how we use it."])}
<h2>Information we collect</h2>
{ps(["<b>Information you send us.</b> If you email us or use the contact form, we receive your name, email address and message. If you sign up for an event, program or airport pickup, the information you enter goes to us through a Google Form and is governed by Google's privacy policy in addition to this one.",
     "<b>Website visit data.</b> Our website host may keep standard server logs, such as IP address, browser type and pages visited. We do not run advertising trackers on this site."])}
<h2>How we use it</h2>
{ps(["We use your information to respond to you, run events and programs, match students with volunteers and hosts, send acknowledgements and tax receipts for gifts, and keep our community informed. We do not sell your personal information."])}
<h2>Sharing</h2>
{ps(["We share information only with the volunteers and partners who need it to run a program, with service providers who help us operate (for example, payment and form providers), or when required by law."])}
<h2>Donations</h2>
{ps(["Gifts made through GoFundMe, Zelle, your bank or a brokerage are processed by those providers under their own policies. We keep a record of gifts so we can issue receipts and meet our legal obligations as a 501(c)(3) nonprofit."])}
<h2>Children</h2>
{ps(["Our programs serve university students and adults. We do not knowingly collect information from children under 13."])}
<h2>Your choices</h2>
{ps(["You can ask us to see, correct or delete the personal information we hold about you by emailing <a href=\"mailto:info@kontagious.org\">info@kontagious.org</a>."])}
<h2>Changes</h2>
{ps(["We may update this policy and will post the new date above."])}
<h2>Contact</h2>
{CONTACT_BLOCK}
</div></section>'''
    terms = f'''{hero("Legal", "Terms &amp; Conditions", "Last updated: October 2026")}
<section class="section"><div class="wrap narrow prose legal">
{ps(["By using this website you agree to these terms. If you do not agree, please do not use the site."])}
<h2>About this site</h2>
{ps(["This website is run by Kontagious, a 501(c)(3) nonprofit (EIN 81-3433550), to share information about our programs and events. Information is provided in good faith and may change; event dates and details are confirmed through each sign-up."])}
<h2>Using the site</h2>
{ps(["You may use the site for lawful purposes only. Please do not misuse it, attempt to disrupt it, or submit false information through our forms. Airport pickup and event sign-ups require accurate information, and people who intentionally provide false information may be responsible for resulting costs."])}
<h2>Donations</h2>
{ps(["Kontagious is a tax-exempt 501(c)(3) organization and contributions may be tax-deductible to the extent the law allows. Please consult your tax advisor. Gifts are generally non-refundable."])}
<h2>Content and ownership</h2>
{ps(["The text, photos and design on this site belong to Kontagious or are used with permission. Please ask before reusing them."])}
<h2>Links to other sites</h2>
{ps(["We link to outside services such as Google Forms, GoFundMe and social media. We do not control them and are not responsible for their content or practices."])}
<h2>No warranty and limits of liability</h2>
{ps(["The site is provided &ldquo;as is&rdquo;. To the fullest extent permitted by law, Kontagious is not liable for losses arising from your use of the site."])}
<h2>Changes</h2>
{ps(["We may update these terms and will post the new date above."])}
<h2>Contact</h2>
{CONTACT_BLOCK}
</div></section>'''
    page("privacy.html", "Privacy Policy", "How Kontagious collects, uses and protects your information.", priv, "")
    page("terms.html", "Terms & Conditions", "Terms for using the Kontagious website.", terms, "")

# ---------------------------------------------------------------- 404
def build_404():
    body = hero("Page not found", "We couldn't find that page", "Try the home page or pick a section from the menu.") + f'''<section class="section"><div class="wrap">{cta("Back to home", "index.html")}</div></section>'''
    page("404.html", "Page not found", "Page not found.", body, "")


# ================================================================ data-driven pages
import json, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "dist")

def load(name):
    with open(os.path.join(ROOT, "content", name + ".json"), encoding="utf-8") as f:
        return json.load(f)

def esc(s):
    return html.escape(s or "", quote=True)

URL_OK = re.compile(r"^(https?://|mailto:|tel:|#|[\w./%-]+(#[\w-]+)?$)", re.I)

def inline_md(s):
    """Tiny, safe markdown: **bold**, *italic*, [text](url). Everything else is escaped."""
    s = html.escape(s or "", quote=False)
    def link(m):
        url = m.group(2).replace("&amp;", "&")
        if not URL_OK.match(url):
            return m.group(0)
        return f'<a href="{html.escape(url, quote=True)}">{m.group(1)}</a>'
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s.replace("\n", "<br>")

def paras(text):
    return "".join(f"<p>{inline_md(t.strip())}</p>" for t in re.split(r"\n\s*\n", text or "") if t.strip())

def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s or "")
    return re.sub(r"[*_]", "", s)

def fmt_date(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    except Exception:
        return iso or ""

def imgp(path, alt="", cls="", eager=False, w=None, h=None):
    a = f' class="{cls}"' if cls else ""
    load_attr = "" if eager else ' loading="lazy"'
    size = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img{a}{load_attr} src="{esc(path)}" alt="{esc(alt)}"{size}>'

def safe_href(u):
    u = (u or "").strip()
    return u if URL_OK.match(u) else "#"

# ---------------------------------------------------------------- events
def event_visible(items):
    return [e for e in items if e.get("visible", True)]

def event_when_html(e):
    sd, label = e.get("startDate") or "", e.get("dateLabel") or ""
    if not label:
        return ""
    return f'<time datetime="{esc(sd)}">{esc(label)}</time>' if sd else esc(label)

def home_event_cards(events):
    out = []
    for e in event_visible(events):
        if not e.get("home", True):
            continue
        end = f' data-end="{esc(e["endDate"])}"' if e.get("endDate") else ""
        meta = " &middot; ".join(x for x in [event_when_html(e), esc(e.get("where", ""))] if x)
        im = imgp(e["image"], "", w=640, h=360) if e.get("image") else ""
        out.append(f'''<article class="event card"{end}>
  {im}
  <div class="event-body">
    <p class="meta">{meta}</p>
    <h3>{esc(e["title"])}</h3>
    <p>{esc(e.get("short", ""))}</p>
    <a class="link-arrow" href="events.html#{esc(e["id"])}">Details &amp; sign-up &rarr;</a>
  </div>
</article>''')
    return "\n".join(out[:6])

def build_events(events):
    items = ""
    for e in event_visible(events):
        end = f' data-end="{esc(e["endDate"])}"' if e.get("endDate") else ""
        im = f'<div class="ef-img">{imgp(e["image"], "", w=640, h=360)}</div>' if e.get("image") else ""
        facts = []
        if e.get("when"): facts.append(f"<b>When:</b> {esc(e['when'])}")
        if e.get("where"): facts.append(f"<b>Where:</b> {esc(e['where'])}")
        facts_html = f'<p class="facts">{"<br>".join(facts)}</p>' if facts else ""
        btn = f'<p>{cta(esc(e.get("ctaText") or "Learn more"), esc(safe_href(e["ctaUrl"])))}</p>' if e.get("ctaUrl") else ""
        solo = "" if e.get("image") else " noimg"
        items += f'''<article class="event-full card{solo}" id="{esc(e["id"])}"{end}>
  {im}
  <div class="ef-body">
    <p class="meta">{event_when_html(e)}</p>
    <h2>{esc(e["title"])}</h2>
    {facts_html}
    {paras(e.get("details") or e.get("short", ""))}
    {btn}
  </div>
</article>'''
    body = hero("Events", "Upcoming events", "Dinners, camps, workshops and welcomes. Everyone is invited.") + f'''
<section class="section tint"><div class="wrap">
  <div class="stackc" id="event-list">
    {items}
  </div>
  <p class="empty" id="no-events" hidden>No events are scheduled right now. Check back soon, or <a href="index.html#contact">get in touch</a>.</p>
</div></section>
<section class="section"><div class="wrap two-col">
  <div><h2>Want to help at an event?</h2></div>
  <div class="prose"><p>Volunteers drive, cook, host, mentor and lead. There is a place for you.</p><p>{cta("Get involved", "get-involved.html")}</p></div>
</div></section>'''
    page("events.html", "Events", "Upcoming Kontagious events for international students: dinners, leadership camps, workshops and airport pickup.", body, "events")

# ---------------------------------------------------------------- blog
def post_file(p):
    return f"post-{p['slug']}.html"

def post_blurb(p):
    if p.get("blurb"):
        return p["blurb"]
    for b in p.get("blocks", []):
        if b.get("type") == "paragraph" and b.get("text"):
            t = plain(b["text"]).strip()
            return t if len(t) <= 170 else t[:167].rsplit(" ", 1)[0] + "…"
    return ""

def video_html(url):
    m = re.search(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})", url or "")
    if m:
        return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{m.group(1)}" title="Video" loading="lazy" '
                'allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>')
    m = re.search(r"vimeo\.com/(\d+)", url or "")
    if m:
        return f'<div class="video"><iframe src="https://player.vimeo.com/video/{m.group(1)}" title="Video" loading="lazy" allowfullscreen></iframe></div>'
    return f'<p><a href="{esc(safe_href(url))}">Watch the video</a></p>'

def blocks_html(blocks):
    out = []
    for b in blocks:
        t = b.get("type")
        if t == "heading":
            out.append(f"<h2>{esc(b.get('text'))}</h2>")
        elif t == "paragraph":
            out.append(f"<p>{inline_md(b.get('text'))}</p>")
        elif t == "image" and b.get("src"):
            cap = b.get("caption") or ""
            alt = b.get("alt") or cap
            fc = f"<figcaption>{esc(cap)}</figcaption>" if cap else ""
            out.append(f'<figure>{imgp(b["src"], alt, w=900, h=600)}{fc}</figure>')
        elif t == "list":
            tag = "ol" if b.get("ordered") else "ul"
            lis = "".join(f"<li>{inline_md(i)}</li>" for i in b.get("items", []) if i.strip())
            out.append(f'<{tag} class="bullets">{lis}</{tag}>')
        elif t == "quote":
            out.append(f"<blockquote>{inline_md(b.get('text'))}</blockquote>")
        elif t == "video":
            out.append(video_html(b.get("url")))
        elif t == "button" and b.get("url"):
            out.append(f'<p>{cta(esc(b.get("text") or "Learn more"), esc(safe_href(b["url"])))}</p>')
    return "\n".join(out)

def post_card(p):
    cover = imgp(p["cover"], "", w=640, h=360) if p.get("cover") else ""
    thumb = f'<a href="{post_file(p)}" class="thumb" tabindex="-1" aria-hidden="true">{cover}</a>' if cover else ""
    return f'''<article class="card post">
  {thumb}
  <p class="meta">{fmt_date(p.get("date"))} &middot; {esc(p.get("author"))}</p>
  <h3><a href="{post_file(p)}">{esc(p["title"])}</a></h3>
  <p>{esc(post_blurb(p))}</p>
  <a class="link-arrow" href="{post_file(p)}">Read story &rarr;</a>
</article>'''

def build_blog(posts):
    vis = [p for p in posts if p.get("visible", True)]
    cards = "".join(post_card(p) for p in vis)
    empty = '<p class="empty">No stories yet. Check back soon.</p>' if not vis else ""
    body = hero("Blog", "Stories &amp; updates", "How Kontagious welcomes, connects and grows international students.") + f'''
<section class="section"><div class="wrap"><div class="cards three" style="margin-top:0">{cards}</div>{empty}</div></section>'''
    page("blog.html", "Blog", "Stories and updates from Kontagious.", body, "blog", og_key=(vis[0]["cover"] if vis and vis[0].get("cover") else "hero"))

def build_posts(posts):
    for p in posts:
        if not p.get("visible", True):
            continue
        inline_srcs = {b.get("src") for b in p.get("blocks", []) if b.get("type") == "image"}
        cover = ""
        if p.get("cover") and p["cover"] not in inline_srcs:
            cover = imgp(p["cover"], p["title"], eager=True, w=1000, h=560, cls="post-cover")
        body = f'''<article class="post-page">
<header class="post-head"><div class="wrap narrow"><p class="eyebrow"><a href="blog.html">&larr; Blog</a></p><h1>{esc(p["title"])}</h1>
<p class="meta">{fmt_date(p.get("date"))} &middot; By {esc(p.get("author"))}</p></div></header>
<div class="wrap narrow article">
{cover}
{blocks_html(p.get("blocks", []))}
<hr><p class="more"><a class="link-arrow" href="blog.html">&larr; More stories</a></p>
</div></article>''' + closing_cta()
        page(post_file(p), p["title"], post_blurb(p), body, "blog", og_key=(p.get("cover") or "hero"))

# ---------------------------------------------------------------- gallery
def build_gallery(items):
    vis = [g for g in items if g.get("visible", True)]
    g = "".join(f'<figure>{imgp(i["src"], i.get("caption", ""), w=640, h=480)}' + (f'<figcaption>{esc(i["caption"])}</figcaption>' if i.get("caption") else "") + "</figure>" for i in vis)
    empty = '<p class="empty">No photos yet.</p>' if not vis else ""
    body = hero("Gallery", "Moments of welcome", "A look at dinners, hikes, camps and celebrations with our community.") + f'''
<section class="section"><div class="wrap"><div class="photos">{g}</div>{empty}</div></section>''' + closing_cta()
    page("gallery.html", "Gallery", "Photos from Kontagious dinners, camps, hikes and celebrations.", body, "gallery")

# ---------------------------------------------------------------- main
def check_images():
    missing = set()
    for fn in os.listdir(OUT):
        if fn.endswith(".html"):
            for m in re.finditer(r'(?:src|content)="(?:https://www\.kontagious\.org/)?(images/[^"]+)"', open(os.path.join(OUT, fn), encoding="utf-8").read()):
                if not os.path.exists(os.path.join(ROOT, m.group(1))):
                    missing.add(m.group(1))
    return sorted(missing)

def main():
    events, posts, gallery = load("events"), load("posts"), load("gallery")
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    build_index(events, posts, gallery)
    build_about(); build_initiatives(); build_chapters(); build_alumni()
    build_events(events); build_airport(); build_involved()
    build_blog(posts); build_posts(posts); build_gallery(gallery)
    build_donate(); build_legal(); build_404()
    for f in ("style.css", "script.js", "CNAME"):
        if os.path.exists(os.path.join(ROOT, f)):
            shutil.copy(os.path.join(ROOT, f), OUT)
    for d in ("images", "admin"):
        if os.path.isdir(os.path.join(ROOT, d)):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /admin/\n")
    missing = check_images()
    pages = len([f for f in os.listdir(OUT) if f.endswith(".html")])
    print(f"Built {pages} pages into {OUT}")
    if missing:
        print(f"WARNING: {len(missing)} image(s) referenced but not in images/ (run scripts/download-images.sh):")
        for m in missing[:15]:
            print("  ", m)

if __name__ == "__main__":
    main()
