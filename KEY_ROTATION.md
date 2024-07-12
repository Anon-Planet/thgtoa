PGP/GPG key ID `7DFFD7471FB76E2A8ABBBCDDD769B3749E933B8A` is no longer active  
PGP/GPG key ID `42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920` is no longer active  
PGP/GPG key ID `9EA98278639F1CD853E096CBFF94507587A6A9B9` is no longer active  

This project now uses separate master, release signing, and email keys.  

Current master key fingerprint: `9FA5 436D 0EE3 6098 5157  3825 17EC A05F 768D EDF6`  
Current release key fingerprint: `C302 3DBE A3FB 38C4 38BA  1EED CEC6 0AED E8B9 92A2`  
Current email key fingerprint: `FCBD 2CAB DEFD 1FBA 2E9E  7591 A1A8 2CD2 DD2C F890`  

You can import the current master signing key for Anonymous Planet from the repo root:  
`gpg2 --import keys/*Master-Signing-Key_*.asc`  

The email and release keys should be signed by the master keys.  
The master key takes precedence over all other project keys.  
------------------------------------------------------------------------------------

Minisign key  
```
untrusted comment: minisign public key 902835EC74825934  
RWQ0WYJ07DUokK8V/6LNJ9bf/O/QM9k4FSlDmzgEeXm7lEpw3ecYjXDM  
```
is no longer active  

Use  
```
untrusted comment: minisign public key FE6A09A3AF18F7A7  
RWSn9xivowlq/ihAzclDBxhCxbYz4bLkC8E645lHgSUlQNlDvoTxO5Fv  
```
instead  

Files signed using this key pair can be verified with the following command:  

```
minisign -Vm <file> -P RWSn9xivowlq/ihAzclDBxhCxbYz4bLkC8E645lHgSUlQNlDvoTxO5Fv  
```
