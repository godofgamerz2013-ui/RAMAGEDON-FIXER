const pages = {
 home: "home.html", description: "description.html", projects: "projects.html",
 setup: "setup.html", discord: "discord.html", steam: "steam.html",
 guns: "guns.html", contact: "contact.html", settings: "settings.html"
};
const app = document.getElementById("app");
const nav = document.getElementById("nav");
const menuToggle = document.getElementById("menuToggle");
const navMore = document.getElementById("navMore");
const moreTrigger = navMore?.querySelector(".nav-more-trigger");
async function loadPage(name, push = true) {
  const file = pages[name] || pages.home;
  try {
    const response = await fetch("./pages/" + file, {cache:"no-cache"});
    if (!response.ok) throw new Error("Page not found");
    app.innerHTML = await response.text();
    document.querySelectorAll("[data-page]").forEach(a => a.classList.toggle("active", a.dataset.page === name));
    if (push) history.pushState({page:name}, "", location.pathname + location.search);
    nav.classList.remove("open");
    menuToggle.setAttribute("aria-expanded", "false");
    navMore?.classList.remove("open");
    moreTrigger?.setAttribute("aria-expanded", "false");
    window.scrollTo({top:0,behavior:"smooth"});
  } catch (error) {
    app.innerHTML = '<section class="content"><p class="eyebrow">404 · PAGE NOT FOUND</p><h1 class="page-title">That page is missing.</h1><p>Try returning to the home page.</p><a class="button" href="#" data-page="home">Back home</a></section>';
  }
}
document.addEventListener("click", event => {
  const link = event.target.closest("[data-page]");
  if (!link) return;
  event.preventDefault();
  loadPage(link.dataset.page);
});
menuToggle.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(open));
});
moreTrigger?.addEventListener("click", () => {
  const open = navMore.classList.toggle("open");
  moreTrigger.setAttribute("aria-expanded", String(open));
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    nav.classList.remove("open");
    navMore?.classList.remove("open");
    menuToggle.setAttribute("aria-expanded", "false");
    moreTrigger?.setAttribute("aria-expanded", "false");
  }
});
window.addEventListener("popstate", event => loadPage(event.state?.page || "home", false));
document.getElementById("year").textContent = new Date().getFullYear();
loadPage("home", false);