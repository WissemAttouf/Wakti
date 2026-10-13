/* =====================================================================
   Wakti — Gestion des notifications push
===================================================================== */

let VAPID_PUBLIC_KEY = null;

async function fetchVapidPublicKey() {
  if (VAPID_PUBLIC_KEY) return VAPID_PUBLIC_KEY;
  try {
    const res = await fetch('/api/vapid-public-key');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const json = await res.json();
    VAPID_PUBLIC_KEY = json.key;
    return VAPID_PUBLIC_KEY;
  } catch (e) {
    console.error('[Push] Impossible de recuperer la cle VAPID :', e);
    return null;
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; ++i) out[i] = raw.charCodeAt(i);
  return out;
}

function pushSupported() {
  return (
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  );
}

async function savePushSubscription(subscription, meta) {
  try {
    const res = await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subscription, meta })
    });
    return res.ok;
  } catch (e) {
    console.warn('Impossible d\'enregistrer l\'abonnement :', e);
    return false;
  }
}

async function removePushSubscription() {
  try {
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    if (!sub) return true;
    await fetch('/api/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: sub.endpoint })
    });
    await sub.unsubscribe();
    return true;
  } catch (e) {
    console.warn('Erreur lors du desabonnement :', e);
    return false;
  }
}

async function enablePushNotifications(meta) {
  meta = meta || {};
  if (!pushSupported()) return { ok: false, reason: 'unsupported' };

  if (Notification.permission === 'denied') return { ok: false, reason: 'denied' };
  if (Notification.permission === 'default') {
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') return { ok: false, reason: 'denied' };
  }

  const reg = await navigator.serviceWorker.ready;
  let sub = await reg.pushManager.getSubscription();

  if (!sub) {
    const vapidKey = await fetchVapidPublicKey();
    if (!vapidKey) return { ok: false, reason: 'vapid_unavailable' };
    try {
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey)
      });
    } catch (e) {
      console.warn('Erreur souscription push :', e);
      return { ok: false, reason: 'subscribe_failed' };
    }
  }

  const ok = await savePushSubscription(sub, {
    city: meta.city || null,
    country: meta.country || null,
    method: meta.method || 'auto',
    school: meta.school || '0',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    lang: document.documentElement.lang || 'fr',
    app: 'wakti'
  });

  if (!ok) return { ok: false, reason: 'server_failed' };
  return { ok: true };
}

async function disablePushNotifications() {
  const ok = await removePushSubscription();
  return { ok };
}

async function syncPushConfig(meta) {
  try {
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    if (!sub) return false;
    await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subscription: sub, meta: meta || {} })
    });
    return true;
  } catch (e) {
    return false;
  }
}

window.WaktiPush = {
  supported: pushSupported,
  enable: enablePushNotifications,
  disable: disablePushNotifications,
  sync: syncPushConfig,
  permission: () => (('Notification' in window) ? Notification.permission : 'unsupported')
};