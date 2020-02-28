# tg2web

## Intro

This lib help you static telegram channel message into a website, the demo is in [here](https://tg.bmpi.dev)

## Guide

1. Create a .env file to add your Telegram API Key, such as:

```
export TG_API_ID=12345678
export TG_API_HASH='xxxxxxxxxxxxxx'
export CDN_DISTRIBUTION_ID=XXXXXXXX
```

then source it:

```
source .env
```

For more of this TG key, you can see this [document](https://core.telegram.org/api/obtaining_api_id).

2. Create a AWS S3 bucket for store your telegram media and a bucket for your html file

**You need replace S3 bucket in `sync_s3.sh` with your S3 bucket.**

3. Install python dependence lib

```
pip3 install -r requirements.txt
```

4. Run make

```
make
```

just wait a minute, enjoy yourself!
