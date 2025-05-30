"""Configuration management for Lightning Polar Scripts."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class NodeConfig(BaseModel):
    """Configuration for a Lightning Network node."""
    name: str
    implementation: str  # 'CLN' or 'LND'
    rpc_host: str = Field(default="localhost")
    rpc_port: int
    rest_port: Optional[int] = None  # For REST API (both LND and CLN)
    # LND specific
    macaroon_path: Optional[str] = None
    cert_path: Optional[str] = None
    # CLN specific (for REST API)
    rune_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None
    ca_cert_path: Optional[str] = None
    # Legacy CLN socket support
    socket_path: Optional[str] = None
    

class PolarConfig(BaseModel):
    """Configuration for Polar Lightning Network."""
    nodes: Dict[str, NodeConfig] = Field(default_factory=dict)
    polar_home: str = Field(default="~/.polar")
    network_name: str = Field(default="default")


def get_polar_home() -> Path:
    """Get Polar home directory."""
    polar_home = os.getenv('POLAR_HOME', '~/.polar')
    return Path(polar_home).expanduser()


def find_polar_networks() -> list:
    """Find all Polar networks."""
    polar_home = get_polar_home()
    networks_dir = polar_home / "networks"
    
    if not networks_dir.exists():
        return []
    
    networks = []
    for network_dir in networks_dir.iterdir():
        if network_dir.is_dir():
            docker_compose = network_dir / "docker-compose.yml"
            if docker_compose.exists():
                networks.append(network_dir.name)
    
    return networks


def load_polar_network_config(network_name: str = None) -> PolarConfig:
    """Load Polar network configuration."""
    if network_name is None:
        # Try to find the first available network
        networks = find_polar_networks()
        if not networks:
            raise ValueError("No Polar networks found")
        network_name = networks[0]
    
    polar_home = get_polar_home()
    network_dir = polar_home / "networks" / network_name
    
    if not network_dir.exists():
        raise ValueError(f"Network '{network_name}' not found")
    
    # Parse docker-compose.yml to extract node information
    nodes = {}
    
    # Look for Core Lightning nodes
    cln_dirs = list(network_dir.glob("volumes/*/lightningd"))
    for cln_dir in cln_dirs:
        node_name = cln_dir.parent.name
        
        # Set up REST API configuration for CLN
        nodes[node_name] = NodeConfig(
            name=node_name,
            implementation="CLN",
            rpc_host="127.0.0.1",
            rpc_port=0,  # CLN uses socket for RPC, REST for API
            rest_port=8182,  # Default CLN REST port
            rune_path=str(cln_dir / "admin.rune"),
            ca_cert_path=str(cln_dir / "regtest" / "ca.pem"),
            client_cert_path=str(cln_dir / "regtest" / "client.pem"),
            client_key_path=str(cln_dir / "regtest" / "client-key.pem")
        )
    
    # Look for LND nodes
    lnd_dirs = list(network_dir.glob("volumes/*/lnd"))
    for lnd_dir in lnd_dirs:
        node_name = lnd_dir.parent.name
        
        # Set up REST API configuration for LND
        nodes[node_name] = NodeConfig(
            name=node_name,
            implementation="LND",
            rpc_host="127.0.0.1",
            rpc_port=11002,  # Default LND gRPC port
            rest_port=8081,  # Default LND REST port
            macaroon_path=str(lnd_dir / "data" / "chain" / "bitcoin" / "regtest" / "admin.macaroon"),
            cert_path=str(lnd_dir / "tls.cert")
        )
    
    return PolarConfig(
        nodes=nodes,
        network_name=network_name,
        polar_home=str(polar_home)
    )


def load_config_from_env() -> PolarConfig:
    """Load configuration from environment variables."""
    nodes = {}
    
    # Look for CLN configuration (bob)
    cln_socket = os.getenv('CLN_SOCKET_PATH')
    cln_host = os.getenv('CLN_HOST', 'localhost')
    cln_rest_port = os.getenv('CLN_REST_PORT')
    cln_rune = os.getenv('CLN_RUNE_PATH')
    cln_ca_cert = os.getenv('CLN_CA_CERT_PATH')
    cln_client_cert = os.getenv('CLN_CLIENT_CERT_PATH')
    cln_client_key = os.getenv('CLN_CLIENT_KEY_PATH')
    
    if cln_socket or cln_rest_port:
        nodes['bob'] = NodeConfig(
            name='bob',
            implementation='CLN',
            rpc_host=cln_host,
            rpc_port=0 if cln_socket else int(cln_rest_port),
            rest_port=int(cln_rest_port) if cln_rest_port else None,
            socket_path=cln_socket,
            rune_path=cln_rune,
            ca_cert_path=cln_ca_cert,
            client_cert_path=cln_client_cert,
            client_key_path=cln_client_key
        )
    
    # Look for LND configuration (alice)
    lnd_host = os.getenv('LND_HOST', 'localhost')
    lnd_port = os.getenv('LND_PORT')
    lnd_rest_port = os.getenv('LND_REST_PORT')
    lnd_macaroon = os.getenv('LND_MACAROON_PATH')
    lnd_cert = os.getenv('LND_CERT_PATH')
    
    if lnd_port or lnd_rest_port:
        nodes['alice'] = NodeConfig(
            name='alice',
            implementation='LND',
            rpc_host=lnd_host,
            rpc_port=int(lnd_port) if lnd_port else 10001,
            rest_port=int(lnd_rest_port) if lnd_rest_port else None,
            macaroon_path=lnd_macaroon,
            cert_path=lnd_cert
        )
    
    return PolarConfig(nodes=nodes)


def load_config() -> PolarConfig:
    """Load configuration from Polar or environment variables."""
    # First try to load from environment variables
    env_config = load_config_from_env()
    if env_config.nodes:
        return env_config
    
    # Then try to load from Polar
    try:
        return load_polar_network_config()
    except Exception as e:
        # Create a default configuration with example values
        print(f"Warning: Could not load configuration: {e}")
        print("Creating default configuration. Please set up environment variables or Polar network.")
        
        return PolarConfig(
            nodes={
                'alice': NodeConfig(
                    name='alice',
                    implementation='LND',
                    rpc_host='127.0.0.1',
                    rpc_port=11002,
                    rest_port=8080,
                    macaroon_path='/Users/walter/.polar/networks/2/volumes/lnd/alice/data/chain/bitcoin/regtest/admin.macaroon',
                    cert_path='/Users/walter/.polar/networks/2/volumes/lnd/alice/tls.cert'
                ),
                'bob': NodeConfig(
                    name='bob',
                    implementation='CLN',
                    rpc_host='127.0.0.1',
                    rpc_port=0,
                    rest_port=8182,
                    rune_path='/Users/walter/.polar/networks/2/volumes/c-lightning/bob/lightningd/admin.rune',
                    ca_cert_path='/Users/walter/.polar/networks/2/volumes/c-lightning/bob/lightningd/regtest/ca.pem',
                    client_cert_path='/Users/walter/.polar/networks/2/volumes/c-lightning/bob/lightningd/regtest/client.pem',
                    client_key_path='/Users/walter/.polar/networks/2/volumes/c-lightning/bob/lightningd/regtest/client-key.pem'
                )
            }
        ) 