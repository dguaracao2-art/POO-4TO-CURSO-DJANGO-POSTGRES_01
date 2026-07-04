(function () {
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const api = new ApiClient();
  const auth = new AuthService(api);

  const els = {
    form: document.getElementById('loginForm'),
    email: document.getElementById('loginEmail'),
    password: document.getElementById('loginPassword'),
    submit: document.getElementById('loginSubmit'),
    error: document.getElementById('loginError'),
    toggle: document.getElementById('passwordToggle'),
  };

  function showError(msg) {
    els.error.textContent = msg;
    els.error.classList.remove('d-none');
    els.error.setAttribute('role', 'alert');
  }

  function clearError() {
    els.error.classList.add('d-none');
    els.error.textContent = '';
  }

  function setLoading(loading) {
    els.submit.disabled = loading;
    els.submit.classList.toggle('skeleton-btn', loading);
    els.submit.innerHTML = loading
      ? 'Ingresando...'
      : '<i class="bi bi-box-arrow-in-right me-2"></i>Iniciar sesi\u00f3n';
  }

  function validate() {
    const email = els.email.value.trim();
    const password = els.password.value;

    if (!email) { showError('El correo electr\u00f3nico es requerido'); els.email.focus(); return false; }
    if (!EMAIL_REGEX.test(email)) { showError('Ingrese un correo electr\u00f3nico v\u00e1lido'); els.email.focus(); return false; }
    if (!password) { showError('La contrase\u00f1a es requerida'); els.password.focus(); return false; }
    if (password.length < 4) { showError('La contrase\u00f1a debe tener al menos 4 caracteres'); els.password.focus(); return false; }

    return true;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    if (!validate()) return;

    setLoading(true);
    try {
      const result = await auth.login(els.email.value.trim(), els.password.value);
      if (result.resp) {
        window.location.href = '/';
      } else {
        showError(result.error || 'Credenciales incorrectas');
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function togglePassword() {
    const isPassword = els.password.type === 'password';
    els.password.type = isPassword ? 'text' : 'password';
    const icon = els.toggle.querySelector('i');
    icon.classList.toggle('bi-eye');
    icon.classList.toggle('bi-eye-slash');
  }

  els.form.addEventListener('submit', handleSubmit);
  els.toggle.addEventListener('click', togglePassword);
  els.email.addEventListener('input', clearError);
  els.password.addEventListener('input', clearError);

  els.email.focus();
})();
