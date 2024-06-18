import time
import logging
from datetime import datetime
import streamlit as st

# Funcion para el log.
def get_logger():
    # Crear un logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Crear un manejador para la terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Crear un manejador para el archivo de log
    file_handler = logging.FileHandler('taximetro.log')
    file_handler.setLevel(logging.INFO)

    # Formato del logging
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Añadir los manejadores al logger
    if not logger.handlers:
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger

logger = get_logger()

class Taximetro:
    """Clase que simula el funcionamiento de un taxímetro."""

    def __init__(self):
        self.tarifa_por_minuto_movimiento = 3
        self.tarifa_por_minuto_parado = 1.2
        self.tarifa_base = 2.5
        self.reset()
        logger.info ("Taxímetro inicializando con tarifas base.")

    def reset(self):
        self.en_marcha = False
        self.en_movimiento = False
        self.tarifa_total = self.tarifa_base
        self.hora_inicio = None
        self.ultima_hora = None
        self.tiempo_movimiento = 0
        self.tiempo_parado = 0
        logger.info ("Taxímetro restablecido.")

    def iniciar(self):
        # Comienza la carrera en estado parado, ya tarifica 
        self.en_marcha = True
        self.en_movimiento = False
        self.hora_inicio = time.time()
        self.ultima_hora = self.hora_inicio
        st.session_state.messages.append(f"{ahora()} - Inicia la carrera del taxi.")
        logger.info ("Carrera iniciada.")
        
    def mover(self):
        if self.en_marcha and not self.en_movimiento:
            self.actualizar_tarifa()
            self.en_movimiento = True
            self.ultima_hora = time.time()
            st.session_state.messages.append(f"{ahora()} - El taxi se ha puesto en marcha.")
            logger.info ("El taxi se ha puesto en marcha.")

    def parar(self):
        if self.en_marcha and self.en_movimiento:
            self.actualizar_tarifa()
            self.en_movimiento = False
            self.ultima_hora = time.time()
            st.session_state.messages.append(f"{ahora()} - El taxi se ha parado.")
            logger.info ("El taxi se ha parado.")

    def finalizar_carrera(self):
        if self.en_marcha:
            self.actualizar_tarifa()
            st.session_state.tarifa_final = self.tarifa_total  # Guardar la tarifa final en session_state
            st.session_state.messages.append(
                f"{ahora()} - Carrera finalizada. Tiempo de marcha y paro : {self.tiempo_movimiento + self.tiempo_parado :.2f} segundos, Importe total: {self.tarifa_total:.2f} €")
            logger.info(f"Carrera finalizada. Importe total:{self.tarifa_total:.2f} €")
            self.reset()
        else:
            st.session_state.messages.append(f"{ahora()} - No hay carrera en curso para finalizar.")
            logger.warning("Intento de finalizar una carrera que no está en curso")

    def actualizar_tarifa(self):
        hora_actual = time.time()
        if self.en_marcha:
            tiempo_transcurrido = hora_actual - self.ultima_hora
            if self.en_movimiento:
                self.tiempo_movimiento += tiempo_transcurrido
                self.tarifa_total += tiempo_transcurrido * (self.tarifa_por_minuto_movimiento / 60)
            else:
                self.tiempo_parado += tiempo_transcurrido
                self.tarifa_total += tiempo_transcurrido * (self.tarifa_por_minuto_parado / 60)
            self.ultima_hora = hora_actual
            logger.info ("Tarifa actualizada.")

def ahora():
    ahora = datetime.now()
    hora_actual = ahora.strftime("%H:%M:%S")
    return hora_actual

def limpiar_mensajes():
    st.session_state.messages = []

def leer_log():
    try:
        with open('taximetro.log', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "No se encontró el archivo de log."

def main():
     
    st.markdown(
        """
        <h1 style='text-align: center;'>Taxímetro - G5</h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Menú desplegable en la barra lateral
    menu_options = [ "Seleccione Opción", "Cambiar Tarifas", "Ver Log", "Ayuda"]
    menu_selection = st.sidebar.selectbox("Menú", menu_options)
    logger.info(f"Menu seleccionado: {menu_selection}")

    if 'taximetro' not in st.session_state:
        st.session_state.taximetro = Taximetro()
        st.session_state.messages = []
        st.session_state.tarifa_final = 0.0  # Inicializar la variable para la tarifa final
        logger.info ("Sesión inicializada.")

    if menu_selection == "Ver Log":
        # Mostrar el contenido del log en una sección separada
        st.markdown("### Log del Sistema")
        st.text_area("Log del sistema", value=leer_log(), height=200)
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Iniciar Carrera"):
                st.session_state.taximetro.iniciar()
                logger.info ("Botón 'Iniciar Carrera' presionado.")

        with col2:
            if st.button("Taxi en movimiento"):
                st.session_state.taximetro.mover()
                logger.info ("Botón 'Taxi en movimiento' presionado.")

        with col3:
            if st.button("Taxi parado"):
                st.session_state.taximetro.parar()
                logger.info ("Botón 'Taxi parado' presionado.")

        with col4:
            if st.button("Finalizar Carrera"):
                st.session_state.taximetro.finalizar_carrera()
                logger.info ("Botón 'Finalizar carrera' presionado.")

    # Mostrar mensajes
    st.text_area("Mensajes", value="\n".join(st.session_state.messages), height=200)

    # Mostrar tarifa total dinámicamente
    st.text(f"Tarifa Total: €{st.session_state.tarifa_final:.2f}")

if __name__ == "__main__":
    main()
