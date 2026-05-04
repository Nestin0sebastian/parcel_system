// ============================================
// Main Frontend Controller
// Handles all HTML form submissions and navigation
// ============================================

import { login, signup, logout, isLoggedIn, getCurrentUser } from "./auth.js";
import {
  createParcel,
  confirmParcel,
  getMyParcels,
  getParcelDetail,
  getParcelCheckout,
  cancelParcel,
} from "./parcel.js";
import { trackParcel } from "./tracking.js";

// ============================================
// UTILITIES
// ============================================

/**
 * Toggle password visibility
 */
window.togglePass = function (id, el) {
  const inp = document.getElementById(id);
  if (inp) {
    inp.type = inp.type === "password" ? "text" : "password";
  }
};

/**
 * Show toast/alert message
 */
window.showToast = function (msg, type = "info") {
  alert(msg);
};

/**
 * Redirect to create parcel page (with login check)
 */
window.gotoCreate = function () {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
  } else {
    window.location.href = "create.html";
  }
};

/**
 * Scroll to tracking section on home page
 */
window.scrollToTrack = function () {
  const el = document.getElementById("track-section");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
};

/**
 * Update navigation UI based on login state
 */
window.updateNav = function () {
  const isLogged = isLoggedIn();
  const user = getCurrentUser();

  const navLogin = document.getElementById("nav-login");
  const navSignup = document.getElementById("nav-signup");
  const navDashboard = document.getElementById("nav-dashboard");
  const navAvatar = document.getElementById("nav-avatar");

  if (isLogged) {
    if (navLogin) navLogin.style.display = "none";
    if (navSignup) navSignup.style.display = "none";
    if (navDashboard) navDashboard.style.display = "block";
    if (navAvatar) {
      navAvatar.style.display = "block";
      navAvatar.innerText = (user.username || "U").substring(0, 2).toUpperCase();
    }
  } else {
    if (navLogin) navLogin.style.display = "block";
    if (navSignup) navSignup.style.display = "block";
    if (navDashboard) navDashboard.style.display = "none";
    if (navAvatar) navAvatar.style.display = "none";
  }
};

/**
 * Copy tracking ID to clipboard
 */
window.copyTracking = function () {
  let trackingId = document.getElementById("co-tracking")?.innerText ||
                   document.querySelector(".tracking-id-val")?.innerText ||
                   "";
  if (!trackingId) return;
  navigator.clipboard.writeText(trackingId);
  alert("Tracking ID copied!");
};

/**
 * Logout function
 */
window.logout = function () {
  logout();
};

// ============================================
// AUTH FLOWS
// ============================================

/**
 * Handle login form submission
 */
window.doLogin = async () => {
  const username = document.getElementById("li-email")?.value || "";
  const password = document.getElementById("li-pass")?.value || "";

  if (!username || !password) {
    alert("Please enter both username and password");
    return;
  }

  try {
    const btn = document.getElementById("li-btn");
    if (btn) btn.disabled = true;

    await login(username, password);
    updateNav();
    window.location.href = "dashboard.html";
  } catch (e) {
    const errorMsg = document.getElementById("login-error-msg");
    const errorDiv = document.getElementById("login-error");
    if (errorDiv) {
      if (errorMsg) errorMsg.innerText = e.message;
      errorDiv.style.display = "block";
    } else {
      alert("Login failed: " + e.message);
    }
  } finally {
    const btn = document.getElementById("li-btn");
    if (btn) btn.disabled = false;
  }
};

  /**
   * Handle signup form submission
   */
  window.doSignup = async () => {
    const username = document.getElementById("su-username")?.value || "";
    const email = document.getElementById("su-email")?.value || "";
    const password = document.getElementById("su-pass")?.value || "";
    const terms = document.getElementById("su-terms")?.checked;

    if (!username || !email || !password) {
      alert("Please fill in all fields");
      return;
    }

    if (!terms) {
      alert("Please accept the terms and conditions");
      return;
    }

    try {
      await signup({ username, email, password });
      alert("Signup successful! Please login now.");
      window.location.href = "login.html";
    } catch (e) {
      alert("Signup failed: " + e.message);
    }
  };

