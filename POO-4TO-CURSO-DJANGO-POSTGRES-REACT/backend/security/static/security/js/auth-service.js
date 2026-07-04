class AuthService {
  constructor(apiClient) {
    this.api = apiClient;
  }

  async login(email, password) {
    return this.api.post('/security/login/', {
      username: email,
      password: password,
    });
  }

  async logout() {
    return this.api.post('/security/logout/');
  }
}
