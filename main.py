from pyautd3.driver.geometry.rotation import EulerAngles
import numpy as np, os, keyboard, time
from pyautd3 import (
    AUTD3,
    Controller,
    Duration,
    FixedSchedule,
    Focus,
    FocusOption,
    GainSTM,
    GainSTMMode,
    GainSTMOption,
    GainGroup,
    Hz,
    Intensity,
    Null,
    ParallelMode,
    SenderOption,
    Silencer,
    Static,
)
from pyautd3.link.twincat import TwinCAT

w = AUTD3.DEVICE_WIDTH
h = AUTD3.DEVICE_HEIGHT
autds = (
    AUTD3(pos=[0.0, 2*h, 10.0], rot=EulerAngles.XYZ([np.pi * rad, - np.pi/2 * rad, 0.0 * rad])), 
    AUTD3(pos=[0.0, 2*h, w+10.0], rot=EulerAngles.XYZ([np.pi * rad, - np.pi/2 * rad, 0.0 * rad])), 
    AUTD3(pos=[0.0, h, w+10.0], rot=EulerAngles.XYZ([np.pi * rad, - np.pi/2 * rad, 0.0 * rad])), 
    AUTD3(pos=[0.0, h, 10.0], rot=EulerAngles.XYZ([np.pi * rad, - np.pi/2 * rad, 0.0 * rad])), 
    AUTD3(pos=[w-15.0, h, 0.0], rot=EulerAngles.XYZ([np.pi * rad, 0.0 * rad, 0.0 * rad])), 
    AUTD3(pos=[w-15.0, 2*h, 0.0], rot=EulerAngles.XYZ([np.pi * rad, 0.0 * rad, 0.0 * rad])), 
    AUTD3(pos=[2*w-15.0, 2*h, 0.0], rot=EulerAngles.XYZ([np.pi * rad, 0.0 * rad, 0.0 * rad])), 
    AUTD3(pos=[2*w-15.0, h, 0.0], rot=EulerAngles.XYZ([np.pi * rad, 0.0 * rad, 0.0 * rad])), 
    AUTD3(pos=[2*w-5.0, 10.0, 0.0], rot=[1, 0, 0, 0]), 
    AUTD3(pos=[2*w-5.0, h+10.0, 0.0], rot=[1, 0, 0, 0]), 
    AUTD3(pos=[3*w, 2*h, w], rot=EulerAngles.XYZ([np.pi * rad, np.pi/2 * rad, 0.0 * rad])),
    AUTD3(pos=[3*w, h, w], rot=EulerAngles.XYZ([np.pi * rad, np.pi/2 * rad, 0.0 * rad])),
    AUTD3(pos=[3*w, h, 2*w], rot=EulerAngles.XYZ([np.pi * rad, np.pi/2 * rad, 0.0 * rad])),
    AUTD3(pos=[3*w, 2*h, 2*w], rot=EulerAngles.XYZ([np.pi * rad, np.pi/2 * rad, 0.0 * rad])),
)

if __name__ == "__main__":
    point_num = 7 # points on circle
    radius = 45.0 # radius of circle
    x, y, z = 0.0, 0.0, 400.0
    x_min, x_max = -100.0, 100.0
    y_min, y_max = -150.0, 150.0
    z_min, z_max = 200.0, 700.0
    prev_x, prev_y, prev_z = None, None, None
    step = 5.0 # dist per 1-loop

    outer_intensity = 0
    prev_pow = None

    with Controller.open(
        autds,
        TwinCAT(),
    ) as autd:
        firmware_version = autd.firmware_version()
        print("\n".join([f"[{i}]: {firm}" for i, firm in enumerate(firmware_version)],),)
        sender = autd.sender(
            SenderOption(
                send_interval=Duration.from_millis(1),
                receive_interval=Duration.from_millis(1),
                timeout=Duration.from_millis(0),
                parallel=ParallelMode.Auto,
                strict=False,
            ),
            FixedSchedule(),
        )
        sender.send(Silencer())
        m = Static()

        while True:
            if keyboard.is_pressed("esc"):
                print("quit")
                break

            # enhance outer tr's power
            if keyboard.is_pressed("p"): outer_intensity = min(outer_intensity+16, 0xff) # right
            elif keyboard.is_pressed("l"): outer_intensity = max(outer_intensity-16, 0) # left
            # move
            elif keyboard.is_pressed("d"): x = min(x + step, x_max) # right
            elif keyboard.is_pressed("a"): x = max(x - step, x_min) # left
            elif keyboard.is_pressed("q"): y = min(y + step, y_max) # back
            elif keyboard.is_pressed("e"): y = max(y - step, y_min) # forward
            elif keyboard.is_pressed("w"): z = min(z + step, z_max) # up
            elif keyboard.is_pressed("s"): z = max(z - step, z_min) # down

            # if pressed key
            if (x != prev_x or y != prev_y or z != prev_z or prev_pow != outer_intensity):
                prev_x, prev_y, prev_z, prev_pow = x, y, z, outer_intensity

                center = autd.center() + np.array([x, y, z])
                time.sleep(0.2) # (s) for chattering (like)
                gains = [] # Group list 
                for theta in (2.0*np.pi/point_num *i for i in range(point_num)):
                    max_focus = Focus(
                        pos = center + radius * np.array([np.cos(theta), np.sin(theta), 0]),
                        option = FocusOption(),
                    )
                    min_focus = Focus(
                        pos = center + radius * np.array([np.cos(theta), np.sin(theta), 0]),
                        option = FocusOption(intensity=Intensity(int(outer_intensity))),
                    )
                    gain = GainGroup(
                        # activate Transducer within 150mm from center of circle
                        key_map = lambda _: lambda tr: "in" if np.linalg.norm(tr.position()[:2] - center[:2]) <= 150.0 else "out",
                        gain_map={"in": max_focus, "out": min_focus},
                    )
                    gains.append(gain)

                stm = GainSTM(
                    gains,
                    config = 100 * Hz,
                    option = GainSTMOption(mode = GainSTMMode.PhaseIntensityFull,),
                ).into_nearest()

                sender.send((m, stm))
                print(f"x: {x:.2f}mm, y: {y:.2f}mm, z: {z:.2f}mm, min_power: {outer_intensity}")