// ============================================
// PARCEL FLOWS
// ============================================

/**
 * Initialize create parcel form
 */
window.initCreateForm = function () {
  // Set default values
  updateNav();
};

/**
 * Navigate between create form steps
 */
let currentStep = 1;

window.goStep = function (step) {
  const step1 = document.getElementById("create-step1");
  const step2 = document.getElementById("create-step2");
  const step3 = document.getElementById("create-step3");

  if (step1) step1.style.display = "none";
  if (step2) step2.style.display = "none";
  if (step3) step3.style.display = "none";

  if (step === 1 && step1) {
    step1.style.display = "block";
    currentStep = 1;

  } else if (step === 2 && step2) {
    // 🚫 DO NOT update review here
    step2.style.display = "block";
    currentStep = 2;

  } else if (step === 3 && step3) {
    // ✅ ONLY update review here
    updateReviewFromStep1();
    updateReviewFromStep2();

    step3.style.display = "block";
    currentStep = 3;
  }
};

function updateReviewFromStep1() {
  const sname = document.getElementById("s1-sname")?.value || "—";
  const sphone = document.getElementById("s1-sphone")?.value || "—";
  const scity = document.getElementById("s1-source")?.value || "—";

  const rname = document.getElementById("s1-rname")?.value || "—";
  const rphone = document.getElementById("s1-rphone")?.value || "—";
  const rcity = document.getElementById("s1-dest")?.value || "—";

  const weight = document.getElementById("s2-weight")?.value || "—";

  const el1 = document.getElementById("rv-sname");
  if (el1) el1.innerText = sname;

  const el2 = document.getElementById("rv-sphone");
  if (el2) el2.innerText = sphone;

  const el3 = document.getElementById("rv-scity");
  if (el3) el3.innerText = scity;

  const el4 = document.getElementById("rv-rname");
  if (el4) el4.innerText = rname;

  const el5 = document.getElementById("rv-rphone");
  if (el5) el5.innerText = rphone;

  const el6 = document.getElementById("rv-rcity");
  if (el6) el6.innerText = rcity;

  const el7 = document.getElementById("rv-weight");
  if (el7) el7.innerText = weight + " kg";
}

/**
 * Update review section with step 2 data
 */
function updateReviewFromStep2() {
  const weight = document.getElementById("s2-weight")?.value || "—";
  const rv_weight = document.getElementById("rv-weight");
  if (rv_weight) rv_weight.innerText = weight + " kg";
}

/**
 * Select parcel type
 */
window.selectType = function (el, type) {
  const cards = document.querySelectorAll(".parcel-type-card");
  cards.forEach((c) => c.classList.remove("selected"));
  el.classList.add("selected");

  const rvType = document.getElementById("rv-type");
  if (rvType) {
    const icon = type === "fragile" ? "🔮" : type === "express" ? "⚡" : "📦";
    rvType.innerText = `${icon} ${type.charAt(0).toUpperCase() + type.slice(1)}`;
  }
};

/**
 * Fill sender with user info
 */
window.fillSender = function () {
  const user = getCurrentUser();
  // This would typically fetch user profile from backend
  // For now, just show a message
  alert("User info feature - would fetch from profile");
};

/**
 * Update cost estimate
 */
window.updateEstimate = function () {
  // Simple estimation logic
  const weight = parseFloat(document.getElementById("s2-weight")?.value || 1);
  const baseCost = 80;
  const weightCost = weight * 10;
  const total = baseCost + weightCost + 18; // +18 for GST

  if (document.getElementById("step2-cost"))
    document.getElementById("step2-cost").innerText = "₹" + Math.round(total);
};

/**
 * Create parcel (from form)
 */
