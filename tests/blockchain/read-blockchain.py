import requests
import time
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

BLOCKCHAIN_URL = "http://localhost:8000"
CHECK_INTERVAL = 15

session = requests.Session()
console = Console()

def mine_block():
    console.print(f"[bold cyan]Monitoring blockchain at {BLOCKCHAIN_URL}[/bold cyan]")
    last_seen_index = -1
    backoff = 5
    try:
        while True:
            try:
                response = session.get(f"{BLOCKCHAIN_URL}/chain", timeout=10)
                if response.status_code == 200:
                    chain = response.json()
                    latest_block = chain[-1] if chain else None

                    if latest_block and latest_block['index'] != last_seen_index:
                        console.clear()
                        console.print(
                            Panel(
                                Pretty(latest_block, expand_all=True),
                                title=f"[green]🧱 New Block #{latest_block['index']}[/green]",
                                expand=False
                            )
                        )
                        last_seen_index = latest_block['index']
                    else:
                        console.print(f"[yellow]⏳ No new blocks (last index: {last_seen_index})[/yellow]")

                    time.sleep(CHECK_INTERVAL)
                    backoff = 5
                else:
                    console.print(f"[red]❌ Failed to read chain (HTTP {response.status_code})[/red]")
                    console.print(f"⏳ Retrying in {backoff} seconds...\n")
                    time.sleep(backoff)
                    backoff = min(backoff + 5, 60)
            except requests.exceptions.RequestException as e:
                console.print(f"[red]🚫 Connection error:[/red] {e}")
                console.print(f"⏳ Retrying in {backoff} seconds...\n")
                time.sleep(backoff)
                backoff = min(backoff + 5, 60)
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Monitoring stopped manually. Goodbye.[/bold red]")

if __name__ == "__main__":
    mine_block()
