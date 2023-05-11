# AtolCashier

Work with ATOL driver from Python

.env file :
CASH_IP=""
APP_PORT=""

```
python3 -m venv venv
dpkg -i libfptr10_10.9.4.5_amd64.deb

docker build -t cashapi .
docker run -it -p 8888:8888 --restart=always --detach cashapi
```
