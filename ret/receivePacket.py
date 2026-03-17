#!/usr/bin/env python3

import RNS
import sys
from encryption import DestinationEncryption, get_shared_signal
from configuration import ReticulmConfigManager, get_network_config_interactive

user="ret"
encrypted_peer_hash=None

for i in range(1, len(sys.argv)):
    if i == 1:
        user = sys.argv[i]
    if i == 2:
        encrypted_peer_hash = sys.argv[i].strip()

APP_NAME = "secure_p2p"
ASPECT = "direct_comms"

# Configure network (if needed)
print("\n[INIT] Checking network configuration...")
existing_config = ReticulmConfigManager.load_existing_config()

if existing_config and "TCPServer" in existing_config:
    print("[CONFIG] ✓ Existing receiver config found")
    ReticulmConfigManager.print_config()
else:
    print("[CONFIG] Creating new receiver configuration...")
    config = get_network_config_interactive()
    
    if not config:
        sys.exit(1)
    
    interface_type, listen_ip, listen_port, target_host, target_port = config
    
    if interface_type != "TCPServerInterface":
        print("[ERROR] Receiver must use TCPServerInterface")
        sys.exit(1)
    
    ReticulmConfigManager.create_instance_config(
        interface_type=interface_type,
        listen_ip=listen_ip,
        listen_port=listen_port,
        enable_transport=False
    )

print("[INIT] Initializing Reticulum...")
reticulum = RNS.Reticulum()

print("[INIT] Loaded interfaces:")
if reticulum.router:
    for interface in reticulum.router.interfaces:
        print(f"      {interface}")

print("[INIT] Creating destination...")
identity = RNS.Identity()
destination = RNS.Destination(
    identity,
    RNS.Destination.IN,
    RNS.Destination.SINGLE,
    APP_NAME,
    ASPECT
)

destination_hash_hex = destination.hexhash

print(f"\n" + "= "*30)
print(f"RECEIVER {user}")
print("= "*30)

# Step 1: Get shared signal
shared_signal = get_shared_signal()

encrypted_destination = DestinationEncryption.encrypt_destination(
    destination_hash_hex,
    shared_signal
)

print(f"\n ----> Share this ENCRYPTED hash:")
print(f"         {encrypted_destination}")

# Step 3: Receive encrypted hash from peer
if not encrypted_peer_hash:
    print(f"\nStep 4. Obtain EDH from sender...")
    encrypted_peer_hash = input("[INPUT] Enter EDH: ").strip()

# Step 4: Decrypt peer's hash
try:
    peer_destination_hash = DestinationEncryption.decrypt_destination(
        encrypted_peer_hash,
        shared_signal
    )
    print(f"\n[OK] ✓ Successfully decrypted destination hash")
except Exception as e:
    print(f"[ERROR] ✗ Failed to decrypt: {e}")
    print("[ERROR] ✗ The signal may be incorrect or the hash may be corrupted")
    sys.exit(1)

# Step 5: Set up listener
def receive_packet(packet):
    print(f"\n[RX] ✓ Packet received!")
    print(f"[RX] From: {RNS.prettyhexrep(packet.sender.hash)}")
    try:
        print(f"[RX] Data: {packet.data.decode('utf-8')}")
    except:
        print(f"[RX] Data: {packet.data.hex()}")
    packet.prove()

destination.set_packet_callback(receive_packet)

print("\nStep 5. Wait for link")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n[EXIT] Shutting down...")
    RNS.exit()