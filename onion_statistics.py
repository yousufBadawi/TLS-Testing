import sqlite3
import os
from sqlite3 import Error
import datetime

today = datetime.datetime.now()

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

def nbOfWebsites(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def nbOfSuccessfulConnection(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def nbOfTLS1_3(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 AND highestTLS = \"TLSv1.3\" ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def nbOfUnderTLS1_2(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 AND lowestTLS != \"TLSv1.2\" AND lowestTLS != \"TLSv1.3\";"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def nbOfSafeWebsite(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 AND (lowestTLS = \"TLSv1.2\" OR lowestTLS = \"TLSv1.3\") AND badCiphers = 0 AND badSigalgs = 0;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb


def nbOfsupportingBadCiphers(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 AND badCiphers = 0 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def nbOfsupportingBadSigAlgs(conn):
    nb = -1
    try:
        sql = "SELECT COUNT(*) FROM websites WHERE successfulConnection = 1 AND badSigalgs = 0 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def defaultCiphers(conn):
    ciphers = []
    try:
        sql = "SELECT DISTINCT defaultCipherSuite FROM websites WHERE successfulConnection = 1 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchall()
        for x in result:
            ciphers.append(x[0])
    except Error as e:
        print(e)
    return ciphers

def defaultSigAlgs(conn):
    sigAlgs = []
    try:
        sql = "SELECT DISTINCT defaultSigAlg FROM websites WHERE successfulConnection = 1 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchall()
        for x in result:
            sigAlgs.append(x[0])
    except Error as e:
        print(e)
    return sigAlgs

def defaultKeyExchanges(conn):
    keyExchanges = []
    try:
        sql = "SELECT DISTINCT defaultKeyExchange FROM websites WHERE successfulConnection = 1 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchall()
        for x in result:
            keyExchanges.append(x[0])
    except Error as e:
        print(e)
    return keyExchanges

def nbOfWebsitesPerIssuer(conn, issuer):
    nb = -1
    try:
        sql = "SELECT Count(DISTINCT websites.commonName) FROM websites, caIssuers, certificates WHERE websites.linkedWebsite = certificates.commonName AND certificates.issuerId = caIssuers.id AND caIssuers.organizationName = \"" + issuer + "\" AND websites.successfulConnection = 1;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        nb = result[0]
    except Error as e:
        print(e)
    return nb

def lastCertificate(conn, website):
    try:
        sql = "SELECT id, notBefore FROM certificates WHERE commonName = \"" + website + "\";"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchall()
        lastCertificate = result[0][0]
        x = result[0][1].split('T')[0].split('-')
        lastDate = datetime.datetime(int(x[0]), int(x[1]), int(x[2]))
        for i in range(1,len(result)):
            y = result[i][1].split('T')[0].split('-')
            date = datetime.datetime(int(y[0]), int(y[1]), int(y[2]))
            if(lastDate < date):
                lastDate = date
                lastCertificate = result[i][0]
            elif(lastDate == date):
                lastCertificate = max(lastCertificate, result[i][0])
    except Error as e:
        print(e)
    return (lastCertificate)

def statsOnCertificates(conn, listWebsites):
    listCertificates = []
    try:
        for i in range(len(listWebsites)):
            id = lastCertificate(conn, listWebsites[i])
            sql = "SELECT id, notAfter, signatureAlgorithm, keyLength, publicKeyAlgorithm FROM certificates WHERE id = " + str(id) + ";"
            c = conn.cursor()
            c.execute(sql)
            result = c.fetchone()
            listCertificates.append(result)
        totalCert = len(listCertificates)
        c_expired = 0
        listSigAlgs = []
        listKeyLengths = []
        listKeyAlgs = []
        countSigAlgs = []
        countKeyLengths = []
        countKeyAlgs = []
        for i in range(len(listCertificates)):
            d = listCertificates[i][1].split('T')[0].split('-')
            date = datetime.datetime(int(d[0]), int(d[1]), int(d[2]))
            sigAlg = listCertificates[i][2]
            keyLength = listCertificates[i][3]
            keyAlg = listCertificates[i][4]
            if (date < today):
                c_expired += 1
            if sigAlg in listSigAlgs:
                for k in range(len(listSigAlgs)):
                    if sigAlg == listSigAlgs[k]:
                        countSigAlgs[k]+=1
                        break
            else:
                listSigAlgs.append(sigAlg)
                countSigAlgs.append(1)
            if keyLength in listKeyLengths:
                for k in range(len(listKeyLengths)):
                    if keyLength == listKeyLengths[k]:
                        countKeyLengths[k]+=1
                        break
            else:
                listKeyLengths.append(keyLength)
                countKeyLengths.append(1)
            if keyAlg in listKeyAlgs:
                for k in range(len(listKeyAlgs)):
                    if keyAlg == listKeyAlgs[k]:
                        countKeyAlgs[k]+=1
                        break
            else:
                listKeyAlgs.append(keyAlg)
                countKeyAlgs.append(1)
    except Error as e:
        print(e)
    print("Number of considered certificates : ", totalCert)
    print("Expired certificates : ", c_expired/totalCert*100, "%")
    for i in range(len(listSigAlgs)):
        print("Certificates with signature algorithm ", listSigAlgs[i], " : ", countSigAlgs[i]/totalCert*100, "%")
    for i in range(len(listKeyLengths)):
        print("Certificates with key length of ", listKeyLengths[i], " : ", countKeyLengths[i]/totalCert*100, "%")
    for i in range(len(listKeyAlgs)):
        print("Certificates with public key algorithm ", listKeyAlgs[i], " : ", countKeyAlgs[i]/totalCert*100, "%")

def listActiveWebsites(conn):
    lst = []
    try:
        sql = "SELECT DISTINCT linkedWebsite FROM websites WHERE successfulConnection = 1 ;"
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchall()
        for x in result:
            lst.append(x[0])
    except Error as e:
        print(e)
    return lst


def main():
    database = "onioncertificates.db"
    conn = create_connection(database)
    if conn is not None:
        totalWebsites = nbOfWebsites(conn)
        successfulConnections = nbOfSuccessfulConnection(conn)
        propOfSafeWebsites = nbOfSafeWebsite(conn)/successfulConnections*100
        propOfTLSv1_3 = nbOfTLS1_3(conn)/successfulConnections*100
        propOfUnderTLSv1_2 = nbOfUnderTLS1_2(conn)/successfulConnections*100
        propOfBadCiphers = nbOfsupportingBadCiphers(conn)/successfulConnections*100
        propOfBadSigalgs = nbOfsupportingBadSigAlgs(conn)/successfulConnections*100
        defaultCiphersList = defaultCiphers(conn)
        defaultSigAlgsList = defaultSigAlgs(conn)
        defaultKeyExchangesList = defaultKeyExchanges(conn)
        propOfDigiCert = (nbOfWebsitesPerIssuer(conn, "DigiCert Inc")-1)/successfulConnections*100
        propOfHellenic = nbOfWebsitesPerIssuer(conn, "Hellenic Academic and Research Institutions Cert. Authority")/successfulConnections*100
        print("Total number of Website : ", totalWebsites)
        print("Number of successful connections : ", successfulConnections, "\n")
        print("Among successful connections : \n")
        print("Safe websites : ", propOfSafeWebsites, "%")
        print("Websites supporting TLSv1.3 : ", propOfTLSv1_3, "%")
        print("Websites supporting TLSv1.1 or lower : ", propOfUnderTLSv1_2, "%")
        print("Websites supporting bad cipher suites : ", propOfBadCiphers, "%")
        print("Websites supporting bad signature algorithms : ", propOfBadSigalgs, "%")
        print("DigiCert Inc Certificates : ", propOfDigiCert, "%")
        print("Hellenic Certificates : ", propOfHellenic, "%")
        print("List of default cipher suites : ", defaultCiphersList)
        print("List of default signature algorithms : ", defaultSigAlgsList)
        print("List of default key exchange algorithms : ", defaultKeyExchangesList)
        print("\nFor all Websites that successfully connected we now consider their current certificate on crt.sh : \n")
        print(statsOnCertificates(conn, listActiveWebsites(conn)))
    else:
        print("Error! cannot connect to the database.")




if __name__ == '__main__':
    main()
