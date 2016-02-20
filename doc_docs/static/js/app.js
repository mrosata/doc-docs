/**
 * Created by michael on 2/18/16.
 */
"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var isObject = !!isObject && typeof isObject === "function" ? isObject : function isObject() {
  for (var _len = arguments.length, obj = Array(_len), _key = 0; _key < _len; _key++) {
    obj[_key] = arguments[_key];
  }

  obj.forEach(function (o) {
    if (!o || (typeof o === "undefined" ? "undefined" : _typeof(o)) !== "object") return false;
  });
  return true;
};

var ResponseUtils = function () {
  function ResponseUtils() {
    _classCallCheck(this, ResponseUtils);
  }

  /**
   * Figure out if obj is result of Facebook OAuth2 call. Then return
   * an object with only the values required to send to DocDocs server.
   *
   * @param fbRespObj
   * @return object|boolean Response object or false
   */


  _createClass(ResponseUtils, null, [{
    key: "fbResp",
    value: function fbResp(fbRespObj) {
      if (!isObject(fbRespObj)) return false;
      if (!fbRespObj.status || fbRespObj.status === "unknown") return false;
      if (!fbRespObj.hasOwnProperty('authResponse') || !isObject(fbRespObj.authResponse)) return false;
      var authResponse = fbRespObj.authResponse;
      return {
        type: 'fb',
        user_id: authResponse.userID,
        access_token: authResponse.accessToken,
        expires_in: authResponse.expiresIn,
        signed_request: authResponse.signedRequest
      };
    }

    /**
     * Figure out if obj is result of Google OAuth2 call. Then return
     * an object with only the values required to send to DocDocs server.
     * 
     * @param gplusRespObj obj
     * @return object|boolean Response object or false
     */

  }, {
    key: "gplusResp",
    value: function gplusResp(gplusRespObj) {
      if (!isObject(gplusRespObj)) return false;
      if (!gplusRespObj.id_token || !gplusRespObj.code || !gplusRespObj.client_id) return false;

      var resp = {
        type: 'google'
      };
      resp.client_id = gplusRespObj.client_id;
      resp.code = gplusRespObj.code;
      resp.id_token = gplusRespObj.id_token;

      return resp;
    }

    /**
     * Figure out if obj is result of GitHub OAuth2 call. Then return
     * an object with only the values required to send to DocDocs server.
     * 
     * @param githubRespObj
     * @return object|boolean Response object or false
     */

  }, {
    key: "githubResp",
    value: function githubResp(githubRespObj) {
      if (!isObject(githubRespObj)) return false;
    }
  }]);

  return ResponseUtils;
}();

var respUtil = new ResponseUtils();

/**
 * After page load run Foundation and handle events
 */
jQuery(function ($) {
  var Foundation = $(document).foundation();

  // Get the State for the App set through the templating engine
  var ddStateElem = $('[data-doc-doc-state-object]');
  var _STATE = ddStateElem.length ? ddStateElem.data('appState') : "";

  /**
   * Open Modals with Errors or Flash Message Modals on load
   *
   * Check if a form inside of a reveal modal was submitted with errors
   * and if so then have it be open. If no forms have error messages then
   * this function will also check for Flask Flash Messages and show them
   * inside modals.
   */
  function openFlashMessageAndErrorModalsOnLoad() {
    var formsWithErrors = $('.reveal[data-errors-present="true"]'),
        flaskFlashMessages = $('.flash-messages .reveal');
    if (formsWithErrors.length) {
      formsWithErrors.foundation("open");
    } else if (flaskFlashMessages.length) {
      // We only pop open flash messages if there aren't any forms with errors open.
      flaskFlashMessages.each(function () {
        $(this).foundation("open");
      });
    }
  }
  openFlashMessageAndErrorModalsOnLoad();

  /**
   * Log User out of the app (including fb or any other oauth).
   */
  window.accountDocDocsLogoff = function () {
    FB.logout();
    window.location = "/logout";
  };

  window.facebookDocDocsLogin = function () {

    FB.login(function (fbObject) {

      var fbUserInfo = ResponseUtils.fbResp(fbObject);
      if (!fbUserInfo || !isObject(fbUserInfo)) return false;

      // Put the state of app from page into our response.
      fbUserInfo._state = _STATE;

      $.ajax({
        url: "/api/login",
        type: "post",
        data: JSON.stringify(fbUserInfo),
        contentType: "application/json",
        success: function success(result) {
          // handle response from our own app
          if (isObject(result) && result.status.toLowerCase() === "success") {
            window.location = result.data.location;
          } else {
            // The login failed somehow on server side
            alert("Hew Son, Ve Ack a Pro Blah!");
          }
        },
        error: function error(err) {
          console.error(err);
        }
      });
    }, { scope: 'email,public_profile,user_friends' });
  };

  window.googleDocDocsLogin = function (authResult) {
    console.debug(authResult);
    authResult = ResponseUtils.gplusResp(authResult);
    if (!authResult['code']) return false;

    authResult._state = _STATE;

    $.ajax({
      type: "post",
      url: "/api/login",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify(authResult),
      success: function success(result) {
        // handle response from our own app
        if (isObject(result) && result.status.toLowerCase() === "success") {
          window.location = result.data.location;
        } else {
          // The login failed somehow on server side
          alert("Hew Son, Ve Ack a Pro Blah!");
        }
      }
    });
  };

  window.githubDocDocsStep1 = function () {
    // Unlike Facebook and Google OAuth2, Doc Docs will create the initial request to ask the
    // users for permission to authenticate them using their GitHub account.
    // I put all the needed information inside the template (sort of like Google + FB)
    var githubBtn = document.querySelector(".github-signin");
    var scope = githubBtn.dataset['scope'];
    var client_id = githubBtn.dataset['clientid'];
    var redirect_uri = "" + window.location.origin + githubBtn.dataset['redirecturi'];

    // With the GitHub OAuth we will actually let the page redirect and then afterwards it
    // will redirect back to us.

    window.location = "https://github.com/login/oauth/authorize" + ("?scope=" + scope + "&client_id=" + client_id + "&state=" + _STATE + "&redirecturi=" + redirect_uri);
  };
});
//# sourceMappingURL=app.js.map
