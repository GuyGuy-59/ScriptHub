
#https://www.sans.org/blog/powershell-7-zip-module-versus-compress-archive-with-encryption/
#https://github.com/thoemmi/7Zip4Powershell

#Backup vars
$NOW = Get-Date -Format "yyyy-MM-dd"
$SOURCE=""
$CRYPT="$1"
$BK=""

Function BACKUP_FOLDERS{
    Get-ChildItem -Directory | ForEach-Object {
        $FOLDER_NAME = $_.Name
        $compress = @{
        path = $FOLDER_NAME
        CompressionLevel = "Fastest"
        DestinationPath = "$BK\$NOW.$FOLDER_NAME.zip"
    }
    Compress-Archive @Compress
    }
}

Function BACKUP_FOLDERS_ENCRYPT{
    Set-Location $SOURCE
    New-Item -Path $BK -ItemType Directory -Force
    Get-ChildItem -Directory -Exclude $BK | ForEach-Object {
        Compress-7Zip -Path "$_.FullName" -ArchiveFileName "$BK\$NOW.$_.Name.7z" -Format SevenZip -Password "$CRYPT" -EncryptFilenames
    }

}

BACKUP_FOLDERS
BACKUP_FOLDERS_ENCRYPT
