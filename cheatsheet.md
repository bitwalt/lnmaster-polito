# ⚡ Lightning CLI Cheatsheet (Polar Lab)

This cheatsheet provides quick reference commands for working with LND, CLN, and Bitcoin Core inside a Polar Lightning Network simulation.

---

## 🪙 Bitcoin Core (Funding Nodes)

```bash
# Generate blocks to mature coinbase
bitcoin-cli -regtest generatetoaddress 103 $(bitcoin-cli -regtest getnewaddress)

# Send BTC to a Lightning node
bitcoin-cli -regtest sendtoaddress <NODE_ADDRESS> 1
```

---

## 🔐 LND Node (lncli)

```bash
# Get on-chain address
lncli newaddress p2wkh

# Wallet balance
lncli walletbalance

# Node pubkey
lncli getinfo | jq -r '.identity_pubkey'

# Connect to peer
lncli connect <PUBKEY>@<IP>

# Open channel
lncli openchannel --node_key=<PUBKEY> --local_amt=500000

# List channel status
lncli pendingchannels
lncli listchannels

# Update channel fees
lncli updatechanpolicy --base_fee_msat=1000 --fee_rate=0.000001 --time_lock_delta=40

# Create invoice
lncli addinvoice --amt=100000 --memo="Test Payment"

# Pay invoice
lncli payinvoice <BOLT11_STRING>
```

---

## ⚙️ Core Lightning (CLN - lightning-cli)

```bash
# Get on-chain address
lightning-cli newaddr

# List wallet funds
lightning-cli listfunds

# Get node pubkey
lightning-cli getinfo | jq -r '.id'

# Connect to peer
lightning-cli connect <PUBKEY> <IP> <PORT>

# Open channel
lightning-cli fundchannel <PUBKEY> 500000

# List peers and channels
lightning-cli listpeers
lightning-cli listchannels

# Update channel fees
lightning-cli setchannelfee id=<CHANNEL_ID> base=1000 ppm=1

# Create Bolt11 invoice
lightning-cli invoice 100000 "label" "desc"

# Pay invoice
lightning-cli pay <BOLT11_STRING>

# Create Bolt12 offer
lightning-cli offer 100000 "Bolt12 Test"

# Fetch invoice from offer
lightning-cli fetchinvoice <BOLT12_OFFER>

# Pay fetched invoice
lightning-cli pay <BOLT12_INVOICE>
```

---

## 🛠 Debug / Network Management

```bash
# LND node info
lncli getinfo

# CLN node info
lightning-cli getinfo

# Mine blocks (simulate confirmations)
bitcoin-cli -regtest generatetoaddress 6 $(bitcoin-cli -regtest getnewaddress)
```

---

Use this cheat sheet alongside the full lab guide to quickly reference key commands during hands-on activities.

**Happy hacking ⚡** 