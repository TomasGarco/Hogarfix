// Siempre mostrar el asistente al recargar
try {
  localStorage.removeItem('hf_mascot_hide_until');
} catch (e) {}

// Hacer scroll al inicio al recargar la página
window.addEventListener('DOMContentLoaded', function() {
  window.scrollTo({ top: 0, behavior: 'auto' });
});
console.log('Fixi cargado');

// Forzar que Fixi siempre aparezca, ignorando el localStorage de ocultar
try {
  localStorage.removeItem('hf_mascot_hide_until');
} catch (e) {}
/* ============================================================
  HogarFix — Help Center
  Menu flotante de ayuda + modal de guia rapida + tooltips.
  ============================================================ */
/* ── FAQ content por rol ─────────────────────────────────── */
var FAQ = {
    cliente: [
      {
        icon: 'bi-calendar-plus',
        q: 'Como reservo un servicio',
        a: 'Ve a "Buscar tecnico", elige el servicio y la localidad, selecciona un tecnico y confirma la fecha y hora.',
      },
      {
        icon: 'bi-x-circle',
        q: 'Como cancelo una reserva',
        a: 'En tu historial de reservas, haz clic en el boton "Cancelar" de la reserva. Puedes cancelar hasta 24 horas antes sin penalizacion.',
      },
      {
        icon: 'bi-person',
        q: 'Como edito mi perfil',
        a: 'Haz clic en tu nombre en la barra superior y selecciona "Perfil". Ahi puedes cambiar tus datos, foto y direccion.',
      },
      {
        icon: 'bi-chat',
        q: 'Como contacto al tecnico',
        a: 'Una vez confirmada la reserva, los datos del tecnico aparecen en el detalle de la reserva para que puedas contactarlo directamente.',
      },
      {
        icon: 'bi-shield-check',
        q: 'Mis datos estan seguros',
        a: 'Si. Usamos cifrado HTTPS, contrasenas protegidas y verificacion en dos pasos. Tu informacion nunca se vende a terceros.',
      },
    ],
    tecnico: [
      {
        icon: 'bi-check-circle',
        q: 'Como acepto una solicitud',
        a: 'En tu panel principal, cada solicitud tiene un boton "Aceptar". Confirma y el cliente recibe una notificacion automatica.',
      },
      {
        icon: 'bi-calendar-week',
        q: 'Como gestiono mi disponibilidad',
        a: 'Ve a "Disponibilidad" desde tu panel o perfil. Agrega los bloques de tiempo en que puedes trabajar.',
      },
      {
        icon: 'bi-person-vcard',
        q: 'Como completo mi verificacion',
        a: 'En "Editar perfil" sube la foto de tu cedula (frente y atras) y una selfie. El equipo HogarFix revisara en 24-48 horas.',
      },
      {
        icon: 'bi-star',
        q: 'Como mejoro mi perfil',
        a: 'Agrega fotos de trabajos realizados, escribe una buena descripcion y acumula calificaciones positivas de clientes.',
      },
      {
        icon: 'bi-question-circle',
        q: 'Que pasa si rechazo una solicitud',
        a: 'Puedes rechazar solicitudes que no puedas atender. Rechazos frecuentes sin justificacion pueden afectar tu visibilidad.',
      },
    ],
  };

/* ── State ───────────────────────────────────────────────── */
var role = null;
var panelOpen = false;
var dismissMenuOpen = false;
var modalOpen = false;
var hasTourContext = false;

var MASCOT_HIDE_UNTIL_KEY = 'hf_mascot_hide_until';

