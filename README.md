# Cloudflare WAF to AbuseIPDB

## 告知

此項目對MHuiG的項目進行了修改，新增了以下功能:
- Discord webhook support
- 白名單IP


## 它可以幹嘛

從 Cloudflare Graphql API 獲取被 Cloudflare WAF 攔截(阻止/託管質詢)的 IP 並提交給 AbuseIPDB

## 它要怎麼用

請不要 fork 此倉庫！！ 使用模板導入 [Use this template](https://github.com/MHG-LAB/Cloudflare-WAF-to-AbuseIPDB/generate) !! 瞎點fork按鈕發送垃圾 PR 將直接提交到 GitHub 黑名單中(

config.yml：
- `CLOUDFLARE_ZONE_IDS`: Cloudflare ZONE IDs
- `CLOUDFLARE_API_KEY`: Cloudflare API Key
- `CLOUDFLARE_EMAIL`: Cloudflare Email
- `ABUSEIPDB_API_KEY`: AbuseIPDB API Key
- `WHITELISTED_IPS`: 白名單IP
- `DISCORD_WEBHOOK_URL`: Discord Webhook url
- `REPORT_IPS`: 是否舉報IP
- `SEND_DISCORD_WEBHOOK`: 是否發送到discord

### Example
```
REPORT_IPS: "true"
SEND_DISCORD_WEBHOOK: "true"
CLOUDFLARE_ZONE_IDS: 
  - "xxx"
  - "xxx"
  - "xxx"
CLOUDFLARE_EMAIL: "xxx@gmail.com"
CLOUDFLARE_API_KEY: "xxx"
ABUSEIPDB_API_KEY: "xxx"
WHITELISTED_IPS: "1.1.1.1,8.8.8.8,2606:4700:4700::1111"
DISCORD_WEBHOOK_URL: "https://discord.com/api/webhooks/xxxxx"
```

## 這些奇奇怪怪的文件是什麼？

有人經常訪問這些，然而我這裡又沒有這些文件，於是我創建了他們。

例如這些：

- https://abuseipdb.mhuig.top/robots.txt
- https://abuseipdb.mhuig.top/phpinfo.php
- https://abuseipdb.mhuig.top/wp-login.php
- https://abuseipdb.mhuig.top/../../../../../../../etc/passwd
- etc.

## 相關項目
此項目對MHuiG的項目進行了修改
[Cloudflare WAF to AbuseIPDB](https://github.com/MHG-LAB/Cloudflare-WAF-to-AbuseIPDB)
## Support

[AbuseIPDB](https://www.abuseipdb.com/) : AbuseIPDB is an IP address blacklist for webmasters and sysadmins to report IP addresses engaging in abusive behavior on their networks

[Cloudflare](https://www.cloudflare.com/)

[Cloudflare Block Bad Bot Ruleset](https://github.com/XMD0718/cloudflare-block-bad-bot-ruleset)

## License

[MIT](https://github.com/MHG-LAB/Cloudflare-WAF-to-AbuseIPDB/blob/main/LICENSE)