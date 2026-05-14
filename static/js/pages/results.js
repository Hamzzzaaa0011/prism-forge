import { showToast } from "../components/Toast.js";

const root = document.querySelector(".results-shell");
const lensKeys = ["viability", "risk", "timing", "differentiation", "personal_fit"];
const rendered = new Set();
let accumulated = "";

function findLensCard(lensName) {
  return document.querySelector(`[data-lens-card="${lensName}"]`);
}

function setText(parent, selector, value) {
  const node = parent?.querySelector(selector);
  if (node) node.textContent = value ?? "";
}

function renderLens(lensName, lens) {
  const card = findLensCard(lensName);
  if (!card || rendered.has(lensName)) return;

  card.classList.remove("is-loading");
  card.classList.add("is-filled", "glow");
  setText(card, "[data-lens-score]", lens.score);
  setText(card, "[data-lens-headline]", lens.headline);
  setText(card, "[data-lens-analysis]", lens.analysis);
  setText(card, "[data-lens-blind]", lens.blind_spot);
  rendered.add(lensName);

  if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    window.gsap.fromTo(card, { y: 18, opacity: 0.78 }, { y: 0, opacity: 1, duration: 0.42, ease: "power3.out" });
    window.setTimeout(() => card.classList.remove("glow"), 900);
  } else {
    window.setTimeout(() => card.classList.remove("glow"), 900);
  }
}

function animateScore(score) {
  const number = document.querySelector("[data-score-number]");
  const progress = document.querySelector("[data-score-progress]");
  const normalized = Number(score) || 0;
  const circumference = 2 * Math.PI * 52;

  if (progress) {
    progress.style.strokeDasharray = String(circumference);
    progress.style.strokeDashoffset = String(circumference - (circumference * normalized) / 100);
  }

  if (!number) return;
  if (!window.gsap || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    number.textContent = normalized;
    return;
  }

  const value = { n: 0 };
  window.gsap.to(value, {
    n: normalized,
    duration: 0.75,
    ease: "power3.out",
    onUpdate: () => {
      number.textContent = Math.round(value.n);
    },
  });
}

function renderComplete(analysis) {
  const verdict = document.querySelector("[data-verdict]");
  if (verdict) verdict.textContent = analysis.verdict || "";
  animateScore(analysis.composite_score);
  (analysis.lenses || []).forEach((lens) => renderLens(lens.lens_name, lens));
  showToast("Analysis complete.", "success");
}

function extractObjectForKey(source, key) {
  const keyIndex = source.indexOf(`"${key}"`);
  if (keyIndex === -1) return null;
  const colonIndex = source.indexOf(":", keyIndex);
  if (colonIndex === -1) return null;
  const start = source.indexOf("{", colonIndex);
  if (start === -1) return null;

  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let i = start; i < source.length; i += 1) {
    const char = source[i];

    if (escaped) {
      escaped = false;
      continue;
    }
    if (char === "\\") {
      escaped = true;
      continue;
    }
    if (char === '"') {
      inString = !inString;
      continue;
    }
    if (inString) continue;

    if (char === "{") depth += 1;
    if (char === "}") depth -= 1;
    if (depth === 0) {
      return source.slice(start, i + 1);
    }
  }

  return null;
}

function tryRenderPartialLenses() {
  lensKeys.forEach((lensName) => {
    if (rendered.has(lensName)) return;
    const objectText = extractObjectForKey(accumulated, lensName);
    if (!objectText) return;
    try {
      renderLens(lensName, JSON.parse(objectText));
    } catch {
      // Keep accumulating until the object is valid JSON.
    }
  });
}

function initExistingComplete() {
  const current = Number(document.querySelector("[data-score-number]")?.textContent);
  if (!Number.isNaN(current)) {
    animateScore(current);
  }
  document.querySelectorAll("[data-lens-card].is-filled").forEach((card) => {
    rendered.add(card.dataset.lensCard);
  });
}

function replayPrismRays() {
  if (!window.gsap || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const rays = document.querySelectorAll(".result-ray");
  rays.forEach((path) => {
    const length = path.getTotalLength?.() || 400;
    path.style.strokeDasharray = length;
    path.style.strokeDashoffset = length;
  });
  window.gsap.to(rays, {
    strokeDashoffset: 0,
    duration: 0.9,
    stagger: 0.08,
    ease: "power3.out",
  });
}

function initStream() {
  if (!root || root.dataset.shouldStream !== "true") {
    initExistingComplete();
    replayPrismRays();
    return;
  }

  const source = new EventSource(`/api/v1/analyze/stream/${root.dataset.analysisId}`);

  source.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    if (payload.type === "started") {
      showToast("Analysis started.", "info");
      return;
    }
    if (payload.type === "chunk") {
      accumulated += payload.chunk;
      tryRenderPartialLenses();
      return;
    }
    if (payload.type === "complete") {
      source.close();
      renderComplete(payload.analysis);
      replayPrismRays();
      return;
    }
    if (payload.type === "failed") {
      source.close();
      showToast(payload.error || "The lenses went dark. Try again in a moment.", "error");
    }
  };

  source.onerror = () => {
    source.close();
    showToast("The stream was interrupted. Refresh to check the saved result.", "error");
  };
}

initStream();
