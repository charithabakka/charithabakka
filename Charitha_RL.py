# Show status of board and software configuration
import src.cmd_modules.IfxTx2Rx16 as IfxTx2Rx16
import time as time
import matplotlib.pyplot as plt
from numpy import *
import numpy as np
from datetime import datetime
import json
import time
#print("Iniciando Delay")
#time.sleep(7)
#print("Passuou Delay")
c0 = 3e8;

# --------------------------------------------------------------------------
# Setup Connection
# --------------------------------------------------------------------------
# Brd = IfxTx2Rx16.IfxTx2Rx16('RadServe', '10.116.64.43')
Brd = IfxTx2Rx16.IfxTx2Rx16('RadServe', '127.0.0.1')

Brd.BrdRst()
Brd.BrdPwrEna()

Brd.BrdDispSwVers();
Brd.BrdDispInf()
# --------------------------------------------------------------------------
# Configure RF Transceivers
# --------------------------------------------------------------------------
Brd.RfRxEna();

TxPwr = 60
Brd.RfTxEna(1, TxPwr)


TxPosn = Brd.RfGet('TxPosn');
RxPosn = Brd.RfGet('RxPosn');

# --------------------------------------------------------------------------
# ReadCalibration data
# --------------------------------------------------------------------------
dCalCfg = {
    "Mask": 1,
    "Len": 32
}
CalData = Brd.BrdGetCalData(dCalCfg)

Brd.Set('NrChn', 4)
# --------------------------------------------------------------------------
# Use clock from frontend with 80 MHz for synchronous sampling
# --------------------------------------------------------------------------
Brd.Set('ClkSrc', 2, 80e6);

# --------------------------------------------------------------------------
# Configure Connection for RadarLog
# --------------------------------------------------------------------------
#Brd.ConSet('Mult', 16)
Brd.ConSet('BufSiz', 64)
Brd.ConSet('Mult', 32)
#Brd.ConSet('BufSiz', 1048)
Brd.Set('UsbTimeout', 20000)

# --------------------------------------------------------------------------
# Configure Up-Chirp
# --------------------------------------------------------------------------
dCfg = dict()
dCfg['fStrt'] = 76.5e9
dCfg['fStop'] = 77.5e9
# dCfg['TRampUp'] = 204.8e-6
# dCfg['TRampDo'] = 64e-6
# dCfg['TInt'] = 250e-3
dCfg['TRampUp'] = 0.25*66e-6
dCfg['TRampDo'] = 16e-6
dCfg['TInt'] = 0.05e-3
dCfg['N'] = 1024
# dCfg['NrFrms'] = 250
dCfg['NrFrms'] = 1000
dCfg['NLoop'] = 800
dCfg['IniTim'] = 10e-3
dCfg['CfgTim'] = 40e-3
dCfg['IniEve'] = 0
#dCfg['TxPwr'] = TxPwr



lRampCfg = list()
#--------------------------------------------------------------------------
# Configure Up-Chirp
# 0: Power Off
# 1: TX1 on
# 2: TX2 on
# 3: TX3 Off
# 4: TX4 Off
#--------------------------------------------------------------------------
# Up Chirp and trigger sampling
dRampCfg = dict()
dRampCfg['fStrt'] = dCfg['fStrt'];
dRampCfg['fStop'] = dCfg['fStop'];
dRampCfg['TRamp'] = dCfg['TRampUp'];
dRampCfg['RampCfg'] = Brd.SampSeq + Brd.PaCtrl_Tx1;
lRampCfg.append(dRampCfg)
# Downchirp with no sampling
dRampCfg = dict()
dRampCfg['fStrt'] = dCfg['fStop'];
dRampCfg['fStop'] = dCfg['fStrt'];
dRampCfg['TRamp'] = dCfg['TRampDo'];
dRampCfg['RampCfg'] = Brd.PaCtrl_Tx1;
lRampCfg.append(dRampCfg)
Tp = lRampCfg[0]['TRamp'] + lRampCfg[1]['TRamp']

Timeout = dCfg['TInt'] * dCfg['NrFrms'] + 2

#--------------------------------------------------------------------------
# Configure Receiver
#--------------------------------------------------------------------------

