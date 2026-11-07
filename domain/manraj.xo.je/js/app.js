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
  const socialActive = ["discord", "steam", "guns"].includes(name);
  navMore?.classList.toggle("active", socialActive);
  if (socialActive) moreTrigger?.setAttribute("aria-current", "page");
  else moreTrigger?.removeAttribute("aria-current");
}

const motionReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let motionItems = [];
let motionFrame = 0;
let revealObserver = null;

function refreshMotionTargets() {
  if (motionReduced) return;
  if (revealObserver) revealObserver.disconnect();
  motionItems = [...document.querySelectorAll("#app .hero-visual, #app .hero-copy, #app .section-head, #app .card, #app .detail, #app .embed-frame")];
  motionItems.forEach((el, index) => {
    el.classList.add("motion-reveal");
    if (el.matches(".hero-visual,.card,.detail,.embed-frame")) el.classList.add("motion-depth");
    if (el.matches(".card,.detail")) el.classList.add("motion-card");
    el.style.transitionDelay = (index % 3) * 70 + "ms";
  });
  if (!("IntersectionObserver" in window)) {
    motionItems.forEach(el => el.classList.add("is-visible"));
    return;
  }
  revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });
  motionItems.forEach(el => revealObserver.observe(el));
  updateScrollDepth();
}
function updateScrollDepth() {
  if (motionReduced || motionFrame) return;
  motionFrame = requestAnimationFrame(() => {
    motionFrame = 0;
    const vh = window.innerHeight || 1;
    motionItems.forEach(el => {
      if (!el.classList.contains("motion-depth")) return;
      const rect = el.getBoundingClientRect();
      const distance = (rect.top + rect.height * .5 - vh * .5) / vh;
      const offset = Math.max(-1, Math.min(1, distance));
      const strength = el.classList.contains("hero-visual") ? 22 : 13;
      el.style.setProperty("--scroll-y", (-offset * strength).toFixed(2) + "px");
    });
  });
}
if (!motionReduced) {
  document.documentElement.classList.add("motion-ready");
  window.addEventListener("scroll", updateScrollDepth, { passive: true });
  window.addEventListener("resize", updateScrollDepth, { passive: true });
  document.addEventListener("pointermove", event => {
    if (event.pointerType === "touch" || window.innerWidth < 761) return;
    document.querySelectorAll("#app .motion-card").forEach(el => {
      const r = el.getBoundingClientRect();
      const x = (event.clientX - r.left) / Math.max(1, r.width) - .5;
      const y = (event.clientY - r.top) / Math.max(1, r.height) - .5;
      if (x >= -.5 && x <= .5 && y >= -.5 && y <= .5) {
        el.style.setProperty("--tilt-y", (x * 5).toFixed(2) + "deg");
        el.style.setProperty("--tilt-x", (-y * 5).toFixed(2) + "deg");
      }
    });
  }, { passive: true });
  document.addEventListener("pointerout", event => {
    if (!event.relatedTarget) document.querySelectorAll("#app .motion-card").forEach(el => {
      el.style.setProperty("--tilt-x", "0deg");
      el.style.setProperty("--tilt-y", "0deg");
    });
  });
}

async function loadPage(name, options = {}) {
  const page = pages[name] ? name : "home";
  const requestId = ++activeRequest;
  try {
    const response = await fetch("./pages/" + pages[page], { cache: "no-cache" });
    if (!response.ok) throw new Error("Unable to load page: " + response.status);
    const markup = await response.text();
    if (requestId !== activeRequest) return;
    app.innerHTML = markup;
    setActivePage(page);
    refreshMotionTargets();
    if (options.updateUrl && location.hash !== "#" + page) history.pushState({ page }, "", "#" + page);
    closeMenus();
    if (options.scroll !== false) window.scrollTo({ top: 0, behavior: motionReduced ? "auto" : "smooth" });
  } catch (error) {
    if (requestId !== activeRequest) return;
    app.innerHTML = '<section class="content"><p class="eyebrow">PAGE UNAVAILABLE</p><h1 class="page-title">Could not load this page.</h1><p>' +
      String(error.message || "Check your connection and try again.") +
      '</p><button class="button" type="button" id="retryPage">Try again</button></section>';
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
document.addEventListener("keydown", event => { if (event.key === "Escape") closeMenus(); });
window.addEventListener("popstate", () => loadPage(location.hash.slice(1) || "home", { scroll: false }));
document.getElementById("year").textContent = new Date().getFullYear();
// Always start on Home when the site launches, even if an old #guns hash is saved in the URL.
if (location.hash) history.replaceState({ page: "home" }, "", location.pathname + location.search);
loadPage("home", { scroll: false });
