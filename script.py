import os, subprocess
from typing import List, Any
from datetime import datetime


class Log:
    colours = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[0;33m",
        "blue": "\033[0;34m",
        "reset": "\033[0m",
    }

    def __init__(self, filename: str, timestamp: bool) -> None:
        self.timestamp = timestamp
        if not filename.endswith(".log"):
            filename += ".log"
        os.chmod(filename, 0o666)
        self.logfile = open(filename, "w")
        
    def __del__(self) -> None:
        os.chmod(self.logfile.name, 0o444)
        self.logfile.close()
    
    def log(self, message: str, colour: str = "reset") -> None:
        if self.timestamp:
            message = f"[{datetime.now().strftime('%d/%m/%y %H:%M:%S:%f')[:-4]}] {message}"
        print(self.colours[colour] + message + self.colours["reset"])
        self.logfile.write(message + "\n")

    def error(self, message: Any) -> None:
        self.log(f"[error] {message}", "red")
        exit(1)

    def warning(self, message: Any) -> None:
        self.log(f"[warning] {message}", "yellow")
        
    def info(self, message: Any) -> None:
        self.log(f"[info] {message}", "green")
        
    
log = Log(
    filename="script",
    timestamp=False
)

    
def run_command(command: str, error_message: str) -> None:
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
    except subprocess.CalledProcessError as _:
        output = _.stdout.decode("utf-8") + _.stderr.decode("utf-8")
        log.error(f"{error_message}. Reason:\n{output}")
        
        
def run_magic_commands(cellname: str, commands: List[str], error_message: str, output_file: str = "") -> None:
    command = f"echo \"{'; '.join(commands)}; quit -noprompt\" | magic -dnull -noconsole -T tsmc180 {cellname}"
    if output_file != "":
        command += f" > {output_file}"
    run_command(command, error_message)


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
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Test": "Inout",
            "D": "Input",
            "Clock": "Input",
            "nReset": "Input",
            "Q": "Output",
            "nQ": "Output",
        },
        "smux": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "D": "Input",
            "Load": "Input",
            "Q": "Input",
            "Test": "Input",
            "SDI": "Input",
            "M": "Output",
        },
        "fulladder": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "Cin": "Input",
            "S": "Output",
            "Cout": "Output",
        },
        "halfadder": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "S": "Output",
            "C": "Output",
        },
        "xor": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "Y": "Output",
        },
        "mux" : {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "I0": "Input",
            "I1": "Input",
            "S": "Input",
            "Y": "Output",
        },
        "leftbuf": {
            "Vdd!": "Inout",
            "SDI": "Inout",
            "Test": "Input",
            "Clock": "Input",
            "nReset": "Input",
            "nSDO": "Input",
            "GND!": "Input",
            "TestOut": "Output",
            "ClockOut": "Output",
            "nResetOut": "Output",
            "SDO": "Output",
        },
        "rightend": {
            "GND!": "Inout",
            "Vdd!": "Input",
            "Scan": "Input",
            "nScan": "Output",
        },
        "trisbuf": {
            "Vdd!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "GND!": "Inout",
            "A": "Input",
            "Enable": "Input",
            "Y": "Output",
        },
        "tiehigh": {
            "Vdd!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "GND!": "Inout",
            "High": "Output",
        },
        "tielow": {
            "Vdd!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "GND!": "Inout",
            "Low": "Output",
        },
        "rowcrosser": {
            "Vdd!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "GND!": "Inout",
            "Low": "Inout",
        },
        "inv": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "Y": "Output",
        },
        "buffer": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "Y": "Output",
        },
        "nand": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "C": "Input",
            "D": "Input",
            "Y": "Output",
        },
        "nor": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "C": "Input",
            "Y": "Output",
        },
        "and": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "Y": "Output",
        },
        "or": {
            "Vdd!": "Inout",
            "GND!": "Inout",
            "ScanReturn": "Inout",
            "Scan": "Inout",
            "Test": "Inout",
            "Clock": "Inout",
            "nReset": "Inout",
            "A": "Input",
            "B": "Input",
            "Y": "Output",
        },
    }
    
    def __init__(
        self,
        name: str,
        cell_name: str,
        position: Coordinate,
    ) -> None:
        self.name = name
        if cell_name[-1].isdigit():
            cell_name = cell_name[:-1]
        try:
            self.direction = self.directions[cell_name][name]
        except:
            log.error(f"Unknown port {name} in cell {cell_name}")
        self.positions = [position]
        self.capacitance = ""
    
    
class PropagationDelay:
    def __init__(
        self,
        load_capacitance: float = 0.0,
        delay: float = 0.0,
    ):
        self.load_capacitance = load_capacitance
        self.delay = delay


