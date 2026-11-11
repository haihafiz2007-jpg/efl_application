// EFL shared browser helpers, loaded on every page.
function showMessage(id, text) {                                        // Put text into one of the message areas
  document.getElementById(id).textContent = text;                       // textContent shows plain text only, so nobody can inject HTML
}                                                                       // End of showMessage

function formatMoney(value, code) {                                     // Show a number as money with two decimal places
  return Number(value).toLocaleString("en-GB", { style: "currency", currency: code, currencyDisplay: "narrowSymbol", minimumFractionDigits: 2, maximumFractionDigits: 2 });  // Brief: values shown as currency to two decimal places (yen too); narrowSymbol gives $ and £ instead of US$
}                                                                       // End of formatMoney

async function postJson(url, body) {                                    // Send JSON to the server and read the JSON reply
  const response = await fetch(url, {                                   // Send the request; await waits for the reply
    method: "POST",                                                     // POST, as in the route table
    headers: { "Content-Type": "application/json" },                    // Tell the server the body is JSON
    body: JSON.stringify(body),                                         // Turn our data into JSON text
  });                                                                   // End of the request
  if (response.status === 401) {                                        // Not signed in (this starts to happen on Thursday)
    window.location.href = "/login";                                    // Send the user to the login page
  }                                                                     // End of the if
  const data = await response.json();                                   // Read the reply as JSON
  return { ok: response.ok, status: response.status, data: data };      // Give the caller everything it needs
}                                                                       // End of postJson

function cacheForm(name, values) {                                      // Keep what the user typed on this device straight away
  try {                                                                 // Browsers can refuse storage, so protect the call
    localStorage.setItem("efl-" + name, JSON.stringify(values));        // Store the values as text under a name
  } catch (problem) {                                                   // Storage was refused
    console.warn("Could not cache the form", problem);                  // Note it in the browser console and carry on
  }                                                                     // End of try/catch
}                                                                       // End of cacheForm

function restoreForm(name) {                                            // Read back what was cached
  try {                                                                 // Protect the call
    const text = localStorage.getItem("efl-" + name);                   // Read the stored text
    return text ? JSON.parse(text) : null;                              // Turn it back into an object, or null if nothing is stored
  } catch (problem) {                                                   // Storage or JSON failed
    return null;                                                        // Behave as if nothing was stored
  }                                                                     // End of try/catch
}                                                                       // End of restoreForm

function clearCachedForm(name) {                                        // Remove the cache once the request succeeded
  try {                                                                 // Protect the call
    localStorage.removeItem("efl-" + name);                             // Delete the stored entry
  } catch (problem) {                                                   // Storage was refused
    console.warn("Could not clear the cache", problem);                 // Note it and carry on
  }                                                                     // End of try/catch
}                                                                       // End of clearCachedForm

const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    showMessage("login-message", "Sign-in is not connected in this project demo yet.");
  });
}

const quoteForm = document.getElementById("quote-form");
if (quoteForm) {
  quoteForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const plan = document.getElementById("plan");
    showMessage("quote-message", "Plan selected: " + plan.options[plan.selectedIndex].text + ". Projection calculations are not connected yet.");
  });
}