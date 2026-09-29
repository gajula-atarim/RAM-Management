#!/usr/bin/env python3
"""Generate the Elementor data for the RAM Management site (English).

Writes one JSON file per document into ../elementor/:
  kit-settings.json  Elementor Site Settings (global colours, fonts, layout)
  header.json        Saved template used as the site header
  footer.json        Saved template used as the site footer
  home.json, about.json, contact.json  Page layouts

Every section is a real Elementor container with standard widgets, so all
copy, images, colours and spacing stay editable in the Elementor panel.
The few effects Elementor Free can't express (multi-element hovers, rings,
pill nav) are handled by classes styled in the child theme's assets/css/ram.css.

Usage: python3 tools/build_elementor.py
"""

import hashlib
import json
from pathlib import Path

SITE = "https://ram-management.wsdfy.com"
OUT = Path(__file__).resolve().parent.parent / "elementor"

# Media library attachment IDs on ram-management.wsdfy.com.
MEDIA = {
    "logo": (7, "ram-logo.png"),
    "logo_white": (8, "ram-logo-white.png"),
    "home_hero": (9, "home-hero-montreal-skyline.jpg"),
    "about_hero": (10, "about-hero-montreal-skyline.jpg"),
    "justice": (11, "about-lady-justice.jpg"),
    "tax_forms": (12, "about-quote-tax-forms.jpg"),
    "handshake": (13, "contact-hero-handshake.jpg"),
}

NAVY = "#063F57"
NAVY_DARK = "#052C3D"
BLUE = "#095D7F"
GOLD = "#B08D57"
GOLD_LIGHT = "#D9BF8F"
INK = "#211F20"
GREY = "#5E6366"
WHITE = "#FFFFFF"

SERIF = "Source Serif 4"
SANS = "Jost"

# ---------------------------------------------------------------- helpers

_counter = {"n": 0}


def eid(seed):
    """Stable 7-char element id, so regenerating keeps ids unchanged."""
    _counter["n"] += 1
    return hashlib.md5(f"{seed}-{_counter['n']}".encode()).hexdigest()[:7]


def media(key):
    mid, name = MEDIA[key]
    return {"url": f"{SITE}/wp-content/uploads/2026/09/{name}", "id": mid, "source": "library", "alt": "", "size": ""}


def px(size):
    return {"unit": "px", "size": size, "sizes": []}


def box(top, right=None, bottom=None, left=None, unit="px"):
    right = top if right is None else right
    bottom = top if bottom is None else bottom
    left = right if left is None else left
    linked = top == right == bottom == left
    return {"unit": unit, "top": str(top), "right": str(right), "bottom": str(bottom), "left": str(left), "isLinked": linked}


def gap(column, row=None):
    row = column if row is None else row
    return {"column": str(column), "row": str(row), "isLinked": column == row, "unit": "px", "size": column}


def typo(prefix="typography", family=None, size=None, weight=None, lh=None, ls=None, size_t=None, size_m=None, lh_unit="em", transform=None):
    s = {f"{prefix}_typography": "custom"}
    if family:
        s[f"{prefix}_font_family"] = family
    if size is not None:
        s[f"{prefix}_font_size"] = px(size)
    if size_t is not None:
        s[f"{prefix}_font_size_tablet"] = px(size_t)
    if size_m is not None:
        s[f"{prefix}_font_size_mobile"] = px(size_m)
    if weight:
        s[f"{prefix}_font_weight"] = str(weight)
    if lh is not None:
        s[f"{prefix}_line_height"] = {"unit": lh_unit, "size": lh, "sizes": []}
    if ls is not None:
        s[f"{prefix}_letter_spacing"] = px(ls)
    if transform:
        s[f"{prefix}_text_transform"] = transform
    return s


def container(seed, settings, children, inner=False):
    base = {"flex_direction": "column"}
    base.update(settings)
    return {"id": eid(seed), "elType": "container", "isInner": inner, "settings": base, "elements": children}


def widget(seed, wtype, settings):
    return {"id": eid(seed), "elType": "widget", "widgetType": wtype, "isInner": False, "settings": settings, "elements": []}


def section_padding(top, bottom, side=32, top_m=None, bottom_m=None, side_m=20):
    s = {"padding": box(top, side, bottom, side)}
    s["padding_mobile"] = box(top_m if top_m is not None else round(top * 0.7), side_m, bottom_m if bottom_m is not None else round(bottom * 0.7), side_m)
    return s


