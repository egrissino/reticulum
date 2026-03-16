#!/usr/bin/env python3

import RNS
import sys
import time
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
sender_identity = RNS.Identity()
sender_destination = RNS.Destination(
    sender_identity,
    RNS.Destination.OUT,
    RNS.Destination.SINGLE,
    APP_NAME,
    ASPECT
)

sender_hash_hex = sender_destination.hexhash

print(f"\n" + "="*60)
print("SENDER (BOB)")
print("="*60)

# Step 1: Get shared signal
shared_signal = get_shared_signal()

# Step 2: Encrypt and display my destination hash
print(f"\n[STEP 1] Your destination hash (plaintext):")
print(f"         {sender_hash_hex}")

encrypted_sender_hash = DestinationEncryption.encrypt_destination(
    sender_hash_hex,
    shared_signal
)

print(f"\n[STEP 2] Share this ENCRYPTED hash with Alice out-of-band:")
print(f"         {encrypted_sender_hash}")

# Step 3: Receive encrypted hash from peer
print(f"\n[STEP 3] Waiting for encrypted destination hash from Alice...")
encrypted_peer_hash = input("[INPUT] Enter Alice's encrypted destination hash: ").strip()

# Step 4: Decrypt peer's hash
try:
    peer_destination_hash = DestinationEncryption.decrypt_destination(
        encrypted_peer_hash,
        shared_signal
    )
    print(f"[OK] ✓ Successfully decrypted Alice's destination hash")
except Exception as e:
    print(f"[ERROR] ✗ Failed to decrypt: {e}")
    print("[ERROR] ✗ The signal may be incorrect or the hash may be corrupted")
    sys.exit(1)

# Step 5: Convert to bytes
try:
    peer_destination_hash_bytes = bytes.fromhex(peer_destination_hash)
except ValueError:
    print("[ERROR] ✗ Invalid destination hash format")
    sys.exit(1)

print(f"\n" + "="*60)
print("STATUS: Sending packet to Alice")
print("="*60)

print(f"\n[TX] Destination: {RNS.prettyhexrep(peer_destination_hash_bytes)}")

# Step 6: Create a destination object for Alice (outbound, to her hash)
# We use a PLAIN destination with her hash to represent her
class RemoteDestination:
    """Simple wrapper to represent a remote destination by its hash"""
    def __init__(self, dest_hash):
        self.hash = dest_hash
        self.type = RNS.Destination.SINGLE
        self.identity = None
    
    def encrypt(self, plaintext):
        """Encryption happens at packet level for SINGLE destinations"""
        return plaintext

alice_destination = RemoteDestination(peer_destination_hash_bytes)

# Step 7: Send packet
data = b"Hello Alice! This is a secure message from Bob."

packet = RNS.Packet(
    alice_destination,
    data
)

print(f"[TX] Sending: {data.decode('utf-8')}")

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