# Brd.Set('Camera_Type', 32)
#Brd.Set('CicStages', 2);
Brd.Set('fAdc', 40e6)# ok
Brd.Set('AfeGaindB', 20)# ok
Brd.Set('AfeHighPass', 0)# ok
Brd.Set('AfeLowNoise', 'Off');#ok
Brd.Set('AfeIntDcCoupling', 1);#ok
#Brd.Set('AfeFilt', 7e6);

Brd.Set('UsbTimeout', Timeout / 1e-3);
Brd.RfMeas('RccMs', lRampCfg, dCfg);


# --------------------------------------------------------------------------
# Read actual configuration
# --------------------------------------------------------------------------
NrChn = Brd.Get('NrChn')
N = Brd.Get('N')
fs = Brd.Get('fs')

# --------------------------------------------------------------------------
# Store parameters to file
# --------------------------------------------------------------------------
Brd.SetFileParam('MeasDescription', 'Generate Measdescription')
Brd.SetFileParam('MeasDate', '11')
Brd.ConSetFileParam('TxPosn', TxPosn, 'ARRAY64')
Brd.ConSetFileParam('RxPosn', RxPosn, 'ARRAY64')

Brd.ConSetFileParam('CalRe', ascontiguousarray(real(CalData)), 'ARRAY64')
Brd.ConSetFileParam('CalIm', ascontiguousarray(imag(CalData)), 'ARRAY64')

Brd.SetFileParam('fs', fs)
Brd.SetFileParam('FuSca', Brd.FuSca)
# Brd.SetFileParam('AdcGain', AdcGain)
# Brd.SetFileParam('AdcDcCoupl', AdcDcCoupl)
#Brd.ConSetFileParam('CalRe', np.ascontiguousarray(np.transpose(np.real(CalData))), 'ARRAY64')
#Brd.ConSetFileParam('CalIm', np.ascontiguousarray(np.transpose(np.imag(CalData))), 'ARRAY64')
Brd.ConSetFileParam('NrFrms', dCfg['NrFrms'], 'INT')
Brd.ConSetFileParam('NLoop', dCfg['NLoop'], 'INT')
Brd.ConSetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')
Brd.ConSetFileParam('fStop', dCfg['fStop'], 'DOUBLE')
Brd.ConSetFileParam('TRampUp', dCfg['TRampUp'], 'DOUBLE')
Brd.ConSetFileParam('TRampDo', dCfg['TRampDo'], 'DOUBLE')
Brd.ConSetFileParam('TInt', dCfg['TInt'], 'DOUBLE')
Brd.ConSetFileParam('MIMO', False, 'BOOL')
Brd.SetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')
Brd.SetFileParam('fStop', dCfg['fStop'], 'DOUBLE')
Brd.SetFileParam('TRampUp', dCfg['TRampUp'], 'DOUBLE')
Brd.SetFileParam('TRampDo', dCfg['TRampDo'], 'DOUBLE')
Brd.SetFileParam('IntVal', 10, 'INT')
Brd.SetFileParam('TestStr', 'text description of measurement.', 'STRING')
Brd.SetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')

print('NrChn: ', NrChn)
print('N: ', N)

Brd.Prnt('fs')

DataRate = N * dCfg['NLoop'] * NrChn * 16 / dCfg['TInt'];

print(['Rate: ', (DataRate / 1e6), ' MBit'])
# --------------------------------------------------------------------------
# Stream Data to File
# (1) File Name HDF5 file:
#  - use RadServe HDF5->Settings menu to select default folder
# (2) Max number of packets stored
# --------------------------------------------------------------------------
# Streaming is terminated after wait 10 s or after max packets is reached
Brd.BrdDispLmkSts()
print('Stream Measurement Data to File')

# time_wait = 6*dCfg['NrFrms']
time_wait = (((dCfg['NrFrms']+dCfg['NrFrms'])*dCfg['N']*dCfg['NLoop'])/10000)
timestr = time.strftime("%Y%m%d_%H%M_%S")
print('Time to wait: ' + str(0.018*time_wait) + 's')
Brd.CreateFile('Measurement_4Ch_' + str(timestr), 0.3*time_wait)
time.sleep(10)
#Data = Brd.BrdGetData(1);
#np.savetxt('test.out', Data ,delimiter=',')   # X is an array
#print(Data.tolist())

Brd.CloseFile()

#time.sleep(0.1)

# for Cycles in range(0, 200):

#     Data        =   Brd.BrdGetData(32);
#     FrmCntr     =   Data[0,:]
#     print("FrmCntr:", FrmCntr)MeaMeasurement_8Ch_20220419_1233_08Measurement_8Ch_20220419_1233_08Measurement_8Ch_20220419_1233_08surement_8Ch_20220419_1233_08

