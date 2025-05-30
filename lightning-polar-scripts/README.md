# Lightning Polar Scripts

Tools for interacting with Polar Lightning Network, supporting both Core Lightning (CLN) and LND implementations.

## Features

- **Core Lightning Support**: Full integration with CLN nodes via pyln-client
- **LND Support**: REST API-based integration with LND nodes (no gRPC dependencies!)
- **Polar Integration**: Automatic detection and configuration of Polar networks
- **CLI Interface**: Rich command-line interface with beautiful output
- **Flexible Configuration**: Support for environment variables and Polar auto-discovery
- **Comprehensive LND API**: Full REST API support including wallets, channels, invoices, and payments

## Installation

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- Polar Lightning Network (optional, for automatic configuration)

### Setup

1. Clone or navigate to the project directory:
```bash
cd lightning-polar-scripts
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Configuration

### Option 1: Polar Auto-Discovery

If you have Polar installed and running, the scripts will automatically detect your networks and nodes. Just make sure Polar is running with nodes started.

### Option 2: Environment Variables

Create a `.env` file in the project root:

```bash
# Core Lightning Configuration
CLN_SOCKET_PATH=/path/to/lightning-rpc

# LND Configuration
LND_HOST=localhost
LND_PORT=10001          # gRPC port (for future use)
LND_REST_PORT=8080      # REST API port
LND_MACAROON_PATH=/path/to/admin.macaroon
LND_CERT_PATH=/path/to/tls.cert

# Polar Configuration (optional)
POLAR_HOME=~/.polar
```

### Option 3: Manual Configuration

The configuration system will create default values if no configuration is found, though you'll need to update the paths to match your setup.

## Usage

### CLI Commands

The project provides a command-line interface accessible via:

```bash
# Using Poetry
poetry run polar-cli --help

# Or if you're in the Poetry shell
polar-cli --help
```

### Core Lightning Commands

```bash
# Get node information
polar-cli cln info --node alice

# Check balance
polar-cli cln balance --node alice

# List channels
polar-cli cln channels --node alice
```

### LND Commands

```bash
# Get node information
polar-cli lnd info --node bob

# Check balances
polar-cli lnd balance --node bob
polar-cli lnd wallet-balance --node bob
polar-cli lnd channel-balance --node bob

# List channels and peers
polar-cli lnd channels --node bob
polar-cli lnd peers --node bob

# Invoice management
polar-cli lnd create-invoice --node bob --amount 1000 --memo "Test invoice"
polar-cli lnd list-invoices --node bob
polar-cli lnd pay-invoice --node bob --payment-request lnbc...

# Payment history
polar-cli lnd list-payments --node bob
```

## Project Structure

```
lightning-polar-scripts/
├── lightning_polar_scripts/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── core_lightning.py    # Core Lightning client
│   └── lnd.py              # LND REST API client
├── examples/
│   ├── basic_usage.py       # Basic usage example
│   └── lnd_rest_demo.py     # LND REST API demo
├── tests/                   # Test files
├── pyproject.toml          # Poetry configuration
├── README.md               # This file
└── .env.example            # Environment variables example
```

## Development

### Dependencies

Core dependencies:
- `pyln-client`: Core Lightning Python client
- `pyln-proto`: Core Lightning protocol definitions
- `requests`: HTTP library for LND REST API
- `urllib3`: HTTP library utilities
- `click`: Command-line interface framework
- `rich`: Rich text and beautiful formatting
- `pydantic`: Data validation and settings management
- `python-dotenv`: Environment variable loading

Development dependencies:
- `pytest`: Testing framework
- `black`: Code formatting
- `isort`: Import sorting
- `flake8`: Linting
- `mypy`: Type checking

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
# Format code
poetry run black lightning_polar_scripts/

# Sort imports
poetry run isort lightning_polar_scripts/

# Run linting
poetry run flake8 lightning_polar_scripts/
```

## API Reference

### Core Lightning Client

