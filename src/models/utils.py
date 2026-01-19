import socket
import ipaddress

def is_local_or_private(host_addr):
    """
    Checks if a hostname or IP is loopback or private.
    Returns (True/False, "Reason")
    """
    try:
        ip_str = socket.gethostbyname(host_addr)
        ip = ipaddress.ip_address(ip_str)

        if ip.is_loopback:
            return True, f"'{host_addr}' resolves to loopback ({ip_str})."
        if ip.is_private:
            return True, f"'{host_addr}' resolves to private IP ({ip_str})."
        
        return False, None
    except Exception:
        return False, None
