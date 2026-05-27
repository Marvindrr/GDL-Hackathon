// Estado de la aplicación
let state = {
    activeSection: 'mapa',
    isStreaming: true,
    selectedCamera: 'cam-001',
    showEscapeAlert: false,
    calculatingRoute: false
};

// Datos de las cámaras
const cameras = {
    'cam-001': { name: 'Entrada Principal', status: 'online' },
    'cam-002': { name: 'Estacionamiento A', status: 'online' },
    'cam-003': { name: 'Perímetro Norte', status: 'online' },
    'cam-004': { name: 'Salida Sur', status: 'offline' }
};

// Títulos de secciones
const sectionTitles = {
    'mapa': 'Mapa Principal',
    'zonas': 'Zonas de Riesgo',
    'graficas': 'Gráficas',
    'reportes': 'Reportes',
    'camaras': 'Cámaras'
};

// Elementos del DOM
const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    sectionTitle: document.getElementById('sectionTitle'),
    calculateRouteBtn: document.getElementById('calculateRouteBtn'),
    routeIcon: document.getElementById('routeIcon'),
    routeBtnText: document.getElementById('routeBtnText'),
    routePath: document.getElementById('routePath'),
    cameraSelect: document.getElementById('cameraSelect'),
    streamToggleBtn: document.getElementById('streamToggleBtn'),
    streamIcon: document.getElementById('streamIcon'),
    streamBtnText: document.getElementById('streamBtnText'),
    liveIndicator: document.getElementById('liveIndicator'),
    cameraFeed: document.getElementById('cameraFeed'),
    cameraOffline: document.getElementById('cameraOffline'),
    cameraInfo: document.getElementById('cameraInfo'),
    cameraName: document.getElementById('cameraName'),
    cameraInfoName: document.getElementById('cameraInfoName'),
    escapeAlert: document.getElementById('escapeAlert'),
    escapeCloseBtn: document.getElementById('escapeCloseBtn')
};

// Inicialización
function init() {
    setupEventListeners();
    updateCameraDisplay();
}

// Configurar event listeners
function setupEventListeners() {
    // Navegación del sidebar
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            handleSectionChange(section);
        });
    });

    // Botón calcular ruta
    elements.calculateRouteBtn.addEventListener('click', handleCalculateRoute);

    // Selector de cámara
    elements.cameraSelect.addEventListener('change', (e) => {
        state.selectedCamera = e.target.value;
        updateCameraDisplay();
    });

    // Botón de stream
    elements.streamToggleBtn.addEventListener('click', toggleStream);

    // Cerrar alerta de escape
    elements.escapeCloseBtn.addEventListener('click', () => {
        state.showEscapeAlert = false;
        updateEscapeAlert();
    });
}

// Cambiar sección activa
function handleSectionChange(section) {
    state.activeSection = section;

    // Actualizar navegación
    elements.navItems.forEach(item => {
        if (item.dataset.section === section) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Actualizar título
    elements.sectionTitle.textContent = `Panel de Control - ${sectionTitles[section]}`;
}

// Calcular ruta de escape
function handleCalculateRoute() {
    if (state.calculatingRoute) return;

    state.calculatingRoute = true;
    updateRouteButton();

    // Mostrar ruta en el mapa
    elements.routePath.style.display = 'block';
    elements.routePath.classList.add('calculating');

    // Simular cálculo
    setTimeout(() => {
        state.calculatingRoute = false;
        state.showEscapeAlert = true;
        updateRouteButton();
        updateEscapeAlert();
        elements.routePath.classList.remove('calculating');
    }, 2000);
}

// Actualizar botón de ruta
function updateRouteButton() {
    if (state.calculatingRoute) {
        elements.routeIcon.classList.add('calculating');
        elements.routeBtnText.textContent = 'Calculando...';
        elements.calculateRouteBtn.disabled = true;
    } else {
        elements.routeIcon.classList.remove('calculating');
        elements.routeBtnText.textContent = 'Calcular Ruta de Escape';
        elements.calculateRouteBtn.disabled = false;
    }
}

// Actualizar alerta de escape
function updateEscapeAlert() {
    if (state.showEscapeAlert) {
        elements.escapeAlert.style.display = 'block';
        elements.routePath.style.display = 'block';
    } else {
        elements.escapeAlert.style.display = 'none';
        elements.routePath.style.display = 'none';
    }
}

// Toggle stream de cámara
function toggleStream() {
    state.isStreaming = !state.isStreaming;
    updateStreamButton();
    updateCameraDisplay();
}

// Actualizar botón de stream
function updateStreamButton() {
    if (state.isStreaming) {
        // Mostrar botón de detener
        elements.streamToggleBtn.className = 'stream-btn stream-stop';
        elements.streamIcon.innerHTML = `
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
        `;
        elements.streamBtnText.textContent = 'Detener';
    } else {
        // Mostrar botón de iniciar
        elements.streamToggleBtn.className = 'stream-btn stream-start';
        elements.streamIcon.innerHTML = `
            <polygon points="5 3 19 12 5 21 5 3"/>
        `;
        elements.streamBtnText.textContent = 'Iniciar';
    }
}

// Actualizar display de cámara
function updateCameraDisplay() {
    const camera = cameras[state.selectedCamera];

    // Actualizar nombre de cámara
    elements.cameraName.textContent = camera.name;
    elements.cameraInfoName.textContent = camera.name;

    // Mostrar/ocultar elementos según estado
    if (state.isStreaming && camera.status === 'online') {
        elements.liveIndicator.style.display = 'flex';
        elements.cameraFeed.style.display = 'flex';
        elements.cameraOffline.style.display = 'none';
        elements.cameraInfo.style.display = 'block';
    } else {
        elements.liveIndicator.style.display = 'none';
        elements.cameraFeed.style.display = 'none';
        elements.cameraOffline.style.display = 'flex';
        elements.cameraInfo.style.display = 'none';
    }
}

// Iniciar aplicación cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
