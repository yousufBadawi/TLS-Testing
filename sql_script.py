import sqlite3
import os
import json
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def website_in_db(conn, website):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    website_exist = 0
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE commonName = \"" +  website + "\" ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        website_exist = result[0]
    except Error as e:
        print(e)
    return website_exist

def create_certificate(conn, certificate):
    """
    Create a new certificate into the certificates table
    :param conn:
    :param certificate:
    :return:
    """
    try:
        sql = ''' INSERT INTO certificates(id, notBefore, notAfter, commonName, hashingAlgorithm, signatureAlgorithm, keyLength, publicKeyAlgorithm, issuerId)
                VALUES(?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, certificate)
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()

def create_caIssuer(conn, issuer):
    """
    Create a new issuer into the caIssuers table
    :param conn:
    :param issuer:
    :return:
    """
    try:
        sql = ''' INSERT INTO caIssuers(id, commonName, organizationName)
                VALUES(?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, issuer)
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()

def create_website(conn, website):
    try:
        cur = conn.cursor()
        sql = ''' INSERT INTO websites(commonName, linkedWebsite, successfulConnection, highestTLS, lowestTLS, defaultCipherSuite, badCiphers, defaultSigAlg, badSigalgs, defaultKeyExchange)
                VALUES(?,?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, website)
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.commit()

def main():

    ls_cert = os.popen("ls certificates").readlines()

    database = "onioncertificates.db"

    sql_create_certificates_table = """ CREATE TABLE IF NOT EXISTS certificates (
                                        id integer PRIMARY KEY,
                                        notBefore text NOT NULL,
                                        notAfter text NOT NULL,
                                        commonName text NOT NULL,
                                        hashingAlgorithm text,
                                        signatureAlgorithm text,
                                        keyLength integer,
                                        publicKeyAlgorithm text,
                                        issuerId integer NOT NULL
                                    ); """

    sql_create_caIssuers_table = """ CREATE TABLE IF NOT EXISTS caIssuers (
                                        id integer PRIMARY KEY,
                                        commonName text NOT NULL,
                                        organizationName text NOT NULL
                                    ); """

    sql_create_websites_table = """ CREATE TABLE IF NOT EXISTS websites(
                                        commonName text PRIMARY KEY,
                                        linkedWebsite text,
                                        successfulConnection integer,
                                        highestTLS text,
                                        lowestTLS text,
                                        defaultCipherSuite text,
                                        badCiphers integer,
                                        defaultSigAlg text,
                                        badSigalgs integer,
                                        defaultKeyExchange text
                                    ); """


    # create a database connection
    conn = create_connection(database)

    # create table
    if conn is not None:
        # create certificates table
        create_table(conn, sql_create_certificates_table)
        create_table(conn, sql_create_caIssuers_table)
        create_table(conn, sql_create_websites_table)

        for i in range(len(ls_cert)):
            print((i+1), "/", len(ls_cert))
            domainList=[]
            certfile = ls_cert[i][:-1]
            if os.path.getsize("certificates/" + certfile) != 0:
                cert = open("certificates/" + certfile)
                data = json.load(cert)
                cert.close()
                common_name = data["subject"]["commonName"]
                if (common_name[:2]=="*."):
                    common_name = common_name[2:]
                if ("sha256" in data):
                    hashingAlgorithm = "sha256"
                elif("sha1" in data):
                    hashingAlgorithm = "sha1"
                else:
                    hashingAlgorithm = ""
                certificate = (int(data["id"]), data["not_before"], data["not_after"], common_name, hashingAlgorithm, data["signature_algorithm"], int(data["publickey"]["size"]), data["publickey"]["algorithm"], data["issuer"]["id"]);
                create_certificate(conn, certificate)
                issuer = (int(data["issuer"]["id"]), data["issuer"]["commonName"], data["issuer"]["organizationName"])
                create_caIssuer(conn, issuer)

                linkedWebsite = common_name
                cert.close()
                if(common_name[-6:] == ".onion"):
                    if(not(common_name in domainList)):
                        domainList.append(common_name)
                else:
                    try:
                        alternative_names = data["extensions"]["alternative_names"]
                    except KeyError:
                        alternative_names = []
                    for j in range(len(alternative_names)):
                        alt_name = alternative_names[j]
                        if (alt_name[:2]=="*."):
                            alt_name = alt_name[2:]
                        if((not(alt_name in domainList)) and (alt_name[-6:] == ".onion")):
                            domainList.append(alt_name)

                for j in range(0, len(domainList)):
                    if website_in_db(conn, domainList[j]) == 0:
                        successfulconnection = 1
                        bashCommand = "torify openssl s_client -connect " + domainList[j] + ":443 -status"
                        bashCommandSsl102 = "torify /opt/openssl-1.0.2g/bin/openssl s_client -connect " + domainList[j] + ":443 -status"
                        import subprocess

                        process = subprocess.run(bashCommand.split(), input='q', encoding='ascii', capture_output=True)
                        if process.returncode != 0:
                            successfulconnection = 0

                        if process.stdout.find("Cipher is (NONE)") != -1:
                            successfulconnection = 0

                        if(not(successfulconnection)):
                            print("unsuccessful connection")
                            website = (domainList[j], linkedWebsite, successfulconnection, "", "", "", -1, "", -1, "")
                            create_website(conn, website)

                        else:
                            connection = process.stdout.split()

                            highestSupportedVersion = "DNE"
                            defaultCipher = ""
                            defaultSigalg = ""
                            defaultKeyExchange = ""
                            for k in range(0, len(connection)):
                                if (connection[k].find("signing") != -1 and connection[k+1].find("digest") != -1):
                                    defaultSigalg = connection[k+2]
                                if (connection[k].find("Temp") != -1 and connection[k+1].find("Key") != -1):
                                    defaultKeyExchange = connection[k+2][:-1]
                                if connection[k].find("TLSv") != -1:
                                    highestSupportedVersion = connection[k]
                                if connection[k].find("Cipher") != -1:
                                    defaultCipher = connection[k+2]

                            # tls tests:
                            tlsProtocols = ["-no_tls1_3", "-no_tls1_2", "-no_tls1_1"]
                            tlsVersion = ["TLSv1.3", "TLSv1.2", "TLSv1.1"]
                            tlsCommand = bashCommand
                            lowestSupportedVersion = highestSupportedVersion
                            failed = False
                            for k in range(0, len(tlsProtocols)):
                                tlsCommand += " " + tlsProtocols[k]
                                processTLS = subprocess.run(tlsCommand.split(), input='q', encoding='ascii', capture_output=True)
                                if processTLS.stdout.find("Cipher is (NONE)") != -1:
                                    failed = True
                                    break
                            if j == 2 and not failed:
                                lowestSupportedVersion = "SSLv3/TLSv1.0 or lower"
                            else:
                                lowestSupportedVersion = tlsVersion[k]
                            if(highestSupportedVersion[-1]==','):
                                highestSupportedVersion = highestSupportedVersion[:-1]

                            #bad ciphers test:
                            badCiphers = ["RC4-MD5", "RC4", "3DES", "NULL"]
                            supportedCiphers=[]
                            for k in range(0, len(badCiphers)):
                                ciphersCommand = bashCommandSsl102 + " -cipher " + badCiphers[k]
                                processCipher = subprocess.run(ciphersCommand.split(), input='q', encoding='ascii', capture_output=True)
                                if processCipher.stdout.find("Cipher is (NONE)") == -1:
                                    supportedCiphers.append(badCiphers[k])
                            supportsBadCiphers = (len(supportedCiphers) != 0)

                            #bad sigalgs test:
                            badsigalgs = ["RSA+SHA1"]
                            supportedsigalgs=[]
                            for k in range(0, len(badsigalgs)):
                                sigalgsCommand = bashCommandSsl102 + " -sigalgs " + badsigalgs[k]
                                processSigalg = subprocess.run(sigalgsCommand.split(), input='q', encoding='ascii', capture_output=True)
                                if processSigalg.stdout.find("Cipher is (NONE)") == -1:
                                    supportedsigalgs.append(badsigalgs[k])
                            supportsBadsigalgs = (len(supportedsigalgs) != 0)

                            website =  (domainList[j], linkedWebsite, successfulconnection, highestSupportedVersion, lowestSupportedVersion, defaultCipher, supportsBadCiphers, defaultSigalg, supportsBadsigalgs, defaultKeyExchange)
                            create_website(conn, website)



    else:
        print("Error! cannot connect to the database.")


if __name__ == '__main__':
    main()


    #Problems to fix :
    #   - highestTLS : "TLSv1.3,"
    #   - lowestTLS : "tlsv1.2" "tls1.3" instead of capital letters
    #   - add issuerID
    #   - maybe test dh ?
    #   - change hash and sgnaature algorithm.
