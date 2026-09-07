/**
 * ParkFlow Billing & Ticket Generator
 */

const Billing = {
  formatDuration(minutes) {
    if (minutes < 60) {
      return `${minutes} min${minutes === 1 ? '' : 's'}`;
    }
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hrs} hr${hrs === 1 ? '' : 's'}${mins > 0 ? ` ${mins} min` : ''}`;
  },

  formatCurrency(val) {
    return '$' + Number(val || 0).toFixed(2);
  },

  formatDateTime(isoString) {
    if (!isoString) return '-';
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { 
      month: 'short', day: 'numeric', year: 'numeric' 
    }) + ' ' + d.toLocaleTimeString(undefined, { 
      hour: '2-digit', minute: '2-digit' 
    });
  },

  renderTicketHTML(data) {
    return `
      <div class="thermal-receipt max-w-sm mx-auto p-6 rounded-md shadow-2xl border border-slate-300 text-slate-800 text-sm">
        <div class="text-center border-b-2 border-dashed border-slate-400 pb-4 mb-4">
          <div class="flex items-center justify-center gap-2 mb-1">
            <span class="text-xl font-black tracking-wider text-slate-900">PARKFLOW</span>
          </div>
          <p class="text-xs text-slate-500 font-mono">SMART AUTOMATED PARKING</p>
          <p class="text-xs text-slate-500 font-mono">100 Tech Hub Blvd, Metro City</p>
          <div class="mt-2 inline-block bg-slate-900 text-white text-xs px-2 py-0.5 rounded font-bold uppercase">
            PARKING ENTRY PASS
          </div>
        </div>

        <div class="space-y-2 mb-4 font-mono text-xs">
          <div class="flex justify-between">
            <span class="text-slate-500">TICKET NO:</span>
            <span class="font-bold text-slate-900">${data.session_id || data.id}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">PLATE NO:</span>
            <span class="font-bold text-slate-900 tracking-wider">${data.plate_number}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">VEHICLE TYPE:</span>
            <span class="font-semibold">${data.vehicle_type}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">ASSIGNED BAY:</span>
            <span class="font-black text-sm text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">${data.slot_id}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">ENTRY TIME:</span>
            <span class="font-medium">${Billing.formatDateTime(data.entry_time)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">DRIVER:</span>
            <span class="font-medium">${data.driver_name || 'Guest'}</span>
          </div>
        </div>

        <!-- Simulated Barcode -->
        <div class="text-center py-2 border-t border-b border-dashed border-slate-300 my-4">
          <div class="barcode-strip my-1"></div>
          <div class="text-[10px] font-mono tracking-widest text-slate-600 mt-1">${data.session_id || data.id}</div>
        </div>

        <div class="text-center text-[11px] text-slate-500 space-y-1">
          <p>Please keep this ticket with you.</p>
          <p>Standard tariffs apply after 15 minutes grace.</p>
          <p class="font-semibold text-slate-700">Thank you for visiting ParkFlow!</p>
        </div>
      </div>
    `;
  },

  renderInvoiceHTML(data) {
    return `
      <div class="thermal-receipt max-w-sm mx-auto p-6 rounded-md shadow-2xl border border-slate-300 text-slate-800 text-sm">
        <div class="text-center border-b-2 border-dashed border-slate-400 pb-4 mb-4">
          <div class="flex items-center justify-center gap-2 mb-1">
            <span class="text-xl font-black tracking-wider text-slate-900">PARKFLOW</span>
          </div>
          <p class="text-xs text-slate-500 font-mono">OFFICIAL EXIT RECEIPT & TAX INVOICE</p>
          <div class="mt-2 inline-block bg-emerald-800 text-white text-xs px-2 py-0.5 rounded font-bold uppercase">
            PAYMENT SETTLED
          </div>
        </div>

        <div class="space-y-2 mb-4 font-mono text-xs">
          <div class="flex justify-between">
            <span class="text-slate-500">RECEIPT NO:</span>
            <span class="font-bold text-slate-900">${data.session_id}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">VEHICLE PLATE:</span>
            <span class="font-bold text-slate-900">${data.plate_number}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">VEHICLE CATEGORY:</span>
            <span>${data.vehicle_type}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">PARKING BAY:</span>
            <span class="font-bold text-slate-800">${data.slot_id}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">CHECK-IN:</span>
            <span>${Billing.formatDateTime(data.entry_time)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">CHECK-OUT:</span>
            <span>${Billing.formatDateTime(data.exit_time)}</span>
          </div>
          <div class="flex justify-between font-semibold">
            <span class="text-slate-500">TOTAL DURATION:</span>
            <span class="text-indigo-600">${Billing.formatDuration(data.duration_minutes)}</span>
          </div>
          <div class="flex justify-between text-slate-500">
            <span>BILLED TIME:</span>
            <span>${data.hours_billed} hr(s)</span>
          </div>
        </div>

        <div class="border-t border-b border-dashed border-slate-300 py-3 mb-4 font-mono text-xs space-y-1.5">
          <div class="flex justify-between">
            <span>Base Parking Fee:</span>
            <span>${Billing.formatCurrency(data.base_rate)}</span>
          </div>
          ${data.hours_billed > 1 ? `
          <div class="flex justify-between">
            <span>Hourly Charges (${data.hours_billed - 1}h @ ${Billing.formatCurrency(data.hourly_rate)}):</span>
            <span>${Billing.formatCurrency((data.hours_billed - 1) * data.hourly_rate)}</span>
          </div>` : ''}
          ${data.ev_surcharge ? `
          <div class="flex justify-between text-cyan-700">
            <span>EV Fast Charging Station:</span>
            <span>${Billing.formatCurrency(data.ev_surcharge)}</span>
          </div>` : ''}
          <div class="flex justify-between text-slate-400 text-[10px]">
            <span>Tax (Included):</span>
            <span>${Billing.formatCurrency(data.total_amount * 0.08)}</span>
          </div>
          <div class="flex justify-between text-base font-bold text-slate-900 pt-2 border-t border-slate-200">
            <span>TOTAL PAID:</span>
            <span class="text-emerald-700">${Billing.formatCurrency(data.total_amount)}</span>
          </div>
          <div class="flex justify-between text-xs text-slate-600 pt-1">
            <span>Payment Mode:</span>
            <span class="font-semibold uppercase">${data.payment_method || 'Cash'}</span>
          </div>
        </div>

        <div class="text-center text-[11px] text-slate-500 space-y-1">
          <p>Exit Gate is unlocked for 15 minutes.</p>
          <p class="font-semibold text-slate-700">Safe travels! Have a wonderful day.</p>
        </div>
      </div>
    `;
  }
};

window.Billing = Billing;
