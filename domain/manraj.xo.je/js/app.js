const pages = {
  home: "home.html",
  description: "description.html",
  projects: "projects.html",
  setup: "setup.html",
  discord: "discord.html",
  steam: "steam.html",
  guns: "guns.html",
  contact: "contact.html",
  settings: "settings.html"
};

const app = document.getElementById("app");
const nav = document.getElementById("nav");
const menuToggle = document.getElementById("menuToggle");
const navMore = document.getElementById("navMore");
const moreTrigger = navMore?.querySelector(".nav-more-trigger");
const dockMenu = document.getElementById("dockMenu");
let activeRequest = 0;

function closeMenus() {
  nav.classList.remove("open");
  navMore?.classList.remove("open");
  menuToggle.setAttribute("aria-expanded", "false");
  moreTrigger?.setAttribute("aria-expanded", "false");
  menuToggle.setAttribute("aria-label", "Open navigation");
}

function setActivePage(name) {
  document.querySelectorAll("[data-page]").forEach(link => {
    const active = link.dataset.page === name;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

async function loadPage(name, options = {}) {
  const page = pages[name] ? name : "home";
  const requestId = ++activeRequest;
  try {
    const response = await fetch("./pages/" + pages[page], { cache: "no-cache" });
    if (!response.ok) throw new Error("Unable to load page");
    const markup = await response.text();
    if (requestId !== activeRequest) return;
    app.innerHTML = markup;
    setActivePage(page);
    if (options.updateUrl && location.hash !== "#" + page) {
      history.pushState({ page }, "", "#" + page);
    }
    closeMenus();
    if (options.scroll !== false) window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    if (requestId !== activeRequest) return;
    app.innerHTML = '<section class="content"><p class="eyebrow">PAGE UNAVAILABLE</p><h1 class="page-title">Could not load this page.</h1><p>Check your connection and try again.</p><button class="button" type="button" id="retryPage">Try again</button></section>';
    document.getElementById("retryPage")?.addEventListener("click", () => loadPage(page, { scroll: false }));
  }
}

document.addEventListener("click", event => {
  const link = event.target.closest("[data-page]");
  if (!link) return;
  event.preventDefault();
  loadPage(link.dataset.page, { updateUrl: true });
});

menuToggle.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  if (open) navMore?.classList.remove("open");
});

dockMenu?.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  if (open) navMore?.classList.remove("open");
});

moreTrigger?.addEventListener("click", () => {
  const open = navMore.classList.toggle("open");
  moreTrigger.setAttribute("aria-expanded", String(open));
});

document.addEventListener("click", event => {
  if (!event.target.closest("#navMore")) {
    navMore?.classList.remove("open");
    moreTrigger?.setAttribute("aria-expanded", "false");
  }
  if (!event.target.closest(".topbar") && !event.target.closest(".mobile-dock")) closeMenus();
});

document.addEventListener("keydown", event => {
  if (event.key === "Escape") closeMenus();
});

window.addEventListener("popstate", () => {
  const requested = location.hash.slice(1) || "home";
  loadPage(requested, { scroll: false });
});

document.getElementById("year").textContent = new Date().getFullYear();
loadPage(location.hash.slice(1) || "home", { scroll: false });