// 🔥 CREATE PARCEL FROM DRAFT
window.submitParcel = async () => {
  try {
    const data = JSON.parse(localStorage.getItem("parcel_draft"));

    if (!data) {
      alert("No parcel data found");
      return;
    }

    const res = await createParcel(data);

    localStorage.setItem("parcel_id", res.parcel_id);

    window.location.href = "checkout.html";

  } catch (e) {
    alert("Error creating parcel: " + e.message);
  }
};

/**
 * Confirm/pay for parcel
 */
window.confirmOrder = async () => {
  const parcelId = localStorage.getItem("parcel_id");

  if (!parcelId) {
    alert("No parcel to confirm");
    return;
  }

  try {
    const btn = document.getElementById("co-btn");
    if (btn) btn.disabled = true;

    await confirmParcel(parcelId);
    alert("Parcel confirmed successfully!");
    window.location.href = "dashboard.html";
  } catch (e) {
    alert("Error confirming parcel: " + e.message);
  } finally {
    const btn = document.getElementById("co-btn");
    if (btn) btn.disabled = false;
  }
};

window.doConfirm = window.confirmOrder;

/**
 * Shorthand for confirmOrder
 */


// ============================================
// DASHBOARD
// ============================================



// ============================================
// PARCEL DETAIL
// ============================================

/**
 * Load and display parcel detail
 */
window.loadDetail = async () => {
  updateNav();

  const id = localStorage.getItem("view_id");

  if (!id) {
    alert("No parcel selected");
    return;
  }

  try {
    const data = await getParcelDetail(id);

    const p = data.parcel || {};
    const history = data.tracking_history || [];

    // =========================
    // HERO
    // =========================
    document.querySelector(".hero-title").innerText = p.tracking_id || "—";

    const chip = document.querySelector(".hero-chips .chip");
    if (chip) chip.innerText = p.status || "—";

    // =========================
    // ROUTE
    // =========================
    const cities = document.querySelectorAll(".route-city");

    if (cities[0]) cities[0].innerText = p.source_city;
    if (cities[1]) cities[1].innerText = p.destination_city;

    // =========================
    // PROGRESS
    // =========================
    const progress = Math.min(100, history.length * 20);
    const bar = document.getElementById("hero-progress");
    if (bar) bar.style.width = progress + "%";

    // =========================
    // INFO
    // =========================
    const info = document.querySelectorAll(".info-row");

    if (info[1]) info[1].querySelector(".info-val").innerText = `${p.weight} kg`;

    if (info[4]) info[4].querySelector(".info-val").innerText =
      new Date(p.created_at).toDateString();

    if (info[5]) info[5].querySelector(".info-val").innerText =
      new Date(p.estimated_delivery).toDateString();

    // =========================
    // PEOPLE
    // =========================
    const people = document.querySelectorAll(".person-block");

    if (people[0]) {
      people[0].querySelector("div:last-child").innerText = p.sender;
    }

    if (people[1]) {
      people[1].querySelector("div:last-child").innerText = p.receiver;
    }

    // =========================
    // TIMELINE
    // =========================
    const timeline = document.getElementById("main-timeline");

    if (timeline) {
      timeline.innerHTML = "";

      history.forEach((e) => {
        const el = document.createElement("div");
        el.className = "tl-item";

        el.innerHTML = `
          <div class="tl-node done">✓</div>
          <div>
            <div class="tl-title">${e.status}</div>
            <div class="tl-sub">${e.location}</div>
          </div>
        `;

        timeline.appendChild(el);
      });
    }

    // =========================
    // EVENT LOG
    // =========================
    const log = document.getElementById("event-log");

    if (log) {
      log.innerHTML = "";

      history.forEach((e) => {
        const row = document.createElement("div");
        row.className = "event-log-row";

        row.innerHTML = `
          <span class="text-xs text-muted">
            ${new Date(e.time).toLocaleString()}
          </span><br>
          <span>${e.status} — ${e.location}</span>
        `;

        log.appendChild(row);
      });
    }

  } catch (e) {
    console.error(e);
    alert("Failed to load parcel detail");
  }
};
///////////

