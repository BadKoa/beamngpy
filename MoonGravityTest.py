from beamngpy import BeamNGpy, Scenario, Vehicle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from beamngpy.sensors import (
    Damage, Electrics,)
from beamngpy.sensors import IMU

sns.set()  


bng = BeamNGpy('localhost', 64256, home="E:\SteamLibrary\steamapps\common\BeamNG.drive")

bng.open()

scenario = Scenario('west_coast_usa', 'AI Drives Moon Gravity Test')

vehicle = Vehicle('ego_vehicle', model='etk800', license='im tryin')
vehicle_imu = IMU(pos=(0.73, 0.51, 0.8), debug=True)
vehicle.sensors.attach('vehicle_imu', vehicle_imu)


scenario.add_vehicle(vehicle, pos=(-717, 103, 118), rot_quat=(0, 0, 0.3826834, 0.9238795))

scenario.make(bng)

vehicle_data = []


bng.scenario.load(scenario)
bng.env.set_gravity(gravity=-9.807*.166)

bng.settings.set_deterministic()
bng.settings.set_steps_per_second(60)

bng.scenario.start()

vehicle.ai.set_mode('span')
vehicle.ai.set_aggression(10000000)


for t in range(0, 1800, 30):
    vehicle.sensors.poll()
    row = [
        t,
        'aggressive',
        vehicle_imu['aX'],
        vehicle_imu['aY'],
        vehicle_imu['aZ'],
        vehicle_imu['gX'],
        vehicle_imu['gY'],
        vehicle_imu['gZ'],
    ]
    vehicle_data.append(row)
    bng.control.step(30)
    
    data = vehicle_data
df = pd.DataFrame(data, columns=['T', 'Behavior', 'aX', 'aY', 'aZ', 'gX', 'gY', 'gZ'])

df['Force'] = df.apply(lambda r: np.linalg.norm([r['gX'], r['gY'], r['gZ']]), axis=1)
df['Rotation'] = df.apply(lambda r: np.linalg.norm([r['aX'], r['aY'], r['aZ']]), axis=1)
df[['Behavior', 'Force', 'Rotation']].groupby('Behavior').agg(['min', 'max', 'mean'])

#draws graph
figure, ax = plt.subplots(2, 1, figsize=(30, 15))
pal = {'aggressive': '#FF4444', 'careful': '#22FF22'}
sns.lineplot(x='T', y='Force', hue='Behavior', data=df, palette=pal, ax=ax[0])
sns.lineplot(x='T', y='Rotation', hue='Behavior', data=df, palette=pal, ax=ax[1])

