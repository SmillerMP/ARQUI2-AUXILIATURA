const MQTT_TOPICS = ["parqueo/gas", "parqueo/espacio/#"];
const TOTAL_SPACES = 5;
const GAS_HISTORY_MAX = 80;

let client = null;
let gasHistory = [];
let latestGas = null;
const parkingState = { 1: "libre", 2: "libre", 3: "libre", 4: "libre", 5: "libre" };

const APP_CONFIG = window.__APP_CONFIG__ || {};
const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";

function normalizeBrokerUrl(rawUrl) {
  const value = (rawUrl || "").trim();
  if (!value) {
    return `${wsProtocol}://${window.location.host}/mqtt`;
  }

  if (value.startsWith("ws://") || value.startsWith("wss://")) {
    return value;
  }

  if (value.startsWith("/")) {
    return `${wsProtocol}://${window.location.host}${value}`;
  }

  return `${wsProtocol}://${value}`;
}

const BROKER_URL = normalizeBrokerUrl(APP_CONFIG.MQTT_BROKER_URL);
const MQTT_USER = APP_CONFIG.MQTT_USER || "";
const MQTT_PASSWORD = APP_CONFIG.MQTT_PASSWORD || "";

const connStateEl = document.getElementById("connState");
const freeCountEl = document.getElementById("freeCount");
const gasValueEl = document.getElementById("gasValue");
const brokerInfoEl = document.getElementById("brokerInfo");
const parkingControlsEl = document.getElementById("parkingControls");

brokerInfoEl.textContent = BROKER_URL;
renderControls();

function updateStatus() {
  const free = Object.values(parkingState).filter((state) => state === "libre").length;
  freeCountEl.textContent = `${free} / ${TOTAL_SPACES}`;
  gasValueEl.textContent = latestGas === null ? "-- ppm" : `${latestGas} ppm`;
}

function getStateLabel(state) {
  if (state === "ocupado") return "ocupado";
  if (state === "deshabilitado") return "deshabilitado";
  return "libre";
}

function renderControls() {
  parkingControlsEl.innerHTML = "";

  for (let i = 1; i <= TOTAL_SPACES; i++) {
    const state = getStateLabel(parkingState[i]);
    const isDisabled = state === "deshabilitado";

    const row = document.createElement("div");
    row.className = "control-row";

    const label = document.createElement("div");
    label.className = "control-label";
    label.innerHTML = `P${i} <small>(${state})</small>`;

    const button = document.createElement("button");
    button.className = `control-btn ${isDisabled ? "enable" : "disable"}`;
    button.textContent = isDisabled ? "Habilitar" : "Deshabilitar";
    button.disabled = !client || !client.connected;
    button.addEventListener("click", () => toggleParking(i));

    row.appendChild(label);
    row.appendChild(button);
    parkingControlsEl.appendChild(row);
  }
}

function toggleParking(space) {
  if (!client || !client.connected) {
    return;
  }

  const current = getStateLabel(parkingState[space]);
  const next = current === "deshabilitado" ? "libre" : "deshabilitado";
  const topic = `parqueo/espacio/${space}`;

  client.publish(topic, next, { retain: true }, (err) => {
    if (err) {
      setConnectionState(`Error publicando control: ${err.message}`);
      return;
    }
    parkingState[space] = next;
    updateStatus();
    renderControls();
  });
}

function setConnectionState(text, ok = false) {
  connStateEl.textContent = text;
  connStateEl.style.color = ok ? "#22c55e" : "#f87171";
}

function connectMQTT() {
  if (client && client.connected) {
    return;
  }

  if (!window.mqtt || typeof window.mqtt.connect !== "function") {
    setConnectionState("MQTT no disponible");
    return;
  }

  try {
    client = mqtt.connect(BROKER_URL, {
      username: MQTT_USER,
      password: MQTT_PASSWORD,
      reconnectPeriod: 2000,
      clean: true
    });
  } catch (error) {
    setConnectionState(`Error MQTT: ${error.message}`);
    return;
  }

  setConnectionState("Conectando...");

  client.on("connect", () => {
    setConnectionState("Conectado", true);
    client.subscribe(MQTT_TOPICS, (err) => {
      if (err) {
        setConnectionState(`Error al suscribir: ${err.message}`);
      }
    });
    renderControls();
  });

  client.on("message", (topic, payloadBuffer) => {
    const payloadText = payloadBuffer.toString();

    if (topic === "parqueo/gas") {
      const value = Number(payloadText);
      if (!Number.isNaN(value)) {
        latestGas = value;
        gasHistory.push(value);
        if (gasHistory.length > GAS_HISTORY_MAX) {
          gasHistory.shift();
        }
      }
    }

    if (topic.startsWith("parqueo/espacio/")) {
      const space = Number(topic.split("/").pop());
      const state = payloadText.toLowerCase().trim();
      if (space >= 1 && space <= TOTAL_SPACES) {
        if (state === "ocupado" || state === "libre" || state === "deshabilitado") {
          parkingState[space] = state;
        } else {
          parkingState[space] = "libre";
        }
      }
    }

    updateStatus();
    renderControls();
  });

  client.on("reconnect", () => {
    setConnectionState("Reconectando...");
    renderControls();
  });
  client.on("close", () => {
    setConnectionState("Desconectado");
    renderControls();
  });
  client.on("error", (err) => {
    setConnectionState(`Error: ${err.message}`);
    renderControls();
  });
}

