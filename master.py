from time import sleep
from pymodbus.client import ModbusTcpClient
with ModbusTcpClient(host='127.0.0.1', port=502) as client:
    while True:
        result = client.read_holding_registers(address=0, count=10, slave=1)
        print(result.getRegister(0))
