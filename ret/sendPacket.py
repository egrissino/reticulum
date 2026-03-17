#!/usr/bin/env python3

import RNS
import sys
import time
from encryption import DestinationEncryption, get_shared_signal
from configuration import ReticulmConfigManager, get_network_config_interactive

user="ret"

for i in range(1, len(sys.argv)):
    if i == 1:
        user = sys.argv[i]
    if i == 2:
        message = sys.argv[i]

APP_NAME = "secure_p2p"
ASPECT = "direct_comms"

# Configure network (if needed)
print("\n[INIT] Checking network configuration...")
existing_config = ReticulmConfigManager.load_existing_config()

if existing_config and "TCPClient" in existing_config:
    print("[CONFIG] ✓ Existing sender config found")
    ReticulmConfigManager.print_config()
else:
    print("[CONFIG] Creating new sender configuration...")
    config = get_network_config_interactive(True)
    
    if not config:
        sys.exit(1)
    
    interface_type, listen_ip, listen_port, target_host, target_port = config
    
    if interface_type != "TCPClientInterface":
        print("[ERROR] Sender must use TCPClientInterface")
        sys.exit(1)
    
    ReticulmConfigManager.create_instance_config(
        interface_type=interface_type,
        target_host=target_host,
        target_port=target_port,
        enable_transport=False
    )

print("[INIT] Initializing Reticulum...")
reticulum = RNS.Reticulum()

print("[INIT] Loaded interfaces:")
if reticulum.router:
    for interface in reticulum.router.interfaces:
        print(f"      {interface}")

print("[INIT] Creating destination...")
sender_identity = RNS.Identity()
sender_destination = RNS.Destination(
    sender_identity,
    RNS.Destination.OUT,
    RNS.Destination.SINGLE,
    APP_NAME,
    ASPECT
)

sender_hash_hex = sender_destination.hexhash

print(f"\n" + "= "*30)
print(f"SENDER ({user})")
print("= "*30)

# Step 1: Get shared signal
shared_signal = get_shared_signal()

encrypted_sender_hash = DestinationEncryption.encrypt_destination(
    sender_hash_hex,
    shared_signal
)

print(f"\n ----> Share this ENCRYPTED hash:")
print(f"         {encrypted_sender_hash}")

# Step 4: Receive encrypted hash from peer
print(f"\nStep 4. Obtain EDH from recipient...")
encrypted_peer_hash = input("[INPUT] Enter EDH: ").strip()

try:
    peer_destination_hash = DestinationEncryption.decrypt_destination(
        encrypted_peer_hash,
        shared_signal
    )
    print(f"[OK] ✓ Successfully decrypted destination hash")
except Exception as e:
    print(f"[ERROR] ✗ Failed to decrypt: {e}")
    print("[ERROR] ✗ The signal may be incorrect or the hash may be corrupted")
    sys.exit(1)

try:
    peer_destination_hash_bytes = bytes.fromhex(peer_destination_hash)
except ValueError:
    print("[ERROR] ✗ Invalid destination hash format")
    sys.exit(1)


class RemoteDestination:
    '''
    Simple wrapper to represent a remote destination by its hash
    '''

    def __init__(self, dest_hash):
        self.hash = dest_hash
        self.type = RNS.Destination.SINGLE
        self.identity = None
    
    def encrypt(self, plaintext):
        '''
        Encryption happens at packet level for SINGLE destinations
        '''

        return plaintext

alice_destination = RemoteDestination(peer_destination_hash_bytes)

# Step 7: Send packet
if not message:
    message = input ("Enter Message: ")

data = bytes(message, 'utf-8')

packet = RNS.Packet(
    alice_destination,
    data
)

print("Step 5. Send Message and wait for link")
print("     Sending packet...")
receipt = packet.send()
timeout = 60 * 10

if receipt:
    print("[TX] ✓ Packet sent")
    print(f"[TX] Waiting for proof ({timeout} seconds)...")
    
    start = time.time()
    while time.time() - start < timeout:
        if receipt.proved:
            print("[TX] ✓ Proof received - message delivered!")
            RNS.exit()
        time.sleep(0.1)
    
    print("[TX] ~ No proof received (packet may still be delivered)")
    RNS.exit()
else:
    print("[TX] ✗ Failed to send packet")
    RNS.exit()