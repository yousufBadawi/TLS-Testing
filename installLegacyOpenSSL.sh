wget https://www.openssl.org/source/openssl-1.0.2l.tar.gz

tar -xzvf openssl-1.0.2l.tar.gz

cd openssl-1.0.2l

./config --prefix=/opt/openssl-1.0.2g --openssldir=/opt/openssl-1.0.2g no-shared enable-ssl2 enable-ssl3 enable-weak-ssl-ciphers

make depend

sudo make install

cd ..

whereis openssl
