import { API } from "../core/api.js";
import { showToast } from "../components/Toast.js";

const form = document.getElementById("idea-form");
const description = document.getElementById("description");
const contextField = document.getElementById("context");
const counter = document.querySelector("[data-char-count]");
const submitButton = document.querySelector("[data-submit-button]");

function syncTextareaHeight(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = `${textarea.scrollHeight}px`;
}

function syncCounter() {
  const used = description.value.length;
  const max = Number(description.getAttribute("maxlength") || 2000);
  counter.textContent = `${used} / ${max}`;
  counter.classList.toggle("is-warning", used >= max * 0.8 && used < max);
  counter.classList.toggle("is-danger", used >= max);
}

[description, contextField].forEach((textarea) => {
  textarea?.addEventListener("input", () => syncTextareaHeight(textarea));
  if (textarea) syncTextareaHeight(textarea);
});

description?.addEventListener("input", syncCounter);
syncCounter();

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  submitButton.querySelector("span").textContent = "Aligning lenses...";

  const payload = {
    title: document.getElementById("title").value.trim(),
    category: document.getElementById("category").value,
    description: description.value.trim(),
    context: contextField.value.trim(),
  };

  try {
    const ideaData = await API.post("/ideas", payload);
    const analysisData = await API.post("/analyze", { idea_id: ideaData.idea.id });
    window.location.href = `/results/${analysisData.analysis_id}`;
  } catch (error) {
    showToast(error.message || "The lenses went dark. Try again in a moment.", "error");
    submitButton.disabled = false;
    submitButton.querySelector("span").textContent = "Analyze";
  }
});
