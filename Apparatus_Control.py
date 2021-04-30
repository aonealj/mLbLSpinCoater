# code to run the apparatus

# import required libraries
import serial
import time



# establish communications ports

# the com ports assignment can be found in the device manager
# to see all com ports, run 'python -m serial.tools.list_ports' in the terminal (cmd prompt)
# if the port assignments  change, update the code to match

# universal timeout for all connections
to = 5  # seconds

# define function to make a new serial connection
# place holder for an upgrade to do later.

# spin coater connection
sc = serial.Serial()
sc.port = 'COM9'
sc.baudrate = 19200
sc.timeout = to
sc.write_timeout = to
sc.open()

# syringe pump connections
sp_baudrate = 19200                 # default baudrate for NE-1000
sp1 = serial.Serial()
sp1.port = 'COM1'
sp1.baudrate = sp_baudrate
sp1.timeout = to
sc.write_timeout = to
sp1.open()

sp2 = serial.Serial()
sp2.port = 'COM2'
sp2.baudrate = sp_baudrate
sp2.timeout = to
sc.write_timeout = to
sp2.open()

sp3 = serial.Serial()
sp3.port = 'COM26'
sp3.baudrate = sp_baudrate
sp3.timeout = to
sc.write_timeout = to
sp3.open()

sp4 = serial.Serial()
sp4.port = 'COM28'
sp4.baudrate = sp_baudrate
sp4.timeout = to
sc.write_timeout = to
sp4.open()


# print port information and test for open.
print('spin coater connection')
print(sc)
print('connection open?', sc.isOpen())

print('syringe pump 1 (sp1) connection')
print(sp1)
print('connection open?', sp1.isOpen())

print('syringe pump 2 (sp2) connection')
print(sp2)
print('connection open?', sp2.isOpen())

print('syringe pump 3 (sp3) connection')
print(sp3)
print('connection open?', sp3.isOpen())

print('syringe pump 4 (sp4) connection')
print(sp4)
print('connection open?', sp4.isOpen())

print('Connections Run')
input('Press enter to continue')

# functions necessary to run the spin coater

# trasnforms strings into appropriate ascii bytes with ending characters (\r\n)
# cmd structure specific to spin coater
def cmdsc(inputChar):
    stringInput = str(inputChar) + '\r\n'
    return bytes(stringInput, 'ascii')


# define a program to startup the connection with the motor
def motorStartup(PWM=110, slope=950, intercept=550):
    # set motor Pulse Width Modulation (PWM)
    PWMstr = 'SetStartPWM,' + str(PWM)
    PWMin = cmdsc(PWMstr)
    sc.write(PWMin)
    time.sleep(1)                       # pause program to ensure clean coms. Might be able to be shorter.

    # set motor profile slope
    slopeStr = 'SetSlope,' + str(slope)
    slopeIn = cmdsc(slopeStr)
    sc.write(slopeIn)
    time.sleep(1)

    # set motor profile intercept
    intStr = 'SetIntercept,' + str(intercept)
    intIn = cmdsc(intStr)
    sc.write(intIn)
    time.sleep(1)

    # turn on the motor
    onCmd = 'BLDCon'
    onCmdByt = cmdsc(onCmd)
    sc.write(onCmdByt)
    time.sleep(1)

    print('Spin Coater Motor Startup Complete')


# function to set the motor speed
def setSpeed(rpm):
    rpmStr = 'SetRPM,' + str(rpm)
    rpmIn = cmdsc(rpmStr)
    sc.write(rpmIn)


# function to query the motor for it's speed
def getSpeed():
    getSpeed = cmdsc('GetRPM')
    sc.write(getSpeed)
    current_speed = sc.read_until(bytes('\n\r', 'ascii'))
    print(current_speed.decode())


# function to turn off the motor
def motorShutoff():
    setSpeed(0)
    time.sleep(5)
    sc.write(cmdsc('BLDCoff'))



# functions necessary to run the syringe pumps

# properly format input for the syringe pumps
def cmdsp(inputChar2):
    stringInput2 = str(inputChar2) + '\r'
    return bytes(stringInput2, 'ascii')


# command to change the diameter
# keep space between command code and associated inputs
def setDIAcmd(dia):                         #units are mm
    DIAstr = 'DIA ' + str(dia)
    return cmdsp(DIAstr)


# command to select phase num
def selPHN(phaseNum):
    phaseNumStr = 'PHN ' + str(phaseNum)
    return cmdsp(phaseNumStr)


# set function to pumping rate type
def funcRate():
    funcRateStr = 'FUN RAT'
    return cmdsp(funcRateStr)


# set rate w/correct units
def pumpRate(pumping_rate, pumping_units):
    pumpRateStr = 'RAT ' + str(pumping_rate) + ' ' + str(pumping_units)
    return cmdsp(pumpRateStr)


# set rate w/o units
def pump_rate_nu(pumping_rate):
    return cmdsp('RAT ' + str(pumping_rate))

# function to set the volume
def setVol(pumpVol):
    pumpVolStr = 'VOL ' + str(pumpVol)
    return cmdsp(pumpVolStr)


