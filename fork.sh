#!/bin/bash
fuser -k $2/tcp
ganache-cli --fork $1 -p $2