/* ── Build help button & menu ────────────────────────────── */
function buildMascotWidget() {
  var meta = document.getElementById('hf-tour-meta');
  role = meta ? meta.getAttribute('data-role') : 'cliente';
  hasTourContext = !!meta;

  var shell = document.createElement('div');
  shell.id = 'hfMascotShell';
  shell.className = 'hf-mascot-shell';
  shell.innerHTML = [
    '<button class="hf-mascot-toggle" id="hfMascotToggle" type="button" aria-expanded="false" aria-controls="hfMascotPanel" aria-label="Abrir asistente HogarFix">',
      '<img src="/static/img/mascota-fixi.png" alt="Mascota Fixi" class="hf-mascot-emoji">',
    '</button>',
    '<div class="hf-mascot-panel hf-mascot-panel-chat" id="hfMascotPanel" aria-hidden="true">',
      '<div class="hf-mascot-chat-head" style="display:flex;align-items:center;justify-content:space-between;gap:8px;">',
        '<span class="hf-mascot-chat-title" style="font-weight:600;font-size:1.1em;">Asistente HogarFix</span>',
        '<button class="hf-mascot-close" id="hfMascotClose" type="button" aria-label="Cerrar panel">&times;</button>',
      '</div>',
      '<div class="hf-mascot-chat-body">',
        '<div class="hf-mascot-chat-msg">Hola, soy el asistente virtual de HogarFix. Te ayudo con registro, reservas, tecnicos y seguridad.</div>',
        '<div class="hf-mascot-chat-quick">',
          '<button class="hf-assistant-chip">Como me registro</button>',
          '<button class="hf-assistant-chip">Como reservo</button>',
          '<button class="hf-assistant-chip">Ser tecnico</button>',
          '<button class="hf-assistant-chip">Seguridad</button>',
        '</div>',
      '</div>',
      '<form class="hf-mascot-chat-form" id="hfMascotChatForm">',
        '<input class="hf-mascot-chat-input" id="hfMascotChatInput" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" />',
        '<button class="hf-mascot-chat-send" type="submit">Enviar</button>',
      '</form>',
    '</div>',
  ].join('');

  // Permitir enviar con Enter y mostrar mensajes
  var chatForm = shell.querySelector('#hfMascotChatForm');
  var chatInput = shell.querySelector('#hfMascotChatInput');
  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var msg = chatInput.value.trim();
      if (msg) {
        var chatBody = shell.querySelector('.hf-mascot-chat-body');
        if (chatBody) {
          var userMsg = document.createElement('div');
          userMsg.className = 'hf-mascot-chat-msg hf-mascot-chat-msg-user';
          userMsg.textContent = msg;
          chatBody.appendChild(userMsg);
          chatBody.scrollTop = chatBody.scrollHeight;
        }
        sendToFixi(msg);
        chatInput.value = '';
      }
    });
  }

  // Botones rápidos usan la misma lógica conversacional
  var quickBtns = shell.querySelectorAll('.hf-assistant-chip');
  if (quickBtns) {
    quickBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var msg = btn.textContent.trim();
        var chatBody = shell.querySelector('.hf-mascot-chat-body');
        if (chatBody) {
          var userMsg = document.createElement('div');
          userMsg.className = 'hf-mascot-chat-msg hf-mascot-chat-msg-user';
          userMsg.textContent = msg;
          chatBody.appendChild(userMsg);
          chatBody.scrollTop = chatBody.scrollHeight;
        }
        sendToFixi(msg);
      });
    });
  }

/* ── Fixi WebSocket ─────────────────────────────────────── */
var fixiSocket = null;
var _fixiPendingTimer = null;

function _fixiFormatText(text) {
  // Escapar HTML para evitar XSS
  var escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
  // Convertir viñetas "- texto" en elementos de lista
  var lines = escaped.split('\n');
  var result = [];
  var inList = false;
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line.startsWith('- ')) {
      if (!inList) { result.push('<ul class="hf-fixi-list">'); inList = true; }
      result.push('<li>' + line.slice(2) + '</li>');
    } else {
      if (inList) { result.push('</ul>'); inList = false; }
      if (line) result.push('<p class="hf-fixi-p">' + line + '</p>');
    }
  }
  if (inList) result.push('</ul>');
  return result.join('');
}

