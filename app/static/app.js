const form = document.getElementById("summary-form");
const submitButton = document.getElementById("submit-button");
const formStatus = document.getElementById("form-status");

const headlineEl = document.getElementById("headline");
const summaryEl = document.getElementById("summary");
const angleEl = document.getElementById("angle");
const modelEl = document.getElementById("model");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const articleText = String(formData.get("article_text") || "").trim();
  const tone = String(formData.get("tone") || "clear and concise").trim();

  if (articleText.length < 50) {
    formStatus.textContent = "Paste at least 50 characters of article text.";
    return;
  }

  submitButton.disabled = true;
  formStatus.textContent = "Summarizing with Groq...";

  try {
    const response = await fetch("/api/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        article_text: articleText,
        tone,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Something went wrong.");
    }

    headlineEl.textContent = data.headline || "No headline returned";
    summaryEl.textContent = data.summary || "No summary returned";
    angleEl.textContent = data.angle || "No angle returned";
    modelEl.textContent = data.model || "Unknown model";
    formStatus.textContent = "Summary ready.";
  } catch (error) {
    formStatus.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
