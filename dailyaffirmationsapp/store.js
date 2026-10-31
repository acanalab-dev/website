// App Store link of Daily Affirmations, used by the app page and every guide.
// PROVIDER_TOKEN is the pt= value from App Store Connect (App Analytics, Campaigns).
// When it's set, each badge with data-ct="<campaign>" links with ?pt=..&ct=..&mt=8,
// so App Store Connect shows which page brought each download.
var APP_STORE_URL = "https://apps.apple.com/app/apple-store/id6809586170";
var PROVIDER_TOKEN = "128486213";
// Campaign names (data-ct, the "ct" field in guides.json) must be 30 characters or fewer.
(function () {
  document.querySelectorAll("a.store").forEach(function (link) {
    if (!APP_STORE_URL) { link.addEventListener("click", function (e) { e.preventDefault(); }); return; }
    var ct = link.getAttribute("data-ct");
    link.href = PROVIDER_TOKEN && ct
      ? APP_STORE_URL + "?pt=" + encodeURIComponent(PROVIDER_TOKEN) + "&ct=" + encodeURIComponent(ct) + "&mt=8"
      : APP_STORE_URL;
    link.classList.remove("soon");
  });
})();
