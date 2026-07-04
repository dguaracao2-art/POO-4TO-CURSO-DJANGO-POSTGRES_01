class ApiClient {
  constructor(config = {}) {
    this.client = axios.create({
      baseURL: config.baseURL || '',
      timeout: config.timeout || 15000,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this._getCsrfToken(),
      },
    });
    this._setupInterceptors();
  }

  _getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const cookie = this._getCookie('csrftoken');
    return cookie || '';
  }

  _getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  _setupInterceptors() {
    this.client.interceptors.response.use(
      (res) => res,
      (err) => {
        const msg = err.response?.data?.error
          || err.response?.data?.detail
          || 'Error de conexión con el servidor';
        return Promise.reject(new Error(msg));
      }
    );
  }

  async post(url, data) {
    const res = await this.client.post(url, data);
    return res.data;
  }

  async get(url, params = {}) {
    const res = await this.client.get(url, { params });
    return res.data;
  }
}
