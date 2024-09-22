# Define backup paths
$backupRoot = "C:\AD_Backup"
$ntdsBackupPath = "$backupRoot\NTDS_Backup"
$gpoBackupPath = "$backupRoot\GPO_Backup"
$dnsBackupPath = "$backupRoot\DNS_Backup"
$NOW = Get-Date -Format "yyyy-MM-dd"
$backupDirectory = "$env:SystemRoot\system32\dns\Backup\$NOW"
$BK = "C:\Backup"
$CRYPT = "Password1"

# Function to create directories if they don't exist
function Create-Directories {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$paths
    )
    foreach ($path in $paths) {
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force
        }
    }
}

# Function to backup Active Directory
function BACKUP_AD {
    # Commande ntdsutil pour créer le média IFM
    $ntdsutilCommand = @"
activate instance ntds
ifm
create full $ntdsBackupPath
quit
quit
"@

    $ntdsutilCommand | ntdsutil.exe

    if ($LASTEXITCODE -eq 0) {
        Write-Output "Backup IFM créé avec succès dans $ntdsBackupPath"
    } else {
        Write-Output "Error during the GPO backup"
    }
}

# Function to backup Group Policy Objects (GPO)
function Backup-GPOs {
    Write-Host "Backing up GPOs..."
    Backup-GPO -All -Path $gpoBackupPath

    if ($?) {
        Write-Host "The GPO backup was successful." -ForegroundColor Green
    } else {
        Write-Host "Error during the GPO backup." -ForegroundColor Red
    }
}

# Function to backup DNS zones
function Backup-DNSZones {
    Write-Host "Backing up DNS zones..."

    $zonesToExclude = @(
        '0.in-addr.arpa',
        '127.in-addr.arpa',
        '255.in-addr.arpa'
    )

    Get-DnsServerZone | Where-Object { $zonesToExclude -notcontains $_.ZoneName } | ForEach-Object {
        Try {
            Write-Output "Backup zonename : $($_.ZoneName)"
            Export-DnsServerZone -Name $_.ZoneName -FileName "Backup\$NOW\Backup.$($_.ZoneName)"
        }
        Catch {
            Write-Error "An error occurred while backing up the zone $($_.ZoneName) : $_"
        }
    }

    if ($?) {
        Write-Host "The DNS backup was successful." -ForegroundColor Green
        Try {
            Move-Item -Path $backupDirectory -Destination $dnsBackupPath -Force
            Write-Output "Backup directory moved to $dnsBackupPath"
        }
        Catch {
            Write-Error "An error occurred while moving the backup directory: $_"
        }
    } else {
        Write-Host "Error during the DNS backup." -ForegroundColor Red
    }
}

# Function to encrypt backup folders
function BACKUP_FOLDERS_ENCRYPT {
    Set-Location $backupRoot
    New-Item -Path $BK -ItemType Directory -Force
    Get-ChildItem -Directory  | ForEach-Object {
        if ($_.FullName -ne $BK){
        $temp_name = $_.BaseName
        Compress-7Zip -Path $_.FullName -ArchiveFileName $BK\$NOW.$temp_name.7z -Format SevenZip -Password "$CRYPT" -EncryptFilenames
        }
    }
}

# Main script execution
Write-Host "Creating backup directories..."
Create-Directories -paths @($ntdsBackupPath, $gpoBackupPath, $dnsBackupPath, $backupDirectory)

BACKUP_AD
Backup-GPOs
Backup-DNSZones
BACKUP_FOLDERS_ENCRYPT

Write-Host "All backups are completed."