window.saveDraftAndReview = () => {
  const getVal = (id) => document.getElementById(id)?.value?.trim();

  const senderName = getVal("s1-sname");
  const senderPhone = getVal("s1-sphone");
  const senderPincode = getVal("s1-source");

  const receiverName = getVal("s1-rname");
  const receiverPhone = getVal("s1-rphone");
  const receiverEmail = getVal("s1-remail");
  const destinationPincode = getVal("s1-dest");

  const weight = getVal("s2-weight");
  const l = getVal("s2-l");
  const w = getVal("s2-w");
  const h = getVal("s2-h");

  // 🔥 VALIDATION
  if (
    !senderName || !senderPhone || !senderPincode ||
    !receiverName || !receiverPhone || !receiverEmail ||
    !destinationPincode || !weight || !l || !w || !h
  ) {
    alert("Please complete all parcel fields before reviewing your order.");
    return;
  }

  const data = {
    sender_name: senderName,
    sender_phone: senderPhone,
    receiver_name: receiverName,
    receiver_phone: receiverPhone,
    receiver_email: receiverEmail,
    source_pincode: senderPincode,
    destination_pincode: destinationPincode,
    weight: parseFloat(weight),
    dimensions: `${l}x${w}x${h}`,
    type: "standard"
  };

  // 🔥 SAVE TO LOCAL
  localStorage.setItem("parcel_draft", JSON.stringify(data));

  // 🔥 SAFE UI UPDATE FUNCTION
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.innerText = value;
  };

  // 🔥 UPDATE REVIEW UI
  setText("rv-sname", data.sender_name);
  setText("rv-sphone", data.sender_phone);
  setText("rv-scity", data.source_pincode);

  setText("rv-rname", data.receiver_name);
  setText("rv-rphone", data.receiver_phone);
  setText("rv-rcity", data.destination_pincode);

  setText("rv-type", "📦 Standard");
  setText("rv-weight", `${data.weight} kg`);
  setText("rv-cost", "₹Pending");

  // 🔥 GO TO REVIEW STEP
  goStep(3);
};
// ============================================
// DASHBOARD FILTERS





// ============================================
// TRACKING
// ============================================

/**
 * Track parcel by tracking ID (public)
 */
window.doTrack = async () => {
  const trackInput = document.getElementById("track-input");
  const trackResult = document.getElementById("track-result");
  const trackError = document.getElementById("track-error");

  if (!trackInput) return;

  const trackingId = trackInput.value.trim();

  if (!trackingId) {
    alert("Please enter a tracking ID");
    return;
  }

  try {
    if (trackError) trackError.style.display = "none";

    const data = await trackParcel(trackingId);

    if (trackResult) {
      trackResult.style.display = "block";
      const timeline = document.getElementById("mini-timeline-content");
      if (timeline) {
        timeline.innerHTML = "";
        if (data.tracking_events && data.tracking_events.length > 0) {
          data.tracking_events.slice(0, 3).forEach((event) => {
            const eventEl = document.createElement("div");
            eventEl.className = "event-log-row";
            eventEl.innerHTML = `
              <span class="text-xs text-muted">${new Date(event.timestamp).toLocaleString()}</span>
              <br>
              <span class="text-sm">${event.status || event.description || "—"}</span>
            `;
            timeline.appendChild(eventEl);
          });
        } else {
          timeline.innerHTML = "<p>No tracking events yet</p>";
        }
      }
    }
  } catch (e) {
    if (trackError) {
      trackError.style.display = "block";
      trackError.innerText = "Tracking ID not found: " + e.message;
    }
  }
};

// ============================================
// CHECKOUT
// ============================================


document.addEventListener("DOMContentLoaded", () => {
  updateNav();

  // ✅ Dashboard
  if (document.getElementById("parcel-grid")) {
    loadDashboard();
  }

  // ✅ Checkout
  if (document.getElementById("co-tracking")) {
    loadCheckout();

    document.getElementById("co-btn")
      ?.addEventListener("click", doConfirm);
  }
});

