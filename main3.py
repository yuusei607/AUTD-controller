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
def generate_abc():
    
    # 1. まず、合計値 S を 0 から 256 の間で決める
    total_sum = random.randint(0, 256)
    
    # 2. 0 から S の間に「2つの仕切り」をランダムに置く
    #    (0からtotal_sumまでの値を2回選ぶ)
    break1 = random.randint(0, total_sum)
    break2 = random.randint(0, total_sum)
    
    # 3. 2つの仕切りをソートする (0 <= p1 <= p2 <= total_sum)
    p1 = min(break1, break2)
    p2 = max(break1, break2)
    
    # 4. 3つの区間の長さが a, b, c になる
    a = p1        # 0 から p1 まで
    b = p2 - p1   # p1 から p2 まで
    c = total_sum - p2 # p2 から total_sum まで
    
    # (a+b+c = p1 + (p2-p1) + (total_sum-p2) = total_sum となる)
    
    return a, b, c

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
        center = np.array([w, h, 300.0])
        radius = 3.0
        # --------------- parameter to be tuned directly ------------------
        point_num = 10
        stm_freq = 5.0 * Hz
        am_freq = 50.0 * Hz
        # -----------------------------------------------------------------
        # --------------- parameter to be calculated ----------------------
        velocity = 2 * np.pi * radius * stm_freq
        
        # -----------------------------------------------------------------


        g = FociSTM(
                foci=(
                    center + radius * np.array([np.cos(theta), np.sin(theta), 0])
                    for theta in (2.0 * np.pi * i / point_num for i in range(point_num))
                ),
                config=stm_freq,
            )   


        m = Sine(
            freq=am_freq,
            option=SineOption(intensity=0xff),
        )

        autd.send((m, g))
        
        # print('データの取得が終了しました.csvファイルに結果を保存しています.')
        # make_load_csv(stimuli_list, hardness_list, roughness_list)
        # print('結果の保存が終了しました.')