def boxed(width=1040):
    return {"content_width": "boxed", "boxed_width": px(width)}


def bg_image(key, ypos=50, xpos=50):
    return {
        "background_background": "classic",
        "background_image": media(key),
        "background_position": "initial",
        "background_xpos": {"unit": "%", "size": xpos, "sizes": []},
        "background_ypos": {"unit": "%", "size": ypos, "sizes": []},
        "background_repeat": "no-repeat",
        "background_size": "cover",
    }


def overlay_gradient(color_a, color_b, angle, stop_b=100):
    return {
        "background_overlay_background": "gradient",
        "background_overlay_color": color_a,
        "background_overlay_color_stop": {"unit": "%", "size": 0, "sizes": []},
        "background_overlay_color_b": color_b,
        "background_overlay_color_b_stop": {"unit": "%", "size": stop_b, "sizes": []},
        "background_overlay_gradient_type": "linear",
        "background_overlay_gradient_angle": {"unit": "deg", "size": angle, "sizes": []},
        "background_overlay_opacity": {"unit": "px", "size": 1, "sizes": []},
    }


def heading(seed, text, tag="h2", color=WHITE, align=None, classes="", **t):
    s = {"title": text, "header_size": tag, "title_color": color}
    s.update(typo(**t))
    if align:
        s["align"] = align
    if classes:
        s["_css_classes"] = classes
    return widget(seed, "heading", s)


def text(seed, html, color=INK, align=None, classes="", p_spacing=None, width=None, width_t=None, **t):
    s = {"editor": html, "text_color": color}
    s.update(typo(**t))
    if align:
        s["align"] = align
    if classes:
        s["_css_classes"] = classes
    if p_spacing is not None:
        s["paragraph_spacing"] = px(p_spacing)
    if width:
        s["_element_width"] = "initial"
        s["_element_custom_width"] = px(width)
        s["_element_width_tablet"] = "inherit" if width_t is None else "initial"
        if width_t is not None:
            s["_element_custom_width_tablet"] = px(width_t)
    return widget(seed, "text-editor", s)


def divider(seed, width, color=GOLD, weight=2, align="left"):
    return widget(seed, "divider", {
        "style": "solid",
        "weight": px(weight),
        "color": color,
        "width": px(width),
        "align": align,
        "gap": px(2),
    })


def eyebrow(seed, label):
    return heading(seed, label, tag="p", color=GOLD_LIGHT, classes="ram-eyebrow", family=SANS, size=13, weight=400, lh=1.4, ls=2.3, transform="uppercase")


def page_hero(seed, title, image_key, ypos):
    """Inner-page banner: photo, navy gradient overlay, large serif title."""
    s = {**boxed(), **section_padding(88, 72), **bg_image(image_key, ypos), **overlay_gradient("rgba(6,63,87,0.94)", "rgba(9,93,127,0.7)", 90), "html_tag": "section", "flex_gap": gap(18)}
    return container(seed, s, [
        heading(seed, title, tag="h1", family=SERIF, size=60, size_t=50, size_m=40, weight=400, lh=1.1, ls=-0.6),
    ])


def nav_links(seed, color, hover, size, inline=True, classes=""):
    items = [("Home", "/"), ("About", "/about/"), ("Contact", "/contact/")]
    s = {
        "view": "inline" if inline else "traditional",
        "icon_list": [{"_id": eid(seed), "text": label, "selected_icon": {"value": "", "library": ""}, "link": {"url": SITE + path, "is_external": "", "nofollow": ""}} for label, path in items],
        "space_between": px(6 if inline else 12),
        "text_color": color,
        "text_color_hover": hover,
        "text_indent": px(0),
    }
    s.update(typo("icon_typography", family=SANS, size=size, weight=400, lh=1.4))
    if classes:
        s["_css_classes"] = classes
    return widget(seed, "icon-list", s)


def icon(seed, value, primary, secondary, size, pad, classes):
    library = "fa-regular" if value.startswith("far ") else "fa-solid"
    return widget(seed, "icon", {
        "selected_icon": {"value": value, "library": library},
        "view": "stacked",
        "shape": "circle",
        "primary_color": primary,
        "secondary_color": secondary,
        "size": px(size),
        "icon_padding": px(pad),
        "align": "left",
        "_css_classes": classes,
    })


