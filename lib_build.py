import sys
import os
import shutil

Import("env")

# Install GitPython for interacting with remote repositories
try:
    import git
except ImportError:
    env.Execute("$PYTHONEXE -m pip install GitPython")
    import git

################################# BUILD MACROS #################################

# For each microcontroller, select the corresponding FreeRTOS port folder:
devices = {
    # libopencm3 macros
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
    "SWM050": "ARM_CM0",

    # Arduino/STM32Cube macros
    "STM32F0xx": "ARM_CM0",
    "STM32F1xx": "ARM_CM3",
    "STM32F2xx": "ARM_CM3",
    "STM32F3xx": "ARM_CM4F",
    "STM32F4xx": "ARM_CM4F",
    "STM32F7xx": "ARM_CM7/r0p1",
    "STM32G0xx": "ARM_CM0",
    "STM32G4xx": "ARM_CM4F",
    "STM32H7xx": "ARM_CM4F",
    "STM32L0xx": "ARM_CM0",
    "STM32L1xx": "ARM_CM3",
    "STM32L4xx": "ARM_CM4F",
    "STM32L5xx": "ARM_CM33/non_secure",
    "STM32WBxx": "ARM_CM4F",
    "STM32WLxx": "ARM_CM4F"
}

################################## CONSTANTS ###################################

KERNEL_URL = "https://github.com/FreeRTOS/FreeRTOS-Kernel.git"
KERNEL_PATH = os.path.realpath('./FreeRTOS-Kernel')

############################### HELPER FUNCTIONS ###############################

def getRemoteTags(url):
    g = git.cmd.Git()
    blob = g.ls_remote(url, sort='-v:refname', tags=True, refs=True)
    entries = blob.split('\n')
    return list(map(lambda x: x.partition('refs/tags/')[2], entries))

def getLocalTag(path):
    g = git.Repo(path)
    return [str(next((tag for tag in g.tags if tag.commit == g.head.commit), None))]
    pass

################################## MAIN SCRIPT ##################################

port = []
freertos_tag = ""
tag_name = ""

# Check all definitions and try to find matching macro/definition:
for item in env.get("CPPDEFINES", []):
    if isinstance(item, tuple):
        if item[0] in devices:
            port.append(item[0])
        # Look for special tags while parsing the macros
        elif item[0] == 'FREERTOS_TAG':
            freertos_tag = item[1]
    else:
        if item in devices:
            port.append(item)

# Try to pull tags from remote repo
try:
    tags = getRemoteTags(KERNEL_URL)
except:
    if os.path.isdir(KERNEL_PATH):
        # If local kernel is available it can be used, but might not be up to date
        tags = getLocalTag(KERNEL_PATH)
        if not freertos_tag:
            sys.stderr.write("Could not get remote tags - the local kernel (%s) may not be the most up-to-date\n" % tags[0])
    else:
        sys.stderr.write("Could not get remote tags - check you can access %s:\n" % KERNEL_URL)
        env.Exit(1)

# Get requested tag name
if not freertos_tag:
    # Checkout latest tag
    for tag in tags:
        if tag.find("SMP") == -1:    # Do not include SMP tags
            tag_name = tag
            break
else:
    # Checkout specified tag
    for tag in tags:
        if freertos_tag == tag:
            tag_name = tag
    if not tag_name:
        sys.stderr.write("PlatformIO-FreeRTOS: Tag '%s' could not be found in local/remote repository!\n" % freertos_tag)
        env.Exit(1)

# Is local kernel the correct tag?
if not(os.path.isdir(KERNEL_PATH)):
    try:
        kernel = git.Repo.clone_from(KERNEL_URL, KERNEL_PATH, depth=1, b=tag_name)
    except:
        sys.stderr.write("Could not clone Kernel - check you can access %s:\n" % KERNEL_URL)
        env.Exit(1)
else:
    # Replace current kernel if wrong version
    if tag_name != getLocalTag(KERNEL_PATH)[0]:
        shutil.rmtree(KERNEL_PATH)
        kernel = git.Repo.clone_from(KERNEL_URL, KERNEL_PATH, depth=1, b=tag_name)

# Throw exception if no macros match a device name:
if len(port) == 0:
    sys.stderr.write("Error: No device defined for FreeRTOS! Please provide platform manually - options below:\n")
    device_keys = devices.keys()
    s = ' ,'.join(device_keys)
    sys.stderr.write(str(s) + '\n')
    env.Exit(1)
# Throw exception if more than one device name is defined:
elif len(port) > 1:
    sys.stderr.write("Error!: Multiple devices defined: %s\n Using %s as default device.\n" % (" ".join(port), port[0]))
    env.Exit(1)
# Else, add the appropriate port folders to the include path and source filter:
else:
    print("PlatformIO-FreeRTOS: building for", port[0])
    env.Append(CPPPATH=[os.path.realpath("FreeRTOS-Kernel/include")])
    env.Append(CPPPATH=[os.path.realpath(os.path.join("FreeRTOS-Kernel/portable/GCC/", devices[port[0]]))])
    env.Replace(SRC_FILTER=[
            "+<FreeRTOS-Kernel/>",
            "-<FreeRTOS-Kernel/portable/>",
            "+<FreeRTOS-Kernel/portable/MemMang/heap_4.c>",
            os.path.join("+<FreeRTOS-Kernel/portable/GCC/", devices[port[0]], ">")
        ])
    # FreeRTOSConfig.h is located in the project space, outside of the lib:
    env.Append(CPPPATH=env.get("PROJECT_INCLUDE_DIR", []))
