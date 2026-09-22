from src.diag_tools import (
    ping_host,
    dns_lookup,
    tcp_port_check,
    read_log,
    arp_check,
    route_check,
    create_diag_tools,
)

from src.tool import registry


def main():

    # =========================
    # 1. Registry
    # =========================

    print("\n===== Registry =====")

    create_diag_tools()

    print(
        list(registry.tools.keys())
    )


    # =========================
    # 2. Ping
    # =========================

    print("\n===== Ping =====")

    print(
        ping_host(
            "127.0.0.1",
            count=2,
            timeout=5
        )
    )


    # =========================
    # 3. DNS
    # =========================

    print("\n===== DNS =====")

    print(
        dns_lookup(
            "localhost"
        )
    )


    # =========================
    # 4. TCP
    # =========================

    print("\n===== TCP =====")

    print(
        tcp_port_check(
            "127.0.0.1",
            8000,
            timeout=3
        )
    )


    # =========================
    # 5. ARP
    # =========================

    print("\n===== ARP =====")

    print(
        arp_check(
            "192.168.1.1"
        )
    )


    # =========================
    # 6. Route
    # =========================

    print("\n===== Route =====")

    print(
        route_check(
            "8.8.8.8"
        )
    )


if __name__ == "__main__":
    main()