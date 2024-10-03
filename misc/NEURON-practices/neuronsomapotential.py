from neuron import h
from neuron.units import ms, mV 
import matplotlib.pyplot as plt

theSoma = h.Section(name="Soma")

theSoma.L = 20
theSoma.diam = 20 # setting the appropriate l & diam for this

aSegment = theSoma(0.5) #middle; 0.5

theSoma.insert(h.hh)
#theSoma(0.5).pas.e = -65

iClamp = h.IClamp(aSegment) # an iclamp is a point process; source of current

iClamp.delay = 2
iClamp.dur = 0.1    # SETTING UP VALUES
iClamp.amp = 0.9

membranePotential = h.Vector().record(aSegment._ref_v) # this is a vector for membrane potential
timestamp = h.Vector().record(h._ref_t) # this is a vector for time stamps

h.load_file("stdrun.hoc")

h.finitialize(-65 * mV) # setting the cell's resting potential
h.continuerun(40 * ms)  # run for 60 ms

plt.figure()
plt.plot(timestamp, membranePotential)
plt.xlabel("Time (ms)")
plt.ylabel("Membrane Potential (mV)")
plt.show()