```python
from lightning_polar_scripts.core_lightning import CoreLightningClient
from lightning_polar_scripts.config import load_config

config = load_config()
client = CoreLightningClient(config, 'alice')

# Get node info
info = client.get_info()

# Get balance
balance = client.get_balance()

# List channels
channels = client.list_channels()
```

### LND REST API Client

```python
from lightning_polar_scripts.lnd import LNDClient
from lightning_polar_scripts.config import load_config

config = load_config()
client = LNDClient(config, 'bob')

# Get node info
info = client.get_info()

# Get balances
wallet_balance = client.get_wallet_balance()
channel_balance = client.get_channel_balance()

# Create invoice
invoice = client.create_invoice(1000, "Test invoice", 3600)

# List channels and peers
channels = client.list_channels()
peers = client.list_peers()

# Payment operations
payments = client.list_payments()
invoices = client.list_invoices()
```

## LND REST API Features

The LND client uses REST API and supports:

✅ **Node Information**
- Get node info, version, sync status
- Check connection and health

✅ **Balance Management**
- Wallet (on-chain) balance
- Channel (Lightning) balance
- Combined balance reporting

✅ **Channel Operations**
- List active channels
- Channel details and status
- Channel balance information

✅ **Peer Management**
- List connected peers
- Peer connection details
- Network statistics

✅ **Invoice Management**
- Create invoices with custom amounts and memos
- List invoices (all or pending only)
- Invoice status and settlement info

✅ **Payment Operations**
- Pay Lightning invoices
- List payment history
- Payment routing information

✅ **Network Operations**
- Decode Lightning invoices
- Route finding
- Network graph information

## Examples

### Basic Node Information

```python
#!/usr/bin/env python3
from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.core_lightning import CoreLightningClient
from lightning_polar_scripts.lnd import LNDClient

# Load configuration
config = load_config()

# Core Lightning example
if 'alice' in config.nodes:
    cln_client = CoreLightningClient(config, 'alice')
    info = cln_client.get_info()
    print(f"CLN Node ID: {info['id']}")
    print(f"CLN Alias: {info['alias']}")

# LND example
if 'bob' in config.nodes:
    lnd_client = LNDClient(config, 'bob')
    info = lnd_client.get_info()
    print(f"LND Node ID: {info['identity_pubkey']}")
    print(f"LND Alias: {info['alias']}")
```

### LND REST API Demo

Run the comprehensive LND REST API demo:

```bash
poetry run python examples/lnd_rest_demo.py
```

This demo showcases:
- Node information retrieval
- Balance checking (wallet and channel)
- Peer and channel listing
- Invoice creation and management
- Payment history

### Creating and Paying Invoices

```python
from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.lnd import LNDClient

config = load_config()
bob = LNDClient(config, 'bob')

# Create an invoice for 1000 sats
invoice = bob.create_invoice(1000, "Test payment", 3600)
print(f"Payment request: {invoice['payment_request']}")

# Pay the invoice (from another node)
# payment = alice.pay_invoice(invoice['payment_request'])
```

## Troubleshooting

### Common Issues

1. **"No Polar networks found"**: Make sure Polar is installed and you have at least one network created.

2. **Socket connection errors**: Verify that the CLN socket path is correct and the node is running.

3. **LND REST API connection errors**: Check that:
   - LND is running and REST API is enabled
   - REST port is correct (default: 8080)
   - Macaroon and certificate paths are correct
   - Network connectivity is available

4. **Permission errors**: Ensure the script has read access to socket files and certificates.

### LND REST API Troubleshooting

**Connection Issues:**
```bash
# Test LND REST API directly
curl -k --header "Grpc-Metadata-macaroon: $(xxd -ps -u -c 1000 /path/to/admin.macaroon)" \
  https://localhost:8080/v1/getinfo
```

**Configuration Issues:**
- Verify `LND_REST_PORT` matches your LND configuration
- Check that macaroon file exists and is readable
- Ensure certificate path is correct (or disable SSL verification for development)

### Debug Mode

Set environment variable for verbose logging:
```bash
export DEBUG=1
polar-cli lnd info
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Polar documentation
3. Check LND REST API documentation
4. Open an issue on the project repository