# ---------------------------------------------------------------- copy (EN)

HOME_TITLE = "RAM Management - Attorneys at Law provides legal and business consulting services."
HOME_INTRO = ("In addition to offering corporate and commercial law services to small and medium-sized businesses, "
              "we are specialized in assisting non-resident entertainers and entertainment companies successfully "
              "navigate their Canadian tax matters.")

ABOUT_LEAD = ("Founded in 1994 as a company primarily managing artists in the music industry and providing legal services "
              "to companies and organizations in the music sector, RAM Management has grown to provide legal counsel to all "
              "areas of business.")
ABOUT_BODY = [
    "RAM Management works closely with small and medium-size businesses, assisting them with their contractual and commercial "
    "relationships and corporate structure. It also works closely with business owners in developing strategies to achieve "
    "growth and enhance the value of their business.",
    "Often being called upon to hire American entertainers on behalf of our Canadian clients for their private and corporate "
    "events, we began assisting some of these entertainers in processing their Canadian tax waivers.",
    "Appreciating our work, non-resident entertainers began hiring our office directly to process tax waivers for all of their "
    "performances in Canada; many of these relationships still exist today.",
]
# "expended" in the design copy corrected to "expanded".
ABOUT_EXPERTISE = ("Today, our expertise has expanded to all aspects of tax compliance for non-resident entertainers as well as "
                   "the contractors and vendors that work on their performances in Canada. We can assist with such matters as:")
SERVICES = [
    ("fas fa-file-signature", "Waivers of Federal Regulation 105 and Quebec Regulation 1016 withholding"),
    ("fas fa-users", "R105 and Part XIII Tax withholdings on employees, contractors, and vendors"),
    ("fas fa-file-invoice-dollar", "Income tax return and information return filings"),
    ("fas fa-search-dollar", "Income tax and withholding audits"),
    ("fas fa-landmark", "Objections and other representations before the CRA and Tax Court of Canada"),
]
ABOUT_QUOTE = ("Over the past decade, we have witnessed the greater attention that the CRA has paid to non-resident entertainers "
               "and their operations and believe it is more important than ever for non-residents working in Canada to ensure "
               "they are addressing all their Canadian tax obligations.")
TEAM = [
    ([
        "RAM Management is owned by Richard Dermer, a long-time resident of Montreal and small business owner himself from 1985 to 1994.",
        "Richard graduated Vassar College with the Bachelor of Arts in History, followed by graduating with a Bachelor of Civil Law "
        "from McGill Law School and becoming a member of the Quebec Bar in 1994.",
        "Richard has served on the board and committees of various community-based organizations and served on the Board and "
        "Executive of the Canadian Independent Record Production Association from 2002-2008.",
    ], "richard"),
    ([
        "Administration and Director of International Client Services Nadine Benny has been with RAM Management for over 20 years. "
        "Graduating from Concordia University in 2005 with a Bachelor of Commerce in Marketing, Nadine participated in the Institute "
        "for Co-operative Education program where she completed internships in advertising, artist management, and the non-profit "
        "sector. A classically trained pianist, Nadine completed the McGill Conservatory of Music program in 1999. Nadine speaks "
        "French and English fluently and completed a Certificate in Law at Université de Montréal in 2011.",
    ], "nadine"),
    ([
        "International Client Coordinator Kayla Papps joined RAM Management shortly after graduating from McGill University in 2019 "
        "with a Bachelor of Arts in Psychology, Kayla has become an integral part of the team, maintaining client relationships and "
        "managing the intricacies of the ever-evolving CRA compliance requirements.",
    ], "kayla"),
]
ADDRESS = ["R.A.M. Management", "5165 Queen Mary Road, suite 405", "Montreal, Quebec", "Canada", "H3W 1X7"]
TEL = "Tel: 514.369.4412"
FAX = "Fax: 514.489.5155"
EMAIL = "info@rammanagement.ca"
EMAIL_SHOWN = "info(at)rammanagement.ca"
MAP_ADDRESS = "5165 Queen Mary Road, Montreal, QC H3W 1X7"


def paras(items):
    return "".join(f"<p>{p}</p>" for p in items)


# ---------------------------------------------------------------- documents

