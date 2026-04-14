# controller.py
# POX app implementing L2 Learning + Spanning Tree + Failure Recovery
# Place this file in the POX ext/ directory (e.g., ~/pox/ext/controller.py)

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpid_to_str

log = core.getLogger()

class FastRecoveryExtension(EventMixin):
    """
    Listens to PortStatus events. When a link goes down, it flushes the 
    flow tables of the switch, forcing l2_learning to relearn paths 
    using the Spanning Tree's backup links.
    """
    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        log.info("Switch %s connected.", dpid_to_str(event.dpid))

    def _handle_PortStatus(self, event):
        if event.modified:
            # Check if port down flag is set
            if (event.port.config & of.OFPPC_PORT_DOWN) or (event.port.state & of.OFPPS_LINK_DOWN):
                log.info("Link DOWN detected on Switch %s, Port %s", dpid_to_str(event.dpid), event.port.port_no)
                
                # Delete all flows from the switch to force re-learning
                msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
                event.connection.send(msg)
                
                log.info("Cleared OpenFlow rules for Switch %s to facilitate recovery.", dpid_to_str(event.dpid))
                
def launch():
    """
    Chains the launch of standard POX modules, then adds our custom recovery.
    """
    # 1. Discovery for topology changes
    import pox.openflow.discovery
    pox.openflow.discovery.launch()

    # 2. Spanning Tree Protocol to break loops
    import pox.openflow.spanning_tree
    # STP by default disables flooding on non-STP ports, preventing loops
    pox.openflow.spanning_tree.launch()

    # 3. L2 Learning for forwarding
    import pox.forwarding.l2_learning
    pox.forwarding.l2_learning.launch()
    
    # 4. Our Fast Recovery Extension
    core.registerNew(FastRecoveryExtension)
    
    log.info("SDN Controller initialized with POX L2 Learning, Spanning Tree, and Fast Recovery.")
