/* ============================================================
   HogarFix — Onboarding Tour
   Guia interactiva paso a paso para nuevos usuarios.
   Soporta roles: cliente | tecnico
   ============================================================ */
(function () {
  'use strict';

  /* ── Config ──────────────────────────────────────────────── */
  var STORAGE_KEY_CLIENT = 'hf_tour_done_cliente';
  var STORAGE_KEY_TECH   = 'hf_tour_done_tecnico';
  var ANIM_MS = 240;

  /* ── Steps por rol ───────────────────────────────────────── */
  var STEPS = {
    cliente: [
      {
        target: '.hf-dash-hero',
        title: 'Bienvenido a HogarFix',
        body: 'Este es tu panel personal. Desde aqui controlas todo: tus reservas, el estado de cada servicio y tu perfil.',
        position: 'bottom',
      },
      {
        target: '[data-tour="nueva-reserva"]',
        title: 'Reservar un servicio',
        body: 'Haz clic en "+ Nueva reserva" para buscar tecnicos disponibles en tu zona y agendar en segundos.',
        position: 'bottom',
      },
      {
        target: '[data-tour="kpis"]',
        title: 'Resumen de tu actividad',
        body: 'Aqui ves de un vistazo cuantas reservas tienes: pendientes, confirmadas y canceladas.',
        position: 'bottom',
      },
      {
        target: '[data-tour="historial"]',
        title: 'Historial de reservas',
        body: 'Encuentra el detalle de cada servicio, su estado y las opciones de cancelacion o calificacion.',
        position: 'top',
      },
      {
        target: '[data-tour="nav-perfil"]',
        title: 'Tu perfil',
        body: 'Desde aqui editas tus datos, configuras notificaciones y activas la verificacion en dos pasos.',
        position: 'bottom',
      },
    ],
    tecnico: [
      {
        target: '.hf-dash-hero',
        title: 'Bienvenido a tu panel tecnico',
        body: 'Desde aqui gestionas todas las solicitudes que recibas, controlas tu agenda y editas tu perfil profesional.',
        position: 'bottom',
      },
      {
        target: '[data-tour="kpis"]',
        title: 'Estado de tus solicitudes',
        body: 'Ve de un vistazo cuantas solicitudes tienes pendientes, cuantas aceptaste y cuantas cancelaste.',
        position: 'bottom',
      },
      {
        target: '[data-tour="solicitudes"]',
        title: 'Solicitudes de clientes',
        body: 'Cada tarjeta es una solicitud de un cliente. Puedes aceptar o rechazar con un solo clic.',
        position: 'top',
      },
      {
        target: '[data-tour="btn-perfil"]',
        title: 'Editar tu perfil',
        body: 'Mantener tu perfil completo y actualizado aumenta tus posibilidades de recibir mas solicitudes.',
        position: 'bottom',
      },
      {
        target: '[data-tour="btn-disponibilidad"]',
        title: 'Tu disponibilidad',
        body: 'Indica los dias y horas en que puedes trabajar para que los clientes puedan agendarte correctamente.',
        position: 'bottom',
      },
    ],
  };

  /* ── State ───────────────────────────────────────────────── */
  var state = {
    role: null,
    steps: [],
    current: 0,
    active: false,
    overlay: null,
    spotlight: null,
    tooltip: null,
    backdrop: null,
  };

  /* ── Helpers ─────────────────────────────────────────────── */
  function storageKey() {
    return state.role === 'tecnico' ? STORAGE_KEY_TECH : STORAGE_KEY_CLIENT;
  }

  function isTourDone() {
    try { return !!localStorage.getItem(storageKey()); } catch (e) { return false; }
  }

  function markTourDone() {
    try { localStorage.setItem(storageKey(), '1'); } catch (e) {}
  }

  function clearTourDone() {
    try { localStorage.removeItem(storageKey()); } catch (e) {}
  }

  function el(selector) {
    return document.querySelector(selector);
  }

  function rect(element) {
    return element.getBoundingClientRect();
  }

  /* ── Build DOM ───────────────────────────────────────────── */
  function buildOverlay() {
    /* Dark overlay with transparent spotlight hole via CSS clip-path */
    var ov = document.createElement('div');
    ov.id = 'hf-tour-overlay';
    ov.setAttribute('role', 'presentation');
    ov.setAttribute('aria-hidden', 'true');

    var sp = document.createElement('div');
    sp.id = 'hf-tour-spotlight';

    document.body.appendChild(ov);
    document.body.appendChild(sp);

    state.overlay   = ov;
    state.spotlight = sp;
  }

  function buildTooltip() {
    var t = document.createElement('div');
    t.id = 'hf-tour-tooltip';
    t.setAttribute('role', 'dialog');
    t.setAttribute('aria-modal', 'true');
    t.setAttribute('aria-label', 'Tour interactivo HogarFix');
    t.innerHTML = [
      '<div class="hf-tour-header">',
        '<div class="hf-tour-progress" id="hf-tour-progress"></div>',
        '<button class="hf-tour-skip" id="hf-tour-skip" type="button" aria-label="Saltar recorrido">Saltar</button>',
      '</div>',
      '<h3 class="hf-tour-title" id="hf-tour-title"></h3>',
      '<p class="hf-tour-body" id="hf-tour-body"></p>',
      '<div class="hf-tour-actions">',
        '<button class="hf-tour-btn hf-tour-btn-ghost" id="hf-tour-prev" type="button">Anterior</button>',
        '<button class="hf-tour-btn hf-tour-btn-primary" id="hf-tour-next" type="button">Siguiente</button>',
      '</div>',
    ].join('');
    document.body.appendChild(t);
    state.tooltip = t;

    document.getElementById('hf-tour-prev').addEventListener('click', prev);
    document.getElementById('hf-tour-next').addEventListener('click', next);
    document.getElementById('hf-tour-skip').addEventListener('click', finish);
  }

  function buildBackdrop() {
    var b = document.createElement('div');
    b.id = 'hf-tour-backdrop';
    b.setAttribute('aria-hidden', 'true');
    b.addEventListener('click', function () { /* absorb clicks */ });
    document.body.appendChild(b);
    state.backdrop = b;
  }

  /* ── Positioning ─────────────────────────────────────────── */
  var PADDING = 10;

  function positionSpotlight(target) {
    var r = rect(target);
    var scrollY = window.scrollY || window.pageYOffset;
    var scrollX = window.scrollX || window.pageXOffset;

    state.spotlight.style.top    = (r.top  + scrollY - PADDING) + 'px';
    state.spotlight.style.left   = (r.left + scrollX - PADDING) + 'px';
    state.spotlight.style.width  = (r.width  + PADDING * 2) + 'px';
    state.spotlight.style.height = (r.height + PADDING * 2) + 'px';
  }

  function positionTooltip(target, position) {
    var r = rect(target);
    var tt = state.tooltip;
    var ttW = tt.offsetWidth  || 320;
    var ttH = tt.offsetHeight || 200;
    var scrollY = window.scrollY || window.pageYOffset;
    var scrollX = window.scrollX || window.pageXOffset;
    var vpW = window.innerWidth;
    var ARROW_GAP = 14;

    var top, left;

    if (position === 'top') {
      top  = r.top  + scrollY - ttH - ARROW_GAP;
      left = r.left + scrollX + r.width / 2 - ttW / 2;
    } else {
      top  = r.top  + scrollY + r.height + ARROW_GAP;
      left = r.left + scrollX + r.width  / 2 - ttW / 2;
    }

    /* Clamp horizontally */
    left = Math.max(12, Math.min(left, vpW - ttW - 12));
    /* Never above viewport */
    top = Math.max(scrollY + 10, top);

    tt.style.top  = top + 'px';
    tt.style.left = left + 'px';

    /* Arrow direction class */
    tt.classList.remove('hf-tour-arrow-top', 'hf-tour-arrow-bottom');
    tt.classList.add(position === 'top' ? 'hf-tour-arrow-bottom' : 'hf-tour-arrow-top');
  }

  /* ── Render step ─────────────────────────────────────────── */
  function renderStep(index) {
    var step = state.steps[index];
    var target = el(step.target) || el('.hf-dash-hero') || document.body;

    /* Scroll target into view */
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });

    window.setTimeout(function () {
      /* Spotlight */
      positionSpotlight(target);

      /* Tooltip content */
      document.getElementById('hf-tour-progress').textContent =
        'Paso ' + (index + 1) + ' de ' + state.steps.length;
      document.getElementById('hf-tour-title').textContent = step.title;
      document.getElementById('hf-tour-body').textContent  = step.body;

      var prevBtn = document.getElementById('hf-tour-prev');
      var nextBtn = document.getElementById('hf-tour-next');

      prevBtn.style.visibility = index === 0 ? 'hidden' : 'visible';

      if (index === state.steps.length - 1) {
        nextBtn.textContent = 'Finalizar';
        nextBtn.classList.add('hf-tour-btn-finish');
      } else {
        nextBtn.textContent = 'Siguiente';
        nextBtn.classList.remove('hf-tour-btn-finish');
      }

      state.tooltip.style.opacity = '0';
      state.tooltip.style.transform = 'translateY(8px)';

      positionTooltip(target, step.position || 'bottom');

      /* Animate in */
      requestAnimationFrame(function () {
        state.tooltip.style.transition = 'opacity ' + ANIM_MS + 'ms ease, transform ' + ANIM_MS + 'ms ease';
        state.tooltip.style.opacity   = '1';
        state.tooltip.style.transform = 'translateY(0)';
      });
    }, 300);
  }

  /* ── Tour controls ───────────────────────────────────────── */
  function start(role, forceRestart) {
    var steps = STEPS[role];
    if (!steps || !steps.length) return;

    if (!forceRestart && isTourDone()) return;

    state.role    = role;
    state.steps   = steps;
    state.current = 0;
    state.active  = true;

    document.body.classList.add('hf-tour-active');

    if (!state.overlay)  buildOverlay();
    if (!state.tooltip)  buildTooltip();
    if (!state.backdrop) buildBackdrop();

    state.overlay.style.display   = 'block';
    state.spotlight.style.display = 'block';
    state.tooltip.style.display   = 'block';
    state.backdrop.style.display  = 'block';

    /* Fade in */
    requestAnimationFrame(function () {
      state.overlay.classList.add('hf-tour-visible');
      state.backdrop.classList.add('hf-tour-visible');
    });

    renderStep(0);

    /* Reposition on resize */
    window.addEventListener('resize', onResize);
  }

  function next() {
    if (!state.active) return;
    if (state.current < state.steps.length - 1) {
      state.current++;
      renderStep(state.current);
    } else {
      finish();
    }
  }

  function prev() {
    if (!state.active || state.current === 0) return;
    state.current--;
    renderStep(state.current);
  }

  function finish() {
    if (!state.active) return;
    state.active = false;

    state.overlay.classList.remove('hf-tour-visible');
    state.backdrop.classList.remove('hf-tour-visible');
    state.tooltip.style.opacity = '0';

    window.setTimeout(function () {
      state.overlay.style.display   = 'none';
      state.spotlight.style.display = 'none';
      state.tooltip.style.display   = 'none';
      state.backdrop.style.display  = 'none';
      document.body.classList.remove('hf-tour-active');
    }, ANIM_MS);

    markTourDone();
    window.removeEventListener('resize', onResize);
  }

  function onResize() {
    if (!state.active) return;
    var step   = state.steps[state.current];
    var target = el(step.target) || el('.hf-dash-hero') || document.body;
    positionSpotlight(target);
    positionTooltip(target, step.position || 'bottom');
  }

  /* ── Auto-init ───────────────────────────────────────────── */
  function init() {
    var meta = document.getElementById('hf-tour-meta');
    if (!meta) return;

    var role = meta.getAttribute('data-role');
    var auto = meta.getAttribute('data-auto') === 'true';

    if (auto && role && !isTourDone()) {
      /* Small delay so page renders fully first */
      window.setTimeout(function () { start(role, false); }, 900);
    }
  }

  /* ── Public API ──────────────────────────────────────────── */
  window.HFTour = {
    start: start,
    restart: function (role) {
      clearTourDone();
      start(role, true);
    },
    finish: finish,
  };

  document.addEventListener('DOMContentLoaded', init);

})();
