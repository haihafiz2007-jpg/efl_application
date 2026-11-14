function quoteMoney(value) {
  return "£" + Number(value).toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderProjectionChart(projections) {
  const years = [1, 5, 10];
  const values = years.map((year) => Number(projections.mid[String(year)].final_value));
  const max = Math.max(...values, 1);
  const points = values.map((value, index) => {
    const x = 50 + index * 190;
    const y = 180 - (value / max) * 145;
    return { x, y, value, year: years[index] };
  });
  const path = points.map((point, index) => `${index ? "L" : "M"} ${point.x} ${point.y}`).join(" ");
  const markers = points.map((point) =>
    `<circle cx="${point.x}" cy="${point.y}" r="5"></circle><text x="${point.x}" y="${point.y - 12}" text-anchor="middle">${quoteMoney(point.value)}</text><text x="${point.x}" y="210" text-anchor="middle">${point.year} year${point.year === 1 ? "" : "s"}</text>`
  ).join("");
  document.getElementById("projection-chart").innerHTML =
    `<svg viewBox="0 0 480 230" role="img" aria-label="Mid-case projected savings value over time"><path class="chart-line" d="${path}"></path>${markers}</svg>`;
}

function displayQuote(data) {
  const results = document.getElementById("quote-results");
  results.hidden = false;
  document.getElementById("quote-result-title").textContent = data.plan_name + " projection";
  document.getElementById("recommendation").textContent =
    "Best 10-year estimated outcome among eligible plans: " + data.recommended_plan_name + ".";
  const rows = document.getElementById("projection-rows");
  rows.replaceChildren();
  for (const scenario of ["low", "mid", "high"]) {
    for (const year of [1, 5, 10]) {
      const projection = data.projections[scenario][String(year)];
      const row = document.createElement("tr");
      for (const value of [
        scenario === "mid" ? "Mid" : scenario[0].toUpperCase() + scenario.slice(1),
        year + (year === 1 ? " year" : " years"),
        quoteMoney(projection.final_value),
        quoteMoney(projection.total_profit),
        quoteMoney(projection.total_fees),
        quoteMoney(projection.total_tax),
      ]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      }
      rows.appendChild(row);
    }
  }
  renderProjectionChart(data.projections);
  const saveButton = document.getElementById("save-quote-button");
  saveButton.hidden = data.is_saved;
  saveButton.dataset.quoteId = data.quote_id;
}

const quoteForm = document.getElementById("quote-form");
if (quoteForm) {
  const cached = restoreForm("quote");
  if (cached) {
    document.getElementById("plan").value = cached.plan_id;
    document.getElementById("lump-sum").value = cached.lump_sum;
    document.getElementById("monthly-amount").value = cached.monthly_amount;
    document.getElementById("save-quote").checked = Boolean(cached.save);
  }
  quoteForm.addEventListener("input", () => {
    cacheForm("quote", {
      plan_id: document.getElementById("plan").value,
      lump_sum: document.getElementById("lump-sum").value,
      monthly_amount: document.getElementById("monthly-amount").value,
      save: document.getElementById("save-quote").checked,
    });
  });
  quoteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = {
      plan_id: document.getElementById("plan").value,
      lump_sum: document.getElementById("lump-sum").value,
      monthly_amount: document.getElementById("monthly-amount").value,
      save: document.getElementById("save-quote").checked,
    };
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
  document.getElementById("save-quote-button").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    try {
      const response = await fetch(`/api/quotes/${button.dataset.quoteId}/save`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        showMessage("quote-message", data.error);
        return;
      }
      button.hidden = true;
      showMessage("quote-message", "Quote saved to your history.");
    } catch (problem) {
      showMessage("quote-message", "Could not reach the server. Your quote is still available on this page.");
    }
  });
}
