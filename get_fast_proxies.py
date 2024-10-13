from FreeProxyManager import FreeProxyManager
import time

def main():
    # Create an instance of FreeProxyManager
    proxy_manager = FreeProxyManager()

    # Update the proxy list (this will fetch and test proxies)
    print("Updating proxy list...")
    proxy_manager.update_proxy_list()

    # Get and print the top 5 fastest proxies
    print("\nTop 5 fastest proxies:")
    for i, (proxy, response_time) in enumerate(proxy_manager.proxies[:5], 1):
        print(f"{i}. {proxy} - Response time: {response_time:.2f} seconds")

    # Demonstrate getting and using a proxy
    print("\nDemonstrating proxy usage:")
    for _ in range(3):  # Try 3 times
        proxy = proxy_manager.get_proxy()
        if proxy:
            print(f"Using proxy: {proxy}")
            # Here you would typically use this proxy in your application
            # For demonstration, we'll just wait a bit
            time.sleep(1)
        else:
            print("No proxy available.")

if __name__ == "__main__":
    main()