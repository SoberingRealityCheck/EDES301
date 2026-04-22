### ADD HEADER ####

# Pin Configuration
#
# Led Connector       Signal meaning      BBB signal
# Row 1, Left Pin     Red 1               Gpio1[27]   gpio59  P2.2
# Row 1, Right Pin    Blue 1              Gpio1[26]   gpio58  P2.4
# Row 2, Left Pin     Green 1             Gpio1[25]   gpio57  P2.6
# Row 2, Right Pin    Ground              Ground
# Row 3, Left Pin     Red 2               Gpio0[23]   gpio23  P2.3
# Row 3, Right Pin    Blue 2              Gpio0[26]   gpio26  P1.34
# Row 4, Left Pin     Green 2             Gpio0[20]   gpio20  P1.20
# Row 4, Right Pin    Ground              Ground
# Row 5, Left Pin     Select A            Gpio1[12]   gpio44  P2.24
# Row 5, Right Pin    Select B            Gpio1[13]   gpio45  P2.33
# Row 6, Left Pin     Select C            Gpio1[14]   gpio46  P2.22
# Row 6, Right Pin    Select D            Gpio1[15]   gpio47  P2.18
# Row 7, Left Pin     Clock               Gpio1[20]   gpio52  P2.10
# Row 7, Right Pin    Latch               Gpio1[28]   gpio60  P2.8
# Row 8, Left Pin     Output Enable       Gpio1[18]   gpio50  P2.1
# Row 8, Right Pin    Ground              

config-pin  P2_02   gpio
config-pin  P2_04   gpio
config-pin  P2_06   gpio

config-pin  P2_03   gpio
config-pin  P1_34   gpio
config-pin  P1_20   gpio

config-pin  P2_24   gpio
config-pin  P2_33   gpio
config-pin  P2_22   gpio
config-pin  P2_18   gpio

config-pin  P2_10   gpio
config-pin  P2_08   gpio
config-pin  P2_01   gpio

