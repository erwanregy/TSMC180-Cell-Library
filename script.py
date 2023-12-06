import os, subprocess
from typing import List, Union, Any, Callable
from datetime import datetime


def cleanup() -> None:
    # TODO: Remove all except files listed in .gitignore?
    log.close()
    os.system("rm -f *.ext *.ext2svmod *.inp *.box *.sv *.vnet *.tcl *.sp *.spice *.ic0 *.mt0 *.pa0 *.st0 *.tr0")


class Log:
    colours = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[0;33m",
        "blue": "\033[0;34m",
        "cyan": "\033[0;36m",
        "reset": "\033[0m",
    }
    
        
    class LogFiles:
        
        
        class LogFile:
            def __init__(self, filename: str) -> None:
                self.filename = filename
                if os.path.exists(filename):
                    os.remove(filename)
                self.file = open(filename, "w")
                os.chmod(filename, 0o666)
                
            def write(self, message: str) -> None:
                self.file.write(message + "\n")
                self.file.flush()
                
            def close(self) -> None:
                os.chmod(self.filename, 0o444)
                self.file.close()
        
        
        def __init__(self) -> None:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            os.chmod("logs", 0o777)
            self.all = self.LogFile("logs/all.log")
            self.info = self.LogFile("logs/info.log")
            self.warnings = self.LogFile("logs/warnings.log")
            self.errors = self.LogFile("logs/errors.log")
            
        def close(self) -> None:
            self.all.close()
            self.info.close()
            self.warnings.close()
            self.errors.close()
            os.chmod("logs", 0o555)
            

    def __init__(self, timestamp: bool) -> None:
        self.timestamp = timestamp
        self.log_files = self.LogFiles()
        self.warnings = 0
        
    def close(self) -> None:
        self.log_files.close()
    
    def log(self, message: str, colour: str = "reset") -> None:
        if self.timestamp:
            message = f"[{datetime.now().strftime('%d/%m/%y %H:%M:%S.%f')[:-4]}] {message}"
        print(self.colours[colour] + message + self.colours["reset"])
        self.log_files.all.write(message)

    def error(self, message: Any) -> None:
        self.log(f"[ERROR] {message}", "red")
        self.log_files.errors.write(message)
        cleanup()
        exit(1)

    def warning(self, message: Any) -> None:
        self.log(f"[WARN]  {message}", "yellow")
        self.log_files.warnings.write(message)
        self.warnings += 1
        
    def info(self, message: Any) -> None:
        self.log(f"[INFO]  {message}", "cyan")
        self.log_files.info.write(message)
        
    def result(self) -> None:
        if self.warnings > 0:
            self.log(f"[FAIL]  Script finished with {self.warnings} warnings", "red")
            exit(1)
        self.log(f"[PASS]  Script completed successfully", "green")
        
    
log = Log(timestamp=True)

    
def run_command(command: str, error_message: str = "Default error message", warn_only: bool = False) -> None:
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
    except subprocess.CalledProcessError as _:
        output = _.stdout.decode("utf-8").strip() + _.stderr.decode("utf-8").strip()
        if warn_only:
            log.warning(f"{error_message}. Reason:\n{output}")
        else:
            log.error(f"{error_message}. Reason:\n{output}")
        
        
def run_magic_commands(cellname: str, commands: List[str], output_file: str = "") -> None:
    command = f"echo \"{'; '.join(commands)}; quit -noprompt\" | magic -dnull -noconsole -T tsmc180 {cellname}"
    if output_file != "":
        command += f" > {output_file}"
    run_command(command, f"Failed to run magic commands on cell {cellname}")


