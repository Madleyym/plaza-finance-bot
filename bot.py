import asyncio
import random
import logging
from datetime import datetime, timedelta
from colorama import Fore
from plaza_bot import PlazaFinanceBot  # Import from plaza_bot.py

# Current info
CURRENT_USER = "Madleyym"
CURRENT_VERSION = "2025-02-14"


async def main():
    try:
        # Initialize bot
        bot = PlazaFinanceBot()

        while True:
            try:
                # Read private keys from file
                with open("private_keys.txt", "r") as f:
                    private_keys = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]

                if not private_keys:
                    print(f"{Fore.RED}No private keys found in private_keys.txt")
                    return

                print(f"{Fore.GREEN}Starting processing {len(private_keys)} wallets")
                print(f"{Fore.YELLOW}Current user: {CURRENT_USER}")
                print(f"{Fore.YELLOW}Bot version: {CURRENT_VERSION}")

                # Process each wallet
                for idx, private_key in enumerate(private_keys, 1):
                    try:
                        success = await bot.process_wallet(
                            private_key, idx, len(private_keys)
                        )

                        # Handle delays between wallets
                        if idx < len(private_keys):
                            if not success:
                                # Longer delay after failure
                                delay = random.randint(180, 300)  # 3-5 minutes
                                print(
                                    f"{Fore.YELLOW}Failed attempt, waiting {delay}s before next wallet..."
                                )
                                await asyncio.sleep(delay)
                            else:
                                # Normal delay between wallets
                                delay = random.randint(60, 120)  # 1-2 minutes
                                print(
                                    f"{Fore.YELLOW}Waiting {delay}s before next wallet..."
                                )
                                await asyncio.sleep(delay)

                    except Exception as wallet_error:
                        print(
                            f"{Fore.RED}Error processing wallet {idx}: {str(wallet_error)}"
                        )
                        logging.error(
                            f"Wallet {idx} error: {wallet_error}", exc_info=True
                        )
                        continue

                # Cycle complete, schedule next run
                print(f"{Fore.GREEN}Cycle complete for all wallets")
                next_run = datetime.now() + timedelta(hours=6)
                print(
                    f"{Fore.GREEN}Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Wait 6 hours before next cycle
                await asyncio.sleep(6 * 60 * 60)

            except Exception as cycle_error:
                print(f"{Fore.RED}Cycle error: {str(cycle_error)}")
                logging.error(f"Cycle error: {cycle_error}", exc_info=True)
                # Wait 5 minutes before retrying
                await asyncio.sleep(300)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Bot stopped by user (Ctrl+C)")
    except Exception as fatal_error:
        print(f"{Fore.RED}Fatal error: {str(fatal_error)}")
        logging.error(f"Fatal error: {fatal_error}", exc_info=True)


if __name__ == "__main__":
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler("plaza_bot.log"), logging.StreamHandler()],
        )

        # Print startup message
        print(f"\n{Fore.GREEN}=== Plaza Finance Auto Bot ===")
        print(f"{Fore.GREEN}Version: {CURRENT_VERSION}")
        print(f"{Fore.GREEN}User: {CURRENT_USER}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop the bot")
        print(f"{Fore.YELLOW}Logging to plaza_bot.log\n")

        # Run the bot
        asyncio.run(main())

    except Exception as e:
        print(f"{Fore.RED}Startup error: {str(e)}")
        logging.error(f"Startup error: {e}", exc_info=True)
    finally:
        print(f"\n{Fore.YELLOW}Bot shutdown complete")
