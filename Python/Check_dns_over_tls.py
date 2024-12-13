import socket, ssl, dns.query, dns.message, dns.rdatatype

def verify_tls_connection(server, port):
    try:
        sock = socket.create_connection((server, port), timeout=5)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with context.wrap_socket(sock, server_hostname=server) as ssock:
            print(f"TLS connection successful with {server}:{port}")
            return True
    except Exception as e:
        print(f"TLS connection error with {server}:{port}: {e}")
        return False

def check_query_dot(server, port, domain):
    if not verify_tls_connection(server, port):
        print(f"Unable to contact DoT server at {server}:{port}")
        return

    try:
        query = dns.message.make_query(domain, dns.rdatatype.A)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        response = dns.query.tls(query, server, port=port, timeout=5, ssl_context=context)

        print(f"DNS response from {server}:{port} for {domain} (type A):")
        for answer in response.answer:
            print(str(answer))

    except Exception as e:
        print(f"DNS query error: {e}")

if __name__ == "__main__":
    server = "9.9.9.9"  # DoT server
    port = 853          # Port
    domain = "example.com"  #Domain
    check_query_dot(server, port, domain)
