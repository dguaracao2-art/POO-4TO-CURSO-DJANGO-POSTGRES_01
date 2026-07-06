class InvoiceCalculator {
  static calcLine(cantidad, precio, descuentoPct, ivaPct) {
    const subtotal = cantidad * precio * (1 - descuentoPct / 100);
    const ivaValor = subtotal * ivaPct / 100;
    const total = subtotal + ivaValor;
    return {
      subtotal: Math.round(subtotal * 100) / 100,
      ivaValor: Math.round(ivaValor * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }

  static calcTotals(lines) {
    let subtotal = 0, iva = 0, total = 0;
    lines.forEach(l => {
      subtotal += l.subtotal;
      iva += l.ivaValor;
      total += l.total;
    });
    return {
      subtotal: Math.round(subtotal * 100) / 100,
      iva: Math.round(iva * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }
}