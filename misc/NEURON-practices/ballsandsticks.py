from neuron import h, gui 
from neuron.units import ms, mV, μm
import matplotlib.pyplot as plt


h.load_file("stdrun.hoc")

class Cell():
    def __init__(self, idnumber, x, y, z, theta):
        self.idnumber = idnumber
        self.morphology()
        self.all = self.soma.wholetree()
        self.biophysics()
        self.x = 0
        self.y = 0 
        self.z = 0 
        h.define_shape()
        self.rotateZ(theta)
        self.setPos(x, y, z)
    
    def setPos(self, x, y, z):
        for section in self.all:
            for i in range(section.n3d()):
                section.pt3dchange(i, x- self.x +section.x3d(i), y - self.y+section.y3d(i), z-self.z+section.z3d(i), section.diam3d(i))
        self.x, self.y, self.z = x, y, z
    
    def rotateZ(self, theta):
        for section in self.all:
            for i in range(section.n3d()):
                x = section.x3d(i)
                y = section.y3d(i)
                z = section.z3d(i)
                cosined = h.cos(theta)
                sined = h.sin(theta)
                xprime = x * cosined - y * sined 
                yprime = x * sined + y * cosined
                section.pt3dchange(i, xprime, yprime, z, section.diam3d(i))
    
    def __repr__(self):
        return f"{self.cellularName}[{self.idnumber}]"

class BallandStick(Cell):
    cellularName = "BallandStick"
    def morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dendrite = h.Section(name="dend", cell=self)
        self.dendrite.connect(self.soma)
        
        self.soma.L = 12.6157 * μm
        self.soma.diam = 12.6157 * μm
        self.dendrite.L = 200 * μm
        self.dendrite.diam = 1 * μm
    
    def biophysics(self):
        for section in self.all:
            section.Ra = 100 
            section.cm = 1 
        
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

def ring_structure(n, r):
    cell_list = []
    for i in range(n):
        theta = i * 2 * h.PI / n
        cell_list.append(BallandStick(i, h.cos(theta)*r, h.sin(theta)*r, 0, theta))
    return cell_list


MyNeurons = ring_structure(7, 100) 

stimSource = h.NetStim()  # source for netcon
synapse_ = h.ExpSyn(MyNeurons[0].dendrite(0.5)) # target for netcon

stimSource.number = 1
stimSource.start = 8
netconStim = h.NetCon(stimSource, synapse_)
netconStim.delay = 2
netconStim.weight[0] = 0.04 # apparently index 0 because it refers to the synaptic weight?

synapse_.tau = 2 

synapses = []
netcons = []

for source, target in zip(MyNeurons, MyNeurons[1:] +[MyNeurons[0]]): # [(BallandStick[0], BallandStick[1]), (BallandStick[1], BallandStick[2]), . . .]
    synapse = h.ExpSyn(target.dendrite(0.5)) # target for netcon
    netcon = h.NetCon(source.soma(0.5)._ref_v, synapse, sec=source.soma) # ask about why reference membrane potential
    netcon.weight[0] = 0.05
    netcon.delay = 1
    netcons.append(netcon)
    synapses.append(synapse)


recordNeuron = MyNeurons[1]
somaV = h.Vector().record(recordNeuron.soma(0.5)._ref_v)
dendV = h.Vector().record(recordNeuron.dendrite(0.5)._ref_v)
time = h.Vector().record(h._ref_t)
# synrecord = h.Vector().record(synapse._ref_i)

spikeTimes = [h.Vector() for x in netcons]
for netcon, spikeVector in zip(netcons, spikeTimes):
    netcon.record(spikeVector)  # ???

h.finitialize(-65)
h.continuerun(100)


for i, spike in enumerate(spikeTimes):
    print(f"Cell {i}: {list(spike)}")



plt.plot(time, somaV, label="Soma Central")
plt.plot(time, dendV, label="Dendrite Central")
plt.legend()
plt.show()

print(list(zip(synapses, netcons)))


# figure = plt.figure()z
# subplot1 = figure.add_subplot(2,1,1)
# subplot1.plot(time, somaV, label="soma central")
# subplot1.plot(time, dendV, label="dendrite central")

# subplot2 = figure.add_subplot(2,1,2)
# subplot2.plot(time, synrecord, label="Synaptic Current")

# subplot1.legend()
# subplot2.legend()
# plt.show()


ps = h.PlotShape(True)
ps.show(0)