class Cell:
    functions = {
        "rdtype": "Raw D-Type Flip-Flop",
        "smux2": "Two Input Multiplexer",
        "smux3": "Three Input Multiplexer",
        "fulladder": "Full Adder",
        "halfadder": "Half Adder",
        "xor2": "Two Input XOR Gate",
        "leftbuf": "Left End of Row Buffer",
        "rightend": "Right End of Row Cell",
        "inv": "Inverter",
        "buffer": "Buffer",
        "nand2": "Two Input NAND Gate",
        "nand3": "Three Input NAND Gate",
        "nand4": "Four Input NAND Gate",
        "trisbuf": "Tri-State Buffer",
        "tiehigh": "Tie High",
        "tielow": "Tie Low",
        "rowcrosser": "Row Crosser",
        "nor2": "Two Input NOR Gate",
        "nor3": "Three Input NOR Gate",
        "and2": "Two Input AND Gate",
        "or2": "Two Input OR Gate",
    }
    
    def __init__(
        self,
        name: str,
    ) -> None:
        log.info(f"Processing cell {name}")
        self.name = name
        if name not in self.functions.keys():
            log.error(f"Unrecognised cell name \"{name}\"")
        self.function = self.functions[name]
        self.check_cell()
        self.extract_cell()
        self.area = self.get_area()
        with open(f"{name}.mag", "r") as magic_file:
            magic_data = magic_file.readlines()
        self.ports = self.get_ports(magic_data)
        self.propagation_delays = self.get_propagation_delays()
        os.remove(f"{name}.ext")
        
    def check_cell(self) -> None:
        run_command(f"check_magic_leaf_cell -T tsmc180 -M 2 {self.name}", f"{self.name} failed cell check")
        
    def extract_cell(self) -> None:
        run_magic_commands(self.name, ["extract"], f"Failed to extract cell {self.name}")
            
    def check_position(self, position: Coordinate, name: str) -> None:
        if (position.y == 0 or position.y == self.height) and not round(position.x / 0.66, 10).is_integer():
            log.warning(f"Vertical port {name} at {position} in cell {self.name} is not aligned to 0.66 µm grid")
        
    def get_ports(self, magic_data: List[str]) -> List[Port]:
        # TODO: Use ext2svmod instead?
        run_command(f"ext2svmod {self.name}", f"Failed to convert ext")
        os.remove(f"{self.name}.sv")
        os.remove(f"{self.name}_stim.sv")
        os.remove(f"{self.name}.vnet")
        os.remove(f"{self.name}.tcl")
        
        ports: List[Port] = []
        for line in magic_data:
            if not line.startswith("rlabel"):
                continue
            name = line.split()[-1]
            position = Coordinate(float(line.split()[2]), float(line.split()[3])) / 50
            self.check_position(position, name)
            port_already_exists = False
            for i, port in enumerate(ports):
                if port.name == name:
                    port_already_exists = True
                    ports[i].positions.append(position)
                    break
            if not port_already_exists:
                ports.append(Port(name, self.name, position))
        # TODO: Calculate input capacitance
        ...
        return ports
        
    def get_area(self) -> float:
        run_magic_commands(self.name, ["select cell", "box"], f"Failed to get area of cell {self.name}", f"{self.name}.box")
        with open(f"{self.name}.box", "r") as box_file:
            box_data = box_file.readlines()[-2].split()
        os.remove(f"{self.name}.box")
        self.width = float(box_data[1])
        self.height = float(box_data[3])
        return float(box_data[-1])
    
    def get_propagation_delays(self) -> List[PropagationDelay]:
        # TODO: Implement
        return []

    def __str__(self) -> str:
        string  = f"\t<h2><code>{self.name}</code></h2>\n"
        string += f"\t<p>{self.function}</p>\n"
        string += "\t<h3>Ports</h3>\n"
        string += "\t<table>\n"
        string += "\t\t<tr><th>Name</th><th>Direction</th><th>Capacitance [fF]</th><th>Positions [µm]</th></tr>\n"
        for port in self.ports:
            string += f"\t\t<tr><td>{port.name}</td><td>{port.direction}</td><td>{port.capacitance}</td>\n"
            string += "\t\t<td>" + ", ".join([str(position) for position in port.positions]) + "</td></tr>\n"
        string += "\t</table>\n"
        string += "\t<h3>Propagation Delays</h3>\n"
        string += "\t<table>\n"
        string += "\t\t<tr><th>Load Capacitance [fF]</th><th>Delay [?s]</th></tr>\n"
        for propagation_delay in self.propagation_delays:
            string += f"\t\t<tr><td>{propagation_delay.load_capacitance}</td><td>{propagation_delay.delay}</td></tr>\n"
        string += "\t</table>\n"
        string += f"\t<h3>Area</h3>\n"
        string += f"\t<p>{self.area} µm²</p>\n"
        string += "\t<br>\n"
        return string


def get_cells() -> List[Cell]:
    cells: List[Cell] = []
    for filename in os.listdir('.'):
        if filename.endswith('.mag'):
            cells.append(Cell(filename[:-4]))
    tellest_cell_height = max(cell.height for cell in cells)    
    log.info(f"Tallest cell height is {tellest_cell_height} µm")
    for cell in cells:
        if cell.height != tellest_cell_height:
            log.warning(f"Cell {cell.name} has height {cell.height} µm, expected {tellest_cell_height} µm")
    return cells


def write_databook(cells: List[Cell]) -> None:
    with open("databook.html", "w") as databook:
        databook.write("<!DOCTYPE html>\n")
        databook.write("<html style='font-family:monospace'>\n")
        databook.write("<head><meta charset='UTF-8'><title>Databook</title></head>\n")
        databook.write("<body>\n")
        databook.write("\t<style>table, th, td {border:1px solid black;}</style>\n")
        databook.write("\t<h1>Databook</h1>\n")
        databook.write("\t<br>\n")
        for cell in cells:
            databook.write(str(cell))
        databook.write("</body>\n")
        databook.write("</html>")


def main() -> None:
    cells = get_cells()
    write_databook(cells)


if __name__ == '__main__':
    main()