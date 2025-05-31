# 🧪 Lightning Network Exercises with Polar

This document outlines a series of exercises for students to practice working with Lightning implementations inside the Polar simulator.

## 1. Channel Setup

- Create a Polar network with LND and two CLN nodes
- Fund each node using `bitcoin-cli`
- Open channels: LND → CLN1 → CLN2

## 2. Bolt11 Payments

- Create an invoice on CLN2 using `lightning-cli invoice`
- Pay it from LND using `lncli payinvoice`
- Verify payment status on all intermediate nodes

## 3. Bolt12 Offers

- Generate a Bolt12 offer on CLN1 using `lightning-cli offer`
- Fetch and pay the offer from CLN2
- Observe how BOLT12 improves privacy and flow

## 4. Channel Policy Tweaks

- Change channel fees using:
  - `lncli updatechanpolicy` for LND
  - `lightning-cli setchannelfee` for CLN
- Try routing a payment again and note the impact

## 5. Network Graph Exploration

- Use ThunderHub or RTL to visualize the graph
- Compare public vs. private channels
- Inspect forwarding history and channel status

## 6. Script Automation (Advanced)

- Write a Bash or Python script to:
  - Open a channel
  - Create and pay invoices
  - Query channel states
- Bonus: log the results to a file with timestamps

💡 **Tip:** Encourage students to snapshot the network state in Polar before and after each step for comparison and recovery.

**Have fun experimenting with Lightning! ⚡** 