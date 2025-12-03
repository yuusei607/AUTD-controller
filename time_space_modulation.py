from calendar import c
import pathlib 
import datetime
import csv
import time
import random
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
    FociSTM
)
from pyautd3.link.ethercrab import EtherCrab, EtherCrabOption
from pyautd3.modulation import Fourier, FourierOption, Custom

# ----------------- Grobal Function ----------------------
def err_handler(idx: int, status: Status) -> None:
    print(f"Device[{idx}]: {status}")

def make_load_csv(stimuli_list: list, hardness_list: list, roughness_list: list): # stimuli = [[a0, b0, c0], [a1, b1, c1], ...], hardness = [3, 5, 1, ...], roughness = [1, 4, 8, ...]
    output_dir = pathlib.Path('./results')
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now()
    timestamp_str = now.strftime('%Y%m%d_%H%M%S')
    file_name = f'results_{timestamp_str}.csv'
    file_path = output_dir / file_name

    with open(file_path, mode='w', new_line='', enconfig='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['meissner', 'merkel', 'pacinian', 'hardness', 'roughness'])
        for i in range(len(hardness_list)):
            writer.writerow([stimuli_list[i][0], stimuli_list[i][1], stimuli_list[i][2], hardness_list[i], roughness_list[i]])



    
# -------------------------- main function --------------------------------
    

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
        # Random path generation with distance constraint
        # 3mm * 3mm square, z=0
        # Vertices: [0,0,0] and [3,3,0]
        # Distance between points: 1.0mm - 1.5mm
        points = []
        current_point = np.array([random.uniform(0.0, 8.0), random.uniform(0.0, 8.0), 0.0])
        points.append(current_point)

        for _ in range(99):
            while True:
                angle = random.uniform(0, 2 * np.pi)
                distance = random.uniform(1.0, 1.5)
                next_x = current_point[0] + distance * np.cos(angle)
                next_y = current_point[1] + distance * np.sin(angle)
                
                if 0.0 <= next_x <= 8.0 and 0.0 <= next_y <= 8.0:
                    current_point = np.array([next_x, next_y, 0.0])
                    points.append(current_point)
                    break

        g = FociSTM(
                foci=points,
                config=5.0 * Hz,
            )

        stimuli_array = np.array([])
        sumpling_freq = 4000.0
        num_sumple = int(sumpling_freq*5)
        t = np.arrange(num_sumple)
        
        stimuli_array = 255*np.sin(2*np.pi*200*t/sumpling_freq)
        while True:
            m = Sine(
                freq=am * Hz,
                option=SineOption(intensity=255)
            )
            autd.send((m, g))
            

