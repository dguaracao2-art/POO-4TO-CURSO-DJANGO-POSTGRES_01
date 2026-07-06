class InvoiceService {
  constructor(api) { this.api = api; }

  async buscarProductos(q) {
    return this.api.get('/invoicing/api/productos/', { q });
  }

  async buscarClientes(q) {
    return this.api.get('/invoicing/api/clientes/', { q });
  }
}