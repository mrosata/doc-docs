/**
 * Created by michael on 2/18/16.
 */
"use strict";

var isObject = (!!isObject && typeof isObject === "function" ? isObject :
    function isObject (...obj) {
      obj.forEach((o)=> {
        if (!o || typeof o !== "object")
          return false;
      });
      return true;
    }
);

class ResponseUtils {
  constructor () {

  }

  /**
   * Figure out if obj is result of Facebook login/logoff
   *
   * @param fbObj obj
   * @return object|boolean "connected", "disconnected", false
   */
  static fbResp(fbObj) {
    if (!fbObj || typeof fbObj !== "object")
      return false;
    if (!fbObj.status || fbObj.status === "unknown")
      return false;
    if (!fbObj.hasOwnProperty('authResponse') || typeof fbObj.authResponse !== "object")
      return false;
    let resp = {
      type: 'fb'
    };
    resp.action = fbObj.status;
    resp.user_id = fbObj.authResponse.userID;
    resp.access_token = fbObj.authResponse.accessToken;
    resp.expires_in = fbObj.authResponse.expiresIn;
    resp.signed_request = fbObj.authResponse.signedRequest;

    return resp
  }

  static error (msg="", code=0) {
    return {
      type: "error",
      msg: msg,
      code: code
    }
  }
}
var respUtil = new ResponseUtils();


/**
 * After page load run Foundation and handle events
 */
jQuery(function ($) {
  var Foundation = $(document).foundation();

  // Get the State for the App set through the templating engine
  let ddStateElem = $('[data-doc-doc-state-object]');
  const _STATE = (ddStateElem.length ? ddStateElem.data('appState') : "");

  /**
   * Open Modals with Errors or Flash Message Modals on load
   *
   * Check if a form inside of a reveal modal was submitted with errors
   * and if so then have it be open. If no forms have error messages then
   * this function will also check for Flask Flash Messages and show them
   * inside modals.
   */
  function openFlashMessageAndErrorModalsOnLoad () {
    var formsWithErrors = $('.reveal[data-errors-present="true"]'),
        flaskFlashMessages = $('.flash-messages .reveal');
    if (formsWithErrors.length) {
      formsWithErrors.foundation("open");
    } else if (flaskFlashMessages.length) {
      // We only pop open flash messages if there aren't any forms with errors open.
      flaskFlashMessages.each(function(t, n, a){
        $(this).foundation("open");
      });
    }
  }
  openFlashMessageAndErrorModalsOnLoad();

  /**
   * Log User out of the app (including fb or any other oauth).
   */
  window.accountFacebookDocDocsLogoff = function() {
    FB.logout();
    window.location = "/logout";
  };

  window.facebookDocDocsLogin = function() {

    FB.login(function(fbObject) {

      console.dir(fbObject);
      let fbUserInfo = ResponseUtils.fbResp(fbObject);
      if (!fbUserInfo || !isObject(fbUserInfo)) return false;

      // Put the state of app from page into our response.
      fbUserInfo._state = _STATE;

      $.ajax({
        url: "/api/login",
        type: "post",
        data: JSON.stringify(fbUserInfo),
        contentType: "application/json",
        success(result) {
          // handle response from our own app
          if (isObject(result) && result.status.toLowerCase() === "success") {
            window.location = result.data.location;
          }
          else {
            // The login failed somehow on server side
            alert("Hew Son, Ve Ack a Pro Blah!");
          }
        },
        error(err) {
          console.error(err);
        }
      });
    }, {scope: 'email,public_profile,user_friends'});


  };


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
