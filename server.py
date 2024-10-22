import subprocess
import time
from adb_controller import try_connect

def server_process_factory(addr: str):
    adb_client = try_connect(addr)
    device = adb_client.device_list()[0]
    device.push("scrcpy-server", "/data/local/tmp/scrcpy-server-manual.jar")
    device.forward("tcp:1234", "localabstract:scrcpy")

    command = "CLASSPATH=/data/local/tmp/scrcpy-server-manual.jar app_process / com.genymobile.scrcpy.Server 2.7 tunnel_forward=true video=false audio=false control=true cleanup=false raw_stream=true max_size=1920"
    try:
        process = subprocess.Popen(
            ['adb', 'shell', command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        print("[Error] Failed to start subprocess: ", e)
        exit(1)

    output = process.stdout.readline() # type: ignore
    print(output)
    time.sleep(0.5)

    return process