del Brd

# --------------------------------------------------------------------------
# Setup Connection
# --------------------------------------------------------------------------
# Brd = IfxTx2Rx16.IfxTx2Rx16('RadServe', '10.116.64.43')
Brd = IfxTx2Rx16.IfxTx2Rx16('RadServe', '127.0.0.1')

Brd.BrdRst()
Brd.BrdPwrEna()

Brd.BrdDispSwVers();
Brd.BrdDispInf()
# --------------------------------------------------------------------------
# Configure RF Transceivers
# --------------------------------------------------------------------------
Brd.RfRxEna();

TxPwr = 60
Brd.RfTxEna(1, TxPwr)


TxPosn = Brd.RfGet('TxPosn');
RxPosn = Brd.RfGet('RxPosn');

# --------------------------------------------------------------------------
# ReadCalibration data
# --------------------------------------------------------------------------
dCalCfg = {
    "Mask": 1,
    "Len": 32
}
CalData = Brd.BrdGetCalData(dCalCfg)

Brd.Set('NrChn', 16)
# --------------------------------------------------------------------------
# Use clock from frontend with 80 MHz for synchronous sampling
# --------------------------------------------------------------------------
Brd.Set('ClkSrc', 2, 80e6);

# --------------------------------------------------------------------------
# Configure Connection for RadarLog
# --------------------------------------------------------------------------
#Brd.ConSet('Mult', 16)
Brd.ConSet('BufSiz', 64)
Brd.ConSet('Mult', 32)
#Brd.ConSet('BufSiz', 1048)
Brd.Set('UsbTimeout', 20000)

# --------------------------------------------------------------------------
# Configure Up-Chirp
# --------------------------------------------------------------------------
dCfg = dict()
dCfg['fStrt'] = 76.5e9
dCfg['fStop'] = 77.5e9
# dCfg['TRampUp'] = 204.8e-6
# dCfg['TRampDo'] = 64e-6
# dCfg['TInt'] = 250e-3
dCfg['TRampUp'] = 1*66e-6
dCfg['TRampDo'] = 16e-6
dCfg['TInt'] = 0.05e-3
dCfg['N'] = 0.5*1024
# dCfg['NrFrms'] = 250
dCfg['NrFrms'] = 1000
dCfg['NLoop'] = 800
dCfg['IniTim'] = 10e-3
dCfg['CfgTim'] = 40e-3
dCfg['IniEve'] = 0
#dCfg['TxPwr'] = TxPwr



lRampCfg = list()
#--------------------------------------------------------------------------
# Configure Up-Chirp
# 0: Power Off
# 1: TX1 on
# 2: TX2 on
# 3: TX3 Off
# 4: TX4 Off
#--------------------------------------------------------------------------
# Up Chirp and trigger sampling
dRampCfg = dict()
dRampCfg['fStrt'] = dCfg['fStrt'];
dRampCfg['fStop'] = dCfg['fStop'];
dRampCfg['TRamp'] = dCfg['TRampUp'];
dRampCfg['RampCfg'] = Brd.SampSeq + Brd.PaCtrl_Tx1;
lRampCfg.append(dRampCfg)
# Downchirp with no sampling
dRampCfg = dict()
dRampCfg['fStrt'] = dCfg['fStop'];
dRampCfg['fStop'] = dCfg['fStrt'];
dRampCfg['TRamp'] = dCfg['TRampDo'];
dRampCfg['RampCfg'] = Brd.PaCtrl_Tx1;
lRampCfg.append(dRampCfg)
Tp = lRampCfg[0]['TRamp'] + lRampCfg[1]['TRamp']

Timeout = dCfg['TInt'] * dCfg['NrFrms'] + 2

#--------------------------------------------------------------------------
# Configure Receiver
#--------------------------------------------------------------------------

# Brd.Set('Camera_Type', 32)
#Brd.Set('CicStages', 2);
Brd.Set('fAdc', 40e6)# ok
Brd.Set('AfeGaindB', 20)# ok
Brd.Set('AfeHighPass', 0)# ok
Brd.Set('AfeLowNoise', 'Off');#ok
Brd.Set('AfeIntDcCoupling', 1);#ok
#Brd.Set('AfeFilt', 7e6);

