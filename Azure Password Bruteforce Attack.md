# _Very_ Simple CFG For Password Bruteforce Attack
Based on paper: 
```
Chowdhury, A. and Nguyen, H. (2023). CoZure:
Context Free Grammar Co-Pilot Tool for Finding New
Lateral Movements in Azure Active Directory.
International Symposium on Research in Attacks,
Intrusions and Defenses, 26.
doi:https://doi.org/10.1145/3607199.3607228
```

### Commands (terminals)
```
c1 = az login -u <username> -p <password>
c2 = az login -u <sqlserver> -p $accessToken --service-principal
```

### Activities (non-terminals)
```
A = c1 | c2
```

### Starting Production Rule
```
S -> A
```