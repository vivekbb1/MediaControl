"""
HDMI Matrix Switcher Control
Supports common matrix switchers via TCP/IP and RS-232
"""

from typing import Dict, Optional, Any, List
import logging
import socket
import time
from enum import Enum

logger = logging.getLogger(__name__)


class MatrixProtocol(Enum):
    """Matrix control protocols"""
    TCP = "tcp"
    RS232 = "rs232"
    HTTP = "http"


class HDMIMatrix:
    """
    Base class for HDMI matrix switchers
    """
    
    def __init__(
        self,
        matrix_id: str,
        name: str,
        protocol: MatrixProtocol,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        num_inputs: int = 4,
        num_outputs: int = 4,
    ):
        self.id = matrix_id
        self.name = name
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._routing: Dict[int, int] = {}  # output → input mapping
    
    def connect(self) -> bool:
        """Connect to matrix. Override in subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement connect()")
    
    def disconnect(self) -> bool:
        """Disconnect from matrix"""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        self._connected = False
        return True
    
    def route(self, input_num: int, output_num: int) -> bool:
        """
        Route an input to an output.
        Override in subclasses.
        
        Args:
            input_num: Input number (1-based)
            output_num: Output number (1-based)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement route()")
    
    def route_all(self, input_num: int, output_nums: List[int]) -> bool:
        """Route one input to multiple outputs"""
        success = True
        for output in output_nums:
            if not self.route(input_num, output):
                success = False
        return success
    
    def get_routing(self) -> Dict[int, int]:
        """Get current routing (output → input mapping)"""
        return self._routing.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get matrix status"""
        return {
            "id": self.id,
            "name": self.name,
            "connected": self._connected,
            "num_inputs": self.num_inputs,
            "num_outputs": self.num_outputs,
            "routing": self._routing.copy(),
        }


class MonopriceBlackbirdMatrix(HDMIMatrix):
    """
    Monoprice Blackbird 4K HDMI Matrix
    Protocol: TCP/IP with simple text commands
    """
    
    def __init__(
        self,
        matrix_id: str,
        name: str,
        ip: str,
        port: int = 23,  # Telnet port
        num_inputs: int = 4,
        num_outputs: int = 4,
    ):
        super().__init__(
            matrix_id=matrix_id,
            name=name,
            protocol=MatrixProtocol.TCP,
            ip=ip,
            port=port,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
        )
    
    def connect(self) -> bool:
        """Connect to Monoprice matrix via TCP"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((self.ip, self.port))
            self._connected = True
            logger.info(f"{self.name}: Connected to {self.ip}:{self.port}")
            
            # Query current routing
            self._query_routing()
            return True
            
        except Exception as e:
            logger.error(f"{self.name}: Connection failed: {e}")
            self._socket = None
            return False
    
    def _send_command(self, command: str) -> Optional[str]:
        """Send command and get response"""
        if not self._connected or not self._socket:
            return None
        
        try:
            # Send command
            self._socket.sendall(f"{command}\r\n".encode())
            
            # Receive response
            response = self._socket.recv(1024).decode().strip()
            return response
            
        except Exception as e:
            logger.error(f"{self.name}: Command failed: {e}")
            return None
    
    def route(self, input_num: int, output_num: int) -> bool:
        """
        Route input to output.
        Command format: "MT00SW<I><O>" where I=input, O=output
        """
        if not (1 <= input_num <= self.num_inputs):
            logger.error(f"Invalid input number: {input_num}")
            return False
        
        if not (1 <= output_num <= self.num_outputs):
            logger.error(f"Invalid output number: {output_num}")
            return False
        
        command = f"MT00SW{input_num:02d}{output_num:02d}"
        response = self._send_command(command)
        
        if response and "OK" in response:
            self._routing[output_num] = input_num
            logger.info(f"{self.name}: Routed input {input_num} → output {output_num}")
            return True
        else:
            logger.error(f"{self.name}: Route command failed")
            return False
    
    def _query_routing(self) -> bool:
        """Query current routing state"""
        try:
            for output in range(1, self.num_outputs + 1):
                command = f"MT00RD{output:02d}"
                response = self._send_command(command)
                
                if response:
                    # Parse response to get input number
                    # Response format varies, this is simplified
                    import re
                    match = re.search(r'IN(\d+)', response)
                    if match:
                        input_num = int(match.group(1))
                        self._routing[output] = input_num
            
            return True
        except Exception as e:
            logger.error(f"{self.name}: Query routing failed: {e}")
            return False


