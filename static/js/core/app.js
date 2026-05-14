function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function initMobileNav() {
  const topbar = document.querySelector("[data-topbar]");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (!topbar || !toggle) return;

  toggle.addEventListener("click", () => {
    const isOpen = topbar.classList.toggle("is-open");
    toggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    const icon = toggle.querySelector("i");
    if (icon) icon.setAttribute("data-lucide", isOpen ? "x" : "menu");
    initIcons();
  });
}

function initPageEntrance() {
  if (!window.gsap || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  window.gsap.from("main > *", {
    opacity: 0,
    y: 18,
    duration: 0.6,
    ease: "power3.out",
  });
}

initIcons();
initMobileNav();
initPageEntrance();