class Coordinate:
    def __init__(
        self,
        x: float,
        y: float,
    ) -> None:
        self.x = x
        self.y = y

    def __truediv__(self, other: float) -> "Coordinate":
        return Coordinate(self.x / other, self.y / other)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class Port:
    directions = {
        "rdtype": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Test"),
            "Input": ("D", "Clock", "nReset"),
            "Inout": None,
            "Output": ("Q", "nQ"),
        },
        "smux": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Clock", "nReset"),
            "Input": ("D", "Load", "Q", "Test", "SDI"),
            "Inout": None,
            "Output": ("M"),
        },
        "fulladder": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B", "Cin"),
            "Inout": None,
            "Output": ("S", "Cout"),
        },
        "halfadder": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B"),
            "Inout": None,
            "Output": ("S", "C"),
        },
        "xor": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B"),
            "Inout": None,
            "Output": ("Y"),
        },
        "mux" : {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("I0", "I1", "S"),
            "Inout": None,
            "Output": ("Y"),
        },
        "leftbuf": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": None,
            "Input": ("Test", "Clock", "nReset", "nSDO"),
            "Inout": ("SDI"),
            "Output": ("TestOut", "ClockOut", "nResetOut", "SDO"),
        },
        "rightend": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": None,
            "Input": ("Scan"),
            "Inout": None,
            "Output": ("nScan"),
        },
        "scandtype": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn"),
            "Input": ("D", "SDI", "Clock", "nReset", "Test"),
            "Inout": None,
            "Output": ("Q", "nQ"),
        },
        "scanreg": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn"),
            "Input": ("D", "SDI", "Clock", "nReset", "Load", "Test"),
            "Inout": None,
            "Output": ("Q", "nQ"),
        },
        "trisbuf": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "Enable"),
            "Inout": None,
            "Output": ("Y"),
        },
        "tiehigh": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": None,
            "Inout": None,
            "Output": ("High"),
        },
        "tielow": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": None,
            "Inout": None,
            "Output": ("Low"),
        },
        "rowcrosser": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": None,
            "Inout": ("Cross"),
            "Output": None,
        },
        "inv": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A"),
            "Inout": None,
            "Output": ("Y"),
        },
        "buffer": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A"),
            "Inout": None,
            "Output": ("Y"),
        },
        "nand": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B", "C", "D"),
            "Inout": None,
            "Output": ("Y"),
        },
        "nor": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B", "C", "D"),
            "Inout": None,
            "Output": ("Y"),
        },
        "and": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B", "C", "D"),
            "Inout": None,
            "Output": ("Y"),
        },
        "or": {
            "Power": ("Vdd!", "GND!"),
            "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
            "Input": ("A", "B", "C", "D"),
            "Inout": None,
            "Output": ("Y"),
        },
    }
    
    
    class PropagationDelay:
        def __init__(
            self,
            load_capacitance: float = 0.0,
            rise_delay: float = 0.0,
            fall_delay: float = 0.0,
            average_delay: float = 0.0,
        ):
            self.load_capacitance = load_capacitance
            self.rise_delay = rise_delay
            self.fall_delay = fall_delay
            self.average_delay = average_delay
    
    
    def __init__(
        self,
        name: str,
        cell_name: str,
        position: Coordinate,
    ) -> None:
        self.name = name
        if cell_name[-1].isdigit():
            cell_name = cell_name[:-1]
        port_found = False
        for direction, ports in self.directions[cell_name].items():
            if ports is None:
                continue
            elif name in ports:
                self.direction = direction
                port_found = True
                break
        if not port_found:
            log.error(f"Unrecognised port name '{name}' in cell '{cell_name}'")
        self.positions = [position]
        self.capacitance: Union[str, float] = "N/A"
        self.propagation_delays: List[Port.PropagationDelay] = []