// ============================================
// CHECKOUT LOAD (REAL DATA)
// ============================================
window.loadCheckout = async () => {
  try {
     const id = localStorage.getItem("parcel_id");    

    if (!id) {
      alert("No parcel found");
      window.location.href = "create.html";
      return;
    }

    const p = await getParcelCheckout(id);

    console.log("Checkout Data:", p);

    function setText(id, value) {
      const el = document.getElementById(id);
      if (el) el.innerText = value ?? "N/A";
    }

    setText("co-tracking", p.tracking_id);
    setText("co-origin", p.source_city || p.source_pincode);
    setText("co-dest", p.destination_city || p.destination_pincode);
    setText("co-receiver", p.receiver);
    setText("co-weight", `${p.weight} kg`);
    setText("co-status", p.status);

    setText(
      "co-delivery",
      p.estimated_delivery
        ? new Date(p.estimated_delivery).toDateString()
        : "N/A"
    );

    if (p.pricing) {
      setText("co-base", `₹${p.pricing.base}`);
      setText("co-weight-charge", `₹${p.pricing.weight_charge}`);
      setText("co-distance", `₹${p.pricing.distance_charge}`);
      setText("co-total", `₹${p.pricing.total}`);
    }

  } catch (e) {
    console.error("Checkout error:", e);
    alert("Checkout load failed");
  }
};
/**
 * Select payment method
 */
window.selectPayment = function (el) {
  const options = document.querySelectorAll(".payment-option");
  options.forEach((o) => o.classList.remove("selected"));
  el.classList.add("selected");
  const radio = el.querySelector("input");
  if (radio) radio.checked = true;
};

/**
 * Start countdown timer on checkout
 */
window.startTimer = function () {
  let seconds = 15 * 60; // 15 minutes
  const timerEl = document.getElementById("timer");

  const interval = setInterval(() => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (timerEl) {
      timerEl.innerText =
        mins.toString().padStart(2, "0") +
        ":" +
        secs.toString().padStart(2, "0");
    }
    seconds--;
    if (seconds < 0) clearInterval(interval);
  }, 1000);
};

/**
 * Calculate shipping cost estimate
 */
window.calcEstimate = function () {
  const origin = document.getElementById("est-origin")?.value;
  const dest = document.getElementById("est-dest")?.value;
  const weight = parseFloat(document.getElementById("est-weight")?.value || 1);
  const type = document.getElementById("est-type")?.value || "standard";

  if (!origin || !dest) {
    alert("Please select both origin and destination");
    return;
  }

  // Simple pricing logic
  let baseCost = 80;
  const weightCost = weight * 10;
  let surfaceCharge = 0;
  if (type === "express") surfaceCharge = 50;
  if (type === "fragile") surfaceCharge = 50;

  const subtotal = baseCost + weightCost + surfaceCharge;
  const gst = subtotal * 0.18;
  const total = subtotal + gst;

  if (document.getElementById("est-result"))
    document.getElementById("est-result").style.display = "block";
  if (document.getElementById("est-placeholder"))
    document.getElementById("est-placeholder").style.display = "none";

  if (document.getElementById("est-base"))
    document.getElementById("est-base").innerText = "₹" + baseCost;
  if (document.getElementById("est-wc"))
    document.getElementById("est-wc").innerText = "₹" + Math.round(weightCost);
  if (document.getElementById("est-sf"))
    document.getElementById("est-sf").innerText = "₹" + Math.round(surfaceCharge);
  if (document.getElementById("est-cost"))
    document.getElementById("est-cost").innerText = "₹" + Math.round(total);
};

/**
 * Initialize navigation on page load
 */



// ============================================
// DASHBOARD
// ============================================

window.dashboardParcels = [];
window.currentParcelFilter = "all";
window.currentParcelSearch = "";