# function to set the volume units--this cannot be combined with the setting the units
# see the manual for the valid inputs
def setVolUnits(pumpVolUnits):
    pumpVolUnitsStr = 'VOL ' + str(pumpVolUnits)
    return cmdsp(pumpVolUnitsStr)


# function for cmd to set pump direction
def setDir(pumpDir):
    pumpDirStr = 'DIR ' + str(pumpDir)
    return cmdsp(pumpDirStr)


# function for cmd to input stop set
def setStp():
    stpStr = 'FUN STP'
    return cmdsp(stpStr)


def runPrgmNum(PHS_num):
    PHS_num_str = 'RUN ' + str(PHS_num)
    return cmdsp(PHS_num_str)



##Code to run the cycle

# motor cycle function
# upgrade: don't start the dwell till motor speed reaches set point
def motorCycle(top_speed, spin_time):
    setSpeed(top_speed)
    time.sleep(spin_time)  # spin_time is in seconds
    setSpeed(0)


# operation loop

num_cycles = int(input('INPUT REQUIRED--How many cycles would you like to run?: '))
num_cycles_list = list(range(num_cycles))

vol_dep = int(input('INPUT REQUIRED--Volume to deposit every step (mL): '))
vol_withdrawl = 1  # mL, the amount to withdrawl to prevent dripping

speed_spin = int(input('At what speed (rpm) should the spin coater spin? (default 3 krpm) ') or '3000')
spin_dwell = 30  # seconds-> delay for how long to spin

# lead_vol =  5                            #mL--ignore only useful for autopriming of leads, which isn't in this code
# prgm assumes the leads have been primed

dia_input = int(input('What is the diameter (mm) of the syringe? (default 20 mm) ') or '20')

rate_dep = 8  # ml/min based on E.P. Chan's paper

# set diameter for the different pumps
# assumes same syringes for all pumps
sp1.write(setDIAcmd(dia_input))
sp2.write(setDIAcmd(dia_input))
sp3.write(setDIAcmd(dia_input))
sp4.write(setDIAcmd(dia_input))

# program pumps

# sp1
print('Programming Pump 1')
# phase 1--pumping
sp1.write(selPHN(1))  # select phase 1
time.sleep(1)
sp1.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp1.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp1.write(setVol(vol_dep))  # set the volume for pumping
time.sleep(1)
sp1.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp1.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 2--withdraw to prevent dripping
sp1.write(selPHN(2))  # select phase 2
time.sleep(1)
sp1.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp1.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp1.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp1.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp1.write(setDir('WDR'))
time.sleep(1)

# phase 3--stop
sp1.write(selPHN(3))  # select phase 3
time.sleep(1)
sp1.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

# phase 4--pumping
sp1.write(selPHN(4))  # select phase 1
time.sleep(1)
sp1.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp1.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
vol_dep2 = vol_dep + vol_withdrawl
time.sleep(1)
sp1.write(setVol(vol_dep2))  # set the volume for pumping
time.sleep(1)
sp1.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp1.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 5--withdraw to prevent dripping
sp1.write(selPHN(5))  # select phase 2
time.sleep(1)
sp1.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp1.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp1.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp1.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp1.write(setDir('WDR'))
time.sleep(1)

# phase 6--stop
sp1.write(selPHN(6))  # select phase 3
time.sleep(1)
sp1.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

print('Finished Programming Pump 1')

# sp2
print('Programming Pump 2')
# phase 1--pumping
sp2.write(selPHN(1))  # select phase 1
time.sleep(1)
sp2.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp2.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp2.write(setVol(vol_dep))  # set the volume for pumping
time.sleep(1)
sp2.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp2.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 2--withdraw to prevent dripping
sp2.write(selPHN(2))  # select phase 2
time.sleep(1)
sp2.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp2.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp2.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp2.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp2.write(setDir('WDR'))
time.sleep(1)

# phase 3--stop
sp2.write(selPHN(3))  # select phase 3
time.sleep(1)
sp2.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

# phase 4--pumping
sp2.write(selPHN(4))  # select phase 1
time.sleep(1)
sp2.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp2.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
vol_dep2 = vol_dep + vol_withdrawl
time.sleep(1)
sp2.write(setVol(vol_dep2))  # set the volume for pumping
time.sleep(1)
sp2.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp2.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 5--withdraw to prevent dripping
sp2.write(selPHN(5))  # select phase 2
time.sleep(1)
sp2.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp2.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp2.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp2.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp2.write(setDir('WDR'))
time.sleep(1)

# phase 6--stop
sp2.write(selPHN(6))  # select phase 3
time.sleep(1)
sp2.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

print('Finished Programming Pump 2')

# sp3
print('Programming Pump 3')
# phase 1--pumping
sp3.write(selPHN(1))  # select phase 1
time.sleep(1)
sp3.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp3.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp3.write(setVol(vol_dep))  # set the volume for pumping
time.sleep(1)
sp3.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp3.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 2--withdraw to prevent dripping
sp3.write(selPHN(2))  # select phase 2
time.sleep(1)
sp3.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp3.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp3.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp3.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp3.write(setDir('WDR'))
time.sleep(1)