def build_header():
    s = {
        **boxed(),
        "padding": box(16, 32),
        "padding_mobile": box(12, 20),
        "flex_direction": "row",
        "flex_direction_mobile": "column",
        "flex_justify_content": "space-between",
        "flex_align_items": "center",
        "flex_wrap": "wrap",
        "flex_gap": gap(32, 12),
        "background_background": "classic",
        "background_color": "rgba(255,255,255,0.92)",
        "border_border": "solid",
        "border_width": box(0, 0, 1, 0),
        "border_color": "#E1E3E3",
        "css_classes": "ram-header-bar",
    }
    logo = widget("hdr", "image", {
        "image": media("logo"),
        "image_size": "full",
        "width": px(114),
        "link_to": "custom",
        "link": {"url": SITE + "/", "is_external": "", "nofollow": ""},
        "align": "left",
    })
    nav = container("hdr", {
        "content_width": "full",
        "width": px(380),
        "width_mobile": {"unit": "%", "size": 100, "sizes": []},
        "flex_direction": "row",
        "flex_justify_content": "flex-end",
        "flex_justify_content_mobile": "flex-start",
        "flex_align_items": "center",
        "flex_gap": gap(8),
        "padding": box(0),
    }, [
        nav_links("hdr", INK, INK, 15, classes="ram-nav"),
        widget("hdr", "shortcode", {"shortcode": "[ram_language_switcher]"}),
    ], inner=True)
    return [container("hdr", s, [logo, nav])]


def build_footer():
    s = {
        **boxed(),
        "padding": box(72, 32, 32, 32),
        "padding_mobile": box(56, 20, 24, 20),
        "flex_gap": gap(48),
        "background_background": "gradient",
        "background_color": "#0D4760",  # rgba(19,120,160,.35) over #0A2D3E
        "background_color_stop": {"unit": "%", "size": 0, "sizes": []},
        "background_color_b": "#0A2D3E",
        "background_color_b_stop": {"unit": "%", "size": 60, "sizes": []},
        "background_gradient_type": "radial",
        "background_gradient_position": "top right",
    }
    body = {"family": SANS, "size": 15, "weight": 400, "lh": 1.6}
    cols = container("ftr", {
        "content_width": "full",
        "container_type": "grid",
        "grid_columns_grid": {"unit": "fr", "size": 3, "sizes": []},
        "grid_columns_grid_tablet": {"unit": "fr", "size": 2, "sizes": []},
        "grid_columns_grid_mobile": {"unit": "fr", "size": 1, "sizes": []},
        "grid_rows_grid": {"unit": "fr", "size": 1, "sizes": []},
        "grid_gaps": {"column": "56", "row": "40", "isLinked": False, "unit": "px"},
        "grid_auto_flow": "row",
        "padding": box(0),
    }, [
        container("ftr", {"content_width": "full", "flex_gap": gap(20), "padding": box(0)}, [
            widget("ftr", "image", {"image": media("logo_white"), "image_size": "full", "width": px(165), "align": "left"}),
            text("ftr", f"<p>{HOME_TITLE}</p>", color=WHITE, width=300, **body),
        ], inner=True),
        container("ftr", {"content_width": "full", "padding": box(0)}, [
            nav_links("ftr", WHITE, GOLD_LIGHT, 15, inline=False),
        ], inner=True),
        container("ftr", {"content_width": "full", "flex_gap": gap(14), "padding": box(0)}, [
            heading("ftr", "Contact", tag="h4", color=GOLD_LIGHT, family=SERIF, size=20, weight=500, lh=1.3),
            text("ftr", "<p>" + "<br>".join(ADDRESS) + "</p>", color=WHITE, **body),
            text("ftr", f"<p>{TEL}<br>{FAX}</p>", color=WHITE, **body),
            text("ftr", f'<p><a href="mailto:{EMAIL}">{EMAIL_SHOWN}</a></p>', color=WHITE, **body),
        ], inner=True),
    ], inner=True)
    rule = divider("ftr", 100, color="rgba(255,255,255,0.18)", weight=1)
    rule["settings"]["width"] = {"unit": "%", "size": 100, "sizes": []}
    return [container("ftr", s, [cols, rule])]