// 🎨 STATUS COLOR
function getStatusColor(status) {
  const colors = {
    CREATED: "#fbbf24",
    CONFIRMED: "#3b82f6",
    PICKED_UP: "#8b5cf6",
    IN_TRANSIT: "#06b6d4",
    DELIVERED: "#10b981",
    CANCELLED: "#ef4444",
  };
  return colors[status] || "#6b7280";
}

// 📊 STATS
function updateStats() {
  const parcels = window.dashboardParcels;

  const total = parcels.length;
  const transit = parcels.filter(p => p.status === "IN_TRANSIT").length;
  const delivered = parcels.filter(p => p.status === "DELIVERED").length;
  const pending = parcels.filter(p => p.status === "CREATED").length;

  const stats = document.querySelectorAll(".stat-num");

  if (stats.length >= 4) {
    stats[0].innerText = total;
    stats[1].innerText = transit;
    stats[2].innerText = delivered;
    stats[3].innerText = pending;
  }
}

// 🧱 RENDER
function renderDashboard() {
  const list = document.getElementById("parcel-grid");
  if (!list) return;

  const filtered = window.dashboardParcels.filter((p) => {
    const search = window.currentParcelSearch.toLowerCase();
    const id = (p.tracking_id || "").toLowerCase();
    const route = `${p.source || ""} ${p.destination || ""}`.toLowerCase();
    const status = (p.status || "").toLowerCase();

    const matchesSearch =
      !search || id.includes(search) || route.includes(search);

    const matchesFilter =
      window.currentParcelFilter === "all" ||
      status.includes(window.currentParcelFilter);

    return matchesSearch && matchesFilter;
  });

  list.innerHTML = "";

  if (!filtered.length) {
    list.innerHTML = "<p>No parcels found</p>";
    return;
  }

  filtered.forEach((p) => {
    const color = getStatusColor(p.status);

    const card = document.createElement("div");
card.className = "parcel-card";

card.innerHTML = `
  <div class="card-top">
    <div>
      <div class="card-id">${p.tracking_id}</div>
      <div class="card-route">
        ${p.source} <span class="arrow">→</span> ${p.destination}
      </div>
    </div>

    <span class="status-badge ${p.status.toLowerCase()}">
      ${p.status}
    </span>
  </div>

  <div class="card-meta">
    <span>📦 ${p.weight || 0} kg</span>
    <span>📅 ${new Date(p.created_at).toLocaleDateString()}</span>
  </div>

  <div class="card-actions">
    <button class="btn-view">View</button>
  </div>
`;

    card.querySelector(".btn-view")?.addEventListener("click", (e) => {
      e.stopPropagation();
      localStorage.setItem("view_id", p.parcel_id);
      window.location.href = "parcel-detail.html";  
    });

    list.appendChild(card);
  });
}

// 🔍 SEARCH
function setupSearch() {
  const input = document.getElementById("search-input");

  input?.addEventListener("input", (e) => {
    window.currentParcelSearch = e.target.value;
    renderDashboard();
  });
}

// 🎛 FILTER
function setupFilters() {
  const tabs = document.querySelectorAll(".filter-tab");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      window.currentParcelFilter = tab.dataset.filter;
      renderDashboard();
    });
  });
}

// 🚀 LOAD
window.loadDashboard = async () => {
  try {
    const parcels = await getMyParcels();

    window.dashboardParcels = parcels || [];

    updateStats();
    renderDashboard();
    setupFilters();
    setupSearch();

  } catch (e) {
    console.error("Dashboard error:", e);
  }
};





//////




window.showCancelModal = function () {
  const modal = document.getElementById("cancel-modal");
  if (modal) modal.style.display = "flex";
};

window.closeCancelModal = function () {
  const modal = document.getElementById("cancel-modal");
  if (modal) modal.style.display = "none";
};

window.confirmCancelParcel = async () => {
  const id = localStorage.getItem("view_id");

  if (!id) {
    alert("No parcel selected");
    return;
  }

  try {
    await cancelParcel(id);

    alert("Parcel cancelled successfully");

    window.location.href = "dashboard.html";

  } catch (e) {
    alert("Cancel failed: " + e.message);
  }
};