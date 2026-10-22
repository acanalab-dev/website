// App Store link of Daily Affirmations, used by the app page and every guide.
// Leave empty until it's live (the App Store buttons then do nothing on tap).
var APP_STORE_URL = "";
(function () {
  document.querySelectorAll("a.store").forEach(function (link) {
    if (APP_STORE_URL) { link.href = APP_STORE_URL; link.classList.remove("soon"); }
    else link.addEventListener("click", function (e) { e.preventDefault(); });
  });
})();
