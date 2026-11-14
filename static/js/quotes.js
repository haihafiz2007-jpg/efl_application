function quoteNumber(value) {
  return Math.round(Number(value)).toLocaleString("en-GB");
}

function formatQuoteInput(input) {
  const value = input.value.replace(/,/g, "").trim();
  if (/^\d+(?:\.\d{0,2})?$/.test(value)) {
    input.value = Number(value).toLocaleString("en-GB", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
}

function quoteFormData() {
  return {
    plan_id: document.getElementById("plan").value,
    lump_sum: document.getElementById("lump-sum").value.replace(/,/g, ""),
    monthly_amount: document.getElementById("monthly-amount").value.replace(/,/g, ""),
    save: true,
  };
}

function renderProjectionChart(projections) {
  const years = [1, 5, 10];
  const values = years.map((year) => Number(projections.mid[String(year)].final_value));
  const max = Math.max(...values, 1);
  const bars = values.map((value, index) => {
    const height = Math.max((value / max) * 150, 4);
    return `<rect class="chart-bar chart-bar-${index}" x="${75 + index * 130}" y="${190 - height}" width="72" height="${height}"></rect>`;
  }).join("");
  document.getElementById("projection-chart").innerHTML =
    `<svg viewBox="0 0 480 210" role="img" aria-label="Estimated savings value bars at 1, 5, and 10 years">${bars}<line class="chart-baseline" x1="25" y1="190" x2="455" y2="190"></line></svg>`;
}

function displayQuote(data) {
  const results = document.getElementById("quote-results");
  results.hidden = false;
  document.getElementById("recommendation").textContent =
    "Recommended plan: Option " + data.recommended_plan_id + " " + data.recommended_plan_name;
  const rows = document.getElementById("projection-rows");
  rows.replaceChildren();
  for (const year of [1, 5, 10]) {
    const low = data.projections.low[String(year)];
    const mid = data.projections.mid[String(year)];
    const high = data.projections.high[String(year)];
    const row = document.createElement("tr");
    for (const value of [
      year,
      quoteNumber(low.final_value),
      quoteNumber(high.final_value),
      quoteNumber(mid.total_profit),
      quoteNumber(mid.total_fees),
      quoteNumber(mid.total_tax),
    ]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    rows.appendChild(row);
  }
  renderProjectionChart(data.projections);
}

const quoteForm = document.getElementById("quote-form");
if (quoteForm) {
  const cached = restoreForm("quote");
  if (cached) {
    document.getElementById("plan").value = cached.plan_id;
    document.getElementById("lump-sum").value = cached.lump_sum;
    document.getElementById("monthly-amount").value = cached.monthly_amount;
  }
  for (const input of document.querySelectorAll("#lump-sum, #monthly-amount")) {
    formatQuoteInput(input);
    input.addEventListener("blur", () => formatQuoteInput(input));
  }
  quoteForm.addEventListener("input", () => {
    cacheForm("quote", quoteFormData());
  });
  quoteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = quoteFormData();
    cacheForm("quote", body);
    showMessage("quote-message", "");
    try {
      const reply = await postJson("/api/quotes", body);
      if (!reply.ok) {
        showMessage("quote-message", reply.data.error);
        return;
      }
      displayQuote(reply.data);
      clearCachedForm("quote");
    } catch (problem) {
      showMessage("quote-message", "Could not reach the server. Your entries are saved on this device; try again shortly.");
    }
  });
}
