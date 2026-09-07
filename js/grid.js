/**
 * ParkFlow Interactive Visual Parking Grid
 */

const ParkingGrid = {
  containerId: 'parking-grid-container',
  selectedFloor: 'all',
  selectedType: 'all',
  searchQuery: '',

  getVehicleIcon(type) {
    switch(type) {
      case 'Two-Wheeler':
        return `<svg class="w-5 h-5 text-indigo-400" fill="currentColor" viewBox="0 0 24 24"><path d="M19 7a2 2 0 0 0-2-2h-3v2h3v2.65L13.52 14H10V9H7a4 4 0 1 0 0 8 4 4 0 0 0 4-4h3l3.8-5.7A1.99 1.99 0 0 0 19 7zM5 15a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm14 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/></svg>`;
      case 'EV':
        return `<svg class="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l3-8H7zm9 13h2v2h-2v-2zm0-4h2v2h-2v-2zm0-4h2v2h-2V7z"/></svg>`;
      case 'SUV':
        return `<svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 24 24"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.85 7h10.29l1.04 3H5.81l1.04-3zM19 17H5v-4.66l.12-.34h13.77l.11.34V17z"/><circle cx="7.5" cy="14.5" r="1.5"/><circle cx="16.5" cy="14.5" r="1.5"/></svg>`;
      case 'Priority':
        return `<svg class="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm7 15.5c0-.83-.67-1.5-1.5-1.5H16v-4.5c0-1.1-.9-2-2-2h-3c-.55 0-1 .45-1 1s.45 1 1 1h3v4.5h-1.5c-.83 0-1.5.67-1.5 1.5V21h-2v-7.5c0-1.93 1.57-3.5 3.5-3.5h2c1.93 0 3.5 1.57 3.5 3.5V21h-2v-1.5zM6 13c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>`;
      default: // Car
        return `<svg class="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.85 7h10.29l1.08 3.11H5.77L6.85 7zM19 17H5v-5h14v5z"/><circle cx="7.5" cy="14.5" r="1.5"/><circle cx="16.5" cy="14.5" r="1.5"/></svg>`;
    }
  },

  render(slots) {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    // Filter slots by floor, type, and search query
    let filtered = slots.filter(slot => {
      const matchFloor = (this.selectedFloor === 'all') || (slot.floor.toLowerCase().includes(this.selectedFloor.toLowerCase()));
      const matchType = (this.selectedType === 'all') || (slot.type === this.selectedType);
      const query = this.searchQuery.trim().toLowerCase();
      const matchSearch = !query || 
        slot.id.toLowerCase().includes(query) || 
        (slot.plate_number && slot.plate_number.toLowerCase().includes(query)) ||
        (slot.driver_name && slot.driver_name.toLowerCase().includes(query));
      return matchFloor && matchType && matchSearch;
    });

    // Group by floor
    const floors = {};
    filtered.forEach(slot => {
      if (!floors[slot.floor]) floors[slot.floor] = [];
      floors[slot.floor].push(slot);
    });

    if (Object.keys(floors).length === 0) {
      container.innerHTML = `
        <div class="text-center py-16 text-slate-400">
          <svg class="w-16 h-16 mx-auto mb-3 opacity-40 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <p class="text-lg font-medium text-slate-300">No parking slots matched your filters</p>
          <p class="text-sm mt-1">Try clearing your search query or selecting "All Floors".</p>
        </div>
      `;
      return;
    }

    let html = '';
    for (const [floorName, floorSlots] of Object.entries(floors)) {
      const occupiedCount = floorSlots.filter(s => s.is_occupied).length;
      const totalCount = floorSlots.length;
      const availableCount = totalCount - occupiedCount;
      const pct = totalCount ? Math.round((occupiedCount / totalCount) * 100) : 0;

      html += `
        <div class="mb-8 bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur">
          <!-- Floor Header -->
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4 mb-5">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-lg">
                ${floorName.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <h3 class="text-lg font-bold text-white tracking-wide">${floorName}</h3>
                <p class="text-xs text-slate-400">Automated Bay Area • Monitored 24/7</p>
              </div>
            </div>

            <!-- Floor Stats Badges -->
            <div class="flex items-center gap-3 text-xs">
              <span class="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-semibold flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                ${availableCount} Available
              </span>
              <span class="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 font-semibold">
                ${occupiedCount} Occupied
              </span>
              <span class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 font-medium">
                ${pct}% Full
              </span>
            </div>
          </div>

          <!-- Parking Bay Slots Grid -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3.5">
            ${floorSlots.map(slot => this.renderSlotCard(slot)).join('')}
          </div>
        </div>
      `;
    }

    container.innerHTML = html;
  },

  renderSlotCard(slot) {
    const isOccupied = Boolean(slot.is_occupied);
    const isEV = slot.type === 'EV';
    const isPriority = slot.type === 'Priority';
    
    let statusClass = 'slot-status-available';
    let badgeText = 'AVAILABLE';
    let badgeColor = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';

    if (isOccupied) {
      statusClass = 'slot-status-occupied';
      badgeText = isEV ? 'CHARGING' : 'OCCUPIED';
      badgeColor = isEV ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30';
    } else if (isEV) {
      statusClass = 'slot-status-ev';
    } else if (isPriority) {
      statusClass = 'slot-status-priority';
    }

    return `
      <div 
        class="parking-slot-card ${statusClass} rounded-xl p-3 flex flex-col justify-between min-h-[140px] ${isOccupied && isEV ? 'pulse-charging' : ''}"
        onclick="App.handleSlotClick('${slot.id}', ${isOccupied})"
        title="${slot.id} - ${isOccupied ? 'Click to Check-Out or View Ticket' : 'Click to Check-In a vehicle'}"
      >
        <!-- Top row: Slot ID and Type icon -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="font-mono font-bold text-sm text-white tracking-wider">${slot.id}</span>
          </div>
          <span title="${slot.type}">${this.getVehicleIcon(slot.type)}</span>
        </div>

        <!-- Center: Visual status / Vehicle plate -->
        <div class="my-2 text-center">
          ${isOccupied ? `
            <div class="license-plate max-w-full justify-center text-xs">
              <span class="country-code">IND</span>
              <span class="text-white font-bold truncate">${slot.plate_number || 'OCCUPIED'}</span>
            </div>
            ${slot.entry_time ? `
              <div class="text-[10px] text-slate-400 mt-1.5 flex items-center justify-center gap-1">
                <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                <span>${App.getTimeElapsed(slot.entry_time)}</span>
              </div>
            ` : ''}
          ` : `
            <div class="text-xs text-slate-400 flex flex-col items-center justify-center py-2 group-hover:text-emerald-300">
              <svg class="w-6 h-6 text-emerald-500/60 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              <span class="text-[11px] font-medium text-emerald-400/90">CLICK TO PARK</span>
            </div>
          `}
        </div>

        <!-- Bottom row: Badge & Slot Type label -->
        <div class="flex items-center justify-between text-[10px] pt-2 border-t border-slate-800/80">
          <span class="text-slate-400 uppercase font-medium">${slot.type}</span>
          <span class="px-1.5 py-0.5 rounded border text-[9px] font-semibold uppercase ${badgeColor}">
            ${badgeText}
          </span>
        </div>
      </div>
    `;
  }
};

window.ParkingGrid = ParkingGrid;