def build_home():
    s = {
        **boxed(),
        **section_padding(110, 110),
        **bg_image("home_hero", ypos=45),
        **overlay_gradient("rgba(5,44,61,0.96)", "rgba(9,93,127,0.55)", 95),
        "min_height": {"unit": "vh", "size": 88, "sizes": []},
        "min_height_mobile": {"unit": "vh", "size": 80, "sizes": []},
        "flex_justify_content": "center",
        "flex_align_items": "flex-start",
        "flex_gap": gap(32),
        "html_tag": "section",
        "css_classes": "ram-hero",
    }
    return [container("home", s, [
        eyebrow("home", "THE COMPANY"),
        heading("home", HOME_TITLE, tag="h1", family=SERIF, size=76, size_t=56, size_m=40, weight=400, lh=1.06, ls=-1.1),
        divider("home", 72),
        text("home", f"<p>{HOME_INTRO}</p>", color=WHITE, width=640, family=SANS, size=20, size_m=17, weight=300, lh=1.75),
    ])]


def build_about():
    hero = page_hero("about", "ABOUT", "about_hero", 40)

    texture = widget("about", "image", {
        "image": media("justice"),
        "image_size": "full",
        "_css_classes": "ram-texture",
        "_position": "absolute",
        "_element_width": "initial",
        "_element_custom_width": px(380),
        "_offset_orientation_h": "start",
        "_offset_x": px(-40),
        "_offset_orientation_v": "end",
        "_offset_y": px(0),
        "_z_index": 0,
        "hide_mobile": "hidden-mobile",
    })
    intro = container("about", {
        **boxed(),
        **section_padding(104, 104),
        "background_background": "classic",
        "background_color": WHITE,
        "overflow": "hidden",
        "flex_direction": "row",
        "flex_direction_mobile": "column",
        "flex_align_items": "flex-start",
        "flex_gap": gap(72, 48),
        "html_tag": "section",
    }, [
        texture,
        container("about", {"content_width": "full", "width": {"unit": "%", "size": 40, "sizes": []}, "width_mobile": {"unit": "%", "size": 100, "sizes": []}, "_flex_size": "grow", "flex_gap": gap(20), "padding": box(0)}, [
            divider("about", 56),
            text("about", f"<p>{ABOUT_LEAD}</p>", color=INK, family=SERIF, size=28, size_t=24, size_m=22, weight=400, lh=1.45),
        ], inner=True),
        container("about", {"content_width": "full", "width": {"unit": "%", "size": 40, "sizes": []}, "width_mobile": {"unit": "%", "size": 100, "sizes": []}, "_flex_size": "grow", "padding": box(0)}, [
            text("about", paras(ABOUT_BODY), color=GREY, p_spacing=22, family=SANS, size=17, weight=400, lh=1.8),
        ], inner=True),
    ])

    cards = []
    for value, label in SERVICES:
        cards.append(container("svc", {
            "content_width": "full",
            "flex_gap": gap(22),
            "padding": box(24, 20, 28, 20),
            "background_background": "classic",
            "background_color": WHITE,
            "background_hover_background": "classic",
            "background_hover_color": NAVY,
            "border_border": "solid",
            "border_width": box(0, 0, 2, 0),
            "border_color": GOLD,
            "border_radius": box(18),
            "css_classes": "ram-card",
        }, [
            icon("svc", value, WHITE, GOLD, 18, 13, "ram-icon-circle"),
            text("svc", f"<p>{label}</p>", color=NAVY, family=SANS, size=15, weight=500, lh=1.55),
        ], inner=True))
    services = container("about", {
        **boxed(),
        **section_padding(88, 88),
        "background_background": "classic",
        "background_color": "#F4F4F4",
        "flex_align_items": "center",
        "flex_gap": gap(44),
        "html_tag": "section",
    }, [
        text("about", f"<p>{ABOUT_EXPERTISE}</p>", color=NAVY, align="center", width=720, family=SERIF, size=26, size_m=21, weight=400, lh=1.5),
        container("about", {
            "content_width": "full",
            "container_type": "grid",
            "grid_columns_grid": {"unit": "fr", "size": 5, "sizes": []},
            "grid_columns_grid_tablet": {"unit": "fr", "size": 3, "sizes": []},
            "grid_columns_grid_mobile": {"unit": "fr", "size": 1, "sizes": []},
            "grid_rows_grid": {"unit": "fr", "size": 1, "sizes": []},
            "grid_gaps": {"column": "16", "row": "16", "isLinked": True, "unit": "px"},
            "grid_auto_flow": "row",
            "padding": box(0),
        }, cards, inner=True),
    ])

    quote = container("about", {
        **boxed(760),
        **section_padding(96, 96),
        **bg_image("tax_forms"),
        "background_overlay_background": "classic",
        "background_overlay_color": "rgba(6,63,87,0.88)",
        "background_overlay_opacity": {"unit": "px", "size": 1, "sizes": []},
        "flex_align_items": "center",
        "flex_gap": gap(20),
        "html_tag": "section",
    }, [
        heading("about", "“", tag="div", color=GOLD_LIGHT, align="center", family=SERIF, size=48, weight=400, lh=0.6),
        text("about", f"<p>{ABOUT_QUOTE}</p>", color=WHITE, align="center", family=SERIF, size=24, size_m=20, weight=400, lh=1.6),
    ])

    team_cards = []
    for bio, who in TEAM:
        team_cards.append(container("team", {
            "content_width": "full",
            "flex_justify_content": "space-between",
            "flex_gap": gap(16),
            "padding": box(32, 28),
            "background_background": "classic",
            "background_color": "rgba(255,255,255,0.05)",
            "background_hover_background": "classic",
            "background_hover_color": "rgba(255,255,255,0.09)",
            "border_border": "solid",
            "border_width": box(1),
            "border_color": "rgba(255,255,255,0.12)",
            "border_radius": box(22),
            "css_classes": "ram-team-card",
        }, [
            text("team", paras(bio), color=WHITE, p_spacing=16, family=SANS, size=15, weight=300, lh=1.75),
            text("team", f'<p><a href="mailto:{who}@rammanagement.ca">{who}(at)rammanagement.ca</a></p>', color=GOLD_LIGHT, family=SANS, size=15, weight=400, lh=1.75),
        ], inner=True))
    team = container("about", {
        **boxed(),
        **section_padding(96, 96),
        "background_background": "gradient",
        "background_color": "#0B4E6A",  # rgba(19,120,160,.45) over #052C3D
        "background_color_stop": {"unit": "%", "size": 0, "sizes": []},
        "background_color_b": NAVY_DARK,
        "background_color_b_stop": {"unit": "%", "size": 60, "sizes": []},
        "background_gradient_type": "radial",
        "background_gradient_position": "top left",
        "flex_align_items": "flex-start",
        "flex_gap": gap(48),
        "html_tag": "section",
    }, [
        eyebrow("team", "OUR TEAM"),
        container("team", {
            "content_width": "full",
            "container_type": "grid",
            "grid_columns_grid": {"unit": "fr", "size": 3, "sizes": []},
            "grid_columns_grid_tablet": {"unit": "fr", "size": 2, "sizes": []},
            "grid_columns_grid_mobile": {"unit": "fr", "size": 1, "sizes": []},
            "grid_rows_grid": {"unit": "fr", "size": 1, "sizes": []},
            "grid_gaps": {"column": "20", "row": "20", "isLinked": True, "unit": "px"},
            "grid_auto_flow": "row",
            "width": {"unit": "%", "size": 100, "sizes": []},
            "padding": box(0),
        }, team_cards, inner=True),
    ])
    return [hero, intro, services, quote, team]


