# Quick Reply with First Name Greeting

## When / Why

Replying to emails with a personalised greeting ("Hi Sarah,") is a small thing that makes a professional difference, but Outlook doesn't make it easy to extract the sender's first name. This macro handles the common edge cases: LastName/FirstName format in the GAL, honorific stripping (Dr, Prof, etc.), and positions the cursor after the greeting so you can start typing immediately.

Assign to a QAT button or ribbon shortcut for one-click use.

---

## The Code

```vba title="QuickReplyWithGreeting"
' Quick Reply with First Name Greeting
' Assign to QAT button for one-click reply with personalised greeting
' Handles: LastName/FirstName format, honorific stripping, font styling

Sub QuickReplyWithGreeting()
    Dim olItem As Object
    Dim olReply As MailItem
    Dim senderName As String
    Dim firstName As String
    
    ' --- Detect active item (reading pane vs open window) ---
    If TypeName(Application.ActiveWindow) = "Inspector" Then
        Set olItem = Application.ActiveInspector.CurrentItem
    ElseIf Application.ActiveExplorer.Selection.Count > 0 Then
        Set olItem = Application.ActiveExplorer.Selection(1)
    Else
        MsgBox "No email selected.", vbExclamation
        Exit Sub
    End If
    
    ' --- Get sender display name ---
    senderName = olItem.SenderName
    
    ' --- Extract first name ---
    firstName = ExtractFirstName(senderName)
    
    ' --- Create reply and inject greeting ---
    Set olReply = olItem.Reply
    olReply.Display
    
    ' Insert greeting with font styling
    olReply.HTMLBody = "<div style='font-family:Calibri;font-size:11pt'>" & _
        "Hi " & firstName & ",<br><br></div>" & olReply.HTMLBody
    
    ' Position cursor after greeting using SendKeys
    SendKeys "{TAB}", True
    
End Sub
```

---

## Helper: ExtractFirstName

```vba title="ExtractFirstName"
Function ExtractFirstName(fullName As String) As String
    Dim parts() As String
    Dim candidate As String
    
    ' Handle "LastName, FirstName" format (common in GAL)
    If InStr(fullName, ",") > 0 Then
        parts = Split(fullName, ",")
        candidate = Trim(parts(1))
    Else
        parts = Split(fullName, " ")
        candidate = Trim(parts(0))
    End If
    
    ' Strip common honorifics
    Dim honorifics As Variant
    honorifics = Array("Dr", "Dr.", "Prof", "Prof.", "Mr", "Mr.", _
                       "Mrs", "Mrs.", "Ms", "Ms.", "Miss")
    
    Dim h As Variant
    For Each h In honorifics
        If StrComp(candidate, CStr(h), vbTextCompare) = 0 Then
            ' Honorific matched — take the next word instead
            If UBound(parts) >= 1 Then
                candidate = Trim(parts(1))
            End If
            Exit For
        End If
    Next h
    
    ' Final cleanup: take only first word if multiple remain
    If InStr(candidate, " ") > 0 Then
        candidate = Left(candidate, InStr(candidate, " ") - 1)
    End If
    
    ExtractFirstName = candidate
End Function
```

---

## Gotchas & Known Issues

!!! warning "SendKeys is inherently fragile"
    It depends on window focus and can misfire if Outlook loses focus between
    the `Display` call and the `SendKeys` call. This is the best available
    approach without resorting to Word object model manipulation of the
    Inspector body, which introduces its own fragilities.

!!! warning "LastName/FirstName detection relies on the comma"
    If a sender's display name contains a comma for other reasons
    (e.g. "Smith, Jones & Associates"), this will extract incorrectly.
    In practice this is rare for individual senders.

!!! info "Font styling"
    The greeting is injected as HTML with Calibri 11pt to match the default
    Outlook compose font. If your default font is different, update the
    `style` attribute in the `HTMLBody` insertion.

---

## Revision Notes

| Version | Change |
|---|---|
| v1 | Basic reply with first name |
| v2 | Added honorific stripping |
| v3 | Added LastName/FirstName (comma) format handling |
| v4 | Added font styling to match compose defaults |
