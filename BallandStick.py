from neuron import h, gui
from neuron.units import ms, mV
import bokeh.plotting as plt
h.load_file('stdrun.hoc')

import matplotlib.pyplot as plt

class BallAndStick:
    def __init__(self, gid):
        """initialzes ball and stick cell"""
        self.gid = gid  # id
        self._setup_morphology()
        self._setup_biophysics()
    def _setup_morphology(self):
        """initialzes cell morphology"""
        self.soma = h.Section(name='soma', cell=self) # create soma and dendrite
        self.dend = h.Section(name='dend', cell=self)
        self.all = [self.soma, self.dend]
        self.dend.connect(self.soma)  # connect the two, Note that this is not equivalent to attaching the soma to the dend; instead it means that the dendrite begins where the soma ends.
        #We could explicitly specify the connection location via, e.g. self.dend.connect(self.soma(0.5)) which would mean the dendrite was attached to the center of the soma.
        self.soma.L = self.soma.diam = 12.6157  # microns
        self.dend.L = 200
        self.dend.diam = 1
    def _setup_biophysics(self):
        """initlizes cell biophysics"""
        for sec in self.all:
            sec.Ra = 100    # Axial resistance in Ohm * cm
            sec.cm = 1      # Membrane capacitance in micro Farads / cm^2
        self.soma.insert('hh')
        for seg in self.soma: # here we loop over all segments in the soma, even though we only defined one segment.
            seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
            seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
            seg.hh.gl = 0.0003    # Leak conductance in S/cm2
            seg.hh.el = -54.3     # Reversal potential in mV
        # Insert passive current in the dendrite
        self.dend.insert('pas')
        for seg in self.dend:
            seg.pas.g = 0.001  # Passive conductance in S/cm2
            seg.pas.e = -65    # Leak reversal potential mV
    def __repr__(self):
        return f'BallAndStick[{self.gid}]'

my_cell = BallAndStick(0)
my_other_cell = BallAndStick(1)
h.topology()  # shows all created objects
del my_other_cell
h.topology()
print(my_cell.soma(0.5).area()) # approx 500 um^2
# NEURON only returns areas of segments which is why we asked for the center soma segment; since there is only one segment, the area here is the same as the whole Section area
# the surface area of a cylinder with equal length and diameter is the same as the surface area of a sphere with the same diameter
print(my_cell.soma.nseg)

ps = h.PlotShape(True)
ps.show(0)
#input()
#plt.show() # just a line, neuron does not show diams

print(h.units('gnabar_hh')) # gives param units, Pass in a string with the paramater name, an underscore, and then the mechanism name. e.g.

for sec in h.allsec(): # list all that is present
    print('%s: %s' % (sec, ', '.join(sec.psection()['density_mechs'].keys())))

# inject a current pulse into the distal (1) end of the dendrite starting 5 ms after the simulation starts, with a duration of 1 ms, and an amplitude of 0.1 nA
stim = h.IClamp(my_cell.dend(1))
stim.delay = 5
stim.dur = 1
stim.amp = 0.1

# recording
soma_v = h.Vector().record(my_cell.soma(0.5)._ref_v)  # voltage at 0.5
dend_v = h.Vector().record(my_cell.dend(0.5)._ref_v)
t = h.Vector().record(h._ref_t)

# simulation
h.finitialize(-65 * mV)  # -65 mV initialize
h.continuerun(25 * ms)  # run sim until 25 ms

fig = plt.figure()
plt.xlabel("t (ms)")
plt.ylabel("v (mV)")
plt.plot(t, soma_v, linewidth=2)
plt.show()

# vary current and measure results

fig2 = plt.figure()
plt.xlabel("t (ms)")
plt.ylabel("v (mV)")
amps = [0.075 * i for i in range(1, 5)]
colors = ['green', 'blue', 'red', 'black']
for amp, color in zip(amps, colors):
    stim.amp = amp
    for my_cell.dend.nseg, width in [(1, 2), (101, 1)]:
        h.finitialize(-65 * mV)
        h.continuerun(25 * ms)
        plt.plot(t, list(soma_v), linewidth=width, label=f"amp={round(amp, 3)}" if my_cell.dend.nseg == 1 else None, color=color)
        # make a copy of the values by passing in list(soma_v) instead of soma_v. If this copying was omitted, only the last set of values would be plotted.
        plt.plot(t, list(dend_v), '--', linewidth=width, color=color)
plt.legend()
plt.show()

#Here we see with the high-resolution simulation that the soma peaks should be reduced and delayed and the dendrite peaks increased relative to what was seen in the nseg=1 case.



