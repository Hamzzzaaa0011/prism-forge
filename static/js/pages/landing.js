if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const edges = document.querySelectorAll(".prism-edge, .prism-ray");
  edges.forEach((path) => {
    const length = path.getTotalLength?.() || 600;
    path.style.strokeDasharray = length;
    path.style.strokeDashoffset = length;
  });

  window.gsap
    .timeline({ defaults: { ease: "power3.out" } })
    .to(".prism-edge", { strokeDashoffset: 0, duration: 1.2, stagger: 0.12 }, 0.1)
    .to(".ray-in", { strokeDashoffset: 0, duration: 0.55 }, 0.55)
    .to(".prism-ray:not(.ray-in)", { strokeDashoffset: 0, duration: 0.8, stagger: 0.08 }, 0.9)
    .from(".lens-strip article", { opacity: 0, y: 28, duration: 0.55, stagger: 0.08 }, 0.35);
}
