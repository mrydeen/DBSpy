import matplotlib.pyplot as plt
import numpy as np


Fs = 1653
f = 5
numberOfSamples = 1653
x = np.arange(numberOfSamples)
numberOfWaves = 6
y = np.sin(numberOfWaves * np.pi * f * x / Fs)
y2 = []
for i in range(0,len(y)):
    y2.append(y[i]+2)
y3 = np.array(y2)

plt.plot(x, y3)
plt.xlabel('voltage(V)')
plt.ylabel('sample(n)')
plt.show()