# phase 3--stop
sp3.write(selPHN(3))  # select phase 3
time.sleep(1)
sp3.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

# phase 4--pumping
sp3.write(selPHN(4))  # select phase 1
time.sleep(1)
sp3.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp3.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
vol_dep2 = vol_dep + vol_withdrawl
time.sleep(1)
sp3.write(setVol(vol_dep2))  # set the volume for pumping
time.sleep(1)
sp3.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp3.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 5--withdraw to prevent dripping
sp3.write(selPHN(5))  # select phase 2
time.sleep(1)
sp3.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp3.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp3.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp3.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp3.write(setDir('WDR'))
time.sleep(1)

# phase 6--stop
sp3.write(selPHN(6))  # select phase 3
time.sleep(1)
sp3.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

print('Finished Programming Pump 3')

# sp4
print('Programming Pump 4')
# phase 1--pumping
sp4.write(selPHN(1))  # select phase 1
time.sleep(1)
sp4.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp4.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp4.write(setVol(vol_dep))  # set the volume for pumping
time.sleep(1)
sp4.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp4.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 2--withdraw to prevent dripping
sp4.write(selPHN(2))  # select phase 2
time.sleep(1)
sp4.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp4.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp4.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp4.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp4.write(setDir('WDR'))
time.sleep(1)

# phase 3--stop
sp4.write(selPHN(3))  # select phase 3
time.sleep(1)
sp4.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

# phase 4--pumping
sp4.write(selPHN(4))  # select phase 1
sp4.write(funcRate())  # make phase 1 a pump rate program
time.sleep(1)
sp4.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
vol_dep2 = vol_dep + vol_withdrawl
time.sleep(1)
sp4.write(setVol(vol_dep2))  # set the volume for pumping
time.sleep(1)
sp4.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp4.write(setDir('INF'))  # set to infuse
time.sleep(1)

# phase 5--withdraw to prevent dripping
sp4.write(selPHN(5))  # select phase 2
time.sleep(1)
sp4.write(funcRate())  # make phase 2 a pump rate program
time.sleep(1)
sp4.write(pumpRate(rate_dep, 'MM'))  # set the pumping rate and units (mL/min)
time.sleep(1)
sp4.write(setVol(vol_withdrawl))  # set the volume to withdrawl
time.sleep(1)
sp4.write(setVolUnits('ML'))  # set vol units to mL
time.sleep(1)
sp4.write(setDir('WDR'))
time.sleep(1)

# phase 6--stop
sp4.write(selPHN(6))  # select phase 3
time.sleep(1)
sp4.write(setStp())  # set phase 3 to be a stop phase
time.sleep(1)

print('Finished Programming Pump 4')

rxn_time = 20  # time b/w sending the cmd for pumping and the start of the motor cycle. Allows for complete pumping and rxn

for i in num_cycles_list:
    cycle_num = str(i + 1)
    print('Running cycle ', cycle_num)

    # separate the first run
    if i == 0:
        # pump 1
        print('Pumping Fluid 1')
        sp1.write(runPrgmNum(1))
        pumping_wait = (vol_dep / rate_dep * 60)  # time the pump will take
        time.sleep(pumping_wait)
        sp1.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 2
        print('Pumping Fluid 2')
        sp2.write(runPrgmNum(1))
        time.sleep(pumping_wait)
        sp2.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 3
        print('Pumping Fluid 3')
        sp3.write(runPrgmNum(1))
        time.sleep(pumping_wait)
        sp3.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 4
        print('Pumping Fluid 4')
        sp4.write(runPrgmNum(1))
        time.sleep(pumping_wait)
        sp4.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        print('End Step ', str(cycle_num))
    # all subsequent steps
    else:
        # pump 1
        print('Pumping Fluid 1')
        sp1.write(runPrgmNum(4))
        pumping_wait2 = (
                    vol_dep2 / rate_dep * 60)  # updated time delay to consider increased pumping (this is slight but might be noticeable.
        time.sleep(pumping_wait2)
        sp1.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 2
        print('Pumping Fluid 2')
        sp2.write(runPrgmNum(4))
        time.sleep(pumping_wait2)
        sp2.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 3
        print('Pumping Fluid 3')
        sp3.write(runPrgmNum(4))
        time.sleep(pumping_wait2)
        sp3.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        # pump 4
        print('Pumping Fluid 4')
        sp4.write(runPrgmNum(4))
        time.sleep(pumping_wait2)
        sp4.write(runPrgmNum(2))
        time.sleep(rxn_time)
        print('Starting spin')
        motorCycle(speed_spin, spin_dwell)

        print('End Step ', str(cycle_num))

print('Cycles Complete, initiating shutdown')


# shutdown apparatus and get to a good state

# funciton to turnoff the spin coater
def sc_shutdown():
    setSpeed(0)
    time.sleep(30)
    motorShutoff()


sc_shutdown()

print('Program Complete')
