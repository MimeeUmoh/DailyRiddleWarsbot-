/* script.js
   WebApp frontend logic for DailyRiddleWars.
   Edit BACKEND_BASE to point at your Render app (e.g. "https://your-app.onrender.com")
   This file uses fetch() to talk to your endpoints:
   - POST /register
   - GET  /get_user?user_id=...
   - POST /get_riddle  (you may adapt endpoints to your backend)
   - POST /submit_answer
   - POST /use_hint
   - POST /add_coins or /buy_coins
   - GET  /leaderboard
*/

const BACKEND_BASE = ""; // <-- set to your Render URL, e.g. "https://dailyriddlewars.onrender.com"
const TELEGRAM_INIT = window.Telegram && window.Telegram.WebApp;
if (TELEGRAM_INIT) {
  TELEGRAM_INIT.expand();
}

// UI elements
const signupScreen = document.getElementById("signup-screen");
const gameScreen = document.getElementById("game-screen");
const leaderboardScreen = document.getElementById("leaderboard-screen");
const profileScreen = document.getElementById("profile-screen");

const coinsEl = document.getElementById("coins");
const streakEl = document.getElementById("streak");
const packSelect = document.getElementById("pack-select");
const packLabel = document.getElementById("pack-label");
const riddleQuestion = document.getElementById("riddle-question");
const riddleIndex = document.getElementById("riddle-index");
const answerInput = document.getElementById("answer-input");
const submitBtn = document.getElementById("submit-answer");
const hintBtn = document.getElementById("hint-btn");
const startBtn = document.getElementById("start-btn");
const unlockAllBtn = document.getElementById("unlock-all-btn");
const leaderboardList = document.getElementById("leaderboard-list");
const progressText = document.getElementById("progress-text");
const progressFill = document.getElementById("progress-fill");

// profile elements
const pName = document.getElementById("p-name");
const pPhone = document.getElementById("p-phone");
const pBank = document.getElementById("p-bank");
const pAccount = document.getElementById("p-account");
const pCoins = document.getElementById("p-coins");

// state
let user = null;             // local cached user
let session = {
  pack: "free",
  riddleIndex: 0,
  riddlesCount: 0,
  currentRiddleId: null
};

// helper fetch wrapper
async function api(path, method = "GET", body = null) {
  const url = BACKEND_BASE + path;
  const opts = { method, headers: {} };
  if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  try {
    const res = await fetch(url, opts);
    return await res.json();
  } catch (e) {
    console.error("API error:", e);
    return { error: "network" };
  }
}

// --- Signup logic ---
document.getElementById("signup-btn").onclick = async () => {
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const bank = document.getElementById("bank").value.trim();
  const account = document.getElementById("account").value.trim();

  if (!name) return alert("Please enter your name.");
  // register with backend
  const payload = {
    user_id: (TELEGRAM_INIT && TELEGRAM_INIT.initDataUnsafe && TELEGRAM_INIT.initDataUnsafe.user) ? TELEGRAM_INIT.initDataUnsafe.user.id : Date.now(),
    name, phone, bank, account
  };
  const res = await api("/register","POST",payload);
  if (res.status === "registered" || res.status === "already_registered") {
    await loadUser(payload.user_id);
    showGame();
  } else {
    alert("Signup failed. Try again.");
  }
};

document.getElementById("skip-btn").onclick = () => showGame();

// --- Load user ---
async function loadUser(user_id) {
  const res = await api(`/get_user?user_id=${user_id}`,"GET");
  if (!res || res.error) {
    // create a minimal local user placeholder
    user = { id: user_id, coins:0, streak:0 };
    coinsEl.textContent = 0;
    streakEl.textContent = 0;
    return;
  }
  user = res;
  updateProfileUI();
}

function updateProfileUI() {
  coinsEl.textContent = user.coins || 0;
  streakEl.textContent = user.streak || 0;
  pName.textContent = user.name || "—";
  pPhone.textContent = user.phone || "—";
  pBank.textContent = user.bank || "—";
  pAccount.textContent = user.account_number || "—";
  pCoins.textContent = user.coins || 0;
}

// --- Game flow ---
startBtn.onclick = async () => {
  session.pack = packSelect.value;
  packLabel.textContent = session.pack.charAt(0).toUpperCase() + session.pack.slice(1);
  // ask backend for riddle (endpoint expected: /get_riddle POST {user_id, pack})
  const payload = { user_id: user ? (user.telegram_id || user.id) : Date.now(), pack: session.pack };
  const res = await api("/get_riddle","POST",payload);
  if (res && res.question) {
    session.riddleIndex = res.index || 0;
    session.riddlesCount = res.total || 50;
    session.currentRiddleId = res.id;
    showRiddle(res);
  } else {
    riddleQuestion.textContent = res.error || "No riddles available.";
  }
};

function showRiddle(data) {
  riddleQuestion.textContent = data.question;
  riddleIndex.textContent = (session.riddleIndex + 1);
  progressText.textContent = `${session.riddleIndex + 1} / ${session.riddlesCount}`;
  progressFill.style.width = `${((session.riddleIndex+1)/session.riddlesCount)*100}%`;
}

