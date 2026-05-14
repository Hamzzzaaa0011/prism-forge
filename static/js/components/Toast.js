export function showToast(message, variant = "info") {
  const root = document.getElementById("toast-root");
  if (!root) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${variant}`;
  toast.textContent = message;
  root.appendChild(toast);

  if (window.gsap) {
    window.gsap.fromTo(
      toast,
      { x: 80, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.28, ease: "power3.out" },
    );
  }

  window.setTimeout(() => {
    if (window.gsap) {
      window.gsap.to(toast, {
        x: 80,
        opacity: 0,
        duration: 0.2,
        onComplete: () => toast.remove(),
      });
    } else {
      toast.remove();
    }
  }, 4200);
}
