/**
 * ParkFlow Main Application Controller
 */

const App = {
  currentTab: 'overview',
  slots: [],
  activeSessions: [],
  history: [],
  rates: [],
  stats: null,
  charts: {},

  async init() {
    this.setupClock();
    this.setupEventListeners();
    await this.refreshAllData();

    // Auto refresh every 30 seconds
    setInterval(() => this.refreshAllData(true), 30000);
  },

  setupClock() {
    const clockEl = document.getElementById('live-clock');
    const updateTime = () => {
      if (clockEl) {
        const now = new Date();
        clockEl.textContent = now.toLocaleDateString(undefined, { 
          weekday: 'short', month: 'short', day: 'numeric' 
        }) + ' • ' + now.toLocaleTimeString();
      }
    };
    updateTime();
    setInterval(updateTime, 1000);
  },

  setupEventListeners() {
    // Navigation Tabs
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = btn.getAttribute('data-tab-target');
        this.switchTab(target);
      });
    });

    // Floor filter buttons
    document.querySelectorAll('[data-floor-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-floor-filter]').forEach(b => {
          b.classList.remove('bg-indigo-600', 'text-white');
          b.classList.add('bg-slate-800', 'text-slate-400');
        });
        btn.classList.remove('bg-slate-800', 'text-slate-400');
        btn.classList.add('bg-indigo-600', 'text-white');

        ParkingGrid.selectedFloor = btn.getAttribute('data-floor-filter');
        ParkingGrid.render(this.slots);
      });
    });

    // Vehicle type filter
    const typeFilter = document.getElementById('grid-type-filter');
    if (typeFilter) {
      typeFilter.addEventListener('change', (e) => {
        ParkingGrid.selectedType = e.target.value;
        ParkingGrid.render(this.slots);
      });
    }

    // Grid search bar
    const searchInput = document.getElementById('grid-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        ParkingGrid.searchQuery = e.target.value;
        ParkingGrid.render(this.slots);
      });
    }

    // Check-in form
    const checkinForm = document.getElementById('checkin-form');
    if (checkinForm) {
      checkinForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.submitCheckIn();
      });
    }

    // Checkout search input
    const checkoutQueryInput = document.getElementById('checkout-query');
    if (checkoutQueryInput) {
      checkoutQueryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.searchForCheckout();
        }
      });
    }
  },

  switchTab(tabId) {
    this.currentTab = tabId;

    // Update Nav Buttons
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      const isCurrent = btn.getAttribute('data-tab-target') === tabId;
      if (isCurrent) {
        btn.classList.add('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-500/30');
        btn.classList.remove('text-slate-400', 'hover:bg-slate-800', 'hover:text-white');
      } else {
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-500/30');
        btn.classList.add('text-slate-400', 'hover:bg-slate-800', 'hover:text-white');
      }
    });

    // Update Tab Content Sections
    document.querySelectorAll('.tab-content-panel').forEach(panel => {
      if (panel.id === `tab-${tabId}`) {
        panel.classList.remove('hidden');
      } else {
        panel.classList.add('hidden');
      }
    });

    if (tabId === 'map') {
      ParkingGrid.render(this.slots);
    } else if (tabId === 'history') {
      this.renderHistoryTable();
    } else if (tabId === 'analytics') {
      this.renderCharts();
    }
  },

  async refreshAllData(silent = false) {
    try {
      const [slots, sessions, history, stats, rates] = await Promise.all([
        Store.getSlots(),
        Store.getActiveSessions(),
        Store.getHistory(),
        Store.getStats(),
        Store.getRates()
      ]);

      this.slots = slots;
      this.activeSessions = sessions;
      this.history = history;
      this.stats = stats;
      this.rates = rates;

      this.updateStatsCards();
      this.renderRecentActivities();
      this.updateSlotDropdown();
      ParkingGrid.render(this.slots);

      if (this.currentTab === 'history') {
        this.renderHistoryTable();
      }
      if (this.currentTab === 'analytics') {
        this.renderCharts();
      }
      this.renderTariffTable();
    } catch (err) {
      if (!silent) this.showToast(err.message, 'error');
    }
  },

  updateStatsCards() {
    if (!this.stats) return;

    const totalEl = document.getElementById('stat-total-slots');
    const occupiedEl = document.getElementById('stat-occupied-slots');
    const availableEl = document.getElementById('stat-available-slots');
    const revenueEl = document.getElementById('stat-revenue');
    const occRateEl = document.getElementById('stat-occupancy-rate');
    const occProgressEl = document.getElementById('stat-occupancy-progress');

    if (totalEl) totalEl.textContent = this.stats.total_slots;
    if (occupiedEl) occupiedEl.textContent = this.stats.occupied_slots;
    if (availableEl) availableEl.textContent = this.stats.available_slots;
    if (revenueEl) revenueEl.textContent = Billing.formatCurrency(this.stats.total_revenue);
    if (occRateEl) occRateEl.textContent = `${this.stats.occupancy_rate}%`;
    if (occProgressEl) occProgressEl.style.width = `${Math.min(100, this.stats.occupancy_rate)}%`;
  },

  renderRecentActivities() {
    const container = document.getElementById('recent-activities-list');
    if (!container) return;

    if (this.activeSessions.length === 0 && this.history.length === 0) {
      container.innerHTML = `
        <div class="p-6 text-center text-slate-500 text-sm">
          No parking activities recorded yet.
        </div>
      `;
      return;
    }

    // Combine active entries and recent exits
    const items = [
      ...this.activeSessions.slice(0, 4).map(s => ({ ...s, action: 'ENTERED', time: s.entry_time })),
      ...this.history.slice(0, 4).map(h => ({ ...h, action: 'EXITED', time: h.exit_time }))
    ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 5);

    container.innerHTML = items.map(item => {
      const isEntry = item.action === 'ENTERED';
      return `
        <div class="flex items-center justify-between p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:bg-slate-800/80 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center ${isEntry ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'}">
              ${isEntry ? `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>
              ` : `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
              `}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="font-mono font-bold text-xs text-white">${item.plate_number}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${isEntry ? 'bg-emerald-500/20 text-emerald-300' : 'bg-indigo-500/20 text-indigo-300'}">
                  ${item.action}
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-0.5">Bay: <strong class="text-slate-200">${item.slot_id}</strong> • ${item.vehicle_type}</p>
            </div>
          </div>
          <div class="text-right">
            ${!isEntry && item.total_amount ? `
              <span class="font-bold text-emerald-400 text-xs">${Billing.formatCurrency(item.total_amount)}</span>
            ` : `
              <span class="text-xs font-semibold text-slate-300">Parked</span>
            `}
            <p class="text-[10px] text-slate-500 mt-0.5">${this.getTimeElapsed(item.time)}</p>
          </div>
        </div>
      `;
    }).join('');
  },

  updateSlotDropdown() {
    const selectEl = document.getElementById('preferred-slot-select');
    if (!selectEl) return;

    const availableSlots = this.slots.filter(s => !s.is_occupied);
    selectEl.innerHTML = `
      <option value="">Auto-Assign (Recommended)</option>
      ${availableSlots.map(s => `
        <option value="${s.id}">${s.id} (${s.floor} - ${s.type})</option>
      `).join('')}
    `;
  },

  handleSlotClick(slotId, isOccupied) {
    if (isOccupied) {
      // Find session
      const session = this.activeSessions.find(s => s.slot_id === slotId);
      if (session) {
        this.switchTab('checkout');
        const queryInput = document.getElementById('checkout-query');
        if (queryInput) {
          queryInput.value = session.plate_number;
          this.searchForCheckout();
        }
      }
    } else {
      // Direct check-in for this slot
      this.switchTab('checkin');
      const slotSelect = document.getElementById('preferred-slot-select');
      if (slotSelect) {
        slotSelect.value = slotId;
      }
      const plateInput = document.getElementById('plate-number');
      if (plateInput) plateInput.focus();
    }
  },

  async submitCheckIn() {
    const plateInput = document.getElementById('plate-number');
    const typeSelect = document.getElementById('vehicle-type');
    const nameInput = document.getElementById('driver-name');
    const phoneInput = document.getElementById('driver-phone');
    const slotSelect = document.getElementById('preferred-slot-select');

    const plate_number = plateInput.value.trim().toUpperCase();
    if (!plate_number) {
      this.showToast('Please enter a vehicle license plate number', 'error');
      return;
    }

    try {
      const result = await Store.checkIn({
        plate_number,
        vehicle_type: typeSelect.value,
        driver_name: nameInput.value,
        driver_phone: phoneInput.value,
        slot_id: slotSelect.value || null
      });

      this.showToast(`Vehicle ${plate_number} parked in ${result.slot_id}!`, 'success');
      
      // Reset form
      plateInput.value = '';
      nameInput.value = '';
      phoneInput.value = '';
      slotSelect.value = '';

      await this.refreshAllData();

      // Show ticket pass modal
      this.showTicketModal(result);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  fillSampleCheckin(plate, type, name, phone) {
    document.getElementById('plate-number').value = plate;
    document.getElementById('vehicle-type').value = type;
    document.getElementById('driver-name').value = name;
    document.getElementById('driver-phone').value = phone;
  },

  async searchForCheckout() {
    const queryInput = document.getElementById('checkout-query');
    const query = queryInput.value.trim();
    if (!query) {
      this.showToast('Enter a plate number, ticket ID, or bay number', 'error');
      return;
    }

    const session = this.activeSessions.find(s => 
      s.plate_number.toUpperCase() === query.toUpperCase() || 
      s.id.toUpperCase() === query.toUpperCase() || 
      s.slot_id.toUpperCase() === query.toUpperCase()
    );

    const detailsContainer = document.getElementById('checkout-preview-card');
    if (!session) {
      this.showToast(`No parked vehicle found matching "${query}"`, 'error');
      if (detailsContainer) detailsContainer.classList.add('hidden');
      return;
    }

    // Calculate live bill preview
    const entryDate = new Date(session.entry_time);
    const now = new Date();
    const diffMinutes = Math.max(1, Math.round((now.getTime() - entryDate.getTime()) / 60000));
    const hoursBilled = Math.ceil(diffMinutes / 60);

    const rate = this.rates.find(r => r.vehicle_type === session.vehicle_type) || {
      base_rate: 2.5, hourly_rate: 3.0, daily_max: 25.0, ev_surcharge: 0.0
    };

    let total = hoursBilled <= 1 ? rate.base_rate : rate.base_rate + (hoursBilled - 1) * rate.hourly_rate;
    if (session.vehicle_type === 'EV') total += rate.ev_surcharge;

    const days = Math.ceil(hoursBilled / 24);
    if (total > days * rate.daily_max) total = days * rate.daily_max;

    if (detailsContainer) {
      detailsContainer.innerHTML = `
        <div class="bg-slate-900 border border-indigo-500/30 rounded-2xl p-6 shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
            <div>
              <span class="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Parking Session Found</span>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-2xl font-bold font-mono text-white tracking-wider">${session.plate_number}</span>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  ${session.vehicle_type}
                </span>
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs text-slate-400">Assigned Bay</span>
              <p class="text-xl font-black text-emerald-400 font-mono">${session.slot_id}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
              <span class="text-[11px] text-slate-400 block">Driver</span>
              <span class="font-medium text-white text-sm">${session.driver_name || 'Guest'}</span>
            </div>
            <div class="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
              <span class="text-[11px] text-slate-400 block">Check-In Time</span>
              <span class="font-medium text-white text-sm">${new Date(session.entry_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
            <div class="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
              <span class="text-[11px] text-slate-400 block">Duration</span>
              <span class="font-bold text-indigo-400 text-sm">${Billing.formatDuration(diffMinutes)}</span>
            </div>
            <div class="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
              <span class="text-[11px] text-slate-400 block">Billable Time</span>
              <span class="font-bold text-white text-sm">${hoursBilled} hr(s)</span>
            </div>
          </div>

          <!-- Total Bill Card -->
          <div class="bg-indigo-950/40 border border-indigo-500/20 rounded-xl p-4 mb-6 flex items-center justify-between">
            <div>
              <span class="text-xs text-slate-400 block">Total Payable Tariff</span>
              <span class="text-xs text-indigo-300 font-mono">Base: ${Billing.formatCurrency(rate.base_rate)} + ${hoursBilled > 1 ? `${hoursBilled - 1}h @ ${Billing.formatCurrency(rate.hourly_rate)}` : '0h'} ${session.vehicle_type === 'EV' ? `+ EV Surcharge` : ''}</span>
            </div>
            <div class="text-3xl font-black text-emerald-400 font-mono">
              ${Billing.formatCurrency(total)}
            </div>
          </div>

          <!-- Payment Mode Selection -->
          <div class="mb-6">
            <label class="block text-xs font-semibold text-slate-300 mb-2">Select Payment Method</label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              ${['Cash', 'Credit Card', 'UPI / Fastag', 'Apple/Google Pay'].map((mode, idx) => `
                <label class="flex items-center gap-2 p-3 rounded-xl bg-slate-800/80 border border-slate-700 cursor-pointer hover:border-indigo-500 transition-colors">
                  <input type="radio" name="payment_mode" value="${mode}" ${idx === 0 ? 'checked' : ''} class="text-indigo-600 focus:ring-indigo-500">
                  <span class="text-xs font-semibold text-white">${mode}</span>
                </label>
              `).join('')}
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button 
              onclick="App.processCheckout('${session.plate_number}')"
              class="flex-1 py-3.5 px-6 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm tracking-wider shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              COLLECT PAYMENT & RELEASE GATE
            </button>
          </div>
        </div>
      `;
      detailsContainer.classList.remove('hidden');
    }
  },

  async processCheckout(plate) {
    const selectedMode = document.querySelector('input[name="payment_mode"]:checked')?.value || 'Cash';
    try {
      const result = await Store.checkOut({ query: plate, payment_method: selectedMode });
      this.showToast(`Vehicle ${result.plate_number} checked out successfully!`, 'success');

      // Clear search card
      document.getElementById('checkout-query').value = '';
      const previewCard = document.getElementById('checkout-preview-card');
      if (previewCard) previewCard.classList.add('hidden');

      await this.refreshAllData();

      // Show official invoice modal
      this.showInvoiceModal(result);
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  showTicketModal(ticketData) {
    const modal = document.getElementById('ticket-modal');
    const content = document.getElementById('ticket-modal-content');
    if (!modal || !content) return;

    content.innerHTML = Billing.renderTicketHTML(ticketData);
    modal.classList.remove('hidden');
  },

  showInvoiceModal(invoiceData) {
    const modal = document.getElementById('ticket-modal');
    const content = document.getElementById('ticket-modal-content');
    if (!modal || !content) return;

    content.innerHTML = Billing.renderInvoiceHTML(invoiceData);
    modal.classList.remove('hidden');
  },

  closeModal() {
    const modal = document.getElementById('ticket-modal');
    if (modal) modal.classList.add('hidden');
  },

  printCurrentReceipt() {
    window.print();
  },

  async showGadgetConnectModal() {
    let gadgetUrl = `${window.location.protocol}//${window.location.hostname || 'localhost'}:${window.location.port || '8000'}`;
    try {
      if (await Store.checkApi()) {
        const res = await fetch('/api/network-info');
        if (res.ok) {
          const info = await res.json();
          gadgetUrl = info.gadget_url;
        }
      }
    } catch (e) {
      console.warn('Network info unavailable:', e);
    }

    const urlText = document.getElementById('gadget-url-text');
    const qrImg = document.getElementById('gadget-qr-image');
    if (urlText) urlText.textContent = gadgetUrl;
    if (qrImg) {
      qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(gadgetUrl)}`;
    }

    const modal = document.getElementById('gadget-connect-modal');
    if (modal) modal.classList.remove('hidden');
  },

  closeGadgetModal() {
    const modal = document.getElementById('gadget-connect-modal');
    if (modal) modal.classList.add('hidden');
  },

  copyGadgetUrl() {
    const urlText = document.getElementById('gadget-url-text');
    if (urlText) {
      navigator.clipboard.writeText(urlText.textContent.trim()).then(() => {
        this.showToast('Gadget link copied to clipboard!', 'success');
      }).catch(() => {
        prompt('Copy this URL to open on your phone:', urlText.textContent.trim());
      });
    }
  },

  renderHistoryTable() {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;

    if (this.history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center py-10 text-slate-500 text-sm">
            No completed parking sessions yet.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = this.history.map(item => `
      <tr class="border-b border-slate-800/80 hover:bg-slate-800/40 transition-colors text-xs">
        <td class="py-3 px-4 font-mono font-bold text-white">${item.id}</td>
        <td class="py-3 px-4">
          <span class="license-plate text-xs">
            <span class="country-code">IND</span>
            <span class="text-white font-bold">${item.plate_number}</span>
          </span>
        </td>
        <td class="py-3 px-4">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300">
            ${item.vehicle_type}
          </span>
        </td>
        <td class="py-3 px-4 font-mono font-semibold text-emerald-400">${item.slot_id}</td>
        <td class="py-3 px-4 text-slate-400">${Billing.formatDateTime(item.entry_time)}</td>
        <td class="py-3 px-4 text-slate-300 font-medium">${Billing.formatDuration(item.duration_minutes)}</td>
        <td class="py-3 px-4 font-mono font-bold text-emerald-400">${Billing.formatCurrency(item.total_amount)}</td>
      </tr>
    `).join('');
  },

  exportHistoryCSV() {
    if (this.history.length === 0) {
      this.showToast('No history records to export', 'error');
      return;
    }

    const headers = ['Receipt_ID', 'Plate_Number', 'Vehicle_Type', 'Slot_ID', 'Entry_Time', 'Exit_Time', 'Duration_Minutes', 'Total_Amount', 'Payment_Method'];
    const rows = this.history.map(h => [
      h.id,
      h.plate_number,
      h.vehicle_type,
      h.slot_id,
      h.entry_time,
      h.exit_time,
      h.duration_minutes,
      h.total_amount,
      h.payment_method || 'Cash'
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ParkFlow_Records_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showToast('Exported history CSV successfully!', 'success');
  },

  renderTariffTable() {
    const container = document.getElementById('tariff-list-container');
    if (!container) return;

    container.innerHTML = this.rates.map(rate => `
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div>
          <h4 class="font-bold text-white text-sm">${rate.vehicle_type}</h4>
          <p class="text-xs text-slate-400 mt-0.5">Base: ${Billing.formatCurrency(rate.base_rate)} (1st hr) • Hourly: ${Billing.formatCurrency(rate.hourly_rate)}/hr</p>
          ${rate.ev_surcharge ? `<span class="text-[10px] text-cyan-400 font-semibold">+ ${Billing.formatCurrency(rate.ev_surcharge)} EV Charging Hub fee</span>` : ''}
        </div>
        <div class="text-right">
          <span class="text-xs text-slate-400 block">Daily Cap</span>
          <span class="font-mono font-bold text-emerald-400 text-sm">${Billing.formatCurrency(rate.daily_max)}</span>
        </div>
      </div>
    `).join('');
  },

  renderCharts() {
    if (typeof Chart === 'undefined') return;

    // Occupancy by Vehicle Type Chart
    const ctxOccupancy = document.getElementById('chart-occupancy');
    if (ctxOccupancy && this.stats && this.stats.breakdown) {
      if (this.charts.occupancy) this.charts.occupancy.destroy();

      const labels = this.stats.breakdown.map(b => b.type);
      const occupiedData = this.stats.breakdown.map(b => b.occupied);
      const availableData = this.stats.breakdown.map(b => b.total - b.occupied);

      this.charts.occupancy = new Chart(ctxOccupancy, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: occupiedData.map(v => Math.max(v, 1)), // subtle representation
            backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#06b6d4', '#8b5cf6'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } }
          }
        }
      });
    }

    // Revenue Trend Chart
    const ctxRevenue = document.getElementById('chart-revenue');
    if (ctxRevenue) {
      if (this.charts.revenue) this.charts.revenue.destroy();

      this.charts.revenue = new Chart(ctxRevenue, {
        type: 'bar',
        data: {
          labels: ['8 AM', '10 AM', '12 PM', '2 PM', '4 PM', '6 PM', 'Current'],
          datasets: [{
            label: 'Occupancy Rate %',
            data: [25, 45, 78, 65, 82, 70, this.stats ? this.stats.occupancy_rate : 50],
            backgroundColor: '#4f46e5',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
  },

  getTimeElapsed(isoString) {
    if (!isoString) return '';
    const diffMin = Math.max(0, Math.floor((new Date() - new Date(isoString)) / 60000));
    if (diffMin < 1) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    const hrs = Math.floor(diffMin / 60);
    const mins = diffMin % 60;
    return `${hrs}h ${mins}m ago`;
  },

  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const isError = type === 'error';
    const isSuccess = type === 'success';

    toast.className = `fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl text-xs font-semibold backdrop-blur transition-all duration-300 transform translate-y-4 opacity-0 ${
      isError ? 'bg-red-500/90 text-white border border-red-400' :
      isSuccess ? 'bg-emerald-600/90 text-white border border-emerald-400' :
      'bg-slate-800 text-white border border-slate-700'
    }`;

    toast.innerHTML = `
      <span>${isError ? '⚠️' : isSuccess ? '✅' : 'ℹ️'}</span>
      <span>${message}</span>
    `;

    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-4', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('translate-y-4', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  async resetAllDemoData() {
    if (confirm('Reset parking database with fresh demo data?')) {
      await Store.resetData();
      await this.refreshAllData();
      this.showToast('System reset with clean demo data!', 'success');
    }
  }
};

window.App = App;

// Bootstrap application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