// submit answer
submitBtn.onclick = async () => {
  const answer = answerInput.value.trim();
  if (!answer) return alert("Type an answer.");
  const payload = { user_id: user ? (user.telegram_id || user.id) : Date.now(), riddle_id: session.currentRiddleId, answer, used_hint:false };
  const res = await api("/submit_answer","POST",payload);
  if (res && res.correct !== undefined) {
    alert(res.correct ? `Correct! +${res.score}` : `Wrong. +${res.score}`);
    // update UI / load next
    loadNextRiddle();
    // refresh user coins & score
    await refreshUser();
  } else {
    alert("Error submitting answer.");
  }
};

async function loadNextRiddle() {
  const payload = { user_id: user ? (user.telegram_id || user.id) : Date.now(), pack: session.pack, index: session.riddleIndex+1 };
  const res = await api("/get_riddle","POST",payload);
  if (res && res.question) {
    session.riddleIndex = res.index || (session.riddleIndex + 1);
    session.currentRiddleId = res.id;
    showRiddle(res);
  } else {
    riddleQuestion.textContent = "You've finished this pack or something went wrong.";
  }
}

hintBtn.onclick = async () => {
  if (!confirm("Use a hint for 10 coins? This reduces riddle score from 10→7.")) return;
  const payload = { user_id: user ? (user.telegram_id || user.id) : Date.now(), riddle_id: session.currentRiddleId };
  const res = await api("/use_hint","POST",payload);
  if (res && res.status === "hint_used") {
    // request hint text from /get_hint
    const hintRes = await api("/get_hint","POST",{riddle_id: session.currentRiddleId});
    if (hintRes && hintRes.hint) {
      alert("Hint: " + hintRes.hint);
      await refreshUser();
    } else alert("Hint not available.");
  } else {
    alert(res.error || "Not enough coins.");
  }
};

unlockAllBtn.onclick = async () => {
  const pack = session.pack;
  // Price: handled in backend. We'll open Paystack or a checkout.
  if (!confirm("Unlock all 50 riddles now? This will open payment.")) return;
  // Launch a call to /buy_unlock (backend handles Paystack)
  const payload = { user_id: user ? (user.telegram_id || user.id) : Date.now(), pack };
  const res = await api("/buy_unlock","POST",payload);
  if (res && res.checkout_url) {
    // open Paystack in new window
    window.open(res.checkout_url, "_blank");
    alert("Complete payment in the opened window. After payment, return here and press Start.");
  } else {
    alert("Failed to initiate payment.");
  }
};

// Leaderboard
document.getElementById("leaderboard-btn").onclick = async () => {
  const res = await api("/leaderboard","GET");
  leaderboardList.innerHTML = "";
  if (res && Array.isArray(res)) {
    res.forEach((p, i) => {
      const li = document.createElement("li");
      li.innerHTML = `<div><strong>${i+1}. ${p.username || p.name || 'Player'}</strong><small>${p.user_id}</small></div><div>${p.total_score}</div>`;
      leaderboardList.appendChild(li);
    });
  } else {
    leaderboardList.innerHTML = "<li>No leaderboard yet</li>";
  }
  leaderboardScreen.classList.remove("hidden");
};

// profile
document.getElementById("profile-btn").onclick = () => {
  profileScreen.classList.remove("hidden");
};
document.getElementById("close-profile").onclick = () => profileScreen.classList.add("hidden");
document.getElementById("close-leaderboard").onclick = () => leaderboardScreen.classList.add("hidden");

// buy coins
document.getElementById("buy-coins-btn").onclick = async () => {
  // open buy page or initiate Paystack flow
  const res = await api("/buy_coins","POST",{user_id: user ? (user.telegram_id || user.id) : Date.now(), pack: "50_coins"});
  if (res && res.checkout_url) {
    window.open(res.checkout_url, "_blank");
    alert("Payment window opened for coin purchase.");
  } else {
    alert("Could not start purchase.");
  }
};

// refresh user
async function refreshUser() {
  if (!user) return;
  const res = await api(`/get_user?user_id=${user.id || user.telegram_id}`,"GET");
  if (res && !res.error) {
    user = res;
    updateProfileUI();
  }
}

// Helpers to show/hide main screens
function showGame() {
  signupScreen.classList.add("hidden");
  gameScreen.classList.remove("hidden");
  profileScreen.classList.add("hidden");
  leaderboardScreen.classList.add("hidden");
}

// On load: try to fetch user from Telegram initDataUnsafe
(async function init(){
  let tUserId = Date.now();
  if (TELEGRAM_INIT && TELEGRAM_INIT.initDataUnsafe && TELEGRAM_INIT.initDataUnsafe.user) {
    tUserId = TELEGRAM_INIT.initDataUnsafe.user.id;
  }

  await loadUser(tUserId);
  // if user has no name/phone, show signup
  if (!user || !user.name) {
    signupScreen.classList.remove("hidden");
  } else {
    showGame();
  }
})();
