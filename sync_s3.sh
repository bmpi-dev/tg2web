#!/bin/sh

aws s3 sync --acl public-read media s3://img.bmpi.dev/tg_media
aws s3 sync --acl public-read html s3://channel.bmpi.dev/
