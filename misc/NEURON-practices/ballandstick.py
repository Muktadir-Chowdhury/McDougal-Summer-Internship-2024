from neuron import h, gui
from neuron.units import mV, ms, μm 
import matplotlib.pyplot as plt


h.load_file("stdrun.hoc")

class BallandStick():
    def __init__(self, idnumber):
        self.idnumber = idnumber
        self.morphology()
        self.biophysics()
    
    def morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dendrite = h.Section(name="dend", cell=self)

        self.dendrite.connect(self.soma)

        self.all = self.soma.wholetree()

        self.soma.L = 12.6157 * μm
        self.soma.diam = 12.6157 * μm

        self.dendrite.L = 200 * μm
        self.dendrite.diam = 1 * μm

    
    def biophysics(self):
        for section in self.all:
            section.Ra = 100 # why 100?   | axial resistance
            section.cm = 1 # unit in microfarads | membrane capacitance 
        
        self.soma.insert("hh")
        for segment in self.soma:
            segment.hh.gkbar = 0.036 # potassium
            segment.hh.gnabar = 0.12 # sodium
            segment.hh.gl = 0.0003 # leak
            segment.hh.el = -54.3 * mV # reversal 
        
        self.dendrite.insert("pas")
        for segment in self.dendrite:
            segment.pas.g = 0.001 # passive conductance
            segment.pas.e = -65 * mV # reversal for leak

    def __repr__(self):
        return f"BallandStick[{self.idnumber}]"


myFirstNeuron = BallandStick(0)

stimulus = h.IClamp(myFirstNeuron.dendrite(1))   # (1) is to refer to the distal end of the dendrite; the end node
stimulus.delay = 10
stimulus.dur = 1
plt.figure()

somaV = h.Vector().record(myFirstNeuron.soma(0.5)._ref_v)   # recording the center of the soma
dendV = h.Vector().record(myFirstNeuron.dendrite(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

amps = [0.075 * i for i in range(1, 5)] # testing different amplitudes
colors = ["red", "blue", "green", "orange"]
for amp in amps:
    stimulus.amp = amp 
    color = colors[amps.index(amp)]
    for myFirstNeuron.dendrite.nseg in [1, 101]:
        h.finitialize(-65 * mV)
        h.continuerun(35 * ms)
        plt.plot(time, somaV, label=amp, color=color, linewidth = (2 if myFirstNeuron.dendrite.nseg == 1 else 1))
        plt.plot(time, dendV, linestyle='dashed', color=color, linewidth= (2 if myFirstNeuron.dendrite.nseg == 1 else 1))

plt.xlabel("Time in ms")
plt.ylabel("Membrane Potential of Center Soma & Dendrite; mV")
plt.legend()
plt.show()

#mySecondNeuron = BallandStick(1)
