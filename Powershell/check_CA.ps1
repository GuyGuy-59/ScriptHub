#https://ccadb.my.salesforce-sites.com/microsoft/IncludedCACertificateReportForMSFT
#https://learn.microsoft.com/en-us/security/trusted-root/participants-list

# Function to get certificates
function Get-CertInfo {
    $untrustedCA = @()
    $disabledCertificates = @()

    # Get the list of trusted CAs
    $response = Invoke-WebRequest -Uri 'https://ccadb-public.secure.force.com/microsoft/IncludedCACertificateReportForMSFTCSV'
    $csvData = ConvertFrom-Csv $response.Content
    $trustedCA = @{}
    foreach ($row in $csvData) {
        $trustedCA[$row.'SHA-1 Fingerprint'] = $row
    }

    # Get local certificates
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("ROOT", "LocalMachine")
    $store.Open("ReadOnly")

    # Print the total number of certificates loaded
    Write-Host "Total number of certificates loaded: $($store.Certificates.Count)"

    foreach ($cert in $store.Certificates) {
        try {
            $sha1Hash = $cert.Thumbprint
            $issuer = $cert.Issuer -replace '^CN=|,.*$'
            $expirationDate = $cert.NotAfter.ToString("yyyy-MM-dd")

            if (-not $trustedCA.ContainsKey($sha1Hash)) {
                $untrustedCA += [PSCustomObject]@{
                    Issuer = $issuer
                    SHA1Hash = $sha1Hash
                    ExpirationDate = $expirationDate
                }
            }
            elseif ($trustedCA[$sha1Hash].'Microsoft Status' -eq 'Disabled') {
                $disabledCertificates += [PSCustomObject]@{
                    Issuer = $issuer
                    SHA1Hash = $sha1Hash
                    ExpirationDate = $expirationDate
                }
            }
        }
        catch {
            Write-Host "Error processing a certificate: $_"
        }
    }

    $store.Close()

    # Display untrusted CAs
    Write-Host "Certificates in the system but not present in the CSV file:"
    $untrustedCA | Sort-Object Issuer | ForEach-Object {
        Write-Host "Name: $($_.Issuer), SHA-1 Hash: $($_.SHA1Hash), Expiration Date: $($_.ExpirationDate)"
    }

    # Display disabled certificates
    Write-Host "`nCertificates disabled in the CSV file:"
    $disabledCertificates | Sort-Object Issuer | ForEach-Object {
        Write-Host "Name: $($_.Issuer), SHA-1 Hash: $($_.SHA1Hash), Expiration Date: $($_.ExpirationDate)"
    }
}

# Call the function
Get-CertInfo
