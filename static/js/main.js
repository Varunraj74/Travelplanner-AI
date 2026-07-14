/**
 * TravelPlannerPro — Main JavaScript
 * IBM SkillsBuild Final Project | Problem Statement No. 5
 * Handles: Travel form submission, AI chat, PDF export, dark mode, markdown rendering
 */

"use strict";

/* ─── State ───────────────────────────────────────────────────── */
const State = {
  itinerary: null,
  travelData: null,
  isGenerating: false,
  isChatting: false,
  loadingInterval: null,
};

/* ─── DOM Ready ───────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initInterestTags();
  initTravelForm();
  initWorkspace();
  initChat();
  initPdfExport();
  initDashboardChat();
});

/* =========================================================
   THEME TOGGLE
   ========================================================= */
function initThemeToggle() {
  const btn = document.getElementById("themeToggle");
  if (!btn) return;

  const saved = localStorage.getItem("tpp-theme") || "dark";
  applyTheme(saved);

  btn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("tpp-theme", next);
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.getElementById("themeToggle");
  if (!btn) return;
  const icon = btn.querySelector("i");
  if (icon) {
    icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
  }
}

/* =========================================================
   INTEREST TAGS (Dashboard)
   ========================================================= */
function initInterestTags() {
  const container = document.getElementById("interestTags");
  const textarea = document.getElementById("interests");
  if (!container || !textarea) return;

  container.querySelectorAll(".interest-tag").forEach((tag) => {
    tag.addEventListener("click", () => {
      tag.classList.toggle("selected");
      const selected = Array.from(container.querySelectorAll(".interest-tag.selected"))
        .map((t) => t.dataset.value)
        .join(", ");
      textarea.value = selected;
    });
  });
}

/* =========================================================
   TRAVEL FORM (Dashboard)
   ========================================================= */
function initTravelForm() {
  const form = document.getElementById("travelForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (State.isGenerating) return;

    if (!validateForm(form)) return;

    const formData = collectFormData(form);
    await generateItinerary(formData);
  });
}

function collectFormData(form) {
  const fd = new FormData(form);
  return {
    source:           fd.get("source")?.trim() || "",
    destination:      fd.get("destination")?.trim() || "",
    departure_date:   fd.get("departure_date") || "",
    return_date:      fd.get("return_date") || "",
    travelers:        parseInt(fd.get("travelers") || "1"),
    budget:           fd.get("budget") || "",
    travel_style:     fd.get("travel_style") || "leisure",
    transport:        fd.get("transport") || "any",
    hotel_pref:       fd.get("hotel_pref") || "mid-range",
    interests:        fd.get("interests")?.trim() || "",
    special_requests: fd.get("special_requests")?.trim() || "",
  };
}

function validateForm(form) {
  let valid = true;

  const fields = [
    { id: "source",         msg: "Please enter your departure city." },
    { id: "destination",    msg: "Please enter your destination." },
    { id: "departure_date", msg: "Please select a departure date." },
    { id: "return_date",    msg: "Please select a return date." },
    { id: "budget",         msg: "Please select a budget range." },
  ];

  // Clear previous errors
  fields.forEach(({ id }) => {
    const el = document.getElementById(id);
    const err = document.getElementById(`${id}-error`);
    if (el) el.classList.remove("is-invalid", "is-valid");
    if (err) err.textContent = "";
  });

  fields.forEach(({ id, msg }) => {
    const el = document.getElementById(id);
    const err = document.getElementById(`${id}-error`);
    if (!el) return;
    if (!el.value || !el.value.trim()) {
      el.classList.add("is-invalid");
      if (err) err.textContent = msg;
      valid = false;
    } else {
      el.classList.add("is-valid");
    }
  });

  // Cross-validate dates
  const dep = document.getElementById("departure_date");
  const ret = document.getElementById("return_date");
  if (dep?.value && ret?.value && ret.value <= dep.value) {
    ret.classList.remove("is-valid");
    ret.classList.add("is-invalid");
    const err = document.getElementById("return_date-error");
    if (err) err.textContent = "Return date must be after departure date.";
    valid = false;
  }

  return valid;
}

