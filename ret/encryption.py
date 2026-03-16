#!/usr/bin/env python3

import os
import sys
import secrets
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class DestinationEncryption:
    """
    Encrypt/decrypt destination hashes using a shared signal (password)
    Uses AES-256-CBC with PBKDF2 key derivation
    """
    
    # Constants
    KEY_SIZE = 32  # 256 bits for AES-256
    IV_SIZE = 16   # 128 bits for CBC mode
    ITERATIONS = 100000  # PBKDF2 iterations
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive AES key from password using PBKDF2
        Uses hashlib.pbkdf2_hmac which is built-in to Python
        
        :param password: Shared signal/password
        :param salt: Random salt (16 bytes)
        :return: Derived key (32 bytes for AES-256)
        """
        # Use hashlib.pbkdf2_hmac - built into Python 3.4+
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            DestinationEncryption.ITERATIONS,
            dklen=DestinationEncryption.KEY_SIZE
        )
        return key
    
    @staticmethod
    def encrypt_destination(destination_hash_hex: str, password: str) -> str:
        """
        Encrypt destination hash with shared signal
        
        :param destination_hash_hex: Hex string of destination hash (32 chars)
        :param password: Shared signal/password
        :return: Encrypted hash as hex string (format: salt + iv + ciphertext)
        """
        print("\n[ENCRYPT] Encrypting destination hash...")
        
        # Validate input
        if len(destination_hash_hex) != 32:
            raise ValueError("Destination hash must be 32 hex characters (16 bytes)")
        
        try:
            destination_bytes = bytes.fromhex(destination_hash_hex)
        except ValueError:
            raise ValueError("Invalid hex format for destination hash")
        
        # Generate random salt and IV
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        
        # Derive key from password
        key = DestinationEncryption.derive_key(password, salt)
        
        # Encrypt using AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        plaintext = destination_bytes
        padding_length = 16 - (len(plaintext) % 16)
        plaintext += bytes([padding_length] * padding_length)
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Combine salt + iv + ciphertext and return as hex
        encrypted_data = salt + iv + ciphertext
        encrypted_hex = encrypted_data.hex().upper()
        
        print(f"[ENCRYPT] ✓ Encryption successful")
        print(f"[ENCRYPT] Original:  *** ") #{destination_hash_hex}")
        print(f"[ENCRYPT] Encrypted: {encrypted_hex}")
        
        return encrypted_hex
    
    @staticmethod
    def decrypt_destination(encrypted_hex: str, password: str) -> str:
        """
        Decrypt destination hash with shared signal
        
        :param encrypted_hex: Encrypted hash as hex string
        :param password: Shared signal/password
        :return: Decrypted destination hash as hex string
        """
        print("\n[DECRYPT] Decrypting destination hash...")
        
        try:
            encrypted_data = bytes.fromhex(encrypted_hex)
        except ValueError:
            raise ValueError("Invalid hex format for encrypted hash")
        
        if len(encrypted_data) < 48:  # 16 (salt) + 16 (iv) + 16 (min ciphertext)
            raise ValueError("Encrypted data too short")
        
        # Extract salt, iv, and ciphertext
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        # Derive key from password using same salt
        key = DestinationEncryption.derive_key(password, salt)
        
        # Decrypt using AES-256-CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        )
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = plaintext[-1]
        plaintext = plaintext[:-padding_length]
        
        destination_hex = plaintext.hex().upper()
        
        print(f"[DECRYPT] ✓ Decryption successful")
        print(f"[DECRYPT] Encrypted: {encrypted_hex[:32]}...")
        print(f"[DECRYPT] Decrypted:  *** ")
        
        return destination_hex


def get_shared_signal() -> str:
    """Prompt for shared signal with confirmation"""
    print("\n" + "="*60)
    print("SHARED SIGNAL SETUP")
    print("="*60)
    print("Enter a strong shared signal (password) that both nodes will use.")
    print("This should be communicated out-of-band securely.")
    print("(Min 12 characters, use uppercase, lowercase, numbers, symbols)")
    print("="*60)
    
    while True:
        signal = input("\n[INPUT] Enter shared signal: ").strip()
        
        if len(signal) < 12:
            print("[ERROR] ✗ Signal too short (minimum 12 characters)")
            continue
        
        confirm = input("[INPUT] Confirm shared signal: ").strip()
        
        if signal != confirm:
            print("[ERROR] ✗ Signals don't match, try again")
            continue
        
        print("[OK] ✓ Shared signal confirmed")
        return signal


if __name__ == "__main__":
    print("Encryption Module Test\n")
    
    # Test with example values
    test_hash = "c3d3f8c7a9b4e1d2f5a8c9e1d2f5a8c9"
    test_signal = "MySecureSignal123!"
    
    try:
        # Encrypt
        encrypted = DestinationEncryption.encrypt_destination(test_hash, test_signal)
        
        # Decrypt
        decrypted = DestinationEncryption.decrypt_destination(encrypted, test_signal)
        
        # Verify
        if decrypted == test_hash.upper():
            print("\n✓ Encryption/Decryption successful!")
        else:
            print("\n✗ Mismatch!")
            print(f"  Expected: {test_hash.upper()}")
            print(f"  Got:      {decrypted}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()