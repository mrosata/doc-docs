"use strict";
jQuery(function($){
    var Foundation = $(document).foundation();

    /*
    // Sticky profile menu object to hold all vars/props
    var profileSticky = {};
    // Only setup the sticky menu if this is a page with a container we want to use.
    profileSticky.profileTabs = $('#profile-tabs-container').first();
    console.log(profileSticky);
    if (profileSticky.profileTabs.length) {

        profileSticky.init = function (evt) {
            profileSticky.offsetTop = profileSticky.profileTabs.offset().top;
        };
        profileSticky.scroll = function (evt) {
            profileSticky.menuContainer.toggleClass('floating-menu', profileSticky.offsetTop < profileSticky.profileTabs.scrollTop().top);

            console.log(profileSticky, profileSticky.profileTabs.scrollTop());
        };

        // Get the menu that we will make sticky
        profileSticky.menuContainer = profileSticky.profileTabs.find('.tabs-menu-container');
        // The resize event is just to know the offset height where the menu rests in natural state
        $(window).on('resize', profileSticky.init );
        // When we scroll check offset and set menu to proper state.
        $(window).on('scroll', profileSticky.scroll);

        profileSticky.init();
    }
    */
});