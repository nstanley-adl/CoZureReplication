# CoZureReplication
Based on paper: 
```
Chowdhury, A. and Nguyen, H. (2023). CoZure:
Context Free Grammar Co-Pilot Tool for Finding New
Lateral Movements in Azure Active Directory.
International Symposium on Research in Attacks,
Intrusions and Defenses, 26.
doi:https://doi.org/10.1145/3607199.3607228
```
Three components of the CoZure co-pilot tool have been implemented.

#### CFG reproduction of known attacks w/ command substitution
This tool accepts a hardcoded context-free grammar and generates Azure CLI commands for reproducing lateral attacks. 
The grammar is expanded per a left-derivation tree.
Through methods described in the paper, parameters are correctly substituted based on parameters specified in `/params`.
The output of this script shall be supplied to an Azure Cloud Shell.

To generate possible lateral attacks run:
```shell
python3 cfg.py
```

#### Key entities relational CSV database
This component is non-executable in its own right, rather this component is to be incorporated into a 
complete replication (beyond the scope of the project).
The relevant file is `database.py`. The database stores the key entities described by the paper. The key entities are 
_commands_, which an ordered set of comprises an _activity_, which is grouped into _security attributes_ which lastly belong to a _target_.

The entities are stored relationally within CSV files. _Targets_ exist in several files in `./`. _Security attributes_ exist within `/attributes.csv`. 
Activities exist within `activities.csv`. Commands exist within `commands.csv`.

#### Simple web-scraper (code block extractor)
A simple web-scraper has been devised which shall extract preformatted code blocks from a supplied web page.
Requires BeautifulSoup 4.

Run:
```shell
python3 web-scraper.py
```




