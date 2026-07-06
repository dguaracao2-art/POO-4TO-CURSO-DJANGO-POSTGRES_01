(function () {
  const api = new ApiClient();
  const svc = new InvoiceService(api);

  // Elementos del DOM
  const els = {
    productosBody: document.getElementById('detalleBody'),
    totalSubtotal: document.getElementById('totalSubtotal'),
    totalIva: document.getElementById('totalIva'),
    totalGeneral: document.getElementById('totalGeneral'),
    productosJson: document.getElementById('productosJson'),
    searchProducto: document.getElementById('searchProducto'),
    resultsProducto: document.getElementById('resultsProducto'),
  };

  let lines = [];

  function actualizarTotales() {
    const t = InvoiceCalculator.calcTotals(lines);
    if (els.totalSubtotal) els.totalSubtotal.textContent = '$' + t.subtotal.toFixed(2);
    if (els.totalIva) els.totalIva.textContent = '$' + t.iva.toFixed(2);
    if (els.totalGeneral) els.totalGeneral.textContent = '$' + t.total.toFixed(2);
    if (els.productosJson) els.productosJson.value = JSON.stringify(
      lines.map(l => ({ producto_id: l.id, cantidad: l.cantidad, descuento_pct: l.descuentoPct }))
    );
  }

  function renderLine(index) {
    const l = lines[index];
    const calc = InvoiceCalculator.calcLine(l.cantidad, l.precio, l.descuentoPct, l.ivaPct);
    l.subtotal = calc.subtotal;
    l.ivaValor = calc.ivaValor;
    l.total = calc.total;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${l.codigo}</td>
      <td>${l.nombre}</td>
      <td><input type="number" class="form-control form-control-sm qty" value="${l.cantidad}" min="1" style="width:70px"></td>
      <td>$${l.precio.toFixed(2)}</td>
      <td><input type="number" class="form-control form-control-sm desc" value="${l.descuentoPct}" min="0" max="100" step="0.01" style="width:70px"></td>
      <td class="text-end">$${calc.subtotal.toFixed(2)}</td>
      <td><button type="button" class="btn btn-sm btn-outline-danger remove-line"><i class="bi bi-x"></i></button></td>
    `;
    row.dataset.index = index;

    row.querySelector('.qty').addEventListener('change', function () {
      lines[index].cantidad = parseInt(this.value) || 0;
      if (lines[index].cantidad > l.stockDisponible) this.classList.add('is-invalid');
      else this.classList.remove('is-invalid');
      renderLine(index);
      actualizarTotales();
    });
    row.querySelector('.desc').addEventListener('change', function () {
      lines[index].descuentoPct = parseFloat(this.value) || 0;
      renderLine(index);
      actualizarTotales();
    });
    row.querySelector('.remove-line').addEventListener('click', function () {
      lines.splice(index, 1);
      renderAllLines();
      actualizarTotales();
    });

    const existing = els.productosBody.children[index];
    if (existing) existing.replaceWith(row);
    else els.productosBody.appendChild(row);
  }

  function renderAllLines() {
    els.productosBody.innerHTML = '';
    lines.forEach((_, i) => renderLine(i));
  }

  function addProduct(prod) {
    if (lines.some(l => l.id === prod.id)) return;
    lines.push({
      id: prod.id, codigo: prod.codigo, nombre: prod.nombre,
      precio: parseFloat(prod.precio), ivaPct: parseFloat(prod.iva_porcentaje),
      stockDisponible: prod.stock, cantidad: 1, descuentoPct: 0,
      subtotal: 0, ivaValor: 0, total: 0,
    });
    const idx = lines.length - 1;
    renderLine(idx);
    actualizarTotales();
    if (els.resultsProducto) els.resultsProducto.innerHTML = '';
    if (els.searchProducto) els.searchProducto.value = '';
  }

  if (els.searchProducto) {
    let timeout;
    els.searchProducto.addEventListener('input', function () {
      clearTimeout(timeout);
      const q = this.value.trim();
      if (q.length < 2) { els.resultsProducto.innerHTML = ''; return; }
      timeout = setTimeout(async () => {
        const data = await svc.buscarProductos(q);
        els.resultsProducto.innerHTML = data.map(p =>
          `<a href="#" class="list-group-item list-group-item-action" data-id="${p.id}">
            <strong>${p.codigo}</strong> — ${p.nombre}
            <span class="float-end">$${parseFloat(p.precio).toFixed(2)} | Stock: ${p.stock}</span>
          </a>`
        ).join('');
        els.resultsProducto.querySelectorAll('a').forEach(a => {
          a.addEventListener('click', function (e) {
            e.preventDefault();
            const prod = data.find(p => p.id == this.dataset.id);
            if (prod) addProduct(prod);
          });
        });
      }, 300);
    });
  }

  // Si existe el formulario, inicializar
  if (els.productosBody) actualizarTotales();
})();