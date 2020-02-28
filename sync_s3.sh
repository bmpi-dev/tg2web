#!/bin/sh

aws s3 sync --acl public-read tg_media s3://img.bmpi.dev/tg_media
aws s3 sync --acl public-read html s3://tg.bmpi.dev/

aws cloudfront create-invalidation --distribution-id $CDN_DISTRIBUTION_ID --paths "/*"
