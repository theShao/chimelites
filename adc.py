#
# Using ebay adc from here: http://www.ebay.co.uk/itm/271692980871
#
# 4 channels but includes a few built in sensors that need to be disabled by removing jumpers
# From i2c end of the board:
# J1: ??
# J2: Photoresistor to ain0
# J3: ??
# Leave J1 and J3 off to and get analog from ain3 and light from ain0 seems to work.
# Discussion on control schema here: http://raspberrypi.stackexchange.com/questions/36983/how-to-change-read-channels-on-pcf8591

