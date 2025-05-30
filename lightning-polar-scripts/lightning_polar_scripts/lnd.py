"""LND client for interacting with LND nodes via REST API."""

import requests
import codecs
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from .config import PolarConfig, NodeConfig

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(InsecureRequestWarning)


class LNDClient:
    """Client for interacting with LND nodes via REST API."""
    
    def __init__(self, config: PolarConfig, node_name: str):
        """Initialize LND REST client."""
        if node_name not in config.nodes:
            raise ValueError(f"Node '{node_name}' not found in configuration")
        
        self.node_config = config.nodes[node_name]
        if self.node_config.implementation != "LND":
            raise ValueError(f"Node '{node_name}' is not an LND node")
        
        self.node_name = node_name
        self._setup_rest_client()
    
    def _setup_rest_client(self):
        """Setup REST client configuration."""
        # Determine REST port (default to 8080 if not specified)
        rest_port = self.node_config.rest_port or 8080
        
        # Base URL for REST API
        self.base_url = f"https://{self.node_config.rpc_host}:{rest_port}"
        
        # Read the macaroon file for authentication
        self.headers = {}
        macaroon_path = Path(self.node_config.macaroon_path) if self.node_config.macaroon_path else None
        if macaroon_path and macaroon_path.exists():
            with open(macaroon_path, 'rb') as f:
                macaroon_bytes = f.read()
            macaroon = codecs.encode(macaroon_bytes, 'hex').decode()
            self.headers['Grpc-Metadata-macaroon'] = macaroon
        
        # Setup SSL verification
        cert_path = Path(self.node_config.cert_path) if self.node_config.cert_path else None
        if cert_path and cert_path.exists():
            self.verify = str(cert_path)
        else:
            # For development, disable SSL verification
            self.verify = False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a REST API request to LND."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, verify=self.verify)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, verify=self.verify)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, verify=self.verify)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to LND node '{self.node_name}' at {url}: {e}")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"HTTP error from LND node '{self.node_name}': {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request error from LND node '{self.node_name}': {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from LND node '{self.node_name}': {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get node information."""
        try:
            response = self._make_request('GET', '/v1/getinfo')
            return {
                'identity_pubkey': response.get('identity_pubkey'),
                'alias': response.get('alias'),
                'color': response.get('color'),
                'num_peers': response.get('num_peers', 0),
                'num_pending_channels': response.get('num_pending_channels', 0),
                'num_active_channels': response.get('num_active_channels', 0),
                'num_inactive_channels': response.get('num_inactive_channels', 0),
                'block_height': response.get('block_height'),
                'synced_to_chain': response.get('synced_to_chain'),
                'synced_to_graph': response.get('synced_to_graph'),
                'version': response.get('version')
            }
        except Exception as e:
            raise ConnectionError(f"Failed to get info from LND node '{self.node_name}': {e}")
    
    def get_balance(self) -> int:
        """Get node balance in satoshis."""
        try:
            # Get wallet balance
            wallet_response = self._make_request('GET', '/v1/balance/blockchain')
            wallet_balance = int(wallet_response.get('confirmed_balance', 0))
            
            # Get channel balance
            channel_response = self._make_request('GET', '/v1/balance/channels')
            channel_balance = int(channel_response.get('balance', 0))
            
            return wallet_balance + channel_balance
        except Exception as e:
            raise ConnectionError(f"Failed to get balance from LND node '{self.node_name}': {e}")
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels."""
        try:
            response = self._make_request('GET', '/v1/channels')
            return response.get('channels', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list channels from LND node '{self.node_name}': {e}")
    
    def list_peers(self) -> List[Dict[str, Any]]:
        """List all peers."""
        try:
            response = self._make_request('GET', '/v1/peers')
            return response.get('peers', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list peers from LND node '{self.node_name}': {e}")
    
    def create_invoice(self, amount_sats: int, memo: str = None, expiry: int = 3600) -> Dict[str, Any]:
        """Create a new invoice."""
        try:
            data = {
                'value': str(amount_sats),
                'memo': memo or f'Invoice for {amount_sats} sats',
                'expiry': str(expiry)
            }
            
            response = self._make_request('POST', '/v1/invoices', data)
            return {
                'payment_hash': response.get('r_hash'),
                'payment_request': response.get('payment_request'),
                'add_index': response.get('add_index')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create invoice on LND node '{self.node_name}': {e}")
    
    def pay_invoice(self, payment_request: str, amount_sats: Optional[int] = None) -> Dict[str, Any]:
        """Pay a Lightning invoice."""
        try:
            data = {
                'payment_request': payment_request
            }
            if amount_sats:
                data['amt'] = amount_sats
            
            response = self._make_request('POST', '/v1/channels/transactions', data)
            return {
                'payment_hash': response.get('payment_hash'),
                'payment_preimage': response.get('payment_preimage'),
                'payment_route': response.get('payment_route')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to pay invoice on LND node '{self.node_name}': {e}")
    
    def connect_peer(self, node_id: str, host: str = None, port: int = None) -> bool:
        """Connect to a peer."""
        try:
            if host and port:
                address = f"{node_id}@{host}:{port}"
            else:
                address = node_id
            
            data = {
                'addr': {
                    'pubkey': node_id.split('@')[0] if '@' in node_id else node_id,
                    'host': address.split('@')[1] if '@' in address else f"{host}:{port}" if host and port else ""
                }
            }
            
            self._make_request('POST', '/v1/peers', data)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to connect to peer on LND node '{self.node_name}': {e}")
    
    def open_channel(self, node_id: str, amount_sats: int, push_sats: int = 0) -> Dict[str, Any]:
        """Open a channel with a peer."""
        try:
            data = {
                'node_pubkey_string': node_id,
                'local_funding_amount': str(amount_sats),
                'push_sat': str(push_sats) if push_sats > 0 else "0"
            }
            
            response = self._make_request('POST', '/v1/channels', data)
            return {
                'funding_txid': response.get('funding_txid'),
                'output_index': response.get('output_index')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to open channel on LND node '{self.node_name}': {e}")
    
    def close_channel(self, channel_point: str, force: bool = False) -> Dict[str, Any]:
        """Close a channel."""
        try:
            # Parse channel point (format: txid:output_index)
            txid, output_index = channel_point.split(':')
            
            endpoint = f"/v1/channels/{txid}/{output_index}"
            if force:
                endpoint += "?force=true"
            
            response = self._make_request('DELETE', endpoint)
            return {
                'closing_txid': response.get('closing_txid')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to close channel on LND node '{self.node_name}': {e}")
    
    def decode_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Decode a Lightning invoice."""
        try:
            endpoint = f"/v1/payreq/{payment_request}"
            response = self._make_request('GET', endpoint)
            
            return {
                'payment_hash': response.get('payment_hash'),
                'destination': response.get('destination'),
                'num_satoshis': int(response.get('num_satoshis', 0)),
                'timestamp': int(response.get('timestamp', 0)),
                'expiry': int(response.get('expiry', 0)),
                'description': response.get('description')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to decode invoice on LND node '{self.node_name}': {e}")
    
    def get_route(self, destination: str, amount_sats: int) -> List[Dict[str, Any]]:
        """Get a route to a destination."""
        try:
            data = {
                'pub_key': destination,
                'amt': amount_sats
            }
            
            response = self._make_request('POST', '/v1/graph/routes', data)
            return response.get('routes', [])
        except Exception as e:
            raise RuntimeError(f"Failed to get route on LND node '{self.node_name}': {e}")
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """Get wallet (on-chain) balance."""
        try:
            response = self._make_request('GET', '/v1/balance/blockchain')
            return {
                'confirmed_balance': int(response.get('confirmed_balance', 0)),
                'unconfirmed_balance': int(response.get('unconfirmed_balance', 0)),
                'total_balance': int(response.get('total_balance', 0))
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get wallet balance from LND node '{self.node_name}': {e}")
    
    def get_channel_balance(self) -> Dict[str, Any]:
        """Get channel (Lightning) balance."""
        try:
            response = self._make_request('GET', '/v1/balance/channels')
            return {
                'balance': int(response.get('balance', 0)),
                'pending_open_balance': int(response.get('pending_open_balance', 0))
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get channel balance from LND node '{self.node_name}': {e}")
    
    def list_invoices(self, pending_only: bool = False) -> List[Dict[str, Any]]:
        """List invoices."""
        try:
            endpoint = '/v1/invoices'
            if pending_only:
                endpoint += '?pending_only=true'
            
            response = self._make_request('GET', endpoint)
            return response.get('invoices', [])
        except Exception as e:
            raise RuntimeError(f"Failed to list invoices from LND node '{self.node_name}': {e}")
    
    def list_payments(self) -> List[Dict[str, Any]]:
        """List payments."""
        try:
            response = self._make_request('GET', '/v1/payments')
            return response.get('payments', [])
        except Exception as e:
            raise RuntimeError(f"Failed to list payments from LND node '{self.node_name}': {e}")


# Utility functions for LND gRPC stub generation
def generate_lnd_stubs():
    """
    Generate LND gRPC stubs from proto files.
    This would typically be done as part of the build process.
    """
    # This is a placeholder - in practice you would:
    # 1. Download the LND proto files
    # 2. Use grpcio-tools to generate the Python stubs
    # 3. Import and use them in the LNDClient class
    
    # Example command to generate stubs:
    # python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. rpc.proto
    
    pass


# Note: To use this LND client properly, you would need to:
# 1. Download the LND proto files (rpc.proto, etc.)
# 2. Generate Python gRPC stubs using grpcio-tools
# 3. Replace the mock implementations with actual gRPC calls
# 4. Handle proper error cases and response parsing

# Example of what the actual implementation would look like:
"""
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

class LNDClient:
    def get_info(self):
        stub = lnrpc.LightningStub(self.channel)
        response = stub.GetInfo(ln.GetInfoRequest(), metadata=self.metadata)
        return {
            'identity_pubkey': response.identity_pubkey,
            'alias': response.alias,
            'color': response.color,
            'num_peers': response.num_peers,
            # ... etc
        }
""" 