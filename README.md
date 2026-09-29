# R.A.M. Management website

WordPress + Elementor build of the R.A.M. Management design for https://ram-management.wsdfy.com (English; French to be added with WPML).

## What's on the site

| Item | WordPress ID | Notes |
|---|---|---|
| Home (front page) | page 16 | `/` |
| About | page 19 | `/about/` |
| Contact | page 17 | `/contact/` |
| Site Header | Elementor template 14 | Templates > Saved Templates |
| Site Footer | Elementor template 15 | Templates > Saved Templates |
| Elementor Site Settings | kit 6 | Global colours and fonts (Navy, Gold, Ink, Blue + extras; Source Serif 4 / Jost) |

Every section is an Elementor container with standard widgets (Heading, Text Editor, Image, Icon, Icon List, Divider, Google Maps, Shortcode), so all copy, images, colours and spacing are edited in Elementor. Pages use the **Elementor Full Width** template.

## Child theme — `wp-content/themes/ram-management`

Child of **Hello Elementor**.

- `functions.php` — loader.
- `inc/ram-theme.php`
  - Hides Hello's header/footer and prints the Elementor templates whose IDs are stored in the options `ram_header_template_id` / `ram_footer_template_id`.
  - Resolves those IDs through `wpml_object_id`, so once WPML translates the header/footer templates the French versions show automatically.
  - `[ram_language_switcher]` shortcode (already placed in the header): renders EN/FR pills from WPML's active languages, and prints nothing until WPML is installed.
  - Enqueues Google Fonts (Jost, Source Serif 4), `assets/css/ram.css` and `assets/js/ram.js`.
- `assets/css/ram.css` — the few effects Elementor Free can't set in the panel, attached via Advanced > CSS Classes: `ram-nav`, `ram-eyebrow`, `ram-hero`, `ram-card`, `ram-icon-circle`, `ram-contact-card`, `ram-team-card`, `ram-texture`, `ram-header-bar`.
- `assets/js/ram.js` — marks the current page in the header nav.

## Elementor data — `elementor/`, `tools/build_elementor.py`

`python3 tools/build_elementor.py` regenerates the JSON for every document from one script (copy, media IDs and styles live there). The JSON is what was imported into the site; after that, the site is the source of truth. Edit in Elementor, not here.

## Images — `design-assets/images/`

Extracted from the design bundle and uploaded to the media library as attachments 7–13.

## Adding French with WPML

1. Install WPML + WPML String Translation (+ the Elementor integration WPML ships).
2. Add French as a language (e.g. `/fr/` directory).
3. Translate the three pages **and** the Site Header / Site Footer templates. The theme picks the translated header/footer by itself.
4. The EN/FR switcher appears in the header automatically.

The French copy is in the original design bundle (`T.fr` in the HTML files).