def build_contact():
    hero = page_hero("contact", "CONTACT", "handshake", 50)

    body = {"family": SANS, "size": 16, "weight": 400, "lh": 1.75}

    def card(seed, icon_value, html, link=None):
        s = {
            "content_width": "full",
            "flex_gap": gap(18),
            "padding": box(28, 24, 32, 24),
            "background_background": "classic",
            "background_color": WHITE,
            "background_hover_background": "classic",
            "background_hover_color": NAVY,
            "border_border": "solid",
            "border_width": box(0, 0, 2, 0),
            "border_color": GOLD,
            "border_radius": box(18),
            "css_classes": "ram-contact-card",
        }
        if link:
            s["html_tag"] = "a"
            s["link"] = {"url": link, "is_external": "", "nofollow": ""}
        return container(seed, s, [
            icon(seed, icon_value, NAVY, WHITE, 20, 16, "ram-contact-icon"),
            text(seed, html, color="#3E4144", **body),
        ], inner=True)

    cards = container("contact", {
        **boxed(),
        **section_padding(88, 88),
        "background_background": "classic",
        "background_color": "#F2F1EE",
        "html_tag": "section",
    }, [
        container("contact", {
            "content_width": "full",
            "container_type": "grid",
            "grid_columns_grid": {"unit": "fr", "size": 3, "sizes": []},
            "grid_columns_grid_tablet": {"unit": "fr", "size": 1, "sizes": []},
            "grid_columns_grid_mobile": {"unit": "fr", "size": 1, "sizes": []},
            "grid_rows_grid": {"unit": "fr", "size": 1, "sizes": []},
            "grid_gaps": {"column": "20", "row": "20", "isLinked": True, "unit": "px"},
            "grid_auto_flow": "row",
            "padding": box(0),
        }, [
            card("c-addr", "fas fa-map-marker-alt", "<p>" + "<br>".join(ADDRESS) + "</p>"),
            card("c-tel", "fas fa-phone-alt", f"<p>{TEL}<br>{FAX}</p>", link="tel:+15143694412"),
            card("c-mail", "far fa-envelope", f'<p><span style="text-decoration: underline; text-underline-offset: 3px;">{EMAIL_SHOWN}</span></p>', link=f"mailto:{EMAIL}"),
        ], inner=True),
    ])

    map_section = container("contact", {
        **boxed(),
        **section_padding(88, 96),
        "background_background": "classic",
        "background_color": WHITE,
        "flex_gap": gap(24),
        "html_tag": "section",
    }, [
        heading("contact", "MAP", tag="h2", color=NAVY, family=SERIF, size=38, size_m=28, weight=400, lh=1.15),
        container("contact", {
            "content_width": "full",
            "padding": box(0),
            "overflow": "hidden",
            "border_border": "solid",
            "border_width": box(1),
            "border_color": "#E1E3E3",
            "border_radius": box(24),
            "box_shadow_box_shadow_type": "yes",
            "box_shadow_box_shadow": {"horizontal": 0, "vertical": 18, "blur": 40, "spread": 0, "color": "rgba(5,44,61,0.08)"},
        }, [
            widget("contact", "google_maps", {"address": MAP_ADDRESS, "zoom": {"unit": "px", "size": 15, "sizes": []}, "height": px(440), "height_mobile": px(340)}),
        ], inner=True),
    ])
    return [hero, cards, map_section]


