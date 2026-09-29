/**
 * RAM Management — highlight the current page in the header navigation.
 * The nav is an Elementor Icon List with the CSS class "ram-nav".
 */
( function () {
	function normalize( path ) {
		return path.replace( /\/+$/, '' ) || '/';
	}

	function markActive() {
		var here = normalize( window.location.pathname );
		var links = document.querySelectorAll( '.ram-nav a[href]' );

		links.forEach( function ( link ) {
			var target;
			try {
				target = new URL( link.href, window.location.href );
			} catch ( e ) {
				return;
			}
			if ( target.host !== window.location.host ) {
				return;
			}
			var item = link.closest( '.elementor-icon-list-item' ) || link;
			if ( normalize( target.pathname ) === here ) {
				item.classList.add( 'is-active' );
				link.setAttribute( 'aria-current', 'page' );
			}
		} );
	}

	if ( document.readyState === 'loading' ) {
		document.addEventListener( 'DOMContentLoaded', markActive );
	} else {
		markActive();
	}
} )();
