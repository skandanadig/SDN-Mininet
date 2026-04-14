#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

class TriangleTopo(Topo):
    """
    Triangle topology with 3 switches and 2 hosts.
    S1 --- S2
    |      |
    |      |
    S3 ----- (Loop)
    H1 connected to S1
    H2 connected to S3
    """
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

        # Add switches
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch)

        # Add links for Hosts
        self.addLink(h1, s1)
        self.addLink(h2, s3)

        # Add links for Switches (forming the triangle)
        # We can add TCLink configurations like bw=10, delay='1ms' if needed,
        # but standard links are fine for simple functional testing.
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s1)  # The redundant link

def run():
    setLogLevel('info')
    
    info('*** Creating network\n')
    topo = TriangleTopo()
    
    # Use standard RemoteController explicitly pointing to localhost on standard Ryu port
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633), switch=OVSKernelSwitch, link=TCLink)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    run()