class Cell:
    functions = {
        "rdtype": "Raw D-Type Flip-Flop",
        "smux": "Scan Multiplexer",
        "fulladder": "Full Adder",
        "halfadder": "Half Adder",
        "xor": "XOR Gate",
        "mux": "Standard Multiplexer",
        "leftbuf": "Left End of Row Buffer",
        "rightend": "Right End of Row Cell",
        "scandtype": "Scannable D-Type Flip-Flop",
        "scanreg": "Scannable Register",
        "inv": "Inverter",
        "buffer": "Buffer",
        "nand": "NAND Gate",
        "trisbuf": "Tri-State Buffer",
        "tiehigh": "Tie High",
        "tielow": "Tie Low",
        "rowcrosser": "Row Crosser",
        "nor": "NOR Gate",
        "and": "AND Gate",
        "or": "OR Gate",
    }
    
    n_inputs = {
        2: "Two Input",
        3: "Three Input",
        4: "Four Input",
    }
    
    def __init__(
        self,
        name: str,
    ) -> None:
        log.info(f"Processing cell {name}")
        self.name = name
        self.get_function()
        self.check_cell()
        self.extract_cell()
        self.get_area()
        self.get_magic_data()
        self.get_ports()
        os.remove(f"{self.name}.ext")
        
    def get_function(self) -> None:
        try:
            if self.name[-1].isdigit():
                self.function = f"{self.n_inputs[int(self.name[-1])]} {self.functions[self.name[:-1]]}"
            else:
                self.function = self.functions[self.name]
        except:
            log.error(f"Unrecognised cell name '{self.name}'")
        
    def check_cell(self) -> None:
        run_command(f"check_magic_leaf_cell -T tsmc180 {self.name}", f"Cell '{self.name}' failed check_magic_leaf_cell", warn_only=True)
        
    def extract_cell(self) -> None:
        run_magic_commands(self.name, ["extract"])
        if not os.path.exists(f"{self.name}.ext"):
            log.error(f"Failed to extract cell '{self.name}'")
            
    def get_magic_data(self) -> None:
        with open(f"{self.name}.mag", "r") as magic_file:
            self.magic_data = magic_file.readlines()
        
    def get_ports(self) -> None:
        # TODO: Use ext2svmod instead? Or .inp file?
        # run_command(f"ext2svmod {self.name}", f"Failed to convert ext")
        # os.remove(f"{self.name}.sv")
        # os.remove(f"{self.name}_stim.sv")
        # os.remove(f"{self.name}.vnet")
        # os.remove(f"{self.name}.tcl")
        # os.remove(f"{self.name}.ext2svmod")
        not_aligned: Callable[[Coordinate], bool] = lambda position: (position.y == 0 or position.y == self.height) and not round(position.x / 0.66, 10).is_integer()
        self.ports: List[Port] = []
        for line in self.magic_data:
            if not line.startswith("rlabel"):
                continue
            name = line.split()[-1]
            position = Coordinate(float(line.split()[2]), float(line.split()[3])) / 50
            if not_aligned(position):
                log.warning(f"Vertical port {name} at {position} in cell '{self.name}' is not aligned to 0.66 µm grid")
            port_already_exists = False
            for i, port in enumerate(self.ports):
                if port.name == name:
                    port_already_exists = True
                    self.ports[i].positions.append(position)
                    break
            if not port_already_exists:
                self.ports.append(Port(name, self.name, position))
        self.ports = sorted(self.ports, key=lambda port: f"{port.direction} {port.name}")
        # FIXME: Why is input capacitance really high for some ports?
        self.input_ports = list(filter(lambda port: port.direction == "Input", self.ports))
        self.output_ports = list(filter(lambda port: port.direction == "Output", self.ports))
        for input_port in self.input_ports:
            average_capacitance = 0.0
            num_output_ports = len(self.output_ports)
            for output_port in self.output_ports:
                if input_port.name == output_port.name:
                    num_output_ports -= 1 # FIXME: Is this needed?
                    continue
                spice = "\n"
                spice += ".include /opt/cad/designkits/ecs/hspice/tsmc180.mod\n"
                spice += ".temp 25\n"
                spice += ".param vd=1.8V\n"
                spice += ".param CLOAD=OPTC(0.01fF, 0.01fF, 50pF)\n"
                spice += "Vsupply Vdd GND DC vd\n"
                spice += "Vin in GND PULSE(0 vd 10ns 0.25ns 0.25ns 10ns 1s)\n"
                for other_input_port in self.input_ports:
                    if other_input_port.name == input_port.name:
                        continue
                    # if self.name.startswith("or"):
                    #     spice += f"V{other_input_port.name} {other_input_port.name} GND 0\n"
                    # else:
                    #     spice += f"V{other_input_port.name} {other_input_port.name} GND vd\n"
                spice += f"X{self.name}_driver0 mid0  in  Vdd GND {self.name}\n"
                spice += f"X{self.name}_load    out  mid0 Vdd GND {self.name}\n"
                spice += f"X{self.name}_driver1 mid1  in  Vdd GND {self.name}\n"
                spice += "Cload mid1 GND CLOAD \n"
                spice += ".measure TRAN tdr   TRIG v(in) VAL='vd*0.5' FALL=1 TARG v(mid0) VAL='vd*0.5' RISE=1\n"
                spice += ".measure TRAN tdf   TRIG v(in) VAL='vd*0.5' RISE=1 TARG v(mid0) VAL='vd*0.5' FALL=1\n"
                spice += ".measure TRAN tdavg PARAM='(tdr+tdf)/2'\n"
                spice += ".measure TRAN tdrc   TRIG v(in) VAL='vd*0.5' FALL=1 TARG v(mid1) VAL='vd*0.5' RISE=1\n"
                spice += ".measure TRAN tdfc   TRIG v(in) VAL='vd*0.5' RISE=1 TARG v(mid1) VAL='vd*0.5' FALL=1\n"
                spice += ".measure TRAN tdavgc PARAM='(tdrc+tdfc)/2' GOAL=tdavg\n"
                spice += ".model OPT1 opt\n"
                spice += ".tran 1fs 30ns SWEEP OPTIMIZE=optc RESULTS=tdavgc MODEL=OPT1\n"
                spice += ".option scale=0.02u\n"
                spice += f".subckt {self.name} {output_port.name} {input_port.name} Vdd GND\n"
                run_command(f"ext2sp -f {self.name}")
                with open(f"{self.name}.spice", "r") as ext_file:
                    ext_data = ext_file.readlines()[4:-2]
                spice += "\t" + "\t".join(ext_data)
                spice += ".ends\n"
                spice += ".probe v(*)\n"
                spice += ".end\n"
                with open(f"{self.name}.sp", "w") as spice_file:
                    spice_file.write(spice)
                run_command(f"hspice {self.name}.sp", f"Failed to run input capacitance HSPICE on cell '{self.name}'")
                with open(f"{self.name}.mt0", "r") as mt0_file:
                    capacitance = round(float(mt0_file.readlines()[-3].split()[-3]), 2)
                average_capacitance += capacitance * 1e15
                os.remove(f"{self.name}.spice")
                os.remove(f"{self.name}.sp")
                os.remove(f"{self.name}.ic0")
                os.remove(f"{self.name}.mt0")
                os.remove(f"{self.name}.pa0")
                os.remove(f"{self.name}.st0")
                os.remove(f"{self.name}.tr0")
            if num_output_ports == 0:
                continue
            self.ports[self.ports.index(input_port)].capacitance = average_capacitance / num_output_ports
        # TODO: Implement
        for input_port in self.input_ports:
            for load_capacitance in [0.01, 0.1, 1, 10, 50]:
                num_output_ports = len(self.output_ports)
                skip = False
                average = Port.PropagationDelay(load_capacitance)
                for output_port in self.output_ports:
                    if input_port.name == output_port.name:
                        num_output_ports -= 1 # FIXME: Is this needed?
                        continue
                    spice = "\n"
                    spice += ".include /opt/cad/designkits/ecs/hspice/tsmc180.mod\n"
                    spice += f".include {self.name}.spice\n"
                    spice += ".param vd=1.8V\n"
                    spice += "Vsupply Vdd GND vd\n"
                    spice += f"V{input_port.name} {input_port.name} GND PULSE(0 vd 10ns 0.25ns 0.25ns 10ns 1s)\n"
                    for other_input_port in self.input_ports:
                        if other_input_port.name == input_port.name:
                            continue
                        spice += f"V{other_input_port.name} {other_input_port.name} GND 0.5*vd\n"
                    spice += f"Cload {output_port.name} GND {load_capacitance}fF\n"
                    spice += ".tran 1fs 30ns\n"
                    spice += f".measure tran rise_rise_delay TRIG v({input_port.name}) VAL='vd*0.5' RISE=1 TARG  v({output_port.name}) VAL='vd*0.5' RISE=1\n"
                    spice += f".measure tran fall_rise_delay TRIG v({input_port.name}) VAL='vd*0.5' FALL=1 TARG  v({output_port.name}) VAL='vd*0.5' RISE=1\n"
                    spice += f".measure tran rise_fall_delay TRIG v({input_port.name}) VAL='vd*0.5' RISE=1 TARG  v({output_port.name}) VAL='vd*0.5' FALL=1\n"
                    spice += f".measure tran fall_fall_delay TRIG v({input_port.name}) VAL='vd*0.5' FALL=1 TARG  v({output_port.name}) VAL='vd*0.5' FALL=1\n"
                    spice += ".options POST\n"
                    spice += ".options GMINDC=1n\n"
                    spice += ".end\n"
                    run_command(f"ext2sp -f {self.name}")
                    with open(f"{self.name}.sp", "w") as spice_file:
                        spice_file.write(spice)
                    run_command(f"hspice {self.name}.sp", f"Failed to run propagation delay HSPICE on cell '{self.name}'")
                    with open(f"{self.name}.mt0", "r") as mt0_file:
                        delays = mt0_file.readlines()[-2].split()
                    if all(delay == "failed" for delay in delays):
                        skip = True
                        break
                    average.rise_delay += round(max(float(delays[0]), float(delays[1])) * 1e12, 2)
                    average.fall_delay += round(max(float(delays[2]), float(delays[3])) * 1e12, 2)
                    average.average_delay += (average.rise_delay + average.fall_delay) / 2
                    os.remove(f"{self.name}.spice")
                    os.remove(f"{self.name}.sp")
                    os.remove(f"{self.name}.ic0")
                    os.remove(f"{self.name}.mt0")
                    # os.remove(f"{self.name}.pa0")
                    os.remove(f"{self.name}.st0")
                    os.remove(f"{self.name}.tr0")
                if skip:
                    break
                if num_output_ports == 0:
                    continue
                average.rise_delay /= num_output_ports
                average.fall_delay /= num_output_ports
                average.average_delay /= num_output_ports
                self.ports[self.ports.index(input_port)].propagation_delays.append(average)
    
    
    def get_area(self) -> None:
        run_magic_commands(self.name, ["select cell", "box"], f"{self.name}.box")
        with open(f"{self.name}.box", "r") as box_file:
            box_data = box_file.readlines()[-2].split()
        os.remove(f"{self.name}.box")
        self.width = float(box_data[1])
        if not round(self.width / 0.66, 10).is_integer() and self.name != "rightend":
            log.warning(f"Cell '{self.name}' width {self.width} µm is not aligned to 0.66 µm grid")
        self.height = float(box_data[3])
        self.area = float(box_data[-1])


    def __str__(self) -> str:
        string = "\t\t<hr>\n"
        string += f"\t\t<h2>Cell Name: <code>{self.name}</code></h2>\n"
        string += f"\t\t<h3>Function</h3>\n"
        string += f"\t\t\t<p>{self.function}</p>\n"
        string += "\t\t\t<h3>Ports</h3>\n"
        string += "\t\t\t\t<table cellpadding='2' cellspacing='2' border='1'>\n"
        string += "\t\t\t\t\t<tr><th>Name</th><th>Direction</th><th>Positions (x, y) [µm]</th></tr>\n"
        for port in self.ports:
            string += f"\t\t\t\t\t<tr><td>{port.name}</td><td>{port.direction}</td><td>" + ", ".join([str(position) for position in port.positions]) + "</td></tr>\n"
        string += "\t\t\t\t</table>\n"
        if len(self.input_ports) > 0:
            string += "\t\t\t<h3>Input Capacitances</h3>\n"
            string += "\t\t\t\t<table cellpadding='2' cellspacing='2' border='1'>\n"
            string += "\t\t\t\t\t<tr><th>Port</th><th>Capacitance [fF]</th></tr>\n"
            for port in self.input_ports:
                string += f"\t\t\t\t\t<tr><td>{port.name}</td><td>{port.capacitance}</td></tr>\n"
            string += "\t\t\t\t</table>\n"
            string += "\t\t\t<h3>Propagation Delays</h3>\n"
            string += "\t\t\t\t<table cellpadding='2' cellspacing='2' border='1'>\n"
            string += "\t\t\t\t\t<tr><th>Port</th><th>Load Capacitance [fF]</th><th>Rise Delay [ps]</th><th>Fall Delay [ps]</th><th>Average Delay [ps]</th></tr>\n"
            for port in self.ports:
                for propagation_delay in port.propagation_delays:
                    string += f"\t\t\t\t\t<tr><td>{port.name}</td><td>{propagation_delay.load_capacitance}</td><td>{propagation_delay.rise_delay}</td><td>{propagation_delay.fall_delay}</td><td>{propagation_delay.average_delay}</td></tr>\n"
        string += "\t\t\t\t</table>\n"
        string += f"\t\t\t<h3>Dimensions</h3>\n"
        string += f"\t\t\t\t<p>Width:  {self.width} µm</p>\n"
        string += f"\t\t\t\t<p>Height: {self.height} µm</p>\n"
        string += f"\t\t\t<h3>Area</h3>\n"
        string += f"\t\t\t\t<p>{self.area} µm²</p>\n"
        return string


