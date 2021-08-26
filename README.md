# Onion TLS Testing
These scripts allow for generic TLS security testing of .onion websites found on crt.sh, leveraging the torsocks/torify wrapper used with the OpenSSL CLI. 

## Dependencies 
In order to run these scripts, you will need the following packages, as well as python3.

Linux:

 - certsh
 - tor
 - openssl (1.1.1g)
 - openssl with weak ciphers enabled (1.0.2g) (See instructions).

python3 packages:
- sqlite3


## Instructions
First, you need to install the legacy openssl configured with weak ciphers, via `./installLegacyOpenSSL.sh` 
This should create a new directory, `openssl-1.0.2l`, which is ignored when pushing to git.

 1. `python3 cert_extract_list.py`: This creates the list of certificates parsed by the database
 2. `python3 test_void.py`: This tests if cert downloads fail, and retries for those with void values
 3. `python3 sql_script.py`: This tests the certificates for succesful websites and populates the database with results
 4. `python3 onion_statistics.py`: This parses database and adds interesting stats to `statistics.txt`, again covered by .gitignore.



