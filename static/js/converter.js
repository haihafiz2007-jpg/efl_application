// Converter page.
async function loadCurrencies() {                                       // Fill both drop-down lists
  const response = await fetch("/api/currencies");                      // Ask the server for the currency list
  if (!response.ok) {
    throw new Error("Could not load currencies: " + response.status);
  }
  const currencies = await response.json();                             // Turn the reply into a JavaScript list
  for (const select of document.querySelectorAll(".currency-list")) {   // Do this for each drop-down
    for (const item of currencies) {                                    // And for each currency
      const option = document.createElement("option");                  // Make a new option element
      option.value = item.code;                                         // The value sent to the server, such as GBP
      option.textContent = item.code + " - " + item.name;               // The text the user sees
      select.appendChild(option);                                       // Add it to the drop-down
    }                                                                   // End of the currency loop
  }                                                                     // End of the drop-down loop
  document.getElementById("from").value = "GBP";                        // Start with pounds in the first list
  document.getElementById("to").value = "USD";                          // And dollars in the second
}                                                                       // End of loadCurrencies

async function handleConvert(event) {                                   // Runs when the form is sent
  event.preventDefault();                                               // Stop the browser reloading the page
  showMessage("error", "");                                             // Clear the old error
  showMessage("warning", "");                                           // Clear the old warning
  showMessage("result", "");                                            // Clear the old result
  const body = {                                                        // The data we send to the server
    amount: document.getElementById("amount").value,                    // What the user typed
    from: document.getElementById("from").value,                        // Chosen first currency
    to: document.getElementById("to").value,                            // Chosen second currency
  };                                                                    // End of the data
  cacheForm("converter", body);                                         // Cache the entries immediately, in case the system fails
  try {                                                                 // Catch network problems
    const reply = await postJson("/api/convert", body);                 // Send the request
    if (!reply.ok) {                                                    // The server answered with an error code such as 400
      showMessage("error", reply.data.error);                           // Show the server's message
      return;                                                           // Stop here
    }                                                                   // End of the error case
    const d = reply.data;                                               // Shorter name for the answer
    document.getElementById("result-card").hidden = false;
    showMessage("result", formatMoney(d.amount, d.from) + " = " + formatMoney(d.converted, d.to) + " at rate " + d.rate + ". Fee: " + formatMoney(d.fee_usd, "USD") + " (" + d.fee_percent + "%).");  // One sentence with the answer
    if (d.warning) {                                                    // The server sent a warning
      showMessage("warning", d.warning);                                // Show it
    }                                                                   // End of the warning case
    clearCachedForm("converter");                                       // It worked, so the cache is no longer needed
  } catch (problem) {                                                   // The request itself failed, for example the server is off
    showMessage("error", "Could not reach the server. Your entries are saved on this device; try again shortly.");  // Plain message; nothing is lost
  }                                                                     // End of try/catch
}                                                                       // End of handleConvert

async function startConverter() {                                       // Set the page up
  try {
    await loadCurrencies();                                             // Fill the lists first
  } catch (problem) {
    showMessage("error", "Could not load currency options. Refresh the page to try again.");
    console.error(problem);
    return;
  }
  const saved = restoreForm("converter");                               // Was something cached last time?
  if (saved) {                                                          // Yes: put the old entries back
    document.getElementById("amount").value = saved.amount;             // Restore the amount
    document.getElementById("from").value = saved.from;                 // Restore the first currency
    document.getElementById("to").value = saved.to;                     // Restore the second currency
  }                                                                     // End of the restore
  document.getElementById("convert-form").addEventListener("submit", handleConvert);  // When the form is sent, run handleConvert
  document.getElementById("swap-currencies").addEventListener("click", () => {
    const from = document.getElementById("from");
    const to = document.getElementById("to");
    [from.value, to.value] = [to.value, from.value];
  });
}                                                                       // End of startConverter

startConverter();                                                       // Run it as soon as the page loads