class Databook:
    def __init__(self) -> None:
        self.get_cells()
        
    def get_cells(self) -> None:
        self.cells: List[Cell] = []
        for filename in sorted(os.listdir(".")):
        # for filename in ["rdtype.mag"]:
            if filename.endswith(".mag") and filename != "all.mag":
                self.cells.append(Cell(filename[:-4]))
                # try:
                #     self.cells.append(Cell(filename[:-4]))
                # except Exception: # CellInitError
                #     ... # log failure
                #     # continue to next cell
                # else:
                #     ... # log success
                # self.write()
        tallest_cell_height = max(cell.height for cell in self.cells)    
        log.info(f"Tallest cell height is {tallest_cell_height} µm")
        for cell in self.cells:
            if cell.height != tallest_cell_height:
                log.warning(f"Cell '{cell.name}' has height {cell.height} µm, expected {tallest_cell_height} µm")
        self.cells = sorted(self.cells, key=lambda cell: cell.name)

    def write(self) -> None:
        with open("databook.html", "w") as databook:
            databook.write("<!DOCTYPE html>\n")
            # databook.write("<html style='font-family:monospace'>\n")
            databook.write("<html>\n")
            databook.write("<head><meta charset='UTF-8'><title>Databook</title></head>\n")
            databook.write("<body>\n")
            databook.write("\t<h1>Databook</h1>\n")
            for cell in self.cells:
                databook.write(str(cell))
            databook.write("</body>\n")
            databook.write("</html>")
            databook.flush()


def main() -> None:
    databook = Databook()
    databook.write()
    log.result()
    

if __name__ == '__main__':
    # FIXME: Move try except to somewhere else?
    try:
        main()
    except Exception as exception:
        cleanup()
        raise exception
