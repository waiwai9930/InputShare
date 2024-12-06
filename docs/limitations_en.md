# Known Limitations

## Connection Disconnects After Device Screen Turns Off

After the program successfully connects, if either the computer or Android device turns off the screen, the connection will be lost. To continue using the program, it is necessary to restart it and reconnect.

**Solution**: The program currently offers a "Keep Screen On" setting, which can prevent the Android device from turning off the screen, thus mitigating this limitation.

## Conflict with Bonjour

Some similar software, such as [barrier](https://github.com/debauchee/barrier) and [deskflow](https://github.com/deskflow/deskflow), use [Bonjour](https://developer.apple.com/bonjour/) to simplify network connections. However, based on feedback from some users, when running barrier and starting Bonjour on the computer, and then using this software, the connection success rate of this software is significantly reduced.

**Solution**: The exact cause of the conflict between this software and Bonjour is still unknown. You can try connecting with this software first, and then start barrier to avoid this issue.