class GenericTCPMatrix(HDMIMatrix):
    """
    Generic TCP/IP matrix with configurable command format.
    Works with many brands: Kramer, Extron, Atlona, OREI, etc.
    
    Configure command templates in config:
    - route_command: Template for routing command
    - query_command: Template for querying status
    
    Templates use placeholders: {input}, {output}
    """
    
    def __init__(
        self,
        matrix_id: str,
        name: str,
        ip: str,
        port: int,
        num_inputs: int,
        num_outputs: int,
        route_command: str = "#{output}@{input}.",  # Default format
        query_command: Optional[str] = None,
        terminator: str = "\r\n",
        timeout: int = 5,
    ):
        super().__init__(
            matrix_id=matrix_id,
            name=name,
            protocol=MatrixProtocol.TCP,
            ip=ip,
            port=port,
            num_inputs=num_inputs,
            num_outputs=num_outputs,
        )
        self.route_command = route_command
        self.query_command = query_command
        self.terminator = terminator
        self.timeout = timeout
    
    def connect(self) -> bool:
        """Connect to matrix via TCP"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.ip, self.port))
            self._connected = True
            logger.info(f"{self.name}: Connected to {self.ip}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"{self.name}: Connection failed: {e}")
            self._socket = None
            return False
    
    def _send_command(self, command: str) -> bool:
        """Send command (fire and forget)"""
        if not self._connected or not self._socket:
            return False
        
        try:
            full_command = command + self.terminator
            self._socket.sendall(full_command.encode())
            time.sleep(0.1)  # Brief delay for command processing
            return True
            
        except Exception as e:
            logger.error(f"{self.name}: Command failed: {e}")
            return False
    
    def route(self, input_num: int, output_num: int) -> bool:
        """Route input to output using configured command template"""
        if not (1 <= input_num <= self.num_inputs):
            logger.error(f"Invalid input number: {input_num}")
            return False
        
        if not (1 <= output_num <= self.num_outputs):
            logger.error(f"Invalid output number: {output_num}")
            return False
        
        # Build command from template
        command = self.route_command.format(
            input=input_num,
            output=output_num,
            input_hex=f"{input_num:02X}",
            output_hex=f"{output_num:02X}",
        )
        
        if self._send_command(command):
            self._routing[output_num] = input_num
            logger.info(f"{self.name}: Routed input {input_num} → output {output_num}")
            return True
        else:
            return False


# Matrix factory
def create_matrix(config: Dict[str, Any]) -> Optional[HDMIMatrix]:
    """
    Factory function to create matrix from config.
    
    Config format:
    {
        "id": "matrix-1",
        "type": "monoprice_blackbird" or "generic_tcp",
        "name": "4x4 Matrix",
        "ip": "192.168.1.100",
        "port": 23,
        "num_inputs": 4,
        "num_outputs": 4,
        # For generic_tcp only:
        "route_command": "#{output}@{input}.",
        "terminator": "\r\n",
    }
    """
    matrix_type = config.get("type", "generic_tcp")
    
    if matrix_type == "monoprice_blackbird":
        return MonopriceBlackbirdMatrix(
            matrix_id=config["id"],
            name=config["name"],
            ip=config["ip"],
            port=config.get("port", 23),
            num_inputs=config.get("num_inputs", 4),
            num_outputs=config.get("num_outputs", 4),
        )
    
    elif matrix_type == "generic_tcp":
        return GenericTCPMatrix(
            matrix_id=config["id"],
            name=config["name"],
            ip=config["ip"],
            port=config["port"],
            num_inputs=config.get("num_inputs", 4),
            num_outputs=config.get("num_outputs", 4),
            route_command=config.get("route_command", "#{output}@{input}."),
            query_command=config.get("query_command"),
            terminator=config.get("terminator", "\r\n"),
            timeout=config.get("timeout", 5),
        )
    
    else:
        logger.error(f"Unknown matrix type: {matrix_type}")
        return None
