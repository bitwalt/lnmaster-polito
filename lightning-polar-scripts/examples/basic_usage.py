#!/usr/bin/env python3
"""
Basic usage example for Lightning Polar Scripts.

This script demonstrates how to:
1. Load configuration
2. Connect to Core Lightning and LND nodes
3. Get basic node information
4. Display results
"""

from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.core_lightning import CoreLightningClient
from lightning_polar_scripts.lnd import LNDClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def main():
    """Main example function."""
    console.print(Panel.fit("Lightning Polar Scripts - Basic Usage Example", style="bold blue"))
    
    try:
        # Load configuration
        console.print("\n[yellow]Loading configuration...[/yellow]")
        config = load_config()
        
        console.print(f"[green]✓[/green] Configuration loaded successfully")
        console.print(f"Found {len(config.nodes)} nodes: {list(config.nodes.keys())}")
        
        # Try Core Lightning nodes
        cln_nodes = [name for name, node in config.nodes.items() if node.implementation == "CLN"]
        if cln_nodes:
            console.print(f"\n[cyan]Core Lightning Nodes:[/cyan] {cln_nodes}")
            
            for node_name in cln_nodes:
                try:
                    client = CoreLightningClient(config, node_name)
                    info = client.get_info()
                    
                    table = Table(title=f"CLN Node: {node_name}")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")
                    
                    table.add_row("Node ID", str(info.get('id', 'N/A'))[:20] + '...')
                    table.add_row("Alias", str(info.get('alias', 'N/A')))
                    table.add_row("Version", str(info.get('version', 'N/A')))
                    table.add_row("Network", str(info.get('network', 'N/A')))
                    table.add_row("Block Height", str(info.get('blockheight', 'N/A')))
                    table.add_row("Peers", str(info.get('num_peers', 'N/A')))
                    table.add_row("Active Channels", str(info.get('num_active_channels', 'N/A')))
                    
                    console.print(table)
                    
                    # Try to get balance
                    try:
                        balance = client.get_balance()
                        console.print(f"[green]Balance: {balance:,} sats[/green]")
                    except Exception as e:
                        console.print(f"[yellow]Could not get balance: {e}[/yellow]")
                    
                except Exception as e:
                    console.print(f"[red]Error connecting to CLN node '{node_name}': {e}[/red]")
        
        # Try LND nodes
        lnd_nodes = [name for name, node in config.nodes.items() if node.implementation == "LND"]
        if lnd_nodes:
            console.print(f"\n[magenta]LND Nodes:[/magenta] {lnd_nodes}")
            
            for node_name in lnd_nodes:
                try:
                    client = LNDClient(config, node_name)
                    info = client.get_info()
                    
                    table = Table(title=f"LND Node: {node_name}")
                    table.add_column("Property", style="magenta")
                    table.add_column("Value", style="green")
                    
                    table.add_row("Node ID", str(info.get('identity_pubkey', 'N/A'))[:20] + '...')
                    table.add_row("Alias", str(info.get('alias', 'N/A')))
                    table.add_row("Version", str(info.get('version', 'N/A')))
                    table.add_row("Block Height", str(info.get('block_height', 'N/A')))
                    table.add_row("Synced to Chain", str(info.get('synced_to_chain', 'N/A')))
                    table.add_row("Peers", str(info.get('num_peers', 'N/A')))
                    table.add_row("Active Channels", str(info.get('num_active_channels', 'N/A')))
                    
                    console.print(table)
                    
                    # Try to get balance
                    try:
                        balance = client.get_balance()
                        console.print(f"[green]Balance: {balance:,} sats[/green]")
                    except Exception as e:
                        console.print(f"[yellow]Could not get balance: {e}[/yellow]")
                    
                except Exception as e:
                    console.print(f"[red]Error connecting to LND node '{node_name}': {e}[/red]")
        
        if not cln_nodes and not lnd_nodes:
            console.print("\n[yellow]No nodes found in configuration.[/yellow]")
            console.print("Make sure you have:")
            console.print("1. Polar running with nodes started, or")
            console.print("2. Environment variables set correctly, or")
            console.print("3. Manual configuration in place")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\n[yellow]Troubleshooting tips:[/yellow]")
        console.print("1. Make sure Polar is installed and running")
        console.print("2. Check that nodes are started in Polar")
        console.print("3. Verify environment variables in .env file")
        console.print("4. Check file permissions for socket/cert files")


if __name__ == "__main__":
    main() 