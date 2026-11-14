function showMessage(id, text) {
  document.getElementById(id).textContent = text;
}

function formatMoney(value, code) {
  return Number(value).toLocaleString("en-GB", { style: "currency", currency: code, currencyDisplay: "narrowSymbol", minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (response.status === 401) {
    window.location.href = "/login";
  }
  const data = await response.json();
  return { ok: response.ok, status: response.status, data: data };
}

function cacheForm(name, values) {
  try {
    localStorage.setItem("efl-" + name, JSON.stringify(values));
  } catch (problem) {
    console.warn("Could not cache the form", problem);
  }
}

function restoreForm(name) {
  try {
    const text = localStorage.getItem("efl-" + name);
    return text ? JSON.parse(text) : null;
  } catch (problem) {
    return null;
  }
}

function clearCachedForm(name) {
  try {
    localStorage.removeItem("efl-" + name);
  } catch (problem) {
    console.warn("Could not clear the cache", problem);
  }
}

const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage("login-message", "");
    try {
      const reply = await postJson("/api/login", {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      });
      if (!reply.ok) {
        showMessage("login-message", reply.data.error);
        return;
      }
      window.location.href = "/converter";
    } catch (problem) {
      showMessage("login-message", "Could not reach the server. Please try again.");
    }
  });
}

const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const reply = await postJson("/api/register", {
      name: document.getElementById("register-name").value,
      email: document.getElementById("register-email").value,
      phone: document.getElementById("register-phone").value,
      password: document.getElementById("register-password").value,
    }).catch(() => null);
    if (!reply) {
      showMessage("register-message", "Could not reach the server. Please try again.");
    } else if (!reply.ok) {
      showMessage("register-message", reply.data.error);
    } else {
      window.location.href = "/converter";
    }
  });
}

const accountForm = document.getElementById("account-form");
if (accountForm) {
  const cachedAccount = restoreForm("account");
  if (cachedAccount) {
    document.getElementById("account-name").value = cachedAccount.name;
    document.getElementById("account-phone").value = cachedAccount.phone;
  }
  accountForm.addEventListener("input", () => {
    cacheForm("account", {
      name: document.getElementById("account-name").value,
      phone: document.getElementById("account-phone").value,
    });
  });
  accountForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: document.getElementById("account-name").value,
          phone: document.getElementById("account-phone").value,
        }),
      });
      const data = await response.json();
      showMessage("account-message", response.ok ? "Your contact details were saved." : data.error);
      if (response.ok) {
        clearCachedForm("account");
      }
    } catch (problem) {
      showMessage("account-message", "Could not reach the server. Your details remain in this form.");
    }
  });
}

const logoutButton = document.getElementById("logout-button");
if (logoutButton) {
  logoutButton.addEventListener("click", async () => {
    try {
      await fetch("/api/logout", { method: "POST" });
      clearCachedForm("converter");
      clearCachedForm("quote");
      clearCachedForm("account");
      window.location.href = "/login";
    } catch (problem) {
      clearCachedForm("converter");
      clearCachedForm("quote");
      clearCachedForm("account");
      window.location.href = "/login";
    }
  });
}