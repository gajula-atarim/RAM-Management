<?php
/**
 * RAM Management theme logic.
 *
 * - Enqueues the brand stylesheet, fonts and the small front-end script.
 * - Replaces the Hello Elementor header/footer with Elementor templates
 *   (Templates > Saved Templates) so both stay editable in Elementor Free.
 * - Provides [ram_language_switcher], which renders the EN/FR switcher once
 *   WPML is active and outputs nothing before that.
 *
 * @package RAM_Management
 */

defined( 'ABSPATH' ) || exit;

/**
 * Option names holding the Elementor template IDs used as site header/footer.
 */
const RAM_HEADER_OPTION = 'ram_header_template_id';
const RAM_FOOTER_OPTION = 'ram_footer_template_id';

/**
 * Front-end assets.
 */
function ram_enqueue_assets() {
	$dir = get_stylesheet_directory_uri();

	wp_enqueue_style(
		'ram-fonts',
		'https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Source+Serif+4:ital,wght@0,400;0,500;1,400&display=swap',
		array(),
		null
	);

	wp_enqueue_style( 'ram-theme', $dir . '/assets/css/ram.css', array( 'ram-fonts' ), RAM_THEME_VERSION );
	wp_enqueue_script( 'ram-theme', $dir . '/assets/js/ram.js', array(), RAM_THEME_VERSION, true );

	// Load the header/footer template CSS in <head> instead of inline in <body>.
	if ( ram_should_render_site_chrome() && class_exists( '\Elementor\Core\Files\CSS\Post' ) ) {
		foreach ( array( RAM_HEADER_OPTION, RAM_FOOTER_OPTION ) as $option ) {
			$template_id = ram_get_template_id( $option );
			if ( $template_id ) {
				\Elementor\Core\Files\CSS\Post::create( $template_id )->enqueue();
			}
		}
	}
}
add_action( 'wp_enqueue_scripts', 'ram_enqueue_assets', 20 );

/**
 * Hide Hello Elementor's own header/footer; the Elementor templates replace them.
 */
add_filter( 'hello_elementor_header_footer', '__return_false' );

/**
 * Resolve a header/footer template ID, following WPML translations when present.
 *
 * @param string $option Option name.
 * @return int Template post ID, or 0 when unset or unpublished.
 */
function ram_get_template_id( $option ) {
	$template_id = (int) get_option( $option, 0 );
	if ( ! $template_id ) {
		return 0;
	}

	// WPML: use the template translated into the current language when it exists.
	$template_id = (int) apply_filters( 'wpml_object_id', $template_id, 'elementor_library', true );

	return 'publish' === get_post_status( $template_id ) ? $template_id : 0;
}

/**
 * Whether the site header/footer should be printed on this request.
 *
 * Skipped while editing the header/footer templates themselves and on pages
 * using the "Elementor Canvas" template, which is meant to be chrome-free.
 *
 * @return bool
 */
function ram_should_render_site_chrome() {
	if ( ! did_action( 'elementor/loaded' ) ) {
		return false;
	}
	if ( is_singular( 'elementor_library' ) ) {
		return false;
	}
	if ( is_singular() && 'elementor_canvas' === get_page_template_slug() ) {
		return false;
	}
	return true;
}

/**
 * Render one Elementor template inside a landmark element.
 *
 * @param string $option Option name holding the template ID.
 * @param string $tag    Wrapper tag (header|footer).
 * @param string $class  Wrapper class.
 */
function ram_render_template( $option, $tag, $class ) {
	if ( ! ram_should_render_site_chrome() ) {
		return;
	}
	$template_id = ram_get_template_id( $option );
	if ( ! $template_id ) {
		return;
	}

	$html = \Elementor\Plugin::instance()->frontend->get_builder_content_for_display( $template_id );
	if ( '' === trim( (string) $html ) ) {
		return;
	}

	printf( '<%1$s class="%2$s">%3$s</%1$s>', tag_escape( $tag ), esc_attr( $class ), $html ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Elementor output.
}

/**
 * Site header — printed right after <body> opens.
 */
function ram_render_site_header() {
	ram_render_template( RAM_HEADER_OPTION, 'header', 'ram-site-header' );
}
add_action( 'wp_body_open', 'ram_render_site_header', 5 );

/**
 * Site footer — printed before the footer scripts.
 */
function ram_render_site_footer() {
	ram_render_template( RAM_FOOTER_OPTION, 'footer', 'ram-site-footer' );
}
add_action( 'wp_footer', 'ram_render_site_footer', 5 );

/**
 * [ram_language_switcher] — EN / FR pill switcher.
 *
 * Uses WPML's active languages. Returns an empty string while WPML is not
 * installed, so the header can already contain the shortcode.
 *
 * @return string
 */
function ram_language_switcher_shortcode() {
	$languages = apply_filters( 'wpml_active_languages', null, array( 'skip_missing' => 0 ) );
	if ( empty( $languages ) || ! is_array( $languages ) ) {
		return '';
	}

	$items = '';
	foreach ( $languages as $language ) {
		$code   = isset( $language['language_code'] ) ? $language['language_code'] : $language['code'];
		$items .= sprintf(
			'<a class="ram-lang__item%1$s" href="%2$s" hreflang="%3$s" lang="%3$s"%4$s>%5$s</a>',
			! empty( $language['active'] ) ? ' is-active' : '',
			esc_url( $language['url'] ),
			esc_attr( $code ),
			! empty( $language['active'] ) ? ' aria-current="true"' : '',
			esc_html( strtoupper( $code ) )
		);
	}

	return '<nav class="ram-lang" aria-label="' . esc_attr__( 'Language', 'ram-management' ) . '">' . $items . '</nav>';
}
add_shortcode( 'ram_language_switcher', 'ram_language_switcher_shortcode' );
