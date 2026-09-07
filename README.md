# 🚗 ParkFlow — Smart Parking Management System

An interactive, responsive, and production-ready **Parking Management System** web application designed for commercial parking complexes, shopping malls, airports, and corporate towers.

---

## ✨ Features

- 🗺️ **Interactive Multi-Level Floor Grid**:
  - Live bay visualization across **Ground Floor (Level 1)**, **Basement B1**, and **Level 3 EV Charging Hub**.
  - Color-coded bays: **Green** (Available), **Red** (Occupied), **Cyan** (EV Charging with pulsating status), **Purple** (Priority/Accessible).
  - Click any bay to immediately park or inspect/check-out.
  - Filter by floor level or vehicle classification (Sedan, SUV, Two-Wheeler, EV, Priority).
  - Real-time search by bay ID or license plate.

- 🎟️ **Smart Vehicle Check-In & Entry Pass**:
  - Automatic license plate validation & uppercase formatting.
  - Auto-assigns the nearest optimal bay or allows manual bay selection.
  - Generates a **Digital Thermal Ticket Pass** with simulated barcode, timestamp, and printable styling (`Ctrl + P`).

- 💳 **Check-Out & Automated Tariff Billing**:
  - Look up active vehicles by plate number, ticket ID, or bay ID.
  - Automated elapsed time tracking (hours & minutes).
  - Vehicle-specific tiered pricing (First hour base rate, hourly rate, EV charging surcharges, daily caps).
  - Payment mode selector (Cash, Credit Card, UPI / Fastag, Mobile Pay).
  - Official printable tax invoice receipt.

- 📊 **Real-Time Analytics & Dashboard**:
  - Live KPI cards: Total bays, Available bays, Occupancy %, and Today's settled revenue.
  - Interactive Doughnut chart: Vehicle classification breakdown.
  - Utilization trend bar chart by hour.
  - Live gate activity stream of recent arrivals and exits.

- 📁 **Session History & CSV Export**:
  - Audit trail of all completed parking sessions.
  - 1-click **Export to CSV** for management reports.

- 📱 **Access from Any Gadget (Phone, Tablet, Laptop)**:
  - Responsive mobile-first UI with touch-friendly controls.
  - Built-in **QR Code & Link Sharing**: Click "Connect Gadgets" to scan and open directly on your iPhone, Android phone, or iPad.
  - Real-time synchronization across all devices connected to the local Wi-Fi network.

- ⚡ **Zero-Dependency Dual Mode Architecture**:
  - **Option 1 (Standalone)**: Double-click `index.html` to open directly in any browser with instant `localStorage` persistence.
  - **Option 2 (Full REST + SQLite Backend)**: Run `python server.py` to launch a persistent SQLite-backed server on `http://localhost:8000` with **zero `pip install` required** (uses Python's standard library).

---

## 📱 How to Use on Any Gadget (Phones & Tablets)

### Step 1: Start the server on your computer
```powershell
python server.py
```

### Step 2: Connect your gadget to the same Wi-Fi
Make sure your smartphone, iPad, tablet, or secondary laptop is connected to the same Wi-Fi network as your computer.

### Step 3: Open on your gadget
- **Option A (Instant QR Scan)**: Open `http://localhost:8000` on your PC, click the green **"Connect Gadgets"** button at top-right, and scan the QR code with your phone camera!
- **Option B (Direct URL)**: Open the browser on your phone (Chrome / Safari) and enter:
  ```
  http://10.185.31.221:8000
  ```
*(Note: Replace `10.185.31.221` with your computer's IP address if your network changes).*

---

## 🌐 How to Share with Anyone Over the Public Internet (Free)

If you want anyone in the world to access your parking management system from anywhere:

1. **Option 1: Using Cloudflare Tunnel (Zero-cost, no install needed)**
   ```powershell
   winget install Cloudflare.cloudflared
   cloudflared tunnel --url http://localhost:8000
   ```
   *This will generate a free public `https://....trycloudflare.com` link you can share with anyone!*

2. **Option 2: Using ngrok**
   ```powershell
   ngrok http 8000
   ```

---

## 🚀 How to Run

### Method 1: Start with Python SQLite Server (Recommended)

Open PowerShell in this directory and run:

```powershell
python server.py
```

Then open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

### Method 2: Direct Browser Launch (Offline Mode)

Simply double-click **`index.html`** in File Explorer or open it in Google Chrome, Microsoft Edge, or Mozilla Firefox.

---

## 📁 Project Structure

```
├── index.html         # Main Single Page Application interface
├── server.py          # Python standard library HTTP & SQLite REST server
├── css/
│   └── styles.css     # Custom animations, parking bay styles, thermal receipts
├── js/
│   ├── store.js       # Unified data layer (REST API + localStorage fallback)
│   ├── grid.js        # Interactive visual floor plan & slot bay renderer
│   ├── billing.js     # Tariff engine, duration counter, receipt formatter
│   └── app.js         # Master UI controller, search, navigation, charts
└── README.md          # Documentation and setup guide
```

---

## 🏷️ Default Tariff Rates

| Vehicle Category | 1st Hour Base Rate | Hourly Rate (after 1st hr) | Daily Maximum Cap | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Two-Wheeler** | $1.00 | $1.50 / hr | $12.00 | Bikes & Scooters |
| **Sedan / Car** | $2.50 | $3.00 / hr | $25.00 | Standard vehicle bay |
| **SUV** | $3.50 | $4.00 / hr | $35.00 | Large vehicle bay |
| **Electric (EV)** | $3.00 | $3.50 / hr | $30.00 | +$4.00 fast charging hub fee |
| **Priority** | $2.00 | $2.50 / hr | $20.00 | Accessible permit |

---

## 🧪 Testing Tips

1. Go to the **Check-In Gate** tab and click one of the quick test buttons (e.g. `🚗 Sedan (KA-05-NB-7821)`).
2. Click **"Open Barrier & Issue Ticket Pass"** to see the thermal pass pop up.
3. Switch to the **Live Bay Map** tab to see the assigned bay turn red.
4. Click on the occupied bay to instantly load it into the **Check-Out Cashier**.
5. Select a payment method and click **"Collect Payment & Release Gate"** to see the printable tax receipt and free the bay!
