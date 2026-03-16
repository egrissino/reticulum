#!/usr/bin/env python3

import RNS
import sys
from encryption import DestinationEncryption, get_shared_signal

APP_NAME = "secure_p2p"
ASPECT = "direct_comms"

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

print(f"\n" + "="*60)
print("RECEIVER (ALICE)")
print("="*60)

# Step 1: Get shared signal
shared_signal = get_shared_signal()

# Step 2: Encrypt and display my destination hash
# print(f"\n[STEP 1] Your destination hash (plaintext):")
# print(f"         {destination_hash_hex}")

encrypted_destination = DestinationEncryption.encrypt_destination(
    destination_hash_hex,
    shared_signal
)

print(f"\n[STEP 2] Share this ENCRYPTED hash with Bob out-of-band:")
print(f"         {encrypted_destination}")

# Step 3: Receive encrypted hash from peer
print(f"\n[STEP 3] Waiting for encrypted destination hash from Bob...")
encrypted_peer_hash = input("[INPUT] Enter Bob's encrypted destination hash: ").strip()

# Step 4: Decrypt peer's hash
try:
    peer_destination_hash = DestinationEncryption.decrypt_destination(
        encrypted_peer_hash,
        shared_signal
    )
    print(f"[OK] ✓ Successfully decrypted Bob's destination hash")
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

print(f"\n" + "="*60)
print("STATUS: Ready to receive packets from Bob")
print("="*60)
print("[LISTEN] Waiting for incoming packets...\n")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n[EXIT] Shutting down...")
    RNS.exit()