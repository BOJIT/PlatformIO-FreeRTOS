# PlatformIO-FreeRTOS
PlatformIO Wrapper for FreeRTOS based on libopencm3

## Supported Frameworks
- libopencm3

## Supported Platforms
- ST STM32
- GigaDevice GD32V
- Silicon Labs EFM32
- NXP LPC
- Atmel SAM

## Usage
Under your global environment, add the library to ```libdeps```, using either the string **"PlatformIO-FreeRTOS"** or by using the GitHub URL. If using the URL make sure that submodules are cloned recursively.

Alternatively, simply add the library to the ```libs``` folder in your PlatformIO project. The library handles configuring FreeRTOS for your microcontroller's architecture. By default this library wrapper defaults to using ```heap_4.c``` as the FreeRTOS dynamic memory allocation scheme.

Note that the library expects there to be a ```FreeRTOSConfig.h``` file located somewhere in your includePath. IF the config file is not present, compilation will fail!

## Notes
This library has been tested for the following architectures:

- STM32F1
- STM32F4
- STM32F7

The rest of the architectures supported by libopencm3 are added based on the type of ARM core specified in the datasheet. Note that for some devices, this isn't always a direct match. For example, certain Cortex-M7 devices work better with the ARM_CM4F port of FreeRTOS. The STM32H7 line sometimes has both a Cortex-M7 and Cortex-M4 onboard, but the library uses ARM_CM4F by default. Feel free to tweak, submit a Pull Request if an architecture needs building differently, and confirm if architectures not listed here compile and function correctly. Currently, the FreeRTOS ports that utilise the MPU are not utilised.
