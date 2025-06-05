from mininet.topo import Topo

class StopAndWaitTopo(Topo):
    def build(self):
        client = self.addHost('h1')
        server = self.addHost('h2')
        switch = self.addSwitch('s1')

        self.addLink(client, switch, bw=10, delay='100ms', loss=0)
        self.addLink(server, switch, bw=10, delay='100ms', loss=0)

topos = {'stopandwait': (lambda: StopAndWaitTopo())}
