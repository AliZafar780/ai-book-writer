
rule Suspicious_Process_Keywords {
    meta:
        description = "Detects common suspicious keywords found in malware droppers or scripts"
        author = "Z-BOT"
        level = "High"
    strings:
        $pwsh = "powershell" nocase
        $invoke = "Invoke-Expression" nocase
        $webrequest = "System.Net.WebClient"
        $create_thread = "CreateRemoteThread"
        $lsass = "lsass.exe" nocase
    condition:
        2 of them
}
rule Potential_Ransomware_Note {
    meta:
        description = "Detects file names commonly used for ransomware notes"
        author = "Z-BOT"
        level = "Critical"
    strings:
        $f1 = "DECRYPT_INSTRUCTIONS.txt" nocase
        $f2 = "RECOVERY_KEY.txt" nocase
        $f3 = "HowToDecrypt.txt" nocase
        $f4 = "restore_your_files.txt" nocase
    condition:
        filename matches /.*DECRYPT.*/ or filename matches /.*RECOVERY.*/ or filename matches /.*RESTORE.*/
}
