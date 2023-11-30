import os, subprocess
from typing import List


def error(message: str) -> None:
    print(f"\033[0;31m[ERROR] {message}\033[0m")
    exit(1)


def warn(message: str) -> None:
    print(f"\033[0;33m[WARNING] {message}\033[0m")
    
    
def run_command(command: str, error_message: str) -> None:
    try:
        subprocess.run(command.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exception:
        output = exception.stdout.decode("utf-8") + exception.stderr.decode("utf-8")
        error(f"{error_message}. Reason:\n{output}")


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
        # TODO: Figure out how to get direction. Also, is Q an inout? No
        self.name = name
        if cell_name[-1].isdigit():
            cell_name = cell_name[:-1]
        try:
            self.direction = self.directions[cell_name][name]
        except:
            error(f"Unknown port {name} in cell {cell_name}")
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
        self.name = name
        if name not in self.functions.keys():
            error(f"Unknown cell type: {name}")
        self.function = self.functions[name]
        self.check_cell()
        magic_data = open(f"{name}.mag", "r").readlines()
        self.area = self.get_area(magic_data)
        self.ports = self.get_ports(magic_data)
        self.propagation_delays = self.get_propagation_delays()
        
    def check_cell(self) -> None:
        run_command(f"check_magic_leaf_cell -T tsmc180 -M 2 {self.name}", f"{self.name} failed cell check")
            
    def check_position(self, position: Coordinate, name: str) -> None:
        if (position.y == 0 or position.y == self.height) and not round(position.x / 0.66, 10).is_integer():
            warn(f"Vertical port {name} at {position} in cell {self.name} is not aligned to 0.66 µm grid")
        
    def get_ports(self, magic_data: List[str]) -> List[Port]:
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
        run_command(f"ext2sp {self.name}", f"Failed to convert {self.name} cell to spice")
        for line in open(f"{self.name}.spice", "r").readlines():
            if not line.startswith("C"):
                continue
            name = line.split()[1]
            capacitance = float(line.split()[3][:-2])
            for i, port in enumerate(ports):
                if port.name.endswith("!"):
                    port.name = port.name[:-1]
                if port.name == name:
                    ports[i].capacitance = str(capacitance)
                    break
        os.remove(f"{self.name}.spice")
        os.remove(f"{self.name}.sp")
        return ports
        
    def get_area(self, magic_data: List[str]) -> float:
        xs: List[int] = []
        ys: List[int] = []
        for line in magic_data:
            if not line.startswith("rect"):
                continue
            xs.append(int(line.split()[-2]))
            ys.append(int(line.split()[-1]))
        width = max(xs) / 50
        self.height = max(ys) / 50
        return width * self.height
    
    def get_propagation_delays(self) -> List[PropagationDelay]:
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