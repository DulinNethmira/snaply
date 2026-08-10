<script lang="ts">
  import { login, register } from '$lib/api';

  let { onLogin }: { onLogin: () => void } = $props();

  let mode = $state<'login' | 'register'>('login');
  let email = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleSubmit(e: Event) {
      e.preventDefault();
      error = '';
      loading = true;

      try {
          if (mode === 'register') {
              await register(email, password);
              // Auto-login after register
              await login(email, password);
              onLogin();
          } else {
              await login(email, password);
              onLogin();
          }
      } catch (err: any) {
          error = err.message || 'Authentication failed';
      } finally {
          loading = false;
      }
  }
</script>

<div class="auth-container">
  <div class="auth-card">
    <div class="logo">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
      <h1>Snaply</h1>
    </div>
    
    <h2>{mode === 'login' ? 'Welcome back' : 'Create an account'}</h2>
    <p class="subtitle">{mode === 'login' ? 'Sign in to access your shares' : 'Get started with Snaply'}</p>

    <form onsubmit={handleSubmit}>
      {#if error}
        <div class="error-msg">{error}</div>
      {/if}

      <div class="input-group">
        <label for="email">Email</label>
        <input type="email" id="email" bind:value={email} required placeholder="you@example.com" />
      </div>

      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" id="password" bind:value={password} required placeholder="••••••••" />
      </div>

      <button type="submit" class="btn-primary" disabled={loading}>
        {loading ? 'Processing...' : (mode === 'login' ? 'Sign In' : 'Sign Up')}
      </button>
    </form>

    <div class="toggle-mode">
      {#if mode === 'login'}
        Don't have an account? <button class="btn-link" onclick={() => mode = 'register'}>Sign up</button>
      {:else}
        Already have an account? <button class="btn-link" onclick={() => mode = 'login'}>Sign in</button>
      {/if}
    </div>
  </div>
</div>

<style>
  .auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: var(--bg-primary);
  }

  .auth-card {
    background-color: var(--surface-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    color: var(--accent-primary);
    margin-bottom: var(--space-6);
  }

  .logo h1 {
    font-size: var(--font-xl);
    font-weight: 700;
    margin: 0;
    color: var(--text-primary);
  }

  h2 {
    margin: 0 0 var(--space-1);
    font-size: var(--font-lg);
  }

  .subtitle {
    color: var(--text-secondary);
    font-size: var(--font-sm);
    margin-bottom: var(--space-6);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  label {
    font-size: var(--font-xs);
    font-weight: 500;
    color: var(--text-secondary);
  }

  input {
    background-color: var(--surface-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-3);
    color: var(--text-primary);
    font-size: var(--font-sm);
    transition: all 0.2s;
  }

  input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px rgba(124, 109, 247, 0.2);
  }

  .btn-primary {
    background-color: var(--accent-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: var(--space-3);
    font-size: var(--font-sm);
    font-weight: 500;
    cursor: pointer;
    margin-top: var(--space-2);
    transition: background-color 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }
  
  .btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .error-msg {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    padding: var(--space-3);
    border-radius: var(--radius-md);
    font-size: var(--font-sm);
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  .toggle-mode {
    margin-top: var(--space-6);
    text-align: center;
    font-size: var(--font-sm);
    color: var(--text-secondary);
  }

  .btn-link {
    background: none;
    border: none;
    color: var(--accent-primary);
    cursor: pointer;
    font-weight: 500;
    padding: 0;
  }

  .btn-link:hover {
    text-decoration: underline;
  }
</style>
