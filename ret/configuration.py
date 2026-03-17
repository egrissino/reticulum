#!/usr/bin/env python3

import os
import sys
from pathlib import Path

class ReticulmConfigManager:
    """
    Manage Reticulum configuration programmatically
    """
    
    CONFIG_DIR = Path.home() / ".config" / "reticulum"
    CONFIG_FILE = CONFIG_DIR / "config"
    
    @staticmethod
    def ensure_config_dir():
        """Create config directory if it doesn't exist"""
        ReticulmConfigManager.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def create_instance_config(
        interface_type="TCPServerInterface",
        listen_ip="0.0.0.0",
        listen_port=4242,
        target_host=None,
        target_port=4242,
        enable_transport=False
    ):
        """
        Create a basic Reticulum config with network interface
        
        :param interface_type: "TCPServerInterface" or "TCPClientInterface"
        :param listen_ip: IP to listen on (for server)
        :param listen_port: Port to listen on (for server) or connect to (for client)
        :param target_host: Host to connect to (for client)
        :param target_port: Port to connect to (for client)
        :param enable_transport: Enable transport mode (default: False for instance)
        """
        
        ReticulmConfigManager.ensure_config_dir()
        
        transport_setting = "Yes" if enable_transport else "No"
        
        config_content = f"""[reticulum]
enable_transport = {transport_setting}

[interfaces]

"""
        
        if interface_type == "TCPServerInterface":
            config_content += f"""  [[TCPServer]]
    type = TCPServerInterface
    enabled = yes
    listen_ip = {listen_ip}
    listen_port = {listen_port}
    outgoing = True
"""
        
        elif interface_type == "TCPClientInterface":
            if target_host is None:
                raise ValueError("TCPClientInterface requires target_host")
            
            config_content += f"""  [[TCPClient]]
    type = TCPClientInterface
    enabled = yes
    target_host = {target_host}
    target_port = {target_port}
    outgoing = True
"""
        
        # Write config file
        with open(ReticulmConfigManager.CONFIG_FILE, 'w') as f:
            f.write(config_content)
        
        print(f"[CONFIG] ✓ Created config at {ReticulmConfigManager.CONFIG_FILE}")
        print(f"[CONFIG] Interface: {interface_type}")
        
        if interface_type == "TCPServerInterface":
            print(f"[CONFIG] Listening on: {listen_ip}:{listen_port}")
        else:
            print(f"[CONFIG] Connecting to: {target_host}:{target_port}")
        
        return ReticulmConfigManager.CONFIG_FILE
    
    @staticmethod
    def load_existing_config():
        """Load existing config if it exists"""
        if ReticulmConfigManager.CONFIG_FILE.exists():
            with open(ReticulmConfigManager.CONFIG_FILE, 'r') as f:
                return f.read()
        return None
    
    @staticmethod
    def print_config():
        """Print current config"""
        config = ReticulmConfigManager.load_existing_config()
        if config:
            print("\nCurrent Reticulum Config:")
            print("=" * 60)
            print(config)
            print("=" * 60)
        else:
            print("[CONFIG] No existing config found")


def get_network_config_interactive(sender = False):
    """
    Prompt user for network configuration
    Returns: (interface_type, listen_ip, listen_port, target_host, target_port)
    """
    print("\n" + "= "*30)
    print("NETWORK CONFIGURATION")
    print("= "*30)
        
    if sender:
        print("\n[CONFIG] Sender Mode (TCPClientInterface)")
        target_host = input("[INPUT] Receiver IP address: ").strip()
        
        if not target_host:
            print("[ERROR] Receiver IP required")
            return None
        
        target_port_str = input("[INPUT] Receiver Port (default 4242): ").strip() or "4242"
        
        try:
            target_port = int(target_port_str)
        except ValueError:
            print("[ERROR] Invalid port number")
            return None
        
        return ("TCPClientInterface", None, None, target_host, target_port)
    
    else:
        print("\n[CONFIG] Receiver Mode (TCPServerInterface)")
        listen_ip = input("[INPUT] Listen IP (default 0.0.0.0): ").strip() or "0.0.0.0"
        listen_port_str = input("[INPUT] Listen Port (default 4242): ").strip() or "4242"
        
        try:
            listen_port = int(listen_port_str)
        except ValueError:
            print("[ERROR] Invalid port number")
            return None
        
        return ("TCPServerInterface", listen_ip, listen_port, None, None)


if __name__ == "__main__":
    print("Reticulum Config Manager\n")
    
    # Example: Interactive configuration
    config = get_network_config_interactive()
    
    if config:
        interface_type, listen_ip, listen_port, target_host, target_port = config
        
        ReticulmConfigManager.create_instance_config(
            interface_type=interface_type,
            listen_ip=listen_ip,
            listen_port=listen_port,
            target_host=target_host,
            target_port=target_port,
            enable_transport=False
        )
        
        ReticulmConfigManager.print_config()