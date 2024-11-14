Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class InputBlocker {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern int BlockInput(bool fBlockIt);
}
"@
[InputBlocker]::BlockInput($true)
