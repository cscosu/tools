FROM ubuntu:20.04
RUN apt-get update && apt-get install -y socat

# This is needed because if we run it as root, our UIDs inside and outside of
# the containers don't match and we won't have permission to attach
RUN useradd inmate
USER inmate
WORKDIR /home/inmate

COPY chall ./
CMD socat -d -d -s TCP-LISTEN:9000,reuseaddr,fork EXEC:'/home/inmate/chall'