function _fixiShowMsg(text) {
  var typing = document.getElementById('hfFixiTyping');
  if (typing) typing.remove();
  var chatBody = document.querySelector('.hf-mascot-chat-body');
  if (!chatBody) return;
  var botMsg = document.createElement('div');
  botMsg.className = 'hf-mascot-chat-msg';
  botMsg.innerHTML = _fixiFormatText(text);
  chatBody.appendChild(botMsg);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function initFixiSocket() {
  try {
    fixiSocket = io({ transports: ['polling', 'websocket'] });
    fixiSocket.on('connect', function() {
      console.log('[Fixi] Socket conectado, id:', fixiSocket.id);
    });
    fixiSocket.on('fixi_response', function(data) {
      if (_fixiPendingTimer) { clearTimeout(_fixiPendingTimer); _fixiPendingTimer = null; }
      _fixiShowMsg(data.message || 'Ocurrió un error, intenta de nuevo.');
    });
    fixiSocket.on('connect_error', function(err) {
      console.warn('[Fixi] Error de conexión:', err.message);
    });
  } catch(e) {
    console.warn('[Fixi] No se pudo inicializar socket:', e);
    fixiSocket = null;
  }
}

function sendToFixi(msg) {
  var chatBody = document.querySelector('.hf-mascot-chat-body');
  if (!chatBody) return;
  var typing = document.createElement('div');
  typing.className = 'hf-mascot-chat-msg hf-fixi-typing';
  typing.id = 'hfFixiTyping';
  typing.textContent = 'Fixi está escribiendo...';
  chatBody.appendChild(typing);
  chatBody.scrollTop = chatBody.scrollHeight;

  if (fixiSocket) {
    // Emitir y esperar respuesta; fallback a los 5s si no llega
    _fixiPendingTimer = setTimeout(function() {
      _fixiPendingTimer = null;
      _fixiShowMsg('Lo siento, no pude procesar tu consulta. Intenta de nuevo.');
    }, 15000);
    fixiSocket.emit('fixi_message', { message: msg });
  } else {
    setTimeout(function() {
      _fixiShowMsg('No hay conexión con Fixi en este momento. Intenta recargar la página.');
    }, 600);
  }
}

initFixiSocket();

  // Lógica para ocultar asistente por duración
  shell.querySelectorAll('.hf-mascot-hide-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var hours = parseInt(btn.getAttribute('data-hide-hours'), 10);
      var until = Date.now() + hours * 60 * 60 * 1000;
      localStorage.setItem('hf_mascot_hide_until', until);
      shell.style.display = 'none';
    });
  });

  document.body.appendChild(shell);

  var toggleBtn = document.getElementById('hfMascotToggle');
  var closeBtn = document.getElementById('hfMascotClose');
  var dismissMenu = document.getElementById('hfMascotDismissMenu');

  // Mostrar el panel al primer clic y limpiar el chat
  toggleBtn.addEventListener('click', function () {
    // Limpiar el chat antes de abrir
    var chatBody = shell.querySelector('.hf-mascot-chat-body');
    if (chatBody) {
      chatBody.innerHTML = '';
      // Mensaje de bienvenida y botones rápidos
      // Ya no agregamos el headerRow aquí para evitar el duplicado
      // Solo un mensaje de bienvenida, arriba
      var welcome = document.createElement('div');
      welcome.className = 'hf-mascot-chat-msg';
      welcome.textContent = 'Hola, soy el asistente virtual de HogarFix. Te ayudo con registro, reservas, tecnicos y seguridad.';
      chatBody.appendChild(welcome);
      // Asegurar scroll y barra visible
      chatBody.style.maxHeight = '320px';
      chatBody.style.overflowY = 'auto';
      var quick = document.createElement('div');
      quick.className = 'hf-mascot-chat-quick';
      quick.innerHTML = [
        '<button class="hf-assistant-chip">Como me registro<\/button>',
        '<button class="hf-assistant-chip">Como reservo<\/button>',
        '<button class="hf-assistant-chip">Ser tecnico<\/button>',
        '<button class="hf-assistant-chip">Seguridad<\/button>'
      ].join('');
      chatBody.appendChild(quick);
      // Volver a enlazar eventos a los botones rápidos
      quick.querySelectorAll('.hf-assistant-chip').forEach(function(btn) {
        btn.addEventListener('click', function() {
          var msg = btn.textContent.trim();
          var userMsg = document.createElement('div');
          userMsg.className = 'hf-mascot-chat-msg hf-mascot-chat-msg-user';
          userMsg.textContent = msg;
          chatBody.appendChild(userMsg);
          chatBody.scrollTop = chatBody.scrollHeight;
          sendToFixi(msg);
        });
      });
    }
    openPanel();
  });

  // Mostrar menú de ocultar Fixi con click derecho o mantener presionado
  toggleBtn.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    toggleDismissMenu();
  });
  toggleBtn.addEventListener('mousedown', function (e) {
    if (e.button === 0) {
      // Mantener presionado para menú en móvil
      var pressTimer;
      var start = function () {
        pressTimer = window.setTimeout(function () {
          toggleDismissMenu();
        }, 600);
      };
      var cancel = function () {
        clearTimeout(pressTimer);
      };
      toggleBtn.addEventListener('touchstart', start);
      toggleBtn.addEventListener('touchend', cancel);
      toggleBtn.addEventListener('touchmove', cancel);
      toggleBtn.addEventListener('touchcancel', cancel);
    }
  });

  closeBtn.addEventListener('click', closePanel);

  if (dismissMenu) {
    dismissMenu.querySelectorAll('[data-hide-hours]').forEach(function (option) {
      option.addEventListener('click', function () {
        var hours = Number(option.getAttribute('data-hide-hours') || '0');
        if (hours > 0) {
          hideMascotForHours(hours);
          shell.remove();
        }
      });
    });

    dismissMenu.querySelectorAll('[data-hide-cancel]').forEach(function (option) {
      option.addEventListener('click', function () {
        closeDismissMenu();
      });
    });
  }

  shell.querySelectorAll('[data-hf-assistant]').forEach(function (actionBtn) {
    actionBtn.addEventListener('click', function () {
      var action = actionBtn.getAttribute('data-hf-assistant');
      if (action === 'tour') {
        if (hasTourContext && window.HFTour) {
          window.HFTour.restart(role);
        } else {
          appendBotMessage('El recorrido guiado esta disponible en los paneles de cliente y tecnico.');
        }
        closePanel();
        return;
      }

      if (action === 'guide' || action === 'faq') {
        closePanel();
        openModal(action);
      }
    });
  });

  document.addEventListener('click', function (e) {
    if (dismissMenuOpen && dismissMenu && !dismissMenu.contains(e.target) && !dismissBtn.contains(e.target)) {
      closeDismissMenu();
    }

    if (!panelOpen) {
      return;
    }
    if (!shell.contains(e.target)) {
      closePanel();
    }
  });
}

  function toggleDismissMenu() {
    if (dismissMenuOpen) {
      closeDismissMenu();
      return;
    }

    var dismissMenu = document.getElementById('hfMascotDismissMenu');
    if (!dismissMenu) return;
    dismissMenu.hidden = false;
    dismissMenuOpen = true;
  }

  function closeDismissMenu() {
    var dismissMenu = document.getElementById('hfMascotDismissMenu');
    if (!dismissMenu) return;
    dismissMenu.hidden = true;
    dismissMenuOpen = false;
  }

  function openPanel() {
    var panel = document.getElementById('hfMascotPanel');
    var shell = document.getElementById('hfMascotShell');
    var btn = document.getElementById('hfMascotToggle');
    if (!panel || !shell || !btn) return;
    panel.classList.add('is-open');
    panel.setAttribute('aria-hidden', 'false');
    shell.classList.add('is-open');
    btn.setAttribute('aria-expanded', 'true');
    panelOpen = true;
  }

  function closePanel() {
    var panel = document.getElementById('hfMascotPanel');
    var shell = document.getElementById('hfMascotShell');
    var btn = document.getElementById('hfMascotToggle');
    if (!panel || !shell || !btn) return;
    panel.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
    shell.classList.remove('is-open');
    btn.setAttribute('aria-expanded', 'false');
    panelOpen = false;
  }

  function appendBotMessage(message) {
    var chat = document.getElementById('hfAssistantChat');
    if (!chat) return;

    var item = document.createElement('div');
    item.className = 'hf-assistant-msg hf-assistant-msg-bot';
    item.textContent = message;
    chat.appendChild(item);
    chat.scrollTop = chat.scrollHeight;
  }

  function hideMascotForHours(hours) {
    var until = Date.now() + (hours * 60 * 60 * 1000);
    try {
      localStorage.setItem(MASCOT_HIDE_UNTIL_KEY, String(until));
    } catch (e) {
    }
  }

  function mascotIsHidden() {
    try {
      var until = Number(localStorage.getItem(MASCOT_HIDE_UNTIL_KEY) || '0');
      return until > Date.now();
    } catch (e) {
      return false;
    }
  }

  /* ── Modal ───────────────────────────────────────────────── */
  var GUIDE = {
    cliente: [
      { icon: 'bi-1-circle-fill', color: '#1d6fb8', title: 'Busca un tecnico', body: 'Haz clic en "+ Nueva reserva" o "Buscar tecnico". Filtra por tipo de servicio y localidad.' },
      { icon: 'bi-2-circle-fill', color: '#00a67c', title: 'Agenda la cita',   body: 'Elige la fecha y hora disponible del tecnico y confirma la reserva.' },
      { icon: 'bi-3-circle-fill', color: '#e07b00', title: 'Espera confirmacion', body: 'El tecnico acepta la solicitud. Recibiras una notificacion en tu correo y en el panel.' },
      { icon: 'bi-4-circle-fill', color: '#7e22ce', title: 'Califica el servicio', body: 'Cuando el servicio termine, deja una calificacion honesta para ayudar a otros usuarios.' },
    ],
    tecnico: [
      { icon: 'bi-1-circle-fill', color: '#1d6fb8', title: 'Completa tu perfil', body: 'Agrega foto, especialidades, descripcion y verifica tu identidad para aparecer en busquedas.' },
      { icon: 'bi-2-circle-fill', color: '#00a67c', title: 'Configura disponibilidad', body: 'Indica tus dias y horas disponibles para que los clientes puedan agendarte.' },
      { icon: 'bi-3-circle-fill', color: '#e07b00', title: 'Acepta solicitudes', body: 'Cuando llegue una solicitud, revisala y acepta o rechaza desde tu panel principal.' },
      { icon: 'bi-4-circle-fill', color: '#7e22ce', title: 'Entrega con calidad', body: 'Atiende puntual y con buen trabajo. Buenas calificaciones aumentan tu visibilidad.' },
    ],
  };

  function buildModal() {
    var m = document.createElement('div');
    m.id = 'hf-help-modal';
    m.setAttribute('role', 'dialog');
    m.setAttribute('aria-modal', 'true');
    m.setAttribute('aria-label', 'Centro de ayuda HogarFix');
    m.innerHTML = [
      '<div class="hf-help-modal-backdrop" id="hf-help-modal-backdrop"></div>',
      '<div class="hf-help-modal-panel" role="document">',
        '<div class="hf-help-modal-head">',
          '<div class="d-flex align-items-center gap-2">',
            '<span class="hf-tour-progress" id="hf-modal-tab-label">Guia rapida</span>',
          '</div>',
          '<button class="hf-help-modal-close" id="hf-help-modal-close" type="button" aria-label="Cerrar">',
            '<i class="bi bi-x-lg"></i>',
          '</button>',
        '</div>',
        '<div class="hf-help-modal-tabs">',
          '<button class="hf-help-tab active" data-view="guide" type="button">Guia rapida</button>',
          '<button class="hf-help-tab" data-view="faq" type="button">Preguntas frecuentes</button>',
        '</div>',
        '<div class="hf-help-modal-body" id="hf-help-modal-body"></div>',
      '</div>',
    ].join('');
    document.body.appendChild(m);

    document.getElementById('hf-help-modal-close').addEventListener('click', closeModal);
    document.getElementById('hf-help-modal-backdrop').addEventListener('click', closeModal);

    m.querySelectorAll('.hf-help-tab').forEach(function (tab) {
      tab.addEventListener('click', function () {
        m.querySelectorAll('.hf-help-tab').forEach(function (t) { t.classList.remove('active'); });
        this.classList.add('active');
        renderModalContent(this.getAttribute('data-view'));
      });
    });

    document.addEventListener('keydown', function (e) {
      if (modalOpen && e.key === 'Escape') closeModal();
    });
  }

  function renderModalContent(view) {
    var body = document.getElementById('hf-help-modal-body');
    if (!body) return;

    if (view === 'guide') {
      var steps = (GUIDE[role] || GUIDE.cliente);
      body.innerHTML = '<div class="hf-help-guide-grid">' +
        steps.map(function (s) {
          return [
            '<div class="hf-help-guide-card">',
              '<i class="bi ' + s.icon + ' hf-help-guide-num" style="color:' + s.color + '"></i>',
              '<div>',
                '<strong class="hf-help-guide-title">' + s.title + '</strong>',
                '<p class="hf-help-guide-body">' + s.body + '</p>',
              '</div>',
            '</div>',
          ].join('');
        }).join('') +
      '</div>';
    } else {
      var faqs = (FAQ[role] || FAQ.cliente);
      body.innerHTML = '<div class="hf-help-faq-list">' +
        faqs.map(function (f, i) {
          return [
            '<div class="hf-help-faq-item" id="hf-faq-' + i + '">',
              '<button class="hf-help-faq-q" type="button" aria-expanded="false" aria-controls="hf-faq-a-' + i + '">',
                '<i class="bi ' + f.icon + '"></i>',
                '<span>' + f.q + '</span>',
                '<i class="bi bi-chevron-down hf-faq-chevron"></i>',
              '</button>',
              '<div class="hf-help-faq-a" id="hf-faq-a-' + i + '" hidden>' + f.a + '</div>',
            '</div>',
          ].join('');
        }).join('') +
      '</div>';

      /* Accordion */
      body.querySelectorAll('.hf-help-faq-q').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var answer  = document.getElementById(this.getAttribute('aria-controls'));
          var chevron = this.querySelector('.hf-faq-chevron');
          var open    = this.getAttribute('aria-expanded') === 'true';
          this.setAttribute('aria-expanded', String(!open));
          answer.hidden = open;
          if (chevron) chevron.style.transform = open ? 'rotate(0deg)' : 'rotate(180deg)';
        });
      });
    }
  }

  function openModal(view) {
    var m = document.getElementById('hf-help-modal');
    if (!m) { buildModal(); }

    m = document.getElementById('hf-help-modal');
    modalOpen = true;
    m.classList.add('hf-help-modal-open');
    document.body.classList.add('hf-modal-lock');

    /* Set active tab */
    m.querySelectorAll('.hf-help-tab').forEach(function (t) {
      t.classList.toggle('active', t.getAttribute('data-view') === view);
    });
    renderModalContent(view);
  }

  function closeModal() {
    var m = document.getElementById('hf-help-modal');
    if (m) m.classList.remove('hf-help-modal-open');
    modalOpen = false;
    document.body.classList.remove('hf-modal-lock');
  }

  /* ── Tooltips inteligentes ───────────────────────────────── */
  function initTooltips() {
    var tips = document.querySelectorAll('[data-hf-tip]');
    tips.forEach(function (trigger) {
      // El sidebar tiene su propio sistema de tooltips — no duplicar
      if (trigger.closest('.hf-ts')) return;
      var tipEl = document.createElement('div');
      tipEl.className = 'hf-smart-tip';
      tipEl.textContent = trigger.getAttribute('data-hf-tip');
      document.body.appendChild(tipEl);

      function show() {
        var r = trigger.getBoundingClientRect();
        var scrollY = window.scrollY || window.pageYOffset;
        tipEl.style.top  = (r.bottom + scrollY + 8) + 'px';
        tipEl.style.left = (r.left + r.width / 2) + 'px';
        tipEl.classList.add('hf-smart-tip-visible');
      }

      function hide() {
        tipEl.classList.remove('hf-smart-tip-visible');
      }

      trigger.addEventListener('mouseenter', show);
      trigger.addEventListener('focus', show);
      trigger.addEventListener('mouseleave', hide);
      trigger.addEventListener('blur', hide);
    });
  }

  /* ── Init ────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('hfMascotShell')) {
      return;
    }
    buildMascotWidget();
    initTooltips();
  });

