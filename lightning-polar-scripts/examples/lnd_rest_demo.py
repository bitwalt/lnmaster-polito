#!/usr/bin/env python3
"""
LND REST API Demo Script

This script demonstrates how to use the Lightning Polar Scripts
with LND via REST API. It shows various LND operations including:
- Getting node information
- Checking balances (wallet and channel)
- Creating invoices
- Listing peers and channels
- Managing payments
"""

import os
from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.lnd import LNDClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


def demo_node_info(client, node_name):
    """Demonstrate getting node information."""
    console.print("\n[bold cyan]═══ Node Information ═══[/bold cyan]")
    
    try:
        info = client.get_info()
        
        table = Table(title=f"LND Node Information - {node_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Node ID", str(info.get('identity_pubkey', 'N/A'))[:20] + '...')
        table.add_row("Alias", str(info.get('alias', 'N/A')))
        table.add_row("Version", str(info.get('version', 'N/A')))
        table.add_row("Block Height", str(info.get('block_height', 'N/A')))
        table.add_row("Synced to Chain", str(info.get('synced_to_chain', 'N/A')))
        table.add_row("Synced to Graph", str(info.get('synced_to_graph', 'N/A')))
        table.add_row("Peers", str(info.get('num_peers', 'N/A')))
        table.add_row("Active Channels", str(info.get('num_active_channels', 'N/A')))
        table.add_row("Pending Channels", str(info.get('num_pending_channels', 'N/A')))
        
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to get node info: {e}[/red]")
        return False


def demo_balances(client, node_name):
    """Demonstrate getting wallet and channel balances."""
    console.print("\n[bold cyan]═══ Balance Information ═══[/bold cyan]")
    
    try:
        # Wallet balance
        wallet_balance = client.get_wallet_balance()
        
        wallet_table = Table(title="Wallet (On-chain) Balance")
        wallet_table.add_column("Type", style="cyan")
        wallet_table.add_column("Amount (sats)", style="green")
        
        wallet_table.add_row("Confirmed", f"{wallet_balance['confirmed_balance']:,}")
        wallet_table.add_row("Unconfirmed", f"{wallet_balance['unconfirmed_balance']:,}")
        wallet_table.add_row("Total", f"{wallet_balance['total_balance']:,}")
        
        console.print(wallet_table)
        
        # Channel balance
        channel_balance = client.get_channel_balance()
        
        channel_table = Table(title="Channel (Lightning) Balance")
        channel_table.add_column("Type", style="cyan")
        channel_table.add_column("Amount (sats)", style="green")
        
        channel_table.add_row("Available", f"{channel_balance['balance']:,}")
        channel_table.add_row("Pending Open", f"{channel_balance['pending_open_balance']:,}")
        
        console.print(channel_table)
        
        # Total balance
        total = wallet_balance['confirmed_balance'] + channel_balance['balance']
        console.print(f"\n[bold green]💰 Total Balance: {total:,} sats[/bold green]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to get balances: {e}[/red]")
        return False


def demo_peers_and_channels(client, node_name):
    """Demonstrate listing peers and channels."""
    console.print("\n[bold cyan]═══ Peers and Channels ═══[/bold cyan]")
    
    try:
        # List peers
        peers = client.list_peers()
        
        if peers:
            peers_table = Table(title="Connected Peers")
            peers_table.add_column("Public Key", style="cyan")
            peers_table.add_column("Address", style="yellow")
            peers_table.add_column("Sats Sent", style="green")
            peers_table.add_column("Sats Received", style="blue")
            
            for peer in peers[:5]:  # Show first 5
                peers_table.add_row(
                    str(peer.get('pub_key', 'N/A'))[:20] + '...',
                    str(peer.get('address', 'N/A')),
                    str(peer.get('sat_sent', 'N/A')),
                    str(peer.get('sat_recv', 'N/A'))
                )
            
            console.print(peers_table)
        else:
            console.print("[yellow]No peers connected[/yellow]")
        
        # List channels
        channels = client.list_channels()
        
        if channels:
            channels_table = Table(title="Lightning Channels")
            channels_table.add_column("Channel ID", style="cyan")
            channels_table.add_column("Remote Peer", style="yellow")
            channels_table.add_column("Capacity", style="blue")
            channels_table.add_column("Local Balance", style="green")
            channels_table.add_column("Active", style="magenta")
            
            for channel in channels[:5]:  # Show first 5
                channels_table.add_row(
                    str(channel.get('chan_id', 'N/A')),
                    str(channel.get('remote_pubkey', 'N/A'))[:20] + '...',
                    f"{channel.get('capacity', 0):,}",
                    f"{channel.get('local_balance', 0):,}",
                    "✓" if channel.get('active', False) else "✗"
                )
            
            console.print(channels_table)
        else:
            console.print("[yellow]No channels found[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to get peers/channels: {e}[/red]")
        return False


