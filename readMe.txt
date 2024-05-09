No external libraries were used throughout the project except those given under lib directory.

Sync monitor logo (PNG file is included in project files) was generated with an AI from given
description: "Heart logo with a title Sync Monitor". Then this png file was converted into bitmap
on http://www.arduinoblocks.com/web/help/olededitor. Little adjustments were made by hand like the
pixelated title and version without the title. Bytearrays of both are stored in logo.py file.

Idea for blinking led at the same rate as heart is not unique. It was seen on
https://blog.martinfitzpatrick.com/wemos-heart-rate-sensor-display-micropython/ while researching
how to work with heart rate sensor on Python. It is a good indicator when the signal is good as you
can compare it to your pulse.

History of records is stored in history.txt file. Each line being a record in json string format.

Sensor, the only external component, is connected to ADC_0 (GP26).

Device boots on automatically when given power.
On boot device connects to our groups' router with our credentials. Then it connects to mqtt broker via
IP which was looked over in router's settings.

Group 8: Max Kiannu, Chris Otewa, Viswak Ggautham.
