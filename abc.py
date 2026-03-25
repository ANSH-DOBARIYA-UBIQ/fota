

import serial
import time
import json
 
 
class ModbusRTU:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        )
 
        if self.ser.is_open:
            print(f"Serial port {self.ser.port} opened successfully.")
 
    def calculate_crc(self, data: bytes):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
 
    def append_crc(self, frame: bytes):
        crc = self.calculate_crc(frame)
        return frame + crc.to_bytes(2, byteorder='little')
 
    def write_raw(self, hex_string):
        frame = bytes.fromhex(hex_string)
        frame_with_crc = self.append_crc(frame)
 
        self.ser.write(frame_with_crc)
 
        print("TX HEX :", frame_with_crc.hex().upper())
        return frame_with_crc
 
    def read_response(self):
        time.sleep(0.2)
        response = self.ser.read(self.ser.in_waiting or 1)
 
        if not response:
            print("No response received.")
            return None
 
        print("RX HEX :", response.hex().upper())
        return response
 
    def close(self):
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")
 
try:
    modbus = ModbusRTU(port='COM1')
 
    # Shift 1 daily consumption "011302580001"
 
    # Shift 2 daily "011302580002"
 
    # Shift 3 daily "011302580003"
 
    # Monthly "011302CC0001"
 
    # Detailed "01140001000060"
    req = "011303e80001"
 
    modbus.write_raw(req)
 
    response = modbus.read_response()
 
    if response:
 
        func_code = response[1]
 
        # ================= DETAIL =================
        if func_code == 0x14:
            slave_id           = int.from_bytes(response[0:1],  byteorder='big')
            func_code          = int.from_bytes(response[1:2],  byteorder='big')
            nu_bytes           = int.from_bytes(response[2:3],  byteorder='big')
            xx_interval        = int.from_bytes(response[3:4],  byteorder='big')
            start_mode         = int.from_bytes(response[4:5],  byteorder='big')
            stop_mode          = int.from_bytes(response[5:6],  byteorder='big')
            reserved1          = int.from_bytes(response[6:7],  byteorder='big')
            index_number       = int.from_bytes(response[7:11], byteorder='big')
 
            amount             = int.from_bytes(response[11:15], byteorder='big')
            volume             = int.from_bytes(response[15:19], byteorder='big')
            price_at_filling   = int.from_bytes(response[19:23], byteorder='big')
            start_time         = int.from_bytes(response[23:27], byteorder='big')
            stop_time          = int.from_bytes(response[27:31], byteorder='big')
            ic_amt_before      = int.from_bytes(response[31:35], byteorder='big')
            ic_amt_after       = int.from_bytes(response[35:39], byteorder='big')
            card_hw_id         = int.from_bytes(response[39:43], byteorder='big')
 
            user_number        = int.from_bytes(response[43:47], byteorder='big')
            motherboard_number = int.from_bytes(response[47:51], byteorder='big')
            card_number        = int.from_bytes(response[51:53], byteorder='big')
            oil_number         = int.from_bytes(response[53:55], byteorder='big')
            precision          = int.from_bytes(response[55:57], byteorder='big')
            longitude          = int.from_bytes(response[57:61], byteorder='big')
            dimension          = int.from_bytes(response[61:65], byteorder='big')
            reserved2          = int.from_bytes(response[65:67], byteorder='big')
 
            crc = response[67:69].hex().upper()
           
            detail_data = {
            "SLAVE ID": slave_id,
            "FUNCTION CODE": hex(func_code),
            "NUMBER OF BYTES": nu_bytes,
            "XX INTERVAL": xx_interval,
            "START MODE": start_mode,
            "STOP MODE": stop_mode,
            "RESERVED_1": reserved1,
            "INDEX NUMBER": index_number,
            "AMOUNT": amount,
            "VOLUME": volume,
            "PRICE AT FILLING": price_at_filling,
            "START TIME": str(start_time),
            "STOP TIME": str(stop_time),
            "IC AMOUNT BEFORE": ic_amt_before,
            "IC AMOUNT AFTER": ic_amt_after,
            "CARD HARDWARE ID": card_hw_id,
            "USER NUMBER": user_number,
            "MOTHERBOARD NO": motherboard_number,
            "CARD NUMBER": card_number,
            "OIL NUMBER": oil_number,
            "PRECISION": precision,
            "LONGITUDE": longitude,
            "DIMENSION": dimension,
            "RESERVED_2": reserved2,
            "CRC CHECK": hex(crc) if isinstance(crc, int) else str(crc)
        }
 
            print(json.dumps(detail_data, indent=4))
 
        # ================= DAILY =================
        elif func_code == 0x13:
            slave_id   = int.from_bytes(response[0:1], byteorder='big')
            func_code  = int.from_bytes(response[1:2], byteorder='big')
            byte_cnt   = int.from_bytes(response[2:3], byteorder='big')
            amount_raw = int.from_bytes(response[3:11],  byteorder='big')
            volume_raw = int.from_bytes(response[11:19], byteorder='big')
            time_raw   = int.from_bytes(response[19:23], byteorder='big')
            stroke_cnt = int.from_bytes(response[23:27], byteorder='big')
            crc        = response[-2:].hex().upper()
            amount     = amount_raw / 1000.0
            volume     = volume_raw / 1000.0
 
            daily_data = {
            "SLAVE ID": str(slave_id),
            "FUNCTION CODE": hex(func_code),
            "BYTE COUNT": byte_cnt,
            "AMOUNT (₹)": amount,
            "VOLUME (L)": volume,
            "STROKE COUNT": stroke_cnt,
            "CRC CHECK": hex(crc) if isinstance(crc, int) else str(crc)
        }
 
            print(json.dumps(daily_data, indent=4))
 
        else:
            print("Unknown function code")
    time.sleep(0.1)
 
 
except serial.SerialException as e:
    print("Serial error:", e)
 
except KeyboardInterrupt:
    print("Program terminated by user.")
 
finally:
    modbus.close()