async function generateItinerary(formData) {
  State.isGenerating = true;
  State.travelData = formData;

  showLoadingOverlay();

  try {
    const res = await fetch("/api/generate-itinerary", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(formData),
    });

    const json = await res.json();

    if (!json.success) {
      hideLoadingOverlay();
      showFormError(json.error || "Failed to generate itinerary.");
      return;
    }

    // Store globally for workspace
    State.itinerary  = json.data.itinerary;
    State.travelData = formData;

    // Persist to sessionStorage for workspace page
    sessionStorage.setItem("tpp_itinerary",   JSON.stringify(json.data));
    sessionStorage.setItem("tpp_travel_data", JSON.stringify(formData));

    hideLoadingOverlay();

    // Redirect to workspace
    window.location.href = "/workspace";

  } catch (err) {
    hideLoadingOverlay();
    showFormError("Network error. Please check your connection and try again.");
    console.error("generateItinerary error:", err);
  } finally {
    State.isGenerating = false;
  }
}

function showFormError(msg) {
  let el = document.getElementById("formError");
  if (!el) {
    el = document.createElement("div");
    el.id = "formError";
    el.className = "alert alert-warning-custom mt-3";
    const form = document.getElementById("travelForm");
    form?.appendChild(el);
  }
  el.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>${msg}`;
  el.style.display = "block";
  el.scrollIntoView({ behavior: "smooth", block: "center" });
}

/* ─── Loading Overlay ──────────────────────────────────────── */
function showLoadingOverlay() {
  const overlay = document.getElementById("loadingOverlay");
  if (!overlay) return;
  overlay.classList.remove("d-none");

  const bar    = document.getElementById("loadingBar");
  const steps  = ["step1", "step2", "step3", "step4"];
  const msgs   = [
    "🔍 Analysing your preferences...",
    "🗺️ Building day-wise itinerary...",
    "💰 Calculating budget breakdown...",
    "✨ Adding hidden gems & tips...",
  ];

  let progress = 0;
  let stepIdx  = 0;

  // Reset steps
  steps.forEach((id) => {
    const el = document.getElementById(id);
    if (el) { el.classList.remove("active", "done"); }
  });
  if (document.getElementById("step1")) document.getElementById("step1").classList.add("active");
  if (bar) bar.style.width = "0%";

  State.loadingInterval = setInterval(() => {
    progress += Math.random() * 8 + 3;
    if (progress > 92) progress = 92;
    if (bar) bar.style.width = `${progress}%`;

    const msgEl = document.getElementById("loadingMessage");
    if (msgEl && msgs[stepIdx]) msgEl.textContent = msgs[stepIdx];

    if (stepIdx < steps.length) {
      const prev = document.getElementById(steps[stepIdx]);
      if (prev) { prev.classList.remove("active"); prev.classList.add("done"); }
    }
    stepIdx = Math.min(stepIdx + 1, steps.length - 1);
    const curr = document.getElementById(steps[stepIdx]);
    if (curr) curr.classList.add("active");

    if (progress >= 92) clearInterval(State.loadingInterval);
  }, 1800);
}

function hideLoadingOverlay() {
  clearInterval(State.loadingInterval);
  const bar = document.getElementById("loadingBar");
  if (bar) bar.style.width = "100%";
  setTimeout(() => {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) overlay.classList.add("d-none");
  }, 400);
}

/* =========================================================
   WORKSPACE
   ========================================================= */
function initWorkspace() {
  const itineraryContent = document.getElementById("itineraryContent");
  if (!itineraryContent) return;

  // Load from sessionStorage
  const raw  = sessionStorage.getItem("tpp_itinerary");
  const tdRaw = sessionStorage.getItem("tpp_travel_data");

  if (!raw) return;

  try {
    const data = JSON.parse(raw);
    const td   = tdRaw ? JSON.parse(tdRaw) : {};

    State.itinerary  = data.itinerary;
    State.travelData = td;

    renderItinerary(data, td);
    renderTripHeader(data, td);

    document.getElementById("emptyItinerary")?.setAttribute("style", "display:none");
    itineraryContent.style.display = "flex";
  } catch (e) {
    console.error("Workspace load error:", e);
  }

  // Copy button
  document.getElementById("copyItinerary")?.addEventListener("click", copyItinerary);

  // Print button
  document.getElementById("printItinerary")?.addEventListener("click", () => window.print());

  // Toggle chat panel
  document.getElementById("toggleChatPanel")?.addEventListener("click", toggleChatPanel);
}

function renderItinerary(data, td) {
  const body = document.getElementById("itineraryBody");
  if (!body || !data.itinerary) return;
  body.innerHTML = markdownToHtml(data.itinerary);
}

function renderTripHeader(data, td) {
  const route = document.getElementById("tripRoute");
  const meta  = document.getElementById("tripMetaRow");
  if (!route || !td) return;

  const src  = td.source || "Origin";
  const dest = td.destination || "Destination";
  route.textContent = `${src}  ✈  ${dest}`;

  if (meta) {
    const items = [
      { icon: "📅", label: td.departure_date || "" },
      { icon: "🏠", label: td.return_date || "" },
      { icon: "👥", label: `${td.travelers || 1} traveller${td.travelers > 1 ? "s" : ""}` },
      { icon: "💰", label: td.budget || "" },
      { icon: "🏨", label: td.hotel_pref || "" },
      { icon: data.demo_mode ? "🟡" : "🟢", label: data.demo_mode ? "Demo Mode" : "IBM Granite AI" },
    ].filter((i) => i.label);

    meta.innerHTML = items
      .map((i) => `<span class="trip-meta-badge">${i.icon} ${i.label}</span>`)
      .join("");
  }
}

function copyItinerary() {
  if (!State.itinerary) return;
  navigator.clipboard
    .writeText(State.itinerary)
    .then(() => showToast("copyToast"))
    .catch(() => alert("Copy failed. Please select and copy manually."));
}

function toggleChatPanel() {
  const right = document.getElementById("workspaceRight");
  if (!right) return;
  right.classList.toggle("collapsed");
  const icon = document.querySelector("#toggleChatPanel i");
  if (icon) {
    icon.className = right.classList.contains("collapsed")
      ? "bi bi-arrow-bar-left"
      : "bi bi-arrow-bar-right";
  }
}

/* =========================================================
   MARKDOWN → HTML  (simple renderer)
   ========================================================= */
function markdownToHtml(md) {
  if (!md) return "";

  const escapeHtml = (s) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  let html = "";
  const lines = md.split("\n");
  let inCode   = false;
  let inTable  = false;
  let tableRows = [];

  const flushTable = () => {
    if (!tableRows.length) return;
    let t = '<table>';
    tableRows.forEach((row, i) => {
      const cells = row.split("|").map((c) => c.trim()).filter((c) => c !== "");
      if (i === 0) {
        t += "<thead><tr>" + cells.map((c) => `<th>${c}</th>`).join("") + "</tr></thead><tbody>";
      } else if (!cells.every((c) => /^[-:]+$/.test(c))) {
        t += "<tr>" + cells.map((c) => `<td>${processInline(c)}</td>`).join("") + "</tr>";
      }
    });
    t += "</tbody></table>";
    html += t;
    tableRows = [];
    inTable = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Code block
    if (trimmed.startsWith("```")) {
      if (inCode) { html += "</code></pre>"; inCode = false; }
      else { if (inTable) flushTable(); html += "<pre><code>"; inCode = true; }
      continue;
    }
    if (inCode) { html += escapeHtml(line) + "\n"; continue; }

    // Table rows
    if (trimmed.startsWith("|")) {
      if (!inTable) inTable = true;
      tableRows.push(trimmed);
      continue;
    }
    if (inTable) flushTable();

    // HR
    if (/^[-*]{3,}$/.test(trimmed)) { html += "<hr/>"; continue; }

    // Headings
    const hMatch = trimmed.match(/^(#{1,4})\s+(.*)/);
    if (hMatch) {
      const level = hMatch[1].length;
      html += `<h${level}>${processInline(hMatch[2])}</h${level}>`;
      continue;
    }

    // Blockquote
    if (trimmed.startsWith("> ")) {
      html += `<blockquote>${processInline(trimmed.slice(2))}</blockquote>`;
      continue;
    }

    // Unordered list
    if (/^[-*•]\s/.test(trimmed)) {
      html += `<ul><li>${processInline(trimmed.slice(2))}</li></ul>`;
      continue;
    }

    // Ordered list
    if (/^\d+\.\s/.test(trimmed)) {
      html += `<ol><li>${processInline(trimmed.replace(/^\d+\.\s/, ""))}</li></ol>`;
      continue;
    }

    // Empty line
    if (!trimmed) { html += "<br/>"; continue; }

    // Paragraph
    html += `<p>${processInline(trimmed)}</p>`;
  }

  if (inTable) flushTable();
  if (inCode)  html += "</code></pre>";

  // Merge adjacent ul/ol items
  html = html
    .replace(/<\/ul>\s*<ul>/g, "")
    .replace(/<\/ol>\s*<ol>/g, "");

  return html;
}

function processInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" class="chat-link">$1</a>');
}

/* =========================================================
   CHAT ASSISTANT
   ========================================================= */
function initChat() {
  const input   = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendChatBtn");
  const clearBtn = document.getElementById("clearChatBtn");
  if (!input && !sendBtn) return;

  // Send on button click
  sendBtn?.addEventListener("click", sendChat);

  // Send on Enter (Shift+Enter for new line)
  input?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });

  // Auto-resize textarea
  input?.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });

  // Prompt chips
  document.querySelectorAll(".prompt-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      if (input) {
        input.value = chip.dataset.msg || "";
        input.focus();
      }
      sendChat();
    });
  });

  // Clear chat
  clearBtn?.addEventListener("click", async () => {
    if (!confirm("Clear conversation history?")) return;
    try {
      await fetch("/api/chat/clear", { method: "POST" });
      const msgs = document.getElementById("chatMessages");
      if (msgs) {
        msgs.innerHTML = "";
        appendAssistantBubble(
          "💬 Chat cleared! Ask me anything about your trip.",
          "ARIA"
        );
      }
    } catch (e) {
      console.error("Clear chat error:", e);
    }
  });
}

async function sendChat() {
  const input   = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendChatBtn");
  if (!input || State.isChatting) return;

  const msg = input.value.trim();
  if (!msg) return;

  State.isChatting = true;
  input.value = "";
  input.style.height = "auto";
  if (sendBtn) sendBtn.disabled = true;

  // Hide suggested prompts on first message
  document.getElementById("suggestedPrompts")?.classList.add("d-none");

  // Append user bubble
  appendUserBubble(msg);

  // Show typing indicator
  showTyping(true);

  try {
    const res = await fetch("/api/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: msg }),
    });

    const json = await res.json();
    showTyping(false);

    if (json.success) {
      appendAssistantBubble(json.data.response, "ARIA");
    } else {
      appendAssistantBubble(
        "⚠️ Sorry, I couldn't process that request. Please try again.",
        "ARIA"
      );
    }
  } catch (e) {
    showTyping(false);
    appendAssistantBubble("🔌 Network error. Please check your connection.", "ARIA");
    console.error("Chat error:", e);
  } finally {
    State.isChatting = false;
    if (sendBtn) sendBtn.disabled = false;
    input.focus();
  }
}

