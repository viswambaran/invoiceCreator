Option Explicit
Dim shell, fso, folder, pyw, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)

pyw = "pyw.exe"
command = """" & pyw & """ """ & folder & "\Launch Invoice Creator.pyw""""

On Error Resume Next
shell.Run command, 0, False
If Err.Number <> 0 Then
    Err.Clear
    pyw = "pythonw.exe"
    command = """" & pyw & """ """ & folder & "\Launch Invoice Creator.pyw""""
    shell.Run command, 0, False
End If

If Err.Number <> 0 Then
    MsgBox "Python could not be found. Please ask IT to install Python 3.10 or later.", 16, "Invoice Creator"
End If
