import numpy as np
from pyautd3 import (
    AUTD3,
    Controller,
    Focus,
    FocusOption,
    Hz,
    Silencer,
    Sine,
    SineOption,
)
from pyautd3.link.ethercrab import EtherCrab, EtherCrabOption, Status
from pyautd3.modulation import Fourier, FourierOption


def err_handler(idx: int, status: Status) -> None:
    print(f"Device[{idx}]: {status}")


if __name__ == "__main__":
    start_time = time.time()
    with Controller.open(
        [AUTD3(pos=[0.0, 0.0, 0.0], rot=[1, 0, 0, 0])],
        EtherCrab(err_handler=err_handler, option=EtherCrabOption()),
    ) as autd:
        firmware_version = autd.firmware_version()
        print(
            "\n".join(
                [f"[{i}]: {firm}" for i, firm in enumerate(firmware_version)],
            ),
        )

        autd.send(Silencer())

        center = np.array([0.0, 0.0, 150.0])
        point_num = 200
        radius = 30.0

        g = FociSTM(
                foci=(
                    center + radius * np.array([np.cos(theta), np.sin(theta), 0])
                    for theta in (2.0 * np.pi * i / point_num for i in range(point_num))
                ),
                config=1.0 * Hz,
            )

        
        m = Fourier(
            components=[
                Sine(freq=30 * Hz, option=SineOption(intensity=a)),
                Sine(freq=200 * Hz, option=SineOption(intensity=b)),
                Static(intensity=c),
            ], # a + b + c = 255(0xff)
            option=FourierOption(
                scale_factor=None,
                clamp=False,
                offset=0x00,
            ),
        )
        autd.send((m, g))

        _ = input()

        autd.close()