function appendUserBubble(text) {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const el = document.createElement("div");
  el.className = "chat-bubble user";
  el.innerHTML = `
    <div class="bubble-content">${escapeText(text)}</div>
    <div class="bubble-time text-end">You · ${now}</div>
  `;
  container.appendChild(el);
  scrollChat();
}

function appendAssistantBubble(text, name = "ARIA") {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const el = document.createElement("div");
  el.className = "chat-bubble assistant";
  el.innerHTML = `
    <div class="bubble-content">${markdownToHtml(text)}</div>
    <div class="bubble-time">${name} · ${now}</div>
  `;
  container.appendChild(el);
  scrollChat();
}

function showTyping(show) {
  const el = document.getElementById("chatTyping");
  if (!el) return;
  if (show) {
    el.classList.remove("d-none");
    el.classList.add("d-flex");
    scrollChat();
  } else {
    el.classList.remove("d-flex");
    el.classList.add("d-none");
  }
}

function scrollChat() {
  const container = document.getElementById("chatMessages");
  if (container) {
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
  }
}

function escapeText(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br/>");
}

/* =========================================================
   PDF EXPORT
   ========================================================= */
function initPdfExport() {
  const btn = document.getElementById("exportPdfBtn");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    if (!State.itinerary) {
      showToast("exportToast", "⚠️ No itinerary to export. Please generate a plan first.");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Generating PDF...';
    showToast("exportToast", "📄 Generating your professional PDF...");

    try {
      const res = await fetch("/api/export-pdf", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({
          itinerary:   State.itinerary,
          travel_data: State.travelData,
        }),
      });

      if (res.ok && res.headers.get("Content-Type")?.includes("application/pdf")) {
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a");

        const dest   = State.travelData?.destination || "Trip";
        const ts     = new Date().toISOString().slice(0, 10);
        a.download   = `TravelPlan_${dest}_${ts}.pdf`;
        a.href       = url;
        a.click();

        URL.revokeObjectURL(url);
        showToast("exportToast", "✅ PDF downloaded successfully!");
      } else {
        const json = await res.json().catch(() => ({}));
        showToast("exportToast", `❌ ${json.error || "PDF export failed."}`);
      }
    } catch (e) {
      showToast("exportToast", "❌ Network error during PDF export.");
      console.error("PDF export error:", e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-file-earmark-pdf me-1"></i>Export PDF';
    }
  });
}

