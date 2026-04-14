# SDN Link Failure Detection and Recovery

This project demonstrates link failure detection and automated recovery within a Software-Defined Network (SDN) utilizing **Mininet** and the **POX OpenFlow Controller**.

The goal of this project is to create a multi-path triangle network topology, observe normal flow generation, proactively tear down an active link, and visualize the controller dynamically finding an alternate path, unblocking ports, and redirecting traffic seamlessly.

## Network Topology
- **Switches**: 3 OpenvSwitches (S1, S2, S3) arranged in a Triangle to form redundant paths.
- **Hosts**: 2 Hosts (H1 connected to S1, H2 connected to S3).
- **Controller**: Remote POX Controller supporting OpenFlow 1.0.

```mermaid
graph TD;
    H1(Host 1) --- S1(Switch 1);
    S1 --- S2(Switch 2);
    S2 --- S3(Switch 3);
    S3 --- S1(Switch 1 - Redundant Link);
    S3 --- H2(Host 2);
```

## Features
- **Dynamic MAC Learning**: Reactively builds paths based on incoming packets using POX's `l2_learning` component.
- **Loop Prevention**: Implements Spanning Tree Protocol (STP) using POX's native `spanning_tree` component to safely disable redundant loop links during network discovery.
- **Self-Healing / Fallback Recovery**: Actively listens for `PortStatus` events (link down). Upon failure detection, our custom extension quickly clears OpenFlow rule caches across the network, forcing re-learning of packets over the backup routes without permanent connection loss.

## Environment Prerequisites (Ubuntu 22.xx)

To run this on Windows, you must use an Ubuntu Virtual Machine, WSL2, or a Docker container.

1. **Update and Install Mininet**:
    ```bash
    sudo apt update
    sudo apt install mininet
    ```

2. **Verify OpenvSwitch**:
    ```bash
    sudo systemctl enable openvswitch-switch
    sudo systemctl start openvswitch-switch
    ```

3. **Install POX Controller**:
    POX is a Python 3 compatible SDN controller that doesn't have the dependency issues Ryu faces on modern Ubuntu distributions.
    ```bash
    cd ~
    git clone https://github.com/noxrepo/pox.git
    ```

## Execution Instructions

You will need two separate terminal windows (or tabs) within your Linux environment.

**Terminal 1 (POX Controller Setup & Run):**
First, copy the custom controller script to POX's `ext` (extensions) directory so POX can load it.
```bash
# Assuming your project folder is ~/SDN-mininet and POX is at ~/pox
cp ~/SDN-mininet/controller.py ~/pox/ext/
cd ~/pox

# Start POX with our custom extension
./pox.py log.level --INFO controller
```

**Terminal 2 (Mininet Setup):**
Create the network layout and connect it to the listening POX controller.
```bash
cd ~/SDN-mininet
sudo python3 topology.py
```

### Verifying Normal Operation vs. Failure

In the Mininet CLI (`mininet>`), you can simulate the link failure to demonstrate the project:

1. **Initial testing:** Let the switches learn routes and ensure everything works:
   ```text
   mininet> pingall
   ```

2. **Start a continuous ping:**
    Open an Xterm for H1 and H2, or do this inline:
   ```text
   mininet> h1 ping h2
   ```

3. **Simulate the Link Failure:**
   While the ping is running, bring down the primary link (e.g., between S1 and S3) by typing in Mininet:
   ```text
   mininet> link s1 s3 down
   ```

   **Watch the outputs**:
   - The pings will likely drop for a moment.
   - The Controller (Terminal 1) will output: `Link DOWN detected... Cleared OpenFlow rules...`
   - Traffic routed via STP's backup path (S1-S2-S3) naturally resumes.

4. **Performance verification (Optional)**:
   ```text
   mininet> h2 iperf -s &
   mininet> h1 iperf -c h2
   ```

## Troubleshooting
- If Mininet is unresponsive or links remain orphaned, always clear the mininet state using:
  ```bash
  sudo mn -c
  ```
- If POX throws a module not found error, make sure you properly copied `controller.py` into the `pox/ext/` folder, and that you are invoking `./pox.py controller`.

## Evaluation Screenshots

### Topology & Setup (4 Marks)

**Mininet Topology Startup**
A screenshot of the terminal showing the successful execution of `sudo python3 topology.py`.
![Mininet Topology Startup](screenshots/mininet_startup.jpeg)

**Controller Connection**
A screenshot of the POX terminal showing "connected datapath" logs for all three switches (S1, S2, S3).
![Controller Connection](screenshots/controller_connection.jpg)