def demo_invoice_management(client, node_name):
    """Demonstrate invoice creation and listing."""
    console.print("\n[bold cyan]═══ Invoice Management ═══[/bold cyan]")
    
    try:
        # Create a test invoice
        console.print("[yellow]Creating a test invoice for 1000 sats...[/yellow]")
        invoice = client.create_invoice(1000, "Demo invoice from Lightning Polar Scripts", 3600)
        
        console.print(f"[green]✓ Invoice created successfully![/green]")
        console.print(f"[cyan]Payment Request:[/cyan]")
        console.print(f"[dim]{invoice.get('payment_request', 'N/A')}[/dim]")
        
        # List recent invoices
        console.print("\n[yellow]Listing recent invoices...[/yellow]")
        invoices = client.list_invoices()
        
        if invoices:
            invoices_table = Table(title="Recent Invoices")
            invoices_table.add_column("Index", style="cyan")
            invoices_table.add_column("Value (sats)", style="blue")
            invoices_table.add_column("Memo", style="yellow")
            invoices_table.add_column("Settled", style="green")
            
            for invoice in invoices[:5]:  # Show first 5
                memo = str(invoice.get('memo', 'N/A'))
                if len(memo) > 30:
                    memo = memo[:30] + '...'
                
                invoices_table.add_row(
                    str(invoice.get('add_index', 'N/A')),
                    str(invoice.get('value', 'N/A')),
                    memo,
                    "✓" if invoice.get('settled', False) else "✗"
                )
            
            console.print(invoices_table)
        else:
            console.print("[yellow]No invoices found[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to manage invoices: {e}[/red]")
        return False


def demo_payment_history(client, node_name):
    """Demonstrate listing payment history."""
    console.print("\n[bold cyan]═══ Payment History ═══[/bold cyan]")
    
    try:
        payments = client.list_payments()
        
        if payments:
            payments_table = Table(title="Recent Payments")
            payments_table.add_column("Payment Hash", style="cyan")
            payments_table.add_column("Value (sats)", style="blue")
            payments_table.add_column("Fee (sats)", style="yellow")
            payments_table.add_column("Status", style="green")
            
            for payment in payments[:5]:  # Show first 5
                payments_table.add_row(
                    str(payment.get('payment_hash', 'N/A'))[:20] + '...',
                    str(payment.get('value', 'N/A')),
                    str(payment.get('fee', 'N/A')),
                    str(payment.get('status', 'N/A'))
                )
            
            console.print(payments_table)
        else:
            console.print("[yellow]No payments found[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Failed to get payment history: {e}[/red]")
        return False


def main():
    """Main demo function."""
    console.print(Panel.fit("🚀 LND REST API Demo", style="bold blue"))
    
    # Load configuration
    console.print("\n[yellow]Loading configuration...[/yellow]")
    
    try:
        config = load_config()
        
        # Find LND nodes
        lnd_nodes = [name for name, node in config.nodes.items() if node.implementation == "LND"]
        
        if not lnd_nodes:
            console.print("\n[red]❌ No LND nodes found in configuration![/red]")
            console.print("\n[yellow]To use this demo, you need to:[/yellow]")
            console.print("1. Set up a Polar Lightning Network with LND nodes, or")
            console.print("2. Configure environment variables in .env file:")
            console.print("   - LND_HOST=localhost")
            console.print("   - LND_REST_PORT=8080")
            console.print("   - LND_MACAROON_PATH=/path/to/admin.macaroon")
            console.print("   - LND_CERT_PATH=/path/to/tls.cert")
            return
        
        console.print(f"[green]✓ Found {len(lnd_nodes)} LND node(s): {lnd_nodes}[/green]")
        
        # Use the first LND node for demo
        node_name = lnd_nodes[0]
        console.print(f"[cyan]Using node: {node_name}[/cyan]")
        
        # Create LND client
        client = LNDClient(config, node_name)
        console.print(f"[green]✓ Connected to LND node via REST API[/green]")
        
        # Run demonstrations
        success_count = 0
        
        if demo_node_info(client, node_name):
            success_count += 1
        
        if demo_balances(client, node_name):
            success_count += 1
        
        if demo_peers_and_channels(client, node_name):
            success_count += 1
        
        if demo_invoice_management(client, node_name):
            success_count += 1
        
        if demo_payment_history(client, node_name):
            success_count += 1
        
        # Summary
        console.print(f"\n[bold green]✅ Demo completed! {success_count}/5 sections successful[/bold green]")
        
        if success_count < 5:
            console.print("\n[yellow]Some sections failed. This is normal if:[/yellow]")
            console.print("- LND node is not running")
            console.print("- REST API is not accessible")
            console.print("- Macaroon/certificate paths are incorrect")
            console.print("- Network connectivity issues")
    
    except Exception as e:
        console.print(f"\n[red]❌ Demo failed: {e}[/red]")
        console.print("\n[yellow]Troubleshooting tips:[/yellow]")
        console.print("1. Make sure LND is running and accessible")
        console.print("2. Check your .env configuration")
        console.print("3. Verify macaroon and certificate paths")
        console.print("4. Ensure REST API port is correct (default: 8080)")


if __name__ == "__main__":
    main() 