import requests, csv, ssl, OpenSSL.crypto
from io import StringIO
from datetime import datetime

#https://ccadb.my.salesforce-sites.com/microsoft/IncludedCACertificateReportForMSFT
#https://learn.microsoft.com/en-us/security/trusted-root/participants-list

def get_cert():
    untrusted_ca = []
    disabled_certificates = []

    # Get the list of trusted CAs
    response = requests.get('https://ccadb-public.secure.force.com/microsoft/IncludedCACertificateReportForMSFTCSV')
    csv_data = StringIO(response.text)
    reader = csv.DictReader(csv_data)

    # Use the correct column for the SHA-1 Hash
    trusted_ca = {row['SHA-1 Fingerprint']: row for row in reader}

    # Get local certificates
    context = ssl.create_default_context()
    context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)

    # Print the total number of certificates loaded
    certs = context.get_ca_certs(binary_form=True)
    print(f"Total number of certificates loaded: {len(certs)}")

    for cert_dict in certs:
        try:
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_dict)
            sha1_hash = x509.digest('sha1').decode('utf-8').replace(':', '').upper()  # Convert to continuous hexadecimal format
            issuer = x509.get_issuer().CN
            expiration_date = x509.get_notAfter().decode('utf-8')  # Get the expiration date
            expiration_date = datetime.strptime(expiration_date, '%Y%m%d%H%M%SZ').strftime('%Y-%m-%d')  # Convert to yyyy-mm-dd format
            if sha1_hash not in trusted_ca:
                untrusted_ca.append((issuer, sha1_hash, expiration_date))
            elif trusted_ca[sha1_hash]['Microsoft Status'] == 'Disabled':
                disabled_certificates.append((issuer, sha1_hash, expiration_date))
        except Exception as e:
            print(f"Error processing a certificate: {e}")

    # Filter out None elements before sorting
    untrusted_ca = [ca for ca in untrusted_ca if ca is not None and all(ca)]
    disabled_certificates = [ca for ca in disabled_certificates if ca is not None and all(ca)]

    # Display untrusted CAs
    print("Certificates in the system but not present in the CSV file:")
    for issuer, sha1_hash, expiration_date in sorted(set(untrusted_ca)):
        print(f"Name: {issuer}, SHA-1 Hash: {sha1_hash}, Expiration Date: {expiration_date}")

    # Display disabled certificates
    print("\nCertificates disabled in the CSV file:")
    for issuer, sha1_hash, expiration_date in sorted(set(disabled_certificates)):
        print(f"Name: {issuer}, SHA-1 Hash: {sha1_hash}, Expiration Date: {expiration_date}")

get_cert()
