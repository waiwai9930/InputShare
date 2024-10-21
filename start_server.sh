adb push scrcpy-server /data/local/tmp/scrcpy-server-manual.jar
adb forward tcp:1234 localabstract:scrcpy
adb shell CLASSPATH=/data/local/tmp/scrcpy-server-manual.jar app_process / com.genymobile.scrcpy.Server 2.7 tunnel_forward=true video=false audio=false control=true cleanup=false raw_stream=true max_size=1920