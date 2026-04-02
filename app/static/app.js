const newsForm = document.getElementById("news-form");
const newsQueryInput = document.getElementById("news-query");
const newsSearchButton = document.getElementById("news-search-button");
const newsStatus = document.getElementById("news-status");
const articleList = document.getElementById("article-list");
const articleListLabel = document.getElementById("article-list-label");
const articleListCopy = document.getElementById("article-list-copy");

const form = document.getElementById("summary-form");
const submitButton = document.getElementById("submit-button");
const formStatus = document.getElementById("form-status");
const articleTextInput = document.getElementById("article_text");

const headlineEl = document.getElementById("headline");
const summaryEl = document.getElementById("summary");
const angleEl = document.getElementById("angle");
const modelEl = document.getElementById("model");

const escapeHTML = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const renderArticles = (query, articles) => {
  articleListLabel.textContent = `Available articles for "${query}"`;
  articleListCopy.textContent = "These are the fetched articles related to your search.";

  if (!articles.length) {
    articleList.innerHTML = `<p class="empty-state">No matching articles were returned for "${escapeHTML(query)}".</p>`;
    return;
  }

  articleList.innerHTML = articles
    .map((article, index) => {
      const description = escapeHTML(article.description || "No description available.");
      const sourceLine = escapeHTML([article.source, article.published_at].filter(Boolean).join(" • "));
      const title = escapeHTML(article.title);
      const url = escapeHTML(article.url);

      return `
        <article class="article-item">
          <div class="article-copy">
            <p class="article-meta">${sourceLine || "Unknown source"}</p>
            <h3>${title}</h3>
            <p>${description}</p>
          </div>
          <div class="article-actions">
            <button type="button" class="secondary-button" data-article-index="${index}">
              Load Article
            </button>
            <a href="${url}" target="_blank" rel="noreferrer">Open source</a>
          </div>
        </article>
      `;
    })
    .join("");

  articleList.querySelectorAll("[data-article-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const article = articles[Number(button.dataset.articleIndex)];
      articleTextInput.value = article.article_text || "";
      formStatus.textContent = `Loaded "${article.title}" into the summarizer.`;
      articleTextInput.focus();
    });
  });
};

newsForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = newsQueryInput.value.trim();
  if (query.length < 2) {
    newsStatus.textContent = "Enter at least 2 characters to search.";
    return;
  }

  newsSearchButton.disabled = true;
  newsStatus.textContent = "Fetching recent articles...";

  try {
    const response = await fetch(`/api/news?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Unable to fetch articles.");
    }

    renderArticles(query, data.articles || []);
    newsStatus.textContent = `Loaded ${data.articles.length} article${data.articles.length === 1 ? "" : "s"} related to "${query}".`;
  } catch (error) {
    articleList.innerHTML = '<p class="empty-state">Unable to load articles right now.</p>';
    articleListLabel.textContent = "Available articles";
    articleListCopy.textContent = "Search for a topic to load matching articles from NewsAPI.";
    newsStatus.textContent = error.message;
  } finally {
    newsSearchButton.disabled = false;
  }
});

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
