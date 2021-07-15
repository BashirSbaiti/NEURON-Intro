import pprint

from matplotlib import pyplot as plt
from neuron import h
from neuron.units import ms, mV
import pandas as pd

import csv

soma = h.Section(name='soma')  # create a neuron with just one soma (soma is one section)
h.topology()  # displays structure of model
pprint.pprint(soma.psection())  # properties of the section
print(soma.psection()['morphology']['L'])

soma.L = 20
soma.diam = 20

soma.insert('hh')  # insert hh channel

print(type(soma(0.5)))  # segment (subdiv) of section, 1=distal from soma, 0 = closest

mech = soma(0.5).hh
print(type(mech))
print(soma(0.5).hh.gkbar)  # section variables

iclamp = h.IClamp(soma(0.5)) #  insert a current clamp (point souce of current) at 0.5 segment
print([item for item in dir(iclamp) if not item.startswith('__')])  # amp -- the amplitude (in nA), delay -- the time the current clamp switches on (in ms), and dur -- how long (in ms) the current clamp stays on
iclamp.delay = 2
iclamp.dur = 0.1
iclamp.amp = 0.9
pprint.pprint(soma.psection())

v = h.Vector().record(soma(0.5)._ref_v)             # ref to Membrane potential vector
t = h.Vector().record(h._ref_t)                     # ref to Time stamp vector

# running
h.load_file('stdrun.hoc')
h.finitialize(-65 * mV) # resting -65 mV
h.continuerun(40 * ms)  # 0 to 40 ms

# plot

plt.figure()
plt.plot(t, v)
plt.xlabel('t (ms)')
plt.ylabel('v (mV)')
plt.show()

# saving and loading

with open('data.csv', 'w') as f:
    csv.writer(f).writerows(zip(t, v))

#loading
with open('data.csv') as f:
    reader = csv.reader(f)
    tnew, vnew = zip(*[[float(val) for val in row] for row in reader if row])

#or

data = pd.read_csv('data.csv', header=None, names=['t', 'v'])

plt.figure()
plt.plot(data["t"], data["v"])
plt.xlabel('t (ms)')
plt.ylabel('v (mV)')
plt.show()