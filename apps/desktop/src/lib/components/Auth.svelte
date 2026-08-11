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
        await login(email, password);
      } else {
        await login(email, password);
      }
      onLogin();
    } catch (err: any) {
      error = err.message || 'Authentication failed';
    } finally {
      loading = false;
    }
  }

  function switchMode(nextMode: 'login' | 'register') {
    mode = nextMode;
    error = '';
  }
</script>

<div class="auth-shell">
  <section class="auth-panel" aria-label="Snaply authentication">
    <div class="brand-row">
      <img class="mark" src="/snaply-logo.png" alt="" />
      <div>
        <p class="eyebrow">Snaply</p>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1>
      </div>
    </div>

    <div class="mode-switch" aria-label="Authentication mode">
      <button
        type="button"
        class:active={mode === 'login'}
        aria-pressed={mode === 'login'}
        onclick={() => switchMode('login')}
      >
        Sign in
      </button>
      <button
        type="button"
        class:active={mode === 'register'}
        aria-pressed={mode === 'register'}
        onclick={() => switchMode('register')}
      >
        Sign up
      </button>
    </div>

    <form onsubmit={handleSubmit}>
      {#if error}
        <div class="error-msg" role="alert">{error}</div>
      {/if}

      <label class="field">
        <span>Email</span>
        <input
          type="email"
          bind:value={email}
          required
          autocomplete="email"
          placeholder="you@example.com"
        />
      </label>

      <label class="field">
        <span>Password</span>
        <input
          type="password"
          bind:value={password}
          required
          autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
          placeholder="Enter your password"
        />
      </label>

      <button type="submit" class="primary-action" disabled={loading}>
        {#if loading}
          <span class="spinner" aria-hidden="true"></span>
          <span>{mode === 'login' ? 'Signing in' : 'Creating account'}</span>
        {:else}
          <span>{mode === 'login' ? 'Sign in to Snaply' : 'Create account'}</span>
        {/if}
      </button>
    </form>

    <p class="footer-copy">
      {mode === 'login' ? 'New to Snaply?' : 'Already have an account?'}
      <button
        type="button"
        onclick={() => switchMode(mode === 'login' ? 'register' : 'login')}
      >
        {mode === 'login' ? 'Create account' : 'Sign in'}
      </button>
    </p>
  </section>
</div>

<style>
  .auth-shell {
    position: relative;
    display: grid;
    min-height: 100vh;
    place-items: center;
    overflow: hidden;
    padding: var(--space-8);
    background:
      linear-gradient(135deg, var(--snaply-cyan-muted), transparent 34%),
      linear-gradient(225deg, var(--snaply-yellow-muted), transparent 30%),
      var(--bg);
  }

  .auth-shell::before {
    position: absolute;
    inset: 0;
    content: '';
    background-image:
      linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.85), transparent);
    pointer-events: none;
  }

  .auth-panel {
    position: relative;
    width: min(100%, 420px);
    padding: var(--space-8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    background: rgba(18, 23, 34, 0.78);
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.42), 0 0 0 1px var(--snaply-cyan-muted);
    backdrop-filter: blur(18px);
    animation: panel-enter 320ms ease both;
  }

  .brand-row {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
  }

  .mark {
    width: 48px;
    height: 48px;
    flex: 0 0 auto;
    object-fit: contain;
    filter: drop-shadow(0 0 14px var(--snaply-cyan-glow));
  }

  .eyebrow {
    margin: 0 0 var(--space-1);
    color: var(--accent-hover);
    font-size: var(--text-xs);
    font-weight: var(--weight-semibold);
    text-transform: uppercase;
  }

  h1 {
    margin: 0;
    font-size: var(--text-2xl);
  }

  .mode-switch {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-1);
    padding: var(--space-1);
    margin-bottom: var(--space-6);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: rgba(8, 10, 15, 0.62);
  }

  .mode-switch button {
    min-height: 38px;
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: var(--text-sm);
    font-weight: var(--weight-semibold);
    transition: background var(--transition-normal), color var(--transition-normal), transform var(--transition-fast);
  }

  .mode-switch button.active {
    color: var(--text);
    background: var(--elevated);
    box-shadow: var(--shadow-sm);
  }

  form {
    display: grid;
    gap: var(--space-4);
  }

  .field {
    display: grid;
    gap: var(--space-2);
    color: var(--text-secondary);
    font-size: var(--text-xs);
    font-weight: var(--weight-medium);
  }

  .field input {
    height: 44px;
    border-color: rgba(255, 255, 255, 0.1);
    background: rgba(8, 10, 15, 0.7);
    font-size: var(--text-md);
  }

  .field input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--snaply-cyan-glow);
  }

  .primary-action {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    height: 44px;
    margin-top: var(--space-2);
    border-radius: var(--radius-lg);
    color: white;
    background: linear-gradient(135deg, var(--snaply-cyan), var(--snaply-cyan-active));
    font-size: var(--text-md);
    font-weight: var(--weight-semibold);
    box-shadow: 0 14px 30px var(--snaply-cyan-glow);
    transition: transform var(--transition-fast), box-shadow var(--transition-normal), opacity var(--transition-fast);
  }

  .primary-action:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 18px 36px var(--snaply-cyan-glow);
  }

  .primary-action:active:not(:disabled),
  .mode-switch button:active {
    transform: scale(0.98);
  }

  .primary-action:disabled {
    cursor: wait;
    opacity: 0.72;
  }

  .spinner {
    width: 15px;
    height: 15px;
    border: 2px solid rgba(255, 255, 255, 0.34);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 780ms linear infinite;
  }

  .error-msg {
    padding: var(--space-3);
    border: 1px solid rgba(248, 113, 113, 0.24);
    border-radius: var(--radius-lg);
    color: var(--error);
    background: rgba(248, 113, 113, 0.1);
    font-size: var(--text-sm);
    animation: error-enter 180ms ease both;
  }

  .footer-copy {
    margin-top: var(--space-6);
    color: var(--text-secondary);
    font-size: var(--text-sm);
    text-align: center;
  }

  .footer-copy button {
    color: var(--accent-hover);
    font-weight: var(--weight-semibold);
  }

  .footer-copy button:hover {
    color: var(--text);
  }

  @keyframes panel-enter {
    from {
      opacity: 0;
      transform: translateY(12px) scale(0.985);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  @keyframes error-enter {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 520px) {
    .auth-shell {
      padding: var(--space-4);
    }

    .auth-panel {
      padding: var(--space-6);
    }
  }
</style>
