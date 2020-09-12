import sys
from os.path import join, realpath

Import("env")

# This dict contains every supported libopencm3 processor.
# For each microcontroller, select the corresponding FreeRTOS port folder:
devices = {
    "STM32F0": "ARM_CM0",
    "STM32F1": "ARM_CM3",
    "STM32F2": "ARM_CM3",
    "STM32F3": "ARM_CM4F",
    "STM32F4": "ARM_CM4F",
    "STM32F7": "ARM_CM7/r0p1",
    "STM32L0": "ARM_CM0",
    "STM32L1": "ARM_CM3",
    "STM32L4": "ARM_CM4F",
    "STM32G0": "ARM_CM0",
    "STM32G4": "ARM_CM4F",
    "STM32H7": "ARM_CM4F",
    "GD32F1X0": "ARM_CM3",
    "EFM32TG": "ARM_CM3",
    "EFM32G": "ARM_CM3",
    "EFM32LG": "ARM_CM3",
    "EFM32GG": "ARM_CM3",
    "EFM32HG": "ARM_CM0",
    "EFM32WG": "ARM_CM4F",
    "EZR32WG": "ARM_CM4F",
    "LPC13XX": "ARM_CM3",
    "LPC17XX": "ARM_CM3",
    "LPC43XX_M4": "ARM_CM4F",
    "LPC43XX_M0": "ARM_CM0",
    "SAM3A": "ARM_CM3",
    "SAM3N": "ARM_CM3",
    "SAM3S": "ARM_CM3",
    "SAM3U": "ARM_CM3",
    "SAM3X": "ARM_CM3",
    "SAM4L": "ARM_CM4F",
    "SAMD": "ARM_CM0",
    "VF6XX": "ARM_CM4F",
    "PAC55XX": "ARM_CM4F",
    "LM3S": "ARM_CM3",
    "LM4F": "ARM_CM4F",
    "MSP432E4": "ARM_CM4F",
    "SWM050": "ARM_CM0"
}

#env.Append(CPPPATH=["FreeRTOS-Kernel/portable/GCC/ARM_CM7"])

port = []

# Check all definitions and try to find matching libopencm3 definition:
for item in env.get("CPPDEFINES", []):
    if isinstance(item, tuple):
        if item[0] in devices:
            port.append(item[0])

# Throw exception if no defines match a libopencm3 device name:
if len(port) == 0:
    sys.stderr.write("Error: No Libopencm3 device defined for FreeRTOS!\n")
    env.Exit(1)
# Throw exception if more than one libopencm3 device name is defined:
elif len(port) > 1:
    sys.stderr.write("Error!: Multiple Libopencm3 devices defined: %s\n\
Using %s as default device.\n" % (" ".join(port), port[0]))
    env.Exit(1)
# Else, add the appropriate port folders to the include path and source filter:
else:
    print("PlatformIO-FreeRTOS: building for", port[0])
    env.Append(CPPPATH=[realpath("FreeRTOS-Kernel/include")])
    env.Append(CPPPATH=[realpath(join("FreeRTOS-Kernel/portable/GCC/", devices[port[0]]))])
    env.Replace(SRC_FILTER=[
            "+<FreeRTOS-Kernel/>",
            "-<FreeRTOS-Kernel/portable/>",
            "+<FreeRTOS-Kernel/portable/MemMang/heap_4.c>",
            join("+<FreeRTOS-Kernel/portable/GCC/", devices[port[0]], ">")
        ])
    # FreeRTOSConfig.h is located in the project space, outside of the lib:
    env.Append(CPPPATH=env.get("PROJECT_INCLUDE_DIR", []))
