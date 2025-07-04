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
    
    // Elementos del DOM
    const calendarEl = document.getElementById('appointment-calendar');
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const selectedDateEl = document.getElementById('selected-date');
    const appointmentSummary = document.getElementById('appointment-summary');
    const summaryDateEl = document.getElementById('summary-date');
    const summaryTimeEl = document.getElementById('summary-time');
    const submitBtn = document.getElementById('submit-booking');
    const hiddenDateInput = document.getElementById('id_date');
    const hiddenTimeInput = document.getElementById('id_time');
    
    // Botones de filtrado
    document.getElementById('show-all-slots').addEventListener('click', () => toggleFilter(false));
    document.getElementById('show-available-slots').addEventListener('click', () => toggleFilter(true));
    
    // Inicializar el calendario y preparar los eventos
    initCalendar();
    
    /**
     * Inicializa el calendario FullCalendar
     */
    function initCalendar() {
        // Preparar eventos para el calendario
        prepareCalendarEvents();
        
        // Inicializar el calendario
        const calendar = new FullCalendar.Calendar(calendarEl, {
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek'
            },
            initialView: 'dayGridMonth',
            selectable: true,
            selectMirror: true,
            navLinks: true,
            locale: 'es',
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana'
            },
            dayMaxEvents: true,
            events: calendarEvents,
            select: handleDateSelect,
            eventClick: handleEventClick,
            eventClassNames: applyEventStyles
        });
        
        // Renderizar el calendario
        calendar.render();
    }
    
    /**
     * Prepara los eventos para mostrar en el calendario
     */
    function prepareCalendarEvents() {
        // Recorrer todos los slots disponibles y crear eventos
        for (const dateStr in availableSlots) {
            const dateData = availableSlots[dateStr];
            if (dateData.slots && dateData.slots.length > 0) {
                // Fecha con slots disponibles
                calendarEvents.push({
                    title: `${dateData.slots.length} horarios disponibles`,
                    start: dateStr,
                    allDay: true,
                    availability: 'available',
                    slots: dateData.slots
                });
            } else {
                // Fecha sin slots disponibles
                calendarEvents.push({
                    title: 'No disponible',
                    start: dateStr,
                    allDay: true,
                    availability: 'unavailable',
                    slots: []
                });
            }
        }
        
        // Si está activo el filtro de solo disponibles, filtrar los eventos
        if (showOnlyAvailable) {
            calendarEvents = calendarEvents.filter(event => event.availability === 'available');
        }
    }
    
    /**
     * Maneja la selección de una fecha en el calendario
     * @param {Object} info - Información del evento de selección
     */
    function handleDateSelect(info) {
        const dateStr = info.startStr;
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
        const dateStr = info.event.startStr;
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
     * Aplica estilos personalizados a los eventos según su disponibilidad
     * @param {Object} info - Información del evento
     * @return {Array} - Clases CSS a aplicar
     */
    function applyEventStyles(info) {
        const availability = info.event.extendedProps.availability;
        return [
            'calendar-event',
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
        
        // Si hay una fecha seleccionada, actualizar los slots mostrados
        if (selectedDate) {
            displayTimeSlotsForDate(selectedDate);
        }
        
        // Actualizar los eventos en el calendario
        const calendar = new FullCalendar.Calendar(calendarEl);
        calendar.getEvents().forEach(event => event.remove());
        calendarEvents.forEach(event => calendar.addEvent(event));
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
        
        // Crear slots
        const timeSlots = document.createElement('div');
        timeSlots.className = 'time-slots';
        
        // Ordenar los slots por hora
        const slots = [...availableSlots[dateStr].slots].sort((a, b) => {
            return a.time.localeCompare(b.time);
        });
        
        // Crear botones para cada slot
        slots.forEach(slot => {
            const timeSlotBtn = document.createElement('button');
            timeSlotBtn.type = 'button';
            timeSlotBtn.className = 'time-slot-btn';
            timeSlotBtn.setAttribute('data-time', slot.time);
            timeSlotBtn.setAttribute('data-timestamp', slot.timestamp);
            timeSlotBtn.textContent = formatTimeForDisplay(slot.time);
            
            // Evento para seleccionar el horario
            timeSlotBtn.addEventListener('click', function() {
                selectTimeSlot(this, dateStr, slot.time, slot.timestamp);
            });
            
            timeSlots.appendChild(timeSlotBtn);
        });
        
        timeSlotsContainer.appendChild(timeSlots);
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