/* =========================================================
   TOAST UTILITY
   ========================================================= */
function showToast(toastId, message) {
  const el = document.getElementById(toastId);
  if (!el) return;

  if (message) {
    const body = document.getElementById("toastBody") || el.querySelector(".toast-body");
    if (body) body.innerHTML = message;
  }

  const toast = bootstrap.Toast.getOrCreateInstance(el, { delay: 4000 });
  toast.show();
}

/* =========================================================
   DASHBOARD INLINE CHAT  (shared ARIA chat on /dashboard)
   ========================================================= */
function initDashboardChat() {
  const input   = document.getElementById("dashChatInput");
  const sendBtn = document.getElementById("dashSendBtn");
  const clearBtn = document.getElementById("dashClearChat");
  if (!input || !sendBtn) return;

  // Send on button click
  sendBtn.addEventListener("click", sendDashChat);

  // Send on Enter (Shift+Enter = new line)
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendDashChat();
    }
  });

  // Auto-resize textarea
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });

  // Prompt buttons
  document.querySelectorAll(".dash-prompt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      input.value = btn.dataset.msg || "";
      sendDashChat();
    });
  });

  // Clear chat
  clearBtn?.addEventListener("click", async () => {
    if (!confirm("Clear conversation history?")) return;
    try {
      await fetch("/api/chat/clear", { method: "POST" });
      const msgs = document.getElementById("dashChatMessages");
      if (msgs) {
        msgs.innerHTML = "";
        appendDashAssistant("💬 Chat cleared! Ask me anything about your trip.");
      }
    } catch (e) {
      console.error("Clear dash chat error:", e);
    }
  });
}

let _dashChatting = false;

async function sendDashChat() {
  const input   = document.getElementById("dashChatInput");
  const sendBtn = document.getElementById("dashSendBtn");
  if (!input || _dashChatting) return;

  const msg = input.value.trim();
  if (!msg) return;

  _dashChatting = true;
  input.value = "";
  input.style.height = "auto";
  if (sendBtn) sendBtn.disabled = true;

  appendDashUser(msg);
  showDashTyping(true);

  try {
    const res  = await fetch("/api/chat", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: msg }),
    });
    const json = await res.json();
    showDashTyping(false);

    if (json.success) {
      appendDashAssistant(json.data.response);
    } else {
      appendDashAssistant("⚠️ Sorry, I couldn't process that. Please try again.");
    }
  } catch (e) {
    showDashTyping(false);
    appendDashAssistant("🔌 Network error. Please check your connection.");
    console.error("Dash chat error:", e);
  } finally {
    _dashChatting = false;
    if (sendBtn) sendBtn.disabled = false;
    input.focus();
  }
}

function appendDashUser(text) {
  const c   = document.getElementById("dashChatMessages");
  if (!c) return;
  const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const el  = document.createElement("div");
  el.className = "chat-bubble user";
  el.innerHTML = `
    <div class="bubble-content">${escapeText(text)}</div>
    <div class="bubble-time text-end">You · ${now}</div>
  `;
  c.appendChild(el);
  c.scrollTop = c.scrollHeight;
}

function appendDashAssistant(text) {
  const c   = document.getElementById("dashChatMessages");
  if (!c) return;
  const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const el  = document.createElement("div");
  el.className = "chat-bubble assistant";
  el.innerHTML = `
    <div class="bubble-content">${markdownToHtml(text)}</div>
    <div class="bubble-time">ARIA · ${now}</div>
  `;
  c.appendChild(el);
  c.scrollTop = c.scrollHeight;
}

function showDashTyping(show) {
  const el = document.getElementById("dashChatTyping");
  if (!el) return;
  if (show) {
    el.classList.remove("d-none");
    el.classList.add("d-flex");
    const c = document.getElementById("dashChatMessages");
    if (c) c.scrollTop = c.scrollHeight;
  } else {
    el.classList.remove("d-flex");
    el.classList.add("d-none");
  }
}
