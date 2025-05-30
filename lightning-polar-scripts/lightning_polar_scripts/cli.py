"""CLI interface for Lightning Polar Scripts."""

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .core_lightning import CoreLightningClient
from .lnd import LNDClient
from .config import load_config

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    """Lightning Polar Scripts - Tools for interacting with Polar Lightning Network."""
    ctx.ensure_object(dict)
    console.print(f"[bold blue]Lightning Polar Scripts v{__version__}[/bold blue]")


@main.group()
def cln():
    """Core Lightning commands."""
    pass


@main.group()
def lnd():
    """LND commands."""
    pass


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def info(node):
    """Get Core Lightning node info."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        info = client.get_info()
        
        table = Table(title=f"Core Lightning Node Info - {node}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            table.add_row(str(key), str(value))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def info(node):
    """Get LND node info."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        info = client.get_info()
        
        table = Table(title=f"LND Node Info - {node}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            table.add_row(str(key), str(value))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def balance(node):
    """Get Core Lightning node balance."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        balance = client.get_balance()
        
        console.print(f"[green]Node {node} balance: {balance} sats[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def balance(node):
    """Get LND node balance."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        balance = client.get_balance()
        
        console.print(f"[green]Node {node} balance: {balance} sats[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def channels(node):
    """List Core Lightning node channels."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        channels = client.list_channels()
        
        table = Table(title=f"Core Lightning Channels - {node}")
        table.add_column("Channel ID", style="cyan")
        table.add_column("Peer", style="yellow")
        table.add_column("State", style="green")
        table.add_column("Capacity", style="blue")
        table.add_column("Local Balance", style="magenta")
        
        for channel in channels:
            table.add_row(
                channel.get('short_channel_id', 'N/A'),
                channel.get('peer_id', 'N/A')[:20] + '...',
                channel.get('state', 'N/A'),
                str(channel.get('funding', {}).get('local_msat', 0) // 1000),
                str(channel.get('to_us_msat', 0) // 1000)
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='bob', help='Node name in Polar')
def channels(node):
    """List LND node channels."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        channels = client.list_channels()
        
        table = Table(title=f"LND Channels - {node}")
        table.add_column("Channel ID", style="cyan")
        table.add_column("Peer", style="yellow")
        table.add_column("Active", style="green")
        table.add_column("Capacity", style="blue")
        table.add_column("Local Balance", style="magenta")
        
        for channel in channels:
            table.add_row(
                str(channel.get('chan_id', 'N/A')),
                channel.get('remote_pubkey', 'N/A')[:20] + '...',
                str(channel.get('active', False)),
                str(channel.get('capacity', 0)),
                str(channel.get('local_balance', 0))
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def peers(node):
    """List CLN peers."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        peers = client.list_peers()
        
        table = Table(title=f"CLN Peers - {node}")
        table.add_column("ID", style="cyan")
        table.add_column("Connected", style="green")
        table.add_column("Netaddr", style="yellow")
        table.add_column("Features", style="blue")
        
        for peer in peers:
            table.add_row(
                str(peer.get('id', 'N/A'))[:20] + '...',
                str(peer.get('connected', False)),
                str(peer.get('netaddr', ['N/A'])[0] if peer.get('netaddr') else 'N/A'),
                str(len(peer.get('features', []))) + ' features' if peer.get('features') else 'N/A'
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def wallet_balance(node):
    """Get LND wallet (on-chain) balance."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        balance = client.get_wallet_balance()
        
        table = Table(title=f"LND Wallet Balance - {node}")
        table.add_column("Type", style="cyan")
        table.add_column("Amount (sats)", style="green")
        
        table.add_row("Confirmed", f"{balance['confirmed_balance']:,}")
        table.add_row("Unconfirmed", f"{balance['unconfirmed_balance']:,}")
        table.add_row("Total", f"{balance['total_balance']:,}")
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def channel_balance(node):
    """Get LND channel (Lightning) balance."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        balance = client.get_channel_balance()
        
        table = Table(title=f"LND Channel Balance - {node}")
        table.add_column("Type", style="cyan")
        table.add_column("Amount (sats)", style="green")
        
        table.add_row("Available", f"{balance['balance']:,}")
        table.add_row("Pending Open", f"{balance['pending_open_balance']:,}")
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
@click.option('--amount', type=int, required=True, help='Invoice amount in satoshis')
@click.option('--label', required=True, help='Unique label for the invoice')
@click.option('--description', default=None, help='Invoice description')
def create_invoice(node, amount, label, description):
    """Create a new CLN invoice."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        invoice = client.create_invoice(amount, label, description)
        
        console.print(f"[green]✓ Invoice created successfully![/green]")
        console.print(f"[cyan]Payment Hash:[/cyan] {invoice.get('payment_hash', 'N/A')}")
        console.print(f"[cyan]Payment Request:[/cyan]")
        console.print(f"[yellow]{invoice.get('payment_request', 'N/A')}[/yellow]")
        console.print(f"[cyan]Expires At:[/cyan] {invoice.get('expires_at', 'N/A')}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
@click.option('--payment-request', required=True, help='Lightning invoice to pay')
@click.option('--amount', type=int, default=None, help='Amount to pay (for zero-amount invoices)')
def pay_invoice(node, payment_request, amount):
    """Pay a Lightning invoice."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        result = client.pay_invoice(payment_request, amount)
        
        console.print(f"[green]✓ Payment successful![/green]")
        console.print(f"[cyan]Payment Hash:[/cyan] {result.get('payment_hash', 'N/A')}")
        console.print(f"[cyan]Payment Preimage:[/cyan] {result.get('payment_preimage', 'N/A')}")
        console.print(f"[cyan]Amount Sent:[/cyan] {result.get('amount_sent_msat', 0) // 1000} sats")
        console.print(f"[cyan]Status:[/cyan] {result.get('status', 'N/A')}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def list_invoices(node):
    """List CLN invoices."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        invoices = client.list_invoices()
        
        table = Table(title=f"CLN Invoices - {node}")
        table.add_column("Label", style="cyan")
        table.add_column("Amount (sats)", style="blue")
        table.add_column("Description", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Expires At", style="magenta")
        
        for invoice in invoices[:10]:  # Show only first 10
            amount = invoice.get('amount_msat', 0) // 1000 if invoice.get('amount_msat') else 0
            table.add_row(
                str(invoice.get('label', 'N/A')),
                str(amount),
                str(invoice.get('description', 'N/A'))[:30] + '...' if len(str(invoice.get('description', ''))) > 30 else str(invoice.get('description', 'N/A')),
                str(invoice.get('status', 'N/A')),
                str(invoice.get('expires_at', 'N/A'))
            )
        
        console.print(table)
        if len(invoices) > 10:
            console.print(f"[yellow]Showing first 10 of {len(invoices)} invoices[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cln.command()
@click.option('--node', default='bob', help='Node name in Polar')
def list_payments(node):
    """List CLN payments."""
    try:
        config = load_config()
        client = CoreLightningClient(config, node)
        payments = client.list_payments()
        
        table = Table(title=f"CLN Payments - {node}")
        table.add_column("Payment Hash", style="cyan")
        table.add_column("Amount (sats)", style="blue")
        table.add_column("Destination", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Created At", style="magenta")
        
        for payment in payments[:10]:  # Show only first 10
            amount = payment.get('amount_sent_msat', 0) // 1000 if payment.get('amount_sent_msat') else 0
            table.add_row(
                str(payment.get('payment_hash', 'N/A'))[:20] + '...',
                str(amount),
                str(payment.get('destination', 'N/A'))[:20] + '...',
                str(payment.get('status', 'N/A')),
                str(payment.get('created_at', 'N/A'))
            )
        
        console.print(table)
        if len(payments) > 10:
            console.print(f"[yellow]Showing first 10 of {len(payments)} payments[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
@click.option('--amount', type=int, required=True, help='Invoice amount in satoshis')
@click.option('--memo', default=None, help='Invoice memo/description')
@click.option('--expiry', default=3600, help='Invoice expiry in seconds')
def create_invoice(node, amount, memo, expiry):
    """Create a new LND invoice."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        invoice = client.create_invoice(amount, memo, expiry)
        
        console.print(f"[green]✓ Invoice created successfully![/green]")
        console.print(f"[cyan]Payment Hash:[/cyan] {invoice.get('payment_hash', 'N/A')}")
        console.print(f"[cyan]Payment Request:[/cyan]")
        console.print(f"[yellow]{invoice.get('payment_request', 'N/A')}[/yellow]")
        console.print(f"[cyan]Add Index:[/cyan] {invoice.get('add_index', 'N/A')}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
@click.option('--payment-request', required=True, help='Lightning invoice to pay')
@click.option('--amount', type=int, default=None, help='Amount to pay (for zero-amount invoices)')
def pay_invoice(node, payment_request, amount):
    """Pay a Lightning invoice."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        result = client.pay_invoice(payment_request, amount)
        
        console.print(f"[green]✓ Payment successful![/green]")
        console.print(f"[cyan]Payment Hash:[/cyan] {result.get('payment_hash', 'N/A')}")
        console.print(f"[cyan]Payment Preimage:[/cyan] {result.get('payment_preimage', 'N/A')}")
        
        route = result.get('payment_route', {})
        if route:
            console.print(f"[cyan]Total Amount:[/cyan] {route.get('total_amt', 'N/A')} sats")
            console.print(f"[cyan]Total Fees:[/cyan] {route.get('total_fees', 'N/A')} sats")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
@click.option('--pending-only', is_flag=True, help='Show only pending invoices')
def list_invoices(node, pending_only):
    """List LND invoices."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        invoices = client.list_invoices(pending_only)
        
        table = Table(title=f"LND Invoices - {node}")
        table.add_column("Add Index", style="cyan")
        table.add_column("Value (sats)", style="blue")
        table.add_column("Memo", style="yellow")
        table.add_column("Settled", style="green")
        table.add_column("Creation Date", style="magenta")
        
        for invoice in invoices[:10]:  # Show only first 10
            table.add_row(
                str(invoice.get('add_index', 'N/A')),
                str(invoice.get('value', 'N/A')),
                str(invoice.get('memo', 'N/A'))[:30] + '...' if len(str(invoice.get('memo', ''))) > 30 else str(invoice.get('memo', 'N/A')),
                str(invoice.get('settled', False)),
                str(invoice.get('creation_date', 'N/A'))
            )
        
        console.print(table)
        if len(invoices) > 10:
            console.print(f"[yellow]Showing first 10 of {len(invoices)} invoices[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def list_payments(node):
    """List LND payments."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        payments = client.list_payments()
        
        table = Table(title=f"LND Payments - {node}")
        table.add_column("Payment Hash", style="cyan")
        table.add_column("Value (sats)", style="blue")
        table.add_column("Fee (sats)", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Creation Time", style="magenta")
        
        for payment in payments[:10]:  # Show only first 10
            table.add_row(
                str(payment.get('payment_hash', 'N/A'))[:20] + '...',
                str(payment.get('value', 'N/A')),
                str(payment.get('fee', 'N/A')),
                str(payment.get('status', 'N/A')),
                str(payment.get('creation_time_ns', 'N/A'))
            )
        
        console.print(table)
        if len(payments) > 10:
            console.print(f"[yellow]Showing first 10 of {len(payments)} payments[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@lnd.command()
@click.option('--node', default='alice', help='Node name in Polar')
def peers(node):
    """List LND peers."""
    try:
        config = load_config()
        client = LNDClient(config, node)
        peers = client.list_peers()
        
        table = Table(title=f"LND Peers - {node}")
        table.add_column("Public Key", style="cyan")
        table.add_column("Address", style="yellow")
        table.add_column("Bytes Sent", style="blue")
        table.add_column("Bytes Recv", style="green")
        table.add_column("Sats Sent", style="magenta")
        table.add_column("Sats Recv", style="red")
        
        for peer in peers:
            table.add_row(
                str(peer.get('pub_key', 'N/A'))[:20] + '...',
                str(peer.get('address', 'N/A')),
                str(peer.get('bytes_sent', 'N/A')),
                str(peer.get('bytes_recv', 'N/A')),
                str(peer.get('sat_sent', 'N/A')),
                str(peer.get('sat_recv', 'N/A'))
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    main() 