/**
 * ParkFlow Data Store
 * Supports dual-mode:
 * 1. REST API connected to Python SQLite backend (server.py)
 * 2. Automatic fallback to localStorage when opened offline/standalone
 */

const Store = {
  isApiAvailable: null,

  async checkApi() {
    if (this.isApiAvailable !== null) return this.isApiAvailable;
    if (window.location.protocol === 'file:') {
      this.isApiAvailable = false;
      return false;
    }
    try {
      const res = await fetch('/api/slots', { method: 'GET', cache: 'no-store' });
      this.isApiAvailable = res.ok;
    } catch (e) {
      this.isApiAvailable = false;
    }
    return this.isApiAvailable;
  },

  // Fallback LocalStorage Initialization
  initLocalFallback() {
    if (!localStorage.getItem('parkflow_initialized')) {
      const defaultRates = [
        { vehicle_type: "Two-Wheeler", base_rate: 1.0, hourly_rate: 1.5, daily_max: 12.0, ev_surcharge: 0.0 },
        { vehicle_type: "Car", base_rate: 2.5, hourly_rate: 3.0, daily_max: 25.0, ev_surcharge: 0.0 },
        { vehicle_type: "SUV", base_rate: 3.5, hourly_rate: 4.0, daily_max: 35.0, ev_surcharge: 0.0 },
        { vehicle_type: "EV", base_rate: 3.0, hourly_rate: 3.5, daily_max: 30.0, ev_surcharge: 4.0 },
        { vehicle_type: "Priority", base_rate: 2.0, hourly_rate: 2.5, daily_max: 20.0, ev_surcharge: 0.0 },
      ];

      const defaultSlots = [];
      // Level 1: Ground Floor
      for (let i = 1; i <= 6; i++) defaultSlots.push({ id: `L1-B0${i}`, floor: "Level 1", slot_number: i, type: "Two-Wheeler", is_occupied: 0, current_vehicle_id: null });
      for (let i = 7; i <= 16; i++) defaultSlots.push({ id: `L1-C${i < 10 ? '0' + i : i}`, floor: "Level 1", slot_number: i, type: "Car", is_occupied: 0, current_vehicle_id: null });
      for (let i = 17; i <= 20; i++) defaultSlots.push({ id: `L1-S${i}`, floor: "Level 1", slot_number: i, type: "SUV", is_occupied: 0, current_vehicle_id: null });

      // Level 2: Basement B1
      for (let i = 1; i <= 12; i++) defaultSlots.push({ id: `B1-C${i < 10 ? '0' + i : i}`, floor: "Basement B1", slot_number: i, type: "Car", is_occupied: 0, current_vehicle_id: null });
      for (let i = 13; i <= 18; i++) defaultSlots.push({ id: `B1-S${i}`, floor: "Basement B1", slot_number: i, type: "SUV", is_occupied: 0, current_vehicle_id: null });
      for (let i = 19; i <= 20; i++) defaultSlots.push({ id: `B1-P${i}`, floor: "Basement B1", slot_number: i, type: "Priority", is_occupied: 0, current_vehicle_id: null });

      // Level 3: EV & VIP Hub
      for (let i = 1; i <= 8; i++) defaultSlots.push({ id: `L3-EV0${i}`, floor: "Level 3 (EV Hub)", slot_number: i, type: "EV", is_occupied: 0, current_vehicle_id: null });
      for (let i = 9; i <= 14; i++) defaultSlots.push({ id: `L3-C${i < 10 ? '0' + i : i}`, floor: "Level 3 (EV Hub)", slot_number: i, type: "Car", is_occupied: 0, current_vehicle_id: null });
      for (let i = 15; i <= 16; i++) defaultSlots.push({ id: `L3-P${i}`, floor: "Level 3 (EV Hub)", slot_number: i, type: "Priority", is_occupied: 0, current_vehicle_id: null });

      const now = new Date();
      const h2Ago = new Date(now.getTime() - 2.2 * 3600000).toISOString();
      const h1Ago = new Date(now.getTime() - 1.4 * 3600000).toISOString();
      const h3Ago = new Date(now.getTime() - 3.1 * 3600000).toISOString();

      const defaultSessions = [
        {
          id: "PK-2026-001",
          plate_number: "KA-01-MJ-4521",
          vehicle_type: "Car",
          driver_name: "Alex Turner",
          driver_phone: "9876543210",
          slot_id: "L1-C07",
          entry_time: h2Ago,
          status: "active"
        },
        {
          id: "PK-2026-002",
          plate_number: "DL-04-EV-9988",
          vehicle_type: "EV",
          driver_name: "Sarah Chen",
          driver_phone: "9845123654",
          slot_id: "L3-EV01",
          entry_time: h1Ago,
          status: "active"
        },
        {
          id: "PK-2026-003",
          plate_number: "MH-12-AB-3312",
          vehicle_type: "Two-Wheeler",
          driver_name: "Rahul Verma",
          driver_phone: "9765432190",
          slot_id: "L1-B01",
          entry_time: h3Ago,
          status: "active"
        }
      ];

      // Mark occupied slots
      defaultSessions.forEach(s => {
        const slot = defaultSlots.find(sl => sl.id === s.slot_id);
        if (slot) {
          slot.is_occupied = 1;
          slot.current_vehicle_id = s.plate_number;
        }
      });

      localStorage.setItem('parkflow_rates', JSON.stringify(defaultRates));
      localStorage.setItem('parkflow_slots', JSON.stringify(defaultSlots));
      localStorage.setItem('parkflow_sessions', JSON.stringify(defaultSessions));
      localStorage.setItem('parkflow_history', JSON.stringify([]));
      localStorage.setItem('parkflow_initialized', 'true');
    }
  },

  async getSlots() {
    if (await this.checkApi()) {
      const res = await fetch('/api/slots');
      return await res.json();
    }
    this.initLocalFallback();
    const slots = JSON.parse(localStorage.getItem('parkflow_slots') || '[]');
    const sessions = JSON.parse(localStorage.getItem('parkflow_sessions') || '[]');
    return slots.map(s => {
      const ses = sessions.find(sn => sn.slot_id === s.id && sn.status === 'active');
      return {
        ...s,
        plate_number: ses ? ses.plate_number : null,
        entry_time: ses ? ses.entry_time : null,
        session_id: ses ? ses.id : null,
        driver_name: ses ? ses.driver_name : null
      };
    });
  },

  async getActiveSessions() {
    if (await this.checkApi()) {
      const res = await fetch('/api/sessions/active');
      return await res.json();
    }
    this.initLocalFallback();
    const sessions = JSON.parse(localStorage.getItem('parkflow_sessions') || '[]');
    return sessions.filter(s => s.status === 'active');
  },

  async getHistory() {
    if (await this.checkApi()) {
      const res = await fetch('/api/history');
      return await res.json();
    }
    this.initLocalFallback();
    return JSON.parse(localStorage.getItem('parkflow_history') || '[]');
  },

  async getRates() {
    if (await this.checkApi()) {
      const res = await fetch('/api/rates');
      return await res.json();
    }
    this.initLocalFallback();
    return JSON.parse(localStorage.getItem('parkflow_rates') || '[]');
  },

  async getStats() {
    if (await this.checkApi()) {
      const res = await fetch('/api/stats');
      return await res.json();
    }
    this.initLocalFallback();
    const slots = JSON.parse(localStorage.getItem('parkflow_slots') || '[]');
    const history = JSON.parse(localStorage.getItem('parkflow_history') || '[]');
    const totalSlots = slots.length;
    const occupiedSlots = slots.filter(s => s.is_occupied).length;
    const totalRevenue = history.reduce((sum, h) => sum + (h.total_amount || 0), 0);

    const typeCounts = {};
    slots.forEach(s => {
      if (!typeCounts[s.type]) typeCounts[s.type] = { type: s.type, total: 0, occupied: 0 };
      typeCounts[s.type].total++;
      if (s.is_occupied) typeCounts[s.type].occupied++;
    });

    return {
      total_slots: totalSlots,
      occupied_slots: occupiedSlots,
      available_slots: totalSlots - occupiedSlots,
      occupancy_rate: totalSlots ? Number(((occupiedSlots / totalSlots) * 100).toFixed(1)) : 0,
      total_revenue: Number(totalRevenue.toFixed(2)),
      completed_trips: history.length,
      breakdown: Object.values(typeCounts)
    };
  },

  async checkIn({ plate_number, vehicle_type, driver_name, driver_phone, slot_id }) {
    plate_number = plate_number.trim().toUpperCase();
    vehicle_type = vehicle_type || 'Car';
    driver_name = driver_name ? driver_name.trim() : 'Guest';
    driver_phone = driver_phone ? driver_phone.trim() : '-';

    if (await this.checkApi()) {
      const res = await fetch('/api/checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plate_number, vehicle_type, driver_name, driver_phone, slot_id })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Check-in failed');
      return data;
    }

    // Local fallback
    this.initLocalFallback();
    const slots = JSON.parse(localStorage.getItem('parkflow_slots') || '[]');
    const sessions = JSON.parse(localStorage.getItem('parkflow_sessions') || '[]');

    const existing = sessions.find(s => s.plate_number === plate_number && s.status === 'active');
    if (existing) {
      throw new Error(`Vehicle ${plate_number} is already parked in slot ${existing.slot_id}!`);
    }

    let allocatedSlot = null;
    if (slot_id) {
      const target = slots.find(s => s.id === slot_id && !s.is_occupied);
      if (target) allocatedSlot = target.id;
    }

    if (!allocatedSlot) {
      const target = slots.find(s => !s.is_occupied && s.type === vehicle_type);
      if (target) {
        allocatedSlot = target.id;
      } else {
        const anyAvailable = slots.find(s => !s.is_occupied);
        if (anyAvailable) allocatedSlot = anyAvailable.id;
      }
    }

    if (!allocatedSlot) {
      throw new Error('Parking lot is full! No available slots.');
    }

    const sessionId = `PK-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${Math.random().toString(36).substring(2,6).toUpperCase()}`;
    const entryTime = new Date().toISOString();

    const newSession = {
      id: sessionId,
      plate_number,
      vehicle_type,
      driver_name,
      driver_phone,
      slot_id: allocatedSlot,
      entry_time: entryTime,
      status: 'active'
    };

    sessions.unshift(newSession);
    const slotIdx = slots.findIndex(s => s.id === allocatedSlot);
    if (slotIdx >= 0) {
      slots[slotIdx].is_occupied = 1;
      slots[slotIdx].current_vehicle_id = plate_number;
    }

    localStorage.setItem('parkflow_sessions', JSON.stringify(sessions));
    localStorage.setItem('parkflow_slots', JSON.stringify(slots));

    return {
      success: true,
      session_id: sessionId,
      plate_number,
      vehicle_type,
      slot_id: allocatedSlot,
      driver_name,
      driver_phone,
      entry_time: entryTime
    };
  },

  async checkOut({ query, payment_method }) {
    query = query.trim().toUpperCase();
    payment_method = payment_method || 'Cash';

    if (await this.checkApi()) {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, payment_method })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Check-out failed');
      return data;
    }

    // Local fallback
    this.initLocalFallback();
    const sessions = JSON.parse(localStorage.getItem('parkflow_sessions') || '[]');
    const slots = JSON.parse(localStorage.getItem('parkflow_slots') || '[]');
    const rates = JSON.parse(localStorage.getItem('parkflow_rates') || '[]');
    const history = JSON.parse(localStorage.getItem('parkflow_history') || '[]');

    const sIndex = sessions.findIndex(s => 
      s.status === 'active' && 
      (s.plate_number.toUpperCase() === query || s.id.toUpperCase() === query || s.slot_id.toUpperCase() === query)
    );

    if (sIndex === -1) {
      throw new Error(`No active parking session found for '${query}'`);
    }

    const session = sessions[sIndex];
    const entryDate = new Date(session.entry_time);
    const exitDate = new Date();
    const diffMin = Math.max(1, Math.round((exitDate.getTime() - entryDate.getTime()) / 60000));
    const hoursBilled = Math.ceil(diffMin / 60);

    const rateInfo = rates.find(r => r.vehicle_type === session.vehicle_type) || {
      base_rate: 2.5, hourly_rate: 3.0, daily_max: 25.0, ev_surcharge: 0.0
    };

    let totalAmount = 0;
    if (hoursBilled <= 1) {
      totalAmount = rateInfo.base_rate;
    } else {
      totalAmount = rateInfo.base_rate + (hoursBilled - 1) * rateInfo.hourly_rate;
    }

    if (session.vehicle_type === 'EV') {
      totalAmount += (rateInfo.ev_surcharge || 0);
    }

    const days = Math.ceil(hoursBilled / 24);
    const maxAllowed = days * (rateInfo.daily_max || 999);
    if (totalAmount > maxAllowed) {
      totalAmount = maxAllowed;
    }

    totalAmount = Number(totalAmount.toFixed(2));
    const exitTimeStr = exitDate.toISOString();

    session.exit_time = exitTimeStr;
    session.duration_minutes = diffMin;
    session.total_amount = totalAmount;
    session.payment_method = payment_method;
    session.status = 'completed';

    // Move to history
    sessions.splice(sIndex, 1);
    history.unshift(session);

    // Free slot
    const slotIdx = slots.findIndex(s => s.id === session.slot_id);
    if (slotIdx >= 0) {
      slots[slotIdx].is_occupied = 0;
      slots[slotIdx].current_vehicle_id = null;
    }

    localStorage.setItem('parkflow_sessions', JSON.stringify(sessions));
    localStorage.setItem('parkflow_history', JSON.stringify(history));
    localStorage.setItem('parkflow_slots', JSON.stringify(slots));

    return {
      success: true,
      session_id: session.id,
      plate_number: session.plate_number,
      vehicle_type: session.vehicle_type,
      driver_name: session.driver_name,
      slot_id: session.slot_id,
      entry_time: session.entry_time,
      exit_time: exitTimeStr,
      duration_minutes: diffMin,
      hours_billed: hoursBilled,
      base_rate: rateInfo.base_rate,
      hourly_rate: rateInfo.hourly_rate,
      ev_surcharge: session.vehicle_type === 'EV' ? rateInfo.ev_surcharge : 0,
      total_amount: totalAmount,
      payment_method: payment_method
    };
  },

  async resetData() {
    if (await this.checkApi()) {
      await fetch('/api/reset', { method: 'POST' });
      return;
    }
    localStorage.removeItem('parkflow_initialized');
    this.initLocalFallback();
  }
};

window.Store = Store;
