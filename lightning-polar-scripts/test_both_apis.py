#!/usr/bin/env python3
"""
Comprehensive test script for both LND and CLN REST APIs
"""

import sys
from lightning_polar_scripts.config import load_config
from lightning_polar_scripts.lnd import LNDClient
from lightning_polar_scripts.core_lightning import CoreLightningClient
from rich.console import Console
from rich.table import Table

console = Console()

def test_lnd():
    """Test LND REST API functionality."""
    console.print("\n[bold blue]🚀 Testing LND REST API (alice)[/bold blue]")
    
    try:
        config = load_config()
        client = LNDClient(config, 'alice')
        
        # Test 1: Get info
        info = client.get_info()
        console.print(f"[green]✅ LND Info:[/green] {info['alias']} v{info['version']} - {info['num_active_channels']} channels")
        
        # Test 2: Get wallet balance
        balance = client.get_wallet_balance()
        console.print(f"[green]✅ LND Wallet Balance:[/green] {balance['confirmed_balance']:,} sats")
        
        # Test 3: List peers
        peers = client.list_peers()
        console.print(f"[green]✅ LND Peers:[/green] {len(peers)} connected")
        
        # Test 4: List invoices
        invoices = client.list_invoices()
        console.print(f"[green]✅ LND Invoices:[/green] {len(invoices)} total")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ LND Test Failed: {e}[/red]")
        return False

def test_cln():
    """Test CLN REST API functionality."""
    console.print("\n[bold blue]⚡ Testing CLN REST API (bob)[/bold blue]")
    
    try:
        config = load_config()
        client = CoreLightningClient(config, 'bob')
        
        # Test 1: Get info
        info = client.get_info()
        console.print(f"[green]✅ CLN Info:[/green] {info['alias']} {info['version']} - {info['num_active_channels']} channels")
        
        # Test 2: Get balance
        balance = client.get_balance()
        console.print(f"[green]✅ CLN Balance:[/green] {balance:,} sats")
        
        # Test 3: List peers
        peers = client.list_peers()
        console.print(f"[green]✅ CLN Peers:[/green] {len(peers)} connected")
        
        # Test 4: List invoices
        invoices = client.list_invoices()
        console.print(f"[green]✅ CLN Invoices:[/green] {len(invoices)} total")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ CLN Test Failed: {e}[/red]")
        return False

def main():
    """Run comprehensive tests for both implementations."""
    console.print("[bold green]🔥 Lightning Polar Scripts - Comprehensive API Test[/bold green]")
    console.print("[yellow]Testing both LND and CLN REST API implementations...[/yellow]")
    
    # Show configuration summary
    try:
        config = load_config()
        
        table = Table(title="Configuration Summary")
        table.add_column("Node", style="cyan")
        table.add_column("Implementation", style="yellow")
        table.add_column("REST URL", style="green")
        table.add_column("Status", style="blue")
        
        for name, node in config.nodes.items():
            rest_url = f"http://{node.rpc_host}:{node.rest_port}"
            table.add_row(name, node.implementation, rest_url, "✅ Configured")
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)
    
    # Run tests
    lnd_result = test_lnd()
    cln_result = test_cln()
    
    # Summary
    console.print(f"\n[bold]Test Results Summary:[/bold]")
    console.print(f"LND REST API: {'✅ PASS' if lnd_result else '❌ FAIL'}")
    console.print(f"CLN REST API: {'✅ PASS' if cln_result else '❌ FAIL'}")
    
    if lnd_result and cln_result:
        console.print("\n[bold green]🎉 All tests passed! Both LND and CLN REST APIs are working correctly.[/bold green]")
        console.print("[cyan]You can now use both implementations:[/cyan]")
        console.print("  • [yellow]LND (alice):[/yellow] polar-cli lnd --help")
        console.print("  • [yellow]CLN (bob):[/yellow] polar-cli cln --help")
        sys.exit(0)
    else:
        console.print("\n[bold red]❌ Some tests failed. Check the configuration and node status.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 