def build_kit():
    def sys_typo(_id, title, family, weight):
        return {"_id": _id, "title": title, "typography_typography": "custom", "typography_font_family": family, "typography_font_weight": str(weight)}

    return {
        "system_colors": [
            {"_id": "primary", "title": "Navy", "color": NAVY},
            {"_id": "secondary", "title": "Gold", "color": GOLD},
            {"_id": "text", "title": "Ink", "color": INK},
            {"_id": "accent", "title": "Blue", "color": BLUE},
        ],
        "custom_colors": [
            {"_id": "ramnvdk", "title": "Navy Dark", "color": NAVY_DARK},
            {"_id": "ramgldl", "title": "Gold Light", "color": GOLD_LIGHT},
            {"_id": "ramgrey", "title": "Grey Text", "color": GREY},
            {"_id": "ramoffw", "title": "Off White", "color": "#F7F6F3"},
            {"_id": "ramftr", "title": "Footer Navy", "color": "#0A2D3E"},
            {"_id": "rammist", "title": "Mist", "color": "#E4EEF2"},
        ],
        "system_typography": [
            sys_typo("primary", "Headings (Source Serif 4)", SERIF, 400),
            sys_typo("secondary", "Sub-headings (Jost)", SANS, 500),
            sys_typo("text", "Body (Jost)", SANS, 400),
            sys_typo("accent", "Accent (Jost)", SANS, 500),
        ],
        "custom_typography": [],
        "body_background_background": "classic",
        "body_background_color": "#F7F6F3",
        "body_color": INK,
        **typo("body_typography", family=SANS, size=16, weight=400, lh=1.6),
        "link_normal_color": BLUE,
        "link_hover_color": NAVY,
        "container_width": px(1040),
        "container_padding": box(0),
        "space_between_widgets": {"column": "20", "row": "20", "isLinked": True, "unit": "px", "size": 20},
        "site_name": "R.A.M. Management",
        "site_description": "Attorneys at Law",
    }


def main():
    OUT.mkdir(exist_ok=True)
    docs = {
        "kit-settings": build_kit(),
        "header": build_header(),
        "footer": build_footer(),
        "home": build_home(),
        "about": build_about(),
        "contact": build_contact(),
    }
    for name, data in docs.items():
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        print(f"{name}.json", len(json.dumps(data)))


if __name__ == "__main__":
    main()
