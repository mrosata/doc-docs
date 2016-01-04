"use strict";
jQuery(function($){
    var Foundation = $(document).foundation();


    /**
     * Check if a form inside of a reveal modal was submitted with errors
     * and if so then have it be open. I will add validation and ajax
     * checks as well so this probably won't be used too much in the future.
     * At the moment though it's needed or when submitting login/register forms
     * on site with errors it just looks as if the index page reloaded.
     */
    function openModelFormWithErrors () {
        var formsWithErrors = $('.reveal[data-errors-present="true"]');
        if (formsWithErrors.length) {
            formsWithErrors.foundation("open");
        }
    }
    openModelFormWithErrors()

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