function getCanvasDimensions() {
  const container = document.getElementById("canvasContainer");
  const containerWidth = container.clientWidth;
  const fallbackWidth = window.innerWidth > 900 ? window.innerWidth - 360 : window.innerWidth - 32;
  const width = Math.max(640, containerWidth > 0 ? containerWidth : fallbackWidth);
  const height = Math.max(500, Math.min(760, window.innerHeight - 80));
  return { width, height };
}

function setup() {
  const { width, height } = getCanvasDimensions();
  const canvas = createCanvas(width, height);
  canvas.parent("canvasContainer");
  textFont("sans-serif");
  updateStatus();
  setTimeout(connectMQTT, 0);
}

function windowResized() {
  const { width, height } = getCanvasDimensions();
  resizeCanvas(width, height);
}

function draw() {
  background("#020617");

  const contentX = 24;
  const contentY = 28;
  const contentW = width - 48;
  const contentH = height - 56;
  const gap = 28;
  const parkingH = contentH * 0.42;
  drawParkingLayout(contentX, contentY, contentW, parkingH);
  drawGasChart(contentX, contentY + parkingH + gap, contentW, contentH - parkingH - gap);
}

function drawParkingLayout(x, y, w, h) {
  noStroke();
  fill("#e2e8f0");
  textSize(18);
  text("Estado del parqueo", x, y - 8);

  const laneTop = y + 20;
  const laneHeight = h - 20;
  const slotGap = 12;
  const slotW = (w - slotGap * (TOTAL_SPACES - 1)) / TOTAL_SPACES;

  fill("#111827");
  rect(x - 10, laneTop - 10, w + 20, laneHeight + 20, 10);

  for (let i = 1; i <= TOTAL_SPACES; i++) {
    const slotX = x + (i - 1) * (slotW + slotGap);
    const state = getStateLabel(parkingState[i]);

    fill(state === "ocupado" ? "#dc2626" : state === "deshabilitado" ? "#475569" : "#16a34a");
    rect(slotX, laneTop + 20, slotW, laneHeight - 40, 8);

    fill("#f8fafc");
    textSize(12);
    textAlign(CENTER, CENTER);
    text(`P${i}\n${state.toUpperCase()}`, slotX + slotW / 2, laneTop + laneHeight / 2);
  }

  textAlign(LEFT, BASELINE);
}

function drawGasChart(x, y, w, h) {
  noStroke();
  fill("#e2e8f0");
  textSize(18);
  text("Gas (ppm) en tiempo real", x, y - 8);

  fill("#111827");
  rect(x, y, w, h, 10);

  stroke("#334155");
  strokeWeight(1);
  for (let i = 0; i <= 4; i++) {
    const gy = map(i, 0, 4, y + 20, y + h - 20);
    line(x + 20, gy, x + w - 20, gy);
  }

  if (gasHistory.length > 1) {
    const minVal = 0;
    const maxVal = Math.max(100, ...gasHistory);

    noFill();
    stroke("#38bdf8");
    strokeWeight(2);
    beginShape();
    gasHistory.forEach((value, index) => {
      const px = map(index, 0, GAS_HISTORY_MAX - 1, x + 20, x + w - 20);
      const py = map(value, minVal, maxVal, y + h - 20, y + 20);
      vertex(px, py);
    });
    endShape();

    noStroke();
    fill("#cbd5e1");
    textSize(13);
    text(`Min: ${minVal} ppm`, x + 20, y + h - 4);
    text(`Max: ${maxVal} ppm`, x + w - 110, y + h - 4);
  } else {
    noStroke();
    fill("#64748b");
    textSize(14);
    text("Esperando datos de gas...", x + 20, y + h / 2);
  }
}
