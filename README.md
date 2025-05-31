# ⚡ Lightning Network Master Course - Politecnico di Torino

This repository contains educational materials and hands-on exercises for learning Lightning Network development using the [Polar](https://lightningpolar.com/) simulator. The course focuses on practical experience with LND and Core Lightning (CLN) implementations.

## 📚 Repository Contents

### Core Materials
- **[`exercises.md`](exercises.md)** - Step-by-step Lightning Network exercises covering:
  - Channel setup and management
  - BOLT11 payments
  - BOLT12 offers
  - Channel policy configuration
  - Network graph exploration
  - Automation scripting

- **[`cheatsheet.md`](cheatsheet.md)** - Quick reference guide with CLI commands for:
  - Bitcoin Core (regtest funding)
  - LND (`lncli` commands)
  - Core Lightning (`lightning-cli` commands)
  - Network debugging and management

### Scripts and Examples
- **[`lightning-polar-scripts/`](lightning-polar-scripts/)** - Python scripts and automation tools
  - REST API demonstrations
  - Test scripts for both LND and CLN
  - Example implementations

## 🚀 Getting Started

### Prerequisites
1. **Polar Lightning Network Simulator**
   - Download from [lightningpolar.com](https://lightningpolar.com/)
   - Install Docker (required by Polar)

2. **Basic Knowledge**
   - Bitcoin fundamentals
   - Command line interface experience
   - Basic understanding of payment channels

### Setup Instructions

1. **Install Polar**
   ```bash
   # Download and install Polar from the official website
   # Make sure Docker is running
   ```

2. **Clone this repository**
   ```bash
   git clone <repository-url>
   cd lnmaster-polito
   ```

3. **Open the course materials**
   ```bash
   # Open exercises in your browser
   open exercises.md
   
   # Open cheatsheet for reference
   open cheatsheet.md
   ```

4. **Set up your first Polar network**
   - Create a new network in Polar
   - Add 1 LND node and 2 CLN nodes
   - Start the network

## 🎯 Learning Path

### Beginner Level
1. Start with **Exercise 1: Channel Setup**
2. Practice basic funding and channel opening
3. Use the cheatsheet for command reference

### Intermediate Level
4. Complete **BOLT11 and BOLT12 payment exercises**
5. Experiment with **channel policy tweaks**
6. Explore the **network graph visualization**

### Advanced Level
7. Work on **script automation exercises**
8. Dive into the Python scripts in `lightning-polar-scripts/`
9. Create your own automation tools

## 🛠️ Available Node Types

This course covers two major Lightning implementations:

### LND (Lightning Network Daemon)
- CLI tool: `lncli`
- REST and gRPC APIs
- Well-documented and widely adopted

### Core Lightning (CLN)
- CLI tool: `lightning-cli`
- JSON-RPC API
- Highly customizable and plugin-friendly

## 📖 Exercise Overview

| Exercise | Topic | Skills Developed |
|----------|-------|------------------|
| 1 | Channel Setup | Network topology, funding |
| 2 | BOLT11 Payments | Invoice creation, payment routing |
| 3 | BOLT12 Offers | Modern payment flows, privacy |
| 4 | Channel Policies | Fee management, routing optimization |
| 5 | Network Exploration | Graph visualization, monitoring |
| 6 | Script Automation | Programming, API integration |

## 🔧 Commands Quick Reference

### Essential Commands
```bash
# Fund a node
bitcoin-cli -regtest sendtoaddress <address> 1

# Open channel (LND)
lncli openchannel --node_key=<pubkey> --local_amt=500000

# Create invoice (CLN)
lightning-cli invoice 100000 "label" "description"

# Pay invoice (LND)
lncli payinvoice <bolt11_string>
```

For complete command reference, see [`cheatsheet.md`](cheatsheet.md).

## 🎓 Educational Goals

By completing this course, students will:
- Understand Lightning Network architecture
- Gain hands-on experience with major LN implementations
- Learn to manage channels and routing
- Master both BOLT11 and BOLT12 payment protocols
- Develop automation and monitoring skills
- Build confidence for mainnet operations

## 🤝 Contributing

This is an educational repository. Contributions are welcome:
- Bug fixes in exercises or documentation
- Additional example scripts
- Improved explanations or tutorials
- New exercise ideas

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🔗 Resources

- [Polar Lightning Simulator](https://lightningpolar.com/)
- [LND Documentation](https://docs.lightning.engineering/)
- [Core Lightning Documentation](https://lightning.readthedocs.io/)
- [Lightning Network Specifications (BOLTs)](https://github.com/lightning/bolts)

---

**Happy Learning! ⚡**

*Politecnico di Torino - Lightning Network Master Course* 