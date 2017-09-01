
from    machine import UART
from    utime   import sleep_ms
from    struct  import pack, unpack

class MotorBoardMD49 :

    # ============================================================================
    # ===( Constants )============================================================
    # ============================================================================

    # READ COMMANDS,
    GET_SPEED_1         = b'\x21'
    GET_SPEED_2         = b'\x22'
    GET_ENCODER_1       = b'\x23'
    GET_ENCODER_2       = b'\x24'
    GET_ENCODERS        = b'\x25'
    GET_VOLTS           = b'\x26'
    GET_CURRENT_1       = b'\x27'
    GET_CURRENT_2       = b'\x28'
    GET_VERSION         = b'\x29'
    GET_ACCELERATION    = b'\x2A'
    GET_MODE            = b'\x2B'
    GET_VI              = b'\x2C'
    GET_ERROR           = b'\x2D'
    
    # WRITE COMMANDS,
    SET_SPEED_1         = b'\x31'
    SET_SPEED_2_TURN    = b'\x32'
    SET_ACCELERATION    = b'\x33'
    SET_MODE            = b'\x34'
    RESET_ENCODERS      = b'\x35'
    DISABLE_REGULATOR   = b'\x36'
    ENABLE_REGULATOR    = b'\x37'
    DISABLE_TIMEOUT     = b'\x38'
    ENABLE_TIMEOUT      = b'\x39'

    # ============================================================================
    # ===( Constructor )==========================================================
    # ============================================================================

    def __init__(self, uartBus, txPinNum, rxPinNum) :
        txPinId = "P" + str(txPinNum)
        rxPinId = "P" + str(rxPinNum)
        self._uart = UART( uartBus,
                           baudrate = 38400,
                           bits     = 8,
                           parity   = None,
                           stop     = 1,
                           pins     = (txPinId, rxPinId, None, None) )
        self._mode = 0

    # ============================================================================
    # ===( Utils )================================================================
    # ============================================================================

    def _txCmd(self, cmdByte, valueByte=None) :
        if cmdByte is not None and len(cmdByte) == 1 and \
           ( valueByte is None or len(valueByte) == 1 ) :
            if valueByte is not None :
                buf = b'\x00' + cmdByte + valueByte
            else :
                buf = b'\x00' + cmdByte
            res = self._uart.write(buf)
            return ( res is not None and res == len(buf) )
        return False

    # ----------------------------------------------------------------------------

    def _rxRet(self, retSize) :
        ret = b''
        ok  = False
        for i in range(100) :
            buf = self._uart.readall()
            if buf is not None :
                ret += buf
                if len(ret) == retSize :
                    ok = True
                    break
            sleep_ms(10)
        return ret if ok else None

    # ----------------------------------------------------------------------------

    def bitIsUpInByte(self, bitPos, byte) :
        if bitPos >= 1 and bitPos <= 8 :
            return ( byte[0] & pack('B', 0 | 1 << 8-bitPos)[0] ) > 0
        return byte

    # ============================================================================
    # ===( Functions )============================================================
    # ============================================================================

    def GetSpeed1(self) :
        if self._txCmd(MotorBoardMD49.GET_SPEED_1) :
            ret = self._rxRet(1)
            if ret is not None :
                fmt = 'B' if self._mode == 0 or self._mode == 2 else 'b'
                return unpack(fmt, ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetSpeed2(self) :
        if self._txCmd(MotorBoardMD49.GET_SPEED_2) :
            ret = self._rxRet(1)
            if ret is not None :
                fmt = 'B' if self._mode == 0 or self._mode == 2 else 'b'
                return unpack(fmt, ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetEncoder1(self) :
        if self._txCmd(MotorBoardMD49.GET_ENCODER_1) :
            ret = self._rxRet(4)
            if ret is not None :
                return unpack('>i', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetEncoder2(self) :
        if self._txCmd(MotorBoardMD49.GET_ENCODER_2) :
            ret = self._rxRet(4)
            if ret is not None :
                return unpack('>i', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetEncoders(self) :
        if self._txCmd(MotorBoardMD49.GET_ENCODERS) :
            ret = self._rxRet(8)
            if ret is not None :
                return unpack('>ii', ret)
        return None

    # ----------------------------------------------------------------------------

    def GetVolts(self) :
        if self._txCmd(MotorBoardMD49.GET_VOLTS) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetCurrent1(self) :
        if self._txCmd(MotorBoardMD49.GET_CURRENT_1) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0] / 10
        return None

    # ----------------------------------------------------------------------------

    def GetCurrent2(self) :
        if self._txCmd(MotorBoardMD49.GET_CURRENT_2) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetVersion(self) :
        if self._txCmd(MotorBoardMD49.GET_VERSION) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetAcceleration(self) :
        if self._txCmd(MotorBoardMD49.GET_ACCELERATION) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetMode(self) :
        if self._txCmd(MotorBoardMD49.GET_MODE) :
            ret = self._rxRet(1)
            if ret is not None :
                return unpack('B', ret)[0]
        return None

    # ----------------------------------------------------------------------------

    def GetVI(self) :
        if self._txCmd(MotorBoardMD49.GET_VI) :
            ret = self._rxRet(3)
            if ret is not None :
                return unpack('BBB', ret)
        return None

    # ----------------------------------------------------------------------------

    def GetError(self) :
        if self._txCmd(MotorBoardMD49.GET_ERROR) :
            ret = self._rxRet(1)
            if ret is not None :
                return {
                    "MOTOR_1_TRIP"  : self.bitIsUpInByte(6, ret),
                    "MOTOR_2_TRIP"  : self.bitIsUpInByte(5, ret),
                    "MOTOR_1_SHORT" : self.bitIsUpInByte(4, ret),
                    "MOTOR_2_SHORT" : self.bitIsUpInByte(3, ret),
                    "OVER_30V"      : self.bitIsUpInByte(2, ret),
                    "UNDER_16V"     : self.bitIsUpInByte(1, ret)
                }
        return None

    # ----------------------------------------------------------------------------

    def SetSpeed1(self, value) :
        if self._mode == 0 or self._mode == 2 :
            fmt = 'B'
            if value < 0 or value > 255 :
                return False
        else :
            fmt = 'b'
            if value < -128 or value > 127 :
                return False
        return self._txCmd(MotorBoardMD49.SET_SPEED_1, pack(fmt, value))

    # ----------------------------------------------------------------------------

    def SetSpeed2Turn(self, value) :
        if self._mode == 0 or self._mode == 2 :
            fmt = 'B'
            if value < 0 or value > 255 :
                return False
        else :
            fmt = 'b'
            if value < -128 or value > 127 :
                return False
        return self._txCmd(MotorBoardMD49.SET_SPEED_2_TURN, pack(fmt, value))

    # ----------------------------------------------------------------------------

    def SetAcceleration(self, value) :
        if value >= 1 and value <= 10 :
            return self._txCmd(MotorBoardMD49.SET_ACCELERATION, pack('B', value))
        return False

    # ----------------------------------------------------------------------------

    def SetMode(self, mode) :
        if mode >= 0 and mode <= 3 :
            if self._txCmd(MotorBoardMD49.SET_MODE, pack('B', mode)) :
                self._mode = mode
                return True
        return False

    # ----------------------------------------------------------------------------

    def ResetEncoders(self) :
        return self._txCmd(MotorBoardMD49.RESET_ENCODERS)

    # ----------------------------------------------------------------------------

    def DisableRegulator(self) :
        return self._txCmd(MotorBoardMD49.DISABLE_REGULATOR)

    # ----------------------------------------------------------------------------

    def EnableRegulator(self) :
        return self._txCmd(MotorBoardMD49.ENABLE_REGULATOR)

    # ----------------------------------------------------------------------------

    def DisableTimeout(self) :
        return self._txCmd(MotorBoardMD49.DISABLE_TIMEOUT)

    # ----------------------------------------------------------------------------

    def EnableTimeout(self) :
        return self._txCmd(MotorBoardMD49.ENABLE_TIMEOUT)

    # ============================================================================
    # ============================================================================
    # ============================================================================
