# HyperVQuickCreate_Ubuntu
JSON file for Hyper-V Quick Create to add installation source for newer versions of Ubuntu Linux.

Usage:
1. RegEdit to "Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization"
2. Edit GalleryLocations of type REG_MULTI_SZ
3. Set its value to the following 2 lines:

https://go.microsoft.com/fwlink/?linkid=851584
https://raw.githubusercontent.com/stratusjerry/HyperVQuickCreate_Ubuntu/refs/heads/main/HyperV_UbuntuGallery.json

Alternatively, run the following in an elevated PowerShell session:

```powershell
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Virtualization" -Name "GalleryLocations" -Value @(
    "https://go.microsoft.com/fwlink/?linkid=851584",
    "https://raw.githubusercontent.com/stratusjerry/HyperVQuickCreate_Ubuntu/refs/heads/main/HyperV_UbuntuGallery.json"
) -Type MultiString
```

