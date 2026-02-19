from PyQt6.QtWidgets import ( 
    QMainWindow, QHBoxLayout, QWidget,  
    QVBoxLayout, QLabel, QPushButton, QGroupBox, 
    QApplication, QStackedWidget, QTextEdit, QLineEdit, 
    QCheckBox 
) 

import pyqtgraph as pg 
import time 
import sys 
import os 
from PyQt6.QtCore import Qt 
from PyQt6.QtGui import QPixmap 
from daq.dummy_daq import DummyDaq 
from daq.daq_thread import DAQ_Thread 
from logging_data.csv_logger import CSVLogger 
from config.system_config import VALVES, PRESSURE_CHANNELS, TEMP_CHANNELS, DAQ_INTERVAL_MS, MAX_DATA_POINTS 
from daq.ignition_sequence import IgnitionSequence 

# Plots Background colour 
pg.setConfigOption("background", "#434343") 
pg.setConfigOption("foreground", "#DBDBDB") 

class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("DAQ GUI") 
        self.resize(900,600) 

        self.system_armed = False # Initially dis-armed 

        # For dark mode 
        self.setStyleSheet(""" 
            QWidget { 
                background-color: #121212; 
                color: #E0E0E0; 
                font-size: 11pt; 
            } 

            QGroupBox { 
                border: 1px solid #333; 
                border-radius: 5px; 
                margin-top: 6px; 
            } 

            QGroupBox:title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 3px 0 3px; 
            } 

            QPushButton { 
                background-color: #1E1E1E; 
                border: 1px solid #444; 
                padding: 6px; 
                border-radius: 4px; 
            } 

            QPushButton:hover { 
                background-color: #333; 
            } 

            QPushButton:disabled { 
                background-color: #111; 
                color: #555; 
            } 

            """) 

        # Central widget 
        central = QWidget() 
        self.setCentralWidget(central) 
        main_layout = QHBoxLayout() 
        central.setLayout(main_layout) 

        # =================== DAQ ========================================= 
        self.daq = DummyDaq() 
        self.daq_thread = DAQ_Thread(self.daq, DAQ_INTERVAL_MS) 
        self.daq_thread.data_ready.connect(self.handle_new_data) 
        self.daq_thread.start() 

        self.start_time = time.time() 
        self.time_data = [] 
        self.pressure_data = {ch: [] for ch in PRESSURE_CHANNELS} 
        self.temp_data = {ch: [] for ch in TEMP_CHANNELS} 

        # Thrust data (load cell data) 
        self.thrust_data = [] 

        self.ignition_thread = None 
        self.ignition_running = False 

        # Define/Create status labels first BEFORE building status box 
        self.time_label = QLabel("Time: 0.0 s") 
        self.pressure_label = QLabel("Pressure: --") 
        self.thrust_label = QLabel("Thrust: --") 

        # Define/Create buttons BEFORE building status box 
        self.start_log_button = QPushButton("Start Data Logging") 
        self.stop_log_button = QPushButton("Stop Data Logging") 
        self.arm_button = QPushButton("ARM") 
        self.abort_button = QPushButton("ABORT") 

        # Connect the buttons and initialise appropriate response 
        self.start_log_button.clicked.connect(self.start_logging) 
        self.stop_log_button.clicked.connect(self.stop_logging) 
        self.arm_button.clicked.connect(self.arm_system) 
        self.abort_button.clicked.connect(self.abort_system) 

        self.stop_log_button.setEnabled(False) # Log button originally OFF 

        # Ignition buttons 
        ignite_btn = QPushButton("IGNITE") 
        ignite_btn.setStyleSheet("background-color: orange; font-weight: bold") 
        ignite_btn.clicked.connect(self.start_ignition_sequence) 


        # ================== GUI SETUP ====================================== 
        # LEFT SIDEBAR ---------------------------- 
        sidebar = QVBoxLayout() 
        main_layout.addLayout(sidebar, 1) # Width ratio 

        # LOGO 
        logo_label = QLabel() 
        pixmap_path = os.path.join(os.path.dirname(__file__), "images", "pingu.png") 
        pixmap = QPixmap(pixmap_path) 
        pixmap = pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation) # scaling 
        logo_label.setPixmap(pixmap) 
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        sidebar.addWidget(logo_label) 

        # PAGE NAVIGATION 
        self.data_btn = QPushButton("Data Display") 
        self.config_btn = QPushButton("System Config") 
        self.pid_btn = QPushButton("PID") 

        sidebar.addWidget(self.data_btn) 
        sidebar.addWidget(self.config_btn) 
        sidebar.addWidget(self.pid_btn) 

        sidebar.addSpacing(20) 

        # SYSTEM STATE INDICATOR 
        self.state_label = QLabel("SAFE") 
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.state_label.setMinimumHeight(50) 
        self.state_label.setStyleSheet(""" 
            QLabel { 
                background-color: #2E7D32;   /* Green */ 
                color: white; 
                font-size: 16pt; 
                font-weight: bold; 
                border-radius: 8px; 
            } 
        """) 

        sidebar.addWidget(self.state_label) 
        sidebar.addSpacing(15) 

        self.set_system_state("SAFE") # Initially safe state 

        # GLOBAL CONTROLS 
        control_box = QGroupBox("System Control") 
        control_layout = QVBoxLayout() 
        control_box.setLayout(control_layout) 
 
        control_layout.addWidget(self.start_log_button) 
        control_layout.addWidget(self.stop_log_button) 
        control_layout.addSpacing(10) 
        control_layout.addWidget(self.arm_button) 
        control_layout.addWidget(self.abort_button) 
        control_layout.addSpacing(10) 

        # E-STOP styling for abort button 
        self.abort_button.setStyleSheet(""" 
            QPushButton { 
                background-color: darkred; 
                color: white; 
                font-weight: bold; 
            } 

            QPushButton:hover { 
                background-color: red; 
            } 
        """) 

        ignite_btn = QPushButton("IGNITE") 
        ignite_btn.setStyleSheet("background-color: orange; font-weight: bold") 
        ignite_btn.clicked.connect(self.start_ignition_sequence) 
        control_layout.addWidget(ignite_btn) 
        sidebar.addWidget(control_box) 

        sidebar.addStretch() 

        # STACKED WIDGET (RIGHT SIDE PANELS) ------------------------------ 
        self.stack = QStackedWidget() 
        main_layout.addWidget(self.stack, 3) 

        # 1. Data display (plots) ----------------------------------------- 
        self.data_page = QWidget() 
        data_layout = QHBoxLayout() # Horizontal layout, left buttons/control and right plots 
        self.data_page.setLayout(data_layout) 

        ## LEFT Side - Control 
        button_layout = QVBoxLayout() 
        data_layout.addLayout(button_layout, 1) # 1 = width ratio for buttons 

        # Valve buttons (auto-generated from 'system_config.py') 
        self.valve_buttons = {} 
        for valve in VALVES: 
            btn = QPushButton(valve) # Initial text just valve name 
            btn.setCheckable(True) # Toggle-style button 
            btn.setEnabled(False) # Initially de-energised (NC except Vent which is NO) until system armed 
            btn.setStyleSheet(""" 
                QPushButton { 
                    background-color: #111; /* Disarmed colour */ 
                    color: #888; 
                    font-weight: bold; 
                } 
                QPushButton:enabled { 
                    background-color: #F9A825; /* Armed but OFF */ 
                    color: #000; 
                } 
                QPushButton:checked { 
                    background-color: #2E7D32;  /* Green when ON */ 
                    color: white; 
                } 
            """) 

            btn.clicked.connect(lambda checked, v=valve: self.toggle_valve(v, checked)) 
            button_layout.addWidget(btn) 
            self.valve_buttons[valve] = btn 
 

        self.update_valve_buttons() 

        button_layout.addStretch()  # push buttons to top 

        ## RIGHT side - plots 
        # First create the plots 
        self.pressure_plot = pg.PlotWidget(title="Pressure vs Time") 
        self.pressure_curves = {ch: self.pressure_plot.plot(pen=pg.mkPen(color))  
                                for ch, color in zip(PRESSURE_CHANNELS, ["r","g"])} 

        self.temp_plot = pg.PlotWidget(title="Temperature vs Time") 
        self.temp_curves = {ch: self.temp_plot.plot(pen=pg.mkPen(color))  
                            for ch, color in zip(TEMP_CHANNELS, ["y","m"])} 

      
        self.thrust_plot = pg.PlotWidget(title="Thrust vs Time") 
        self.thrust_curve = self.thrust_plot.plot( 
            pen=pg.mkPen("c",width=2) 
        ) 

        plot_layout = QVBoxLayout() 
        data_layout.addLayout(plot_layout,3) # 3 = width ratio for plots 

        plot_layout.addWidget(self.thrust_plot) 
     
        # PRESSURES 
        pressure_section = QHBoxLayout() 
        pressure_section.addWidget(self.pressure_plot, 4) 
        # Add Legend/checkbox panel to select certain PTs 
        pressure_legend_layout = QVBoxLayout() 
        pressure_section.addLayout(pressure_legend_layout,1) 
         
        self.pressure_checkboxes = {} 
        for ch, curve in self.pressure_curves.items(): 
            checkbox = QCheckBox(ch) 
            checkbox.setChecked(True) 
 
            # Get colour of graph to match legend 
            pen = curve.opts["pen"] 
            colour = pen.color().name() # returns hex like #ff0000 
            checkbox.setStyleSheet(f""" 
                QCheckBox {{ 
                    color: {colour}; 
                    font-weight: bold; 
                }} 
            """) 

            checkbox.stateChanged.connect( 
                 lambda state, channel=ch: self.toggle_pressure_curve(channel, state) # Calls helper function to toggle curve 
            ) 
            pressure_legend_layout.addWidget(checkbox) 
            self.pressure_checkboxes[ch] = checkbox 
                  
        pressure_legend_layout.addStretch() 

        plot_layout.addLayout(pressure_section) 

        # TEMPERATURES 
        temp_section = QHBoxLayout() 
        temp_section.addWidget(self.temp_plot, 4) 
        # Add Legend/checkbox panel to select certain TCs 
        temp_legend_layout = QVBoxLayout() 
        temp_section.addLayout(temp_legend_layout, 1) 
 
        self.temp_checkboxes = {} 
 
        for ch, curve in self.temp_curves.items(): 
            checkbox = QCheckBox(ch) 
            checkbox.setChecked(True) 
 
            # Get colour of graph to match legend 
            pen = curve.opts["pen"] 
            colour = pen.color().name() # returns hex like #ff0000 
            checkbox.setStyleSheet(f""" 
                QCheckBox {{ 
                    color: {colour}; 
                    font-weight: bold; 
                }} 
            """) 
 
            checkbox.stateChanged.connect( 
                lambda state, channel=ch: self.toggle_temp_curve(channel, state) 
            ) 
            temp_legend_layout.addWidget(checkbox) 
            self.temp_checkboxes[ch] = checkbox 
 
        temp_legend_layout.addStretch() 
        plot_layout.addLayout(temp_section) 

        # Status labels at bottom of right side 
        status_box = QGroupBox("System Status") 
        status_layout = QVBoxLayout() 
        status_box.setLayout(status_layout) 
        status_layout.addWidget(self.time_label) 
        status_layout.addWidget(self.pressure_label) 
        status_layout.addWidget(self.thrust_label) 
        plot_layout.addWidget(status_box) 
 
        # 2. System config ------------------------------------------------------- 
        self.config_page = QWidget() 
        config_layout = QVBoxLayout() 
        self.config_page.setLayout(config_layout) 
 
        # Define editable features 
        self.valves_edit = QTextEdit(", ".join(VALVES)) 
        self.pressure_edit = QTextEdit(", ".join(PRESSURE_CHANNELS)) 
        self.temp_edit = QTextEdit(", ".join(TEMP_CHANNELS)) 
        self.daq_interval_edit = QLineEdit(str(DAQ_INTERVAL_MS)) 
        self.max_data_points_edit = QLineEdit(str(MAX_DATA_POINTS)) 
 
        # Create wdigets 
        config_layout.addWidget(QLabel("VALVES (comma & space separated):")) 
        config_layout.addWidget(self.valves_edit) 
        config_layout.addWidget(QLabel("PRESSURE_CHANNELS (comma & space separated):")) 
        config_layout.addWidget(self.pressure_edit) 
        config_layout.addWidget(QLabel("TEMP_CHANNELS (comma & space separated):")) 
        config_layout.addWidget(self.temp_edit) 
        config_layout.addWidget(QLabel("DAQ_INTERVAL_MS:")) 
        config_layout.addWidget(self.daq_interval_edit) 
        config_layout.addWidget(QLabel("MAX_DATA_POINTS:")) 
        config_layout.addWidget(self.max_data_points_edit) 

        # Save button 
        save_btn = QPushButton("Save Config") 
        save_btn.clicked.connect(self.save_config) # Calls helper function save_config to save to python file 
        config_layout.addWidget(save_btn) 

        # Spacer 
        config_layout.addStretch() 
 
        # 3. Placeholder PID page ------------------------------------------------ 
        self.pid_page = QWidget() 
        pid_layout = QVBoxLayout() 
        self.pid_page.setLayout(pid_layout) 
        pid_layout.addWidget(QLabel("PID Controller settings")) 

        # Stack usability ------------------------------------------------------- 
        # Add pages to stack 
        self.stack.addWidget(self.data_page)    # index 0 
        self.stack.addWidget(self.config_page)  # index 1 
        self.stack.addWidget(self.pid_page)     # index 2 
 
        # Connect sidebar buttons to switch pages 
        self.data_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0)) 
        self.config_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1)) 
        self.pid_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2)) 

        # LOGGING -------------------------------------------------------------- 
        headers = ["time_s"] + PRESSURE_CHANNELS + TEMP_CHANNELS + ["thrust", "event"] 
        self.logger = CSVLogger(headers) 
        self.logging_enabled = False # No data logging initially 

    # ================== LOGIC/HELPER FUNCTIONS ====================================== 
    # ARM/ABORT logic 
    def arm_system(self): 
        self.system_armed = True 
        self.update_valve_buttons() 
        self.set_system_state("ARMED") 
        self.log_event("ARM") 
        print("SYSTEM ARMED") 

    def abort_system(self): 
        if self.ignition_thread and self.ignition_running: 
            self.ignition_thread.abort() 

        self.system_armed = False 

        # Close all valves 
        for valve in VALVES: 
            self.daq.set_digital(valve, False) 

        self.update_valve_buttons() 
        self.log_event("ABORT") 
        self.set_system_state("ABORTED") 

        print("ABORT triggered. All valves returned to nominal states") 

    def update_valve_buttons(self): 
        for valve, btn in self.valve_buttons.items(): 
            btn.setEnabled(self.system_armed) 
            if not self.system_armed: 
                btn.setChecked(False) 

    # System State update function 
    def set_system_state(self, state: str): 
        """ 
        Valid states: 
        SAFE 
        ARMED 
        FIRING 
        ABORTED 
        """ 
        colors = { 
            "SAFE": "#2E7D32",      # green 
            "ARMED": "#F9A825",     # amber 
            "FIRING": "#EF6000",    # orange 
            "ABORTED": "#C62828"    # red 
        } 

        self.state_label.setText(state) 
        self.state_label.setStyleSheet(f""" 
            QLabel {{ 
                background-color: {colors[state]}; 
                color: white; 
                font-size: 16pt; 
                font-weight: bold; 
                border-radius: 8px; 
            }} 
        """) 

    # Valve toggle 
    def toggle_valve(self, valve, state): 
        if not self.system_armed: 
            print("Cannot operate valves — system not armed") 
            # Reset button to OFF if system disarmed 
            self.valve_buttons[valve].setChecked(False) 
            return 
       
        self.daq.set_digital(valve, state) 

        # Update button text/appearance if needed 
        btn = self.valve_buttons[valve] 
        btn.setChecked(state) 
        event = f"{valve}_{'OPEN' if state else 'CLOSE'}" 
        self.log_event(event) 

    # Legend toggle 
    def toggle_pressure_curve(self, channel, state): 
        visible = state == 2 
        curve = self.pressure_curves[channel] 
        curve.setVisible(visible) 

        checkbox = self.pressure_checkboxes[channel] 
 
        pen = curve.opts["pen"] 
        active_color = pen.color().name() 

        if visible: 
            checkbox.setStyleSheet(f"QCheckBox {{ color: {active_color}; font-weight: bold; }}") 
        else: 
            checkbox.setStyleSheet("QCheckBox { color: grey; }") 

    def toggle_temp_curve(self, channel, state): 
        visible = state == 2 
        curve = self.temp_curves[channel] 
        curve.setVisible(visible) 
 
        checkbox = self.temp_checkboxes[channel] 
 
        pen = curve.opts["pen"] 
        active_color = pen.color().name() 

        if visible: 
            checkbox.setStyleSheet(f"QCheckBox {{ color: {active_color}; font-weight: bold; }}") 
        else: 
            checkbox.setStyleSheet("QCheckBox { color: grey; }") 

    # Ignition 
    def start_ignition_sequence(self): 
        if not self.system_armed: 
            print("Cannot ignite — system not armed") 
            return 

        if self.ignition_running: 
            print("Ignition already running") 
            return 

        self.ignition_thread = IgnitionSequence(self.daq) 
        self.ignition_thread.step_signal.connect(self.log_event) 
        self.ignition_thread.finished_signal.connect(self.ignition_complete) 
        self.ignition_thread.aborted_signal.connect(self.ignition_aborted) 
 
        self.ignition_running = True 
        self.ignition_thread.start() 
 
        self.log_event("IGNITION_START") 
        self.set_system_state("FIRING") 

    def ignition_complete(self): 
        self.ignition_running = False 
        self.log_event("IGNITION_DONE") 
        self.set_system_state("ARMED") 
        print("Ignition sequence complete") 

    def ignition_aborted(self): 
        self.ignition_running = False 
        self.log_event("IGNITION_ABORTED") 
        print("Ignition sequence aborted") 

    # Logging start/stop 
    def start_logging(self): 
        self.logging_enabled = True 
        self.start_log_button.setEnabled(False) 
        self.stop_log_button.setEnabled(True) 
        print("Logging started") 

    def stop_logging(self): 
        self.logging_enabled = False 
        self.start_log_button.setEnabled(True) 
        self.stop_log_button.setEnabled(False) 
        #self.logger.close() 
        print("Logging stopped") 

    # Log events 
    def log_event(self, event_name: str): 
        if not self.logging_enabled: 
            return 
         
        t = time.time() - self.start_time 

        # Fill data columns with blanks so structure stays consistent 
        empty_data = [""]*(len(PRESSURE_CHANNELS) + len(TEMP_CHANNELS)) 
        row = [t] + empty_data + [event_name] 
        self.logger.write_row(row) 

        print(f"[EVENT] {event_name} @ {t:.2f}s") 

    # Safe config to 'system_config.py' 
    def save_config(self): 
        try: 
            # Read GUI values 
            valves = [v.strip() for v in self.valves_edit.toPlainText().split(",") if v.strip()] 
            pressures = [p.strip() for p in self.pressure_edit.toPlainText().split(",") if p.strip()] 
            temps = [t.strip() for t in self.temp_edit.toPlainText().split(",") if t.strip()] 
            daq_interval = int(self.daq_interval_edit.text()) 
            max_data_points = int(self.max_data_points_edit.text()) 

            # Re-write system_config.py 
            config_text = f"""# Valves 

VALVES = {valves} 
# Plot channels 
PRESSURE_CHANNELS = {pressures} 
TEMP_CHANNELS = {temps} 
 
# DAQ settings 
DAQ_INTERVAL_MS = {daq_interval} 
MAX_DATA_POINTS = {max_data_points} 

""" 
   
            current_dir = os.path.dirname(os.path.abspath(__file__)) # Path to THIS file (main.window.py) 
            project_root = os.path.dirname(current_dir) # Go up one folder  
            config_path = os.path.join(project_root, "config", "system_config.py") # Now go into config/system_config.py 
            with open(config_path, "w") as f: 
                f.write(config_text) 

            print(f"Config saved to: {config_path}") 

        except Exception as e: 
            print("Error saving config:", e) 

    # Handle incoming data 
    def handle_new_data(self, data): 
        t = time.time() - self.start_time 
        # Append all data first 
        self.time_data.append(t) 
        for key in PRESSURE_CHANNELS: 
            self.pressure_data[key].append(data[key]) 
        for key in TEMP_CHANNELS: 
            self.temp_data[key].append(data[key]) 
        thrust = data.get("thrust", None) 
        if thrust is not None: 
            self.thrust_data.append(thrust) 
      
        # Trim all data together 
        if len(self.time_data) > MAX_DATA_POINTS: 
            self.time_data = self.time_data[-MAX_DATA_POINTS:] 
            for key in PRESSURE_CHANNELS: 
                self.pressure_data[key] = self.pressure_data[key][-MAX_DATA_POINTS:] 
            for key in TEMP_CHANNELS: 
                self.temp_data[key] = self.temp_data[key][-MAX_DATA_POINTS:] 
            self.thrust_data = self.thrust_data[-MAX_DATA_POINTS:] 

        # Update plots 
        for ch, curve in self.pressure_curves.items(): 
            curve.setData(self.time_data, self.pressure_data[ch]) 
        for ch, curve in self.temp_curves.items(): 
            curve.setData(self.time_data, self.temp_data[ch]) 
        if thrust is not None: 
            self.thrust_curve.setData(self.time_data, self.thrust_data) 
            self.thrust_label.setText(f"Thrust: {thrust:.1f} N") 

        self.time_label.setText(f"Time: {t:.1f} s") 

        # CSV logging 
        if self.logging_enabled: 
            row = ([t]  
            + [data[ch] for ch in PRESSURE_CHANNELS + TEMP_CHANNELS] 
            + [data.get("thrust", "")] 
            + [""]) 
            self.logger.write_row(row) 

    def closeEvent(self, event): 
        print("Shutting down DAQ...") 
 
        try: 
            # Stop DAQ cleanly 
            self.daq_thread.stop() 
            if self.logger: 
                self.logger.close() 
      
        except Exception as e: 
            print("Error during shutdown:", e) 
 