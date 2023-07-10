FROM mariadb:10.3.25

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim 

WORKDIR /

EXPOSE 3306

ADD my.cnf /etc/mysql/my.cnf
