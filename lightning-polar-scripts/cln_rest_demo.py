#!/usr/bin/env python3
"""
Core Lightning REST API Demo Script
This script demonstrates how to interact with a CLN node via REST API
"""

import os
import sys
import time
from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.core_lightning import CoreLightningClient
from rich.console import Console
from rich.table import Table

console = Console()

def demo_connection():
    """Test basic connection to CLN node."""
    console.print("\n[bold blue]1. Testing CLN Connection[/bold blue]")
    
    try:
        config = load_config()
        if 'bob' not in config.nodes:
            console.print("[red]❌ Bob node not found in configuration[/red]")
            return False
        
        client = CoreLightningClient(config, 'bob')
        info = client.get_info()
        
        console.print(f"[green]✅ Connected to CLN node successfully![/green]")
        console.print(f"[cyan]Node ID:[/cyan] {info.get('id', 'N/A')}")
        console.print(f"[cyan]Alias:[/cyan] {info.get('alias', 'N/A')}")
        console.print(f"[cyan]Version:[/cyan] {info.get('version', 'N/A')}")
        console.print(f"[cyan]Block Height:[/cyan] {info.get('blockheight', 'N/A')}")
        console.print(f"[cyan]Network:[/cyan] {info.get('network', 'N/A')}")
        console.print(f"[cyan]Peers:[/cyan] {info.get('num_peers', 0)}")
        console.print(f"[cyan]Channels:[/cyan] {info.get('num_active_channels', 0)} active")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
        return False

def demo_balance():
    """Test balance retrieval."""
    console.print("\n[bold blue]2. Testing Balance Retrieval[/bold blue]")
    
    try:
        config = load_config()
        client = CoreLightningClient(config, 'bob')
        balance = client.get_balance()
        
        console.print(f"[green]✅ Retrieved balance: {balance:,} sats[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Balance retrieval failed: {e}[/red]")
        return False

def demo_peers():
    """Test peer listing."""
    console.print("\n[bold blue]3. Testing Peer Listing[/bold blue]")
    
    try:
        config = load_config()
        client = CoreLightningClient(config, 'bob')
        peers = client.list_peers()
        
        console.print(f"[green]✅ Retrieved {len(peers)} peers[/green]")
        for i, peer in enumerate(peers[:3]):  # Show first 3 peers
            console.print(f"[cyan]Peer {i+1}:[/cyan] {peer.get('id', 'N/A')[:20]}... Connected: {peer.get('connected', False)}")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Peer listing failed: {e}[/red]")
        return False

def demo_invoice():
    """Test invoice creation."""
    console.print("\n[bold blue]4. Testing Invoice Creation[/bold blue]")
    
    try:
        config = load_config()
        client = CoreLightningClient(config, 'bob')
        
        # Create unique label with timestamp
        label = f"test-{int(time.time())}"
        invoice = client.create_invoice(1000, label, "Demo invoice from REST API")
        
        console.print(f"[green]✅ Created invoice successfully![/green]")
        console.print(f"[cyan]Payment Hash:[/cyan] {invoice.get('payment_hash', 'N/A')}")
        console.print(f"[cyan]Payment Request:[/cyan] {invoice.get('payment_request', 'N/A')[:50]}...")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Invoice creation failed: {e}[/red]")
        return False

def demo_invoices_list():
    """Test invoice listing."""
    console.print("\n[bold blue]5. Testing Invoice Listing[/bold blue]")
    
    try:
        config = load_config()
        client = CoreLightningClient(config, 'bob')
        invoices = client.list_invoices()
        
        console.print(f"[green]✅ Retrieved {len(invoices)} invoices[/green]")
        for i, invoice in enumerate(invoices[-3:]):  # Show last 3 invoices
            amount = invoice.get('amount_msat', 0) // 1000 if invoice.get('amount_msat') else 0
            console.print(f"[cyan]Invoice {i+1}:[/cyan] {amount} sats - {invoice.get('status', 'N/A')}")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Invoice listing failed: {e}[/red]")
        return False

def main():
    """Run all demo functions."""
    console.print("[bold green]Core Lightning REST API Demo[/bold green]")
    console.print("[yellow]Testing connection to CLN node via REST API...[/yellow]")
    
    # Show configuration
    try:
        config = load_config()
        if 'bob' in config.nodes:
            node = config.nodes['bob']
            console.print(f"[cyan]Node:[/cyan] {node.name} ({node.implementation})")
            console.print(f"[cyan]REST URL:[/cyan] http://{node.rpc_host}:{node.rest_port}")
            console.print(f"[cyan]Rune Path:[/cyan] {node.rune_path}")
            console.print(f"[cyan]CA Cert:[/cyan] {node.ca_cert_path}")
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)
    
    # Run demo sections
    results = []
    results.append(demo_connection())
    results.append(demo_balance())
    results.append(demo_peers())
    results.append(demo_invoice())
    results.append(demo_invoices_list())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    console.print(f"\n[bold]Demo Results: {passed}/{total} sections passed[/bold]")
    
    if passed == total:
        console.print("[bold green]🎉 All tests passed! CLN REST API is working correctly.[/bold green]")
    else:
        console.print("[bold red]❌ Some tests failed. Check the CLN configuration.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 