Brd.Set('UsbTimeout', Timeout / 1e-3);
Brd.RfMeas('RccMs', lRampCfg, dCfg);


# --------------------------------------------------------------------------
# Read actual configuration
# --------------------------------------------------------------------------
NrChn = Brd.Get('NrChn')
N = Brd.Get('N')
fs = Brd.Get('fs')

# --------------------------------------------------------------------------
# Store parameters to file
# --------------------------------------------------------------------------
Brd.SetFileParam('MeasDescription', 'Generate Measdescription')
Brd.SetFileParam('MeasDate', '11')
Brd.ConSetFileParam('TxPosn', TxPosn, 'ARRAY64')
Brd.ConSetFileParam('RxPosn', RxPosn, 'ARRAY64')

Brd.ConSetFileParam('CalRe', ascontiguousarray(real(CalData)), 'ARRAY64')
Brd.ConSetFileParam('CalIm', ascontiguousarray(imag(CalData)), 'ARRAY64')

Brd.SetFileParam('fs', fs)
Brd.SetFileParam('FuSca', Brd.FuSca)
# Brd.SetFileParam('AdcGain', AdcGain)
# Brd.SetFileParam('AdcDcCoupl', AdcDcCoupl)
#Brd.ConSetFileParam('CalRe', np.ascontiguousarray(np.transpose(np.real(CalData))), 'ARRAY64')
#Brd.ConSetFileParam('CalIm', np.ascontiguousarray(np.transpose(np.imag(CalData))), 'ARRAY64')
Brd.ConSetFileParam('NrFrms', dCfg['NrFrms'], 'INT')
Brd.ConSetFileParam('NLoop', dCfg['NLoop'], 'INT')
Brd.ConSetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')
Brd.ConSetFileParam('fStop', dCfg['fStop'], 'DOUBLE')
Brd.ConSetFileParam('TRampUp', dCfg['TRampUp'], 'DOUBLE')
Brd.ConSetFileParam('TRampDo', dCfg['TRampDo'], 'DOUBLE')
Brd.ConSetFileParam('TInt', dCfg['TInt'], 'DOUBLE')
Brd.ConSetFileParam('MIMO', False, 'BOOL')
Brd.SetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')
Brd.SetFileParam('fStop', dCfg['fStop'], 'DOUBLE')
Brd.SetFileParam('TRampUp', dCfg['TRampUp'], 'DOUBLE')
Brd.SetFileParam('TRampDo', dCfg['TRampDo'], 'DOUBLE')
Brd.SetFileParam('IntVal', 10, 'INT')
Brd.SetFileParam('TestStr', 'text description of measurement.', 'STRING')
Brd.SetFileParam('fStrt', dCfg['fStrt'], 'DOUBLE')

print('NrChn: ', NrChn)
print('N: ', N)

Brd.Prnt('fs')

DataRate = N * dCfg['NLoop'] * NrChn * 16 / dCfg['TInt'];

print(['Rate: ', (DataRate / 1e6), ' MBit'])
# --------------------------------------------------------------------------
# Stream Data to File
# (1) File Name HDF5 file:
#  - use RadServe HDF5->Settings menu to select default folder
# (2) Max number of packets stored
# --------------------------------------------------------------------------
# Streaming is terminated after wait 10 s or after max packets is reached
Brd.BrdDispLmkSts()
print('Stream Measurement Data to File')

# time_wait = 6*dCfg['NrFrms']
time_wait = (((dCfg['NrFrms']+dCfg['NrFrms'])*dCfg['N']*dCfg['NLoop'])/10000)
timestr = time.strftime("%Y%m%d_%H%M_%S")
print('Time to wait: ' + str(0.018*time_wait) + 's')
Brd.CreateFile('Measurement_16Ch_' + str(timestr), 0.3*time_wait)
time.sleep(10)
#Data = Brd.BrdGetData(1);
#np.savetxt('test.out', Data ,delimiter=',')   # X is an array
#print(Data.tolist())

Brd.CloseFile()

#time.sleep(0.1)

# for Cycles in range(0, 200):

#     Data        =   Brd.BrdGetData(32);
#     FrmCntr     =   Data[0,:]
#     print("FrmCntr:", FrmCntr)MeaMeasurement_8Ch_20220419_1233_08Measurement_8Ch_20220419_1233_08Measurement_8Ch_20220419_1233_08surement_8Ch_20220419_1233_08

del Brd