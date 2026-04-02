#!/bin/bash
# --------------------------------------------------------------------------
# Window to Another World - Configure Pins
# --------------------------------------------------------------------------
# License:   
# Copyright 2026 Clay Goldsmith
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# --------------------------------------------------------------------------
# 

### PIN ASSIGNMENTS:

### GPIO PINS 1 - 13: PWM OUTPUTS FOR LED MATRIX
config-pin P2_01 pwm # pin 1
# the actual P2_02 pin is 
config-pin P2_03 pwm # pin 2
config-pin P2_04 pwm # pin 3
config-pin P2_05 pwm # pin 4
config-pin P2_06 pwm # pin 5
config-pin P2_07 pwm # pin 6
config-pin P2_08 pwm # pin 7
config-pin P2_10 pwm # pin 8
config-pin P2_12 pwm # pin 9
config-pin P2_14 pwm # pin 10
config-pin P2_15 pwm # pin 11
config-pin P2_16 pwm # pin 12
config-pin P2_17 pwm # pin 13

### GPIO PIN 14: PWN OUTPUT FOR BUZZER
config-pin P2_18 pwm # pin 14

### GPIO PINS 15 - 18: DIGITAL OUTPUTS FOR BUTTONS
config-pin P2_19 gpio # pin 15
config-pin P2_20 gpio # pin 16
config-pin P2_21 gpio # pin 17
config-pin P2_22 gpio # pin 18

### POCKETBEAGLE I2C PINS: IMU 
config-pin P2_09 i2c # I2C1_SCL
config-pin P2_11 i2c # I2C1_SDA

