/**
 * Integración de FullCalendar para el Sistema de Citas Médicas
 * Este archivo gestiona la visualización y funcionalidad del calendario con FullCalendar
 */

function initAppointmentCalendar(availableSlots) {
    // Variables globales
    let selectedDate = null;
    let selectedTime = null;
    let showOnlyAvailable = false;
    let calendarEvents = [];
    let calendar = null;
    
    // Elementos del DOM
    const calendarEl = document.getElementById('appointment-calendar');
    const calendarTitleEl = document.getElementById('calendar-title');
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const selectedDateEl = document.getElementById('selected-date');
    const appointmentSummary = document.getElementById('appointment-summary');
    const summaryDateEl = document.getElementById('summary-date');
    const summaryTimeEl = document.getElementById('summary-time');
    const submitBtn = document.getElementById('submit-booking');
    const hiddenDateInput = document.getElementById('id_date');
    const hiddenTimeInput = document.getElementById('id_time');
    
    // Botones de navegación y vista
    document.getElementById('prev-btn').addEventListener('click', () => calendar.prev());
    document.getElementById('today-btn').addEventListener('click', () => calendar.today());
    document.getElementById('next-btn').addEventListener('click', () => calendar.next());
    document.getElementById('month-view').addEventListener('click', () => changeView('dayGridMonth'));
    document.getElementById('week-view').addEventListener('click', () => changeView('timeGridWeek'));
    document.getElementById('day-view').addEventListener('click', () => changeView('timeGridDay'));
    document.getElementById('list-view').addEventListener('click', () => changeView('listWeek'));
    
    // Botones de filtrado
    document.getElementById('show-all-slots').addEventListener('click', () => toggleFilter(false));
    document.getElementById('show-available-slots').addEventListener('click', () => toggleFilter(true));
    
    // Inicializar el calendario y preparar los eventos
    initCalendar();
    
    /**
     * Cambia la vista actual del calendario
     * @param {string} viewName - Nombre de la vista a mostrar
     */
    function changeView(viewName) {
        calendar.changeView(viewName);
        updateViewButtons(viewName);
    }
    
    /**
     * Actualiza el estado de los botones de vista
     * @param {string} activeView - Vista actualmente activa
     */
    function updateViewButtons(activeView) {
        const views = ['month-view', 'week-view', 'day-view', 'list-view'];
        const viewMap = {
            'dayGridMonth': 'month-view',
            'timeGridWeek': 'week-view',
            'timeGridDay': 'day-view',
            'listWeek': 'list-view'
        };
        
        views.forEach(view => {
            document.getElementById(view).classList.remove('btn-primary');
            document.getElementById(view).classList.add('btn-outline-primary');
        });
        
        const activeButton = viewMap[activeView];
        if (activeButton) {
            document.getElementById(activeButton).classList.remove('btn-outline-primary');
            document.getElementById(activeButton).classList.add('btn-primary');
        }
    }
    
    /**
     * Inicializa el calendario FullCalendar
     */
    function initCalendar() {
        // Preparar eventos para el calendario
        prepareCalendarEvents();
        
        // Inicializar el calendario con configuración horizontal
        const calendarOptions = {
            initialView: 'dayGridMonth',
            selectable: true,
            navLinks: true,
            editable: false,
            dayMaxEvents: true,
            headerToolbar: false, // Usamos nuestra propia barra de herramientas
            locale: 'es',
            height: 'auto',
            firstDay: 1, // Iniciar semana en lunes
            dayHeaders: true,
            weekNumbers: false,
            fixedWeekCount: false,
            showNonCurrentDates: false,
            events: calendarEvents,
            slotDuration: '01:00:00', // Intervalos de 1 hora
            slotMinTime: '08:00:00',  // Hora de inicio
            slotMaxTime: '20:00:00',  // Hora de fin
            allDaySlot: false,       // No mostrar slot "todo el día"
            slotLabelFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            },
            // Configuración horizontal para las vistas
            dayHeaderFormat: { weekday: 'short', day: 'numeric' },
            dayHeaderContent: (args) => {
                const date = args.date;
                const day = date.getDate();
                const month = date.toLocaleString('es', { month: 'short' });
                return `${args.text.split(' ')[0]}<br>${day}/${month}`;
            },
            datesSet: function(info) {
                updateCalendarTitle(info.view);
            },
            dateClick: handleDateClick,
            eventClick: handleEventClick,
            eventClassNames: applyEventStyles
        };
        
        calendar = new FullCalendar.Calendar(calendarEl, calendarOptions);
        calendar.render();
        
        // Actualizar el título inicialmente
        updateCalendarTitle(calendar.view);
    }
    
    /**
     * Actualiza el título del calendario según la vista actual
     * @param {Object} view - Vista actual del calendario
     */
    function updateCalendarTitle(view) {
        const start = new Date(view.currentStart);
        let end;
        let title;
        
        if (view.type === 'dayGridMonth') {
            // Formato para vista mensual: "Julio 2025"
            title = start.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
            title = title.charAt(0).toUpperCase() + title.slice(1);
        } else if (view.type.includes('timeGrid')) {
            // Formato para vista semanal/diaria: "5 - 11 Jul 2025" o "5 Jul 2025"
            end = new Date(view.currentEnd);
            end.setDate(end.getDate() - 1);
            
            if (view.type === 'timeGridDay') {
                title = start.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
            } else {
                title = start.getDate() + ' - ' + end.getDate() + ' ' + 
                        start.toLocaleDateString('es-ES', { month: 'short' }) + ' ' + 
                        start.getFullYear();
            }
        } else {
            // Formato para vista de lista
            end = new Date(view.currentEnd);
            end.setDate(end.getDate() - 1);
            title = start.getDate() + ' ' + start.toLocaleDateString('es-ES', { month: 'short' }) + ' - ' + 
                    end.getDate() + ' ' + end.toLocaleDateString('es-ES', { month: 'short' }) + ' ' + 
                    start.getFullYear();
        }
        
        calendarTitleEl.textContent = title;
    }
    
    /**
     * Prepara los eventos para mostrar en el calendario
     */
    function prepareCalendarEvents() {
        calendarEvents = [];
        
        // Recorrer todos los slots disponibles y crear eventos
        for (const dateStr in availableSlots) {
            if (availableSlots.hasOwnProperty(dateStr)) {
                const dateData = availableSlots[dateStr];
                
                // Verificar si hay slots para esta fecha
                if (dateData.slots && dateData.slots.length > 0) {
                    // Para cada slot, crear un evento individual
                    dateData.slots.forEach(slot => {
                        // Obtener la hora del slot
                        const [hours, minutes] = slot.time.split(':').map(Number);
                        
                        // Crear fecha completa con hora
                        const startDate = new Date(dateStr);
                        startDate.setHours(hours, minutes, 0);
                        
                        // Calcular hora de fin (1 hora después)
                        const endDate = new Date(startDate);
                        endDate.setHours(endDate.getHours() + 1);
                        
                        // Crear evento para este slot específico
                        calendarEvents.push({
                            title: 'Disponible',
                            start: startDate,
                            end: endDate,
                            allDay: false,
                            availability: 'available',
                            slotData: slot,
                            display: 'block'
                        });
                    });
                }
                
                // También agregamos un evento para el día completo si no hay disponibilidad
                if (!dateData.slots || dateData.slots.length === 0) {
                    calendarEvents.push({
                        title: 'No disponible',
                        start: dateStr,
                        allDay: true,
                        availability: 'unavailable',
                        display: 'background'
                    });
                }
            }
        }
        
        // Si está activo el filtro de solo disponibles, filtrar los eventos
        if (showOnlyAvailable) {
            calendarEvents = calendarEvents.filter(event => event.availability === 'available');
        }
    }
    
    /**
     * Maneja el clic en una fecha del calendario
     * @param {Object} info - Información del evento de clic
     */
    function handleDateClick(info) {
        const dateStr = info.dateStr.split('T')[0]; // Extraer solo la fecha si tiene hora
        selectedDate = dateStr;
        
        // Mostrar fecha seleccionada
        const formattedDate = formatDateForDisplay(dateStr);
        selectedDateEl.textContent = formattedDate;
        
        // Mostrar slots disponibles para esta fecha
        displayTimeSlotsForDate(dateStr);
        
        // Deseleccionar cualquier slot previamente seleccionado
        deselectTimeSlot();
    }
    
    /**
     * Maneja el clic en un evento del calendario
     * @param {Object} info - Información del evento clickeado
     */
    function handleEventClick(info) {
        if (info.event.extendedProps.availability === 'unavailable') {
            return; // No hacer nada si el evento no está disponible
        }
        
        const dateStr = info.event.start.toISOString().split('T')[0];
        const timeSlot = info.event.extendedProps.slotData;
        selectedDate = dateStr;
        
        // Mostrar fecha seleccionada
        const formattedDate = formatDateForDisplay(dateStr);
        selectedDateEl.textContent = formattedDate;
        
        // Mostrar slots disponibles para esta fecha
        displayTimeSlotsForDate(dateStr);
        
        // Si es un evento específico con hora, seleccionar automáticamente ese slot
        if (timeSlot) {
            const buttons = document.querySelectorAll(`.time-slot-btn[data-timestamp="${timeSlot.timestamp}"]`);
            if (buttons.length > 0) {
                selectTimeSlot(buttons[0], dateStr, timeSlot.time, timeSlot.timestamp);
                buttons[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            // Deseleccionar cualquier slot previamente seleccionado
            deselectTimeSlot();
        }
    }
    
    /**
     * Aplica estilos personalizados a los eventos según su disponibilidad
     * @param {Object} info - Información del evento
     * @return {Array} - Clases CSS a aplicar
     */
    function applyEventStyles(info) {
        const availability = info.event.extendedProps.availability;
        return [
            'fc-event',
            `event-${availability}`
        ];
    }
    
    /**
     * Cambia el modo de filtrado del calendario
     * @param {boolean} onlyAvailable - Si debe mostrar solo horarios disponibles
     */
    function toggleFilter(onlyAvailable) {
        showOnlyAvailable = onlyAvailable;
        
        // Actualizar clases de los botones
        document.getElementById('show-all-slots').classList.toggle('active', !onlyAvailable);
        document.getElementById('show-available-slots').classList.toggle('active', onlyAvailable);
        
        // Reiniciar el calendario con el nuevo filtro
        calendarEvents = [];
        prepareCalendarEvents();
        
        // Remover y agregar eventos al calendario
        calendar.getEvents().forEach(event => event.remove());
        calendarEvents.forEach(event => calendar.addEvent(event));
        
        // Si hay una fecha seleccionada, actualizar los slots mostrados
        if (selectedDate) {
            displayTimeSlotsForDate(selectedDate);
        }
    }
    
    /**
     * Muestra los horarios disponibles para una fecha específica
     * @param {string} dateStr - Fecha en formato ISO (YYYY-MM-DD)
     */
    function displayTimeSlotsForDate(dateStr) {
        timeSlotsContainer.innerHTML = '';
        
        // Verificar si hay slots para esta fecha
        if (!availableSlots[dateStr] || !availableSlots[dateStr].slots || availableSlots[dateStr].slots.length === 0) {
            const noSlotsMsg = document.createElement('div');
            noSlotsMsg.className = 'no-slots-message';
            noSlotsMsg.textContent = 'No hay horarios disponibles para esta fecha';
            timeSlotsContainer.appendChild(noSlotsMsg);
            return;
        }
        
        // Crear tabla de horarios para visualización horizontal
        const timeTable = document.createElement('table');
        timeTable.className = 'time-slots-table';
        
        // Crear encabezado de tabla
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const th = document.createElement('th');
        th.textContent = 'Horarios disponibles';
        headerRow.appendChild(th);
        thead.appendChild(headerRow);
        timeTable.appendChild(thead);
        
        // Crear cuerpo de tabla
        const tbody = document.createElement('tbody');
        const timeRow = document.createElement('tr');
        
        // Ordenar los slots por hora
        const slots = [...availableSlots[dateStr].slots].sort((a, b) => {
            return a.time.localeCompare(b.time);
        });
        
        // Crear celdas para cada slot
        slots.forEach(slot => {
            const timeCell = document.createElement('td');
            const timeBtn = document.createElement('button');
            timeBtn.type = 'button';
            timeBtn.className = 'time-slot-btn';
            timeBtn.setAttribute('data-time', slot.time);
            timeBtn.setAttribute('data-timestamp', slot.timestamp);
            timeBtn.textContent = formatTimeForDisplay(slot.time);
            
            // Evento para seleccionar el horario
            timeBtn.addEventListener('click', function() {
                selectTimeSlot(this, dateStr, slot.time, slot.timestamp);
            });
            
            timeCell.appendChild(timeBtn);
            timeRow.appendChild(timeCell);
        });
        
        tbody.appendChild(timeRow);
        timeTable.appendChild(tbody);
        timeSlotsContainer.appendChild(timeTable);
    }
    
    /**
     * Selecciona un horario específico
     * @param {HTMLElement} btnElement - Elemento del botón de horario
     * @param {string} dateStr - Fecha en formato ISO
     * @param {string} timeStr - Hora en formato "HH:MM"
     * @param {string} timestamp - Timestamp para el backend
     */
    function selectTimeSlot(btnElement, dateStr, timeStr, timestamp) {
        // Remover selección anterior
        deselectTimeSlot();
        
        // Marcar este botón como seleccionado
        btnElement.classList.add('selected');
        
        // Guardar datos seleccionados
        selectedTime = timeStr;
        
        // Actualizar los campos ocultos
        hiddenDateInput.value = dateStr;
        hiddenTimeInput.value = timestamp;
        
        // Actualizar el resumen de la cita
        summaryDateEl.textContent = formatDateForDisplay(dateStr);
        summaryTimeEl.textContent = formatTimeForDisplay(timeStr);
        appointmentSummary.style.display = 'block';
        
        // Habilitar el botón de confirmación
        submitBtn.disabled = false;
    }
    
    /**
     * Deselecciona cualquier horario previamente seleccionado
     */
    function deselectTimeSlot() {
        // Quitar selección de botones
        const selectedButtons = document.querySelectorAll('.time-slot-btn.selected');
        selectedButtons.forEach(btn => btn.classList.remove('selected'));
        
        // Reiniciar variables
        selectedTime = null;
        
        // Ocultar resumen
        appointmentSummary.style.display = 'none';
        
        // Deshabilitar botón de confirmación
        submitBtn.disabled = true;
    }
    
    /**
     * Formatea una fecha para mostrar
     * @param {string} dateStr - Fecha en formato ISO
     * @return {string} - Fecha formateada
     */
    function formatDateForDisplay(dateStr) {
        const date = new Date(dateStr);
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('es-ES', options).replace(/^\w/, (c) => c.toUpperCase());
    }
    
    /**
     * Formatea una hora para mostrar
     * @param {string} timeStr - Hora en formato "HH:MM"
     * @return {string} - Hora formateada
     */
    function formatTimeForDisplay(timeStr) {
        const [hour, minute] = timeStr.split(':');
        const hourNum = parseInt(hour);
        const ampm = hourNum >= 12 ? 'PM' : 'AM';
        const hour12 = hourNum % 12 || 12;
        return `${hour12}:${minute} ${ampm}`;
    }
}
