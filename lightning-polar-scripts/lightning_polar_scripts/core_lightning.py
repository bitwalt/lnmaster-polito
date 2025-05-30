"""Core Lightning client for interacting with CLN nodes via REST API."""

import json
import requests
from typing import Dict, List, Any, Optional
from .config import PolarConfig, NodeConfig


class CoreLightningClient:
    """Client for interacting with Core Lightning nodes via REST API."""
    
    def __init__(self, config: PolarConfig, node_name: str):
        """Initialize CLN REST client."""
        if node_name not in config.nodes:
            raise ValueError(f"Node '{node_name}' not found in configuration")
        
        self.node_config = config.nodes[node_name]
        if self.node_config.implementation != "CLN":
            raise ValueError(f"Node '{node_name}' is not a Core Lightning node")
        
        if not self.node_config.rest_port:
            raise ValueError(f"REST port not configured for node '{node_name}'")
        
        self.base_url = f"http://{self.node_config.rpc_host}:{self.node_config.rest_port}"
        self.node_name = node_name
        
        # Setup session with authentication
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication for REST API calls."""
        # Read rune for authentication
        if self.node_config.rune_path:
            try:
                with open(self.node_config.rune_path, 'r') as f:
                    rune = f.read().strip()
                    self.session.headers.update({
                        'Rune': rune
                    })
            except Exception as e:
                print(f"Warning: Could not read rune file: {e}")
        
        # Setup TLS certificates if available
        if (self.node_config.client_cert_path and 
            self.node_config.client_key_path):
            try:
                self.session.cert = (
                    self.node_config.client_cert_path,
                    self.node_config.client_key_path
                )
            except Exception as e:
                print(f"Warning: Could not setup client certificates: {e}")
        
        if self.node_config.ca_cert_path:
            try:
                self.session.verify = self.node_config.ca_cert_path
            except Exception as e:
                print(f"Warning: Could not setup CA certificate: {e}")
                self.session.verify = False
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the CLN REST API."""
        url = f"{self.base_url}/v1/{method}"
        
        try:
            # CLN REST API uses POST for all RPC methods
            payload = {}
            if params:
                payload = params
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to CLN node '{self.node_name}': {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from CLN node '{self.node_name}': {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get node information."""
        try:
            info = self._make_request("getinfo")
            return {
                'id': info.get('id'),
                'alias': info.get('alias'),
                'color': info.get('color'),
                'num_peers': info.get('num_peers'),
                'num_pending_channels': info.get('num_pending_channels'),
                'num_active_channels': info.get('num_active_channels'),
                'num_inactive_channels': info.get('num_inactive_channels'),
                'blockheight': info.get('blockheight'),
                'network': info.get('network'),
                'version': info.get('version')
            }
        except Exception as e:
            raise ConnectionError(f"Failed to get info from CLN node '{self.node_name}': {e}")
    
    def get_balance(self) -> int:
        """Get node balance in satoshis."""
        try:
            balance = self._make_request("listfunds")
            total_outputs = sum(
                output['amount_msat'] for output in balance.get('outputs', []) 
                if output.get('status') == 'confirmed'
            )
            total_channels = sum(
                channel['our_amount_msat'] for channel in balance.get('channels', [])
            )
            return (total_outputs + total_channels) // 1000  # Convert to satoshis
        except Exception as e:
            raise ConnectionError(f"Failed to get balance from CLN node '{self.node_name}': {e}")
    
    def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels."""
        try:
            channels = self._make_request("listchannels")
            return channels.get('channels', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list channels from CLN node '{self.node_name}': {e}")
    
    def list_peers(self) -> List[Dict[str, Any]]:
        """List all peers."""
        try:
            peers = self._make_request("listpeers")
            return peers.get('peers', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list peers from CLN node '{self.node_name}': {e}")
    
    def create_invoice(self, amount_sats: int, label: str, description: str = None) -> Dict[str, Any]:
        """Create a new invoice."""
        try:
            amount_msat = amount_sats * 1000
            params = {
                "amount_msat": amount_msat,
                "label": label,
                "description": description or label
            }
            invoice = self._make_request("invoice", params)
            return {
                'payment_hash': invoice.get('payment_hash'),
                'payment_request': invoice.get('bolt11'),
                'expires_at': invoice.get('expires_at')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create invoice on CLN node '{self.node_name}': {e}")
    
    def list_invoices(self) -> List[Dict[str, Any]]:
        """List all invoices."""
        try:
            invoices = self._make_request("listinvoices")
            return invoices.get('invoices', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list invoices from CLN node '{self.node_name}': {e}")
    
    def pay_invoice(self, payment_request: str, amount_sats: Optional[int] = None) -> Dict[str, Any]:
        """Pay a Lightning invoice."""
        try:
            params = {"bolt11": payment_request}
            if amount_sats:
                params["amount_msat"] = amount_sats * 1000
            
            result = self._make_request("pay", params)
            return {
                'payment_hash': result.get('payment_hash'),
                'payment_preimage': result.get('payment_preimage'),
                'amount_sent_msat': result.get('amount_sent_msat'),
                'status': result.get('status')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to pay invoice on CLN node '{self.node_name}': {e}")
    
    def list_payments(self) -> List[Dict[str, Any]]:
        """List all payments."""
        try:
            payments = self._make_request("listpays")
            return payments.get('pays', [])
        except Exception as e:
            raise ConnectionError(f"Failed to list payments from CLN node '{self.node_name}': {e}")
    
    def connect_peer(self, node_id: str, host: str = None, port: int = None) -> bool:
        """Connect to a peer."""
        try:
            if host and port:
                address = f"{node_id}@{host}:{port}"
            else:
                address = node_id
            
            params = {"id": address}
            self._make_request("connect", params)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to connect to peer on CLN node '{self.node_name}': {e}")
    
    def open_channel(self, node_id: str, amount_sats: int, push_sats: int = 0) -> Dict[str, Any]:
        """Open a channel with a peer."""
        try:
            params = {
                "id": node_id,
                "amount": amount_sats,
            }
            if push_sats > 0:
                params["push_msat"] = push_sats * 1000
            
            result = self._make_request("fundchannel", params)
            return {
                'funding_txid': result.get('txid'),
                'funding_output': result.get('outnum'),
                'channel_id': result.get('channel_id')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to open channel on CLN node '{self.node_name}': {e}")
    
    def close_channel(self, channel_id: str, force: bool = False) -> Dict[str, Any]:
        """Close a channel."""
        try:
            params = {"id": channel_id}
            if force:
                params["unilateraltimeout"] = 1
            
            result = self._make_request("close", params)
            return {
                'closing_txid': result.get('txid'),
                'type': result.get('type')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to close channel on CLN node '{self.node_name}': {e}")
    
    def decode_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Decode a Lightning invoice."""
        try:
            params = {"string": payment_request}
            decoded = self._make_request("decode", params)
            return {
                'payment_hash': decoded.get('payment_hash'),
                'destination': decoded.get('payee'),
                'amount_msat': decoded.get('amount_msat'),
                'timestamp': decoded.get('created_at'),
                'expiry': decoded.get('expiry'),
                'description': decoded.get('description')
            }
        except Exception as e:
            raise RuntimeError(f"Failed to decode invoice on CLN node '{self.node_name}': {e}")
    
    def get_route(self, destination: str, amount_sats: int) -> List[Dict[str, Any]]:
        """Get a route to a destination."""
        try:
            amount_msat = amount_sats * 1000
            params = {
                "id": destination,
                "amount_msat": amount_msat,
                "riskfactor": 1.0
            }
            route = self._make_request("getroute", params)
            return route.get('route', [])
        except Exception as e:
            raise RuntimeError(f"Failed to get route on CLN node '{self.node_name}': {e}") 