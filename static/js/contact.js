(() => {
  const button = document.querySelector("[data-copy-email]");
  if (!button) return;

  const feedback = document.querySelector(".copy-feedback");
  const label = button.querySelector("[data-copy-label]");
  const originalLabel = label ? label.textContent : "Copy email";

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    const field = document.createElement("textarea");
    field.value = value;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.appendChild(field);
    field.select();
    const copied = document.execCommand("copy");
    field.remove();
    if (!copied) throw new Error("Clipboard copy failed");
  }

  button.addEventListener("click", async () => {
    const email = button.dataset.copyEmail;
    try {
      await copyText(email);
      if (label) label.textContent = "Email copied";
      if (feedback) feedback.textContent = "EMAIL COPIED TO CLIPBOARD";
    } catch (error) {
      if (label) label.textContent = "Copy unavailable";
      if (feedback) feedback.textContent = "SELECT THE EMAIL ADDRESS TO COPY IT";
    }
    window.setTimeout(() => {
      if (label) label.textContent = originalLabel;
      if (feedback) feedback.textContent = "";
    }, 2200);
  });
})();
