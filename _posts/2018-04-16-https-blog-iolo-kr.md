---
title: "깃헙 페이지 커스텀 도메인을 Let's Encrypt 인증서로 서비스하기"
date: '2018-04-16'
---

> 2018년 5월 1일부터 커스텀 도메인을 사용하는 깃헙페이지에서도 https를 사용할 수 있다.
>
> 참고: [Custom domains on GitHub Pages gain support for HTTPS](https://blog.github.com/2018-05-01-github-pages-custom-domains-https/)

이 블로그는 [GitHub Pages](https://pages.github.com/)를 통해 서비스되고 있다 .
별다른 설정 없이 <http://iolo.github.io> 또는 <https://iolo.github.io> 로 접속할 수 있으며,
[https를 강제](https://help.github.com/articles/securing-your-github-pages-site-with-https/)할 수도 있다.
그런데 나는 <https://blog.iolo.kr> - 커스텀 도메인을 **https**로 서비스하고 싶다. 별다른 이유는 없다. 그냥 뽀대? 
구글링을 해보면 [CloudFlare의 CDN 서비스를 이용해서 로 GitHub Pages 커스텀 도메인을 https로 서비스하는 방법](https://blog.cloudflare.com/secure-and-fast-github-pages-with-cloudflare/)을 쉽게 찾을 수 있다.
그런데 나는 [Let's Encrypt](https://letsencrypt.org/) 인증서를 쓰고 싶다. 별다른 이유는 없다. 그냥 뽀대!

이 글은 그렇게 시작된 뽀대 드리븐 삽질의 기록이다.

### [certbot](https://certbot.eff.org/) 패키지를 설치

```
# add-apt-repository ppa:certbot/certbot
# apt-get update
# apt-get install python-certbot-nginx
#
# certbot --version
certbot 0.22.2
#
```


### 인증서 발급 & nginx 설정 업데이트

certbot으로 와일드카드 인증서를 받으려면 `--manual` 옵션을 사용해야 한다.
아직은 자동으로 nginx 설정을 업데이트 해주는 `--nginx` 옵션을 함께 사용할 수 없다.

certbot의 nginx 플러그인이 어떤 설정을 만들어주는지 알고 싶어서 한번 해봤는데...
별거 없다. 바로 와일드카드 인증서를 받고, 수동으로 nginx 설정을 업데이트해도 된다.

```
# certbot --nginx -d iolo.kr -d www.iolo.kr
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator nginx, Installer nginx
Starting new HTTPS connection (1): acme-v01.api.letsencrypt.org
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for iolo.kr
http-01 challenge for www.iolo.kr
Waiting for verification...
Cleaning up challenges
Deploying Certificate to VirtualHost /etc/nginx/sites-enabled/default
Deploying Certificate to VirtualHost /etc/nginx/sites-enabled/default

Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access.
-------------------------------------------------------------------------------
1: No redirect - Make no further changes to the webserver configuration.
2: Redirect - Make all requests redirect to secure HTTPS access. Choose this for
new sites, or if you're confident your site works on HTTPS. You can undo this
change by editing your web server's configuration.
-------------------------------------------------------------------------------
Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
Redirecting all traffic on port 80 to ssl in /etc/nginx/sites-enabled/default
Redirecting all traffic on port 80 to ssl in /etc/nginx/sites-enabled/default

-------------------------------------------------------------------------------
Congratulations! You have successfully enabled https://iolo.kr and
https://www.iolo.kr

You should test your configuration at:
https://www.ssllabs.com/ssltest/analyze.html?d=iolo.kr
https://www.ssllabs.com/ssltest/analyze.html?d=www.iolo.kr
-------------------------------------------------------------------------------

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/iolo.kr/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/iolo.kr/privkey.pem
   Your cert will expire on 2018-07-13. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot again
   with the "certonly" option. To non-interactively renew *all* of
   your certificates, run "certbot renew"
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le

#
root@aronia:/etc/letsencrypt# tree /etc/letsencrypt/live
/etc/letsencrypt/live
`-- iolo.kr
    |-- cert.pem -> ../../archive/iolo.kr/cert2.pem
    |-- chain.pem -> ../../archive/iolo.kr/chain2.pem
    |-- fullchain.pem -> ../../archive/iolo.kr/fullchain2.pem
    |-- privkey.pem -> ../../archive/iolo.kr/privkey2.pem
    `-- README
#
```

### nginx 설정 정리 & 검사 & 적용

```
# cat /etc/nginx/site-enabled/default
server {
	listen [::]:443 ssl http2 default_server ipv6only=on;
	listen 443 ssl http2 default_server;
	ssl_certificate /etc/letsencrypt/live/iolo.kr/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/iolo.kr/privkey.pem;
	include /etc/letsencrypt/options-ssl-nginx.conf;
	ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

	server_name iolo.kr www.iolo.kr;

	charset utf-8;

	root /var/www/html;

	location / {
		try_files $uri $uri/ =404;
	}
}

server {
	listen 80 default_server;
	listen [::]:80 default_server;

	server_name iolo.kr www.iolo.kr;

	return 301 https://$host$request_uri;
}
#
# nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
#
# systemctl reload nginx
```

### 1차 결과 확인

* <https://iolo.kr>
* <http://iolo.kr> --> <https://iolo.kr> 로 리디렉트(301)
* <https://www.iolo.kr>
* <http://www.iolo.kr> --> <https://iolo.kr> 로 리디렉트(301)
* <https://www.ssllabs.com/ssltest/analyze.html?d=iolo.kr>


### 와일드카드 인증서 발급

```
# certbot certonly --cert-name iolo.kr --manual \
        --preferred-challenges dns-01  \
        --server https://acme-v02.api.letsencrypt.org/directory \
        -d "*.iolo.kr" -d iolo.kr
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator manual, Installer None
Starting new HTTPS connection (1): acme-v02.api.letsencrypt.org

-------------------------------------------------------------------------------
You are updating certificate iolo.kr to include new domain(s):
+ *.iolo.kr

You are also removing previously included domain(s):
- www.iolo.kr

Did you intend to make this change?
-------------------------------------------------------------------------------
(U)pdate cert/(C)ancel: U
Renewing an existing certificate
Performing the following challenges:
dns-01 challenge for iolo.kr
dns-01 challenge for iolo.kr

-------------------------------------------------------------------------------
NOTE: The IP of this machine will be publicly logged as having requested this
certificate. If you're running certbot in manual mode on a machine that is not
your server, please ensure you're okay with that.

Are you OK with your IP being logged?
-------------------------------------------------------------------------------
(Y)es/(N)o: Y

-------------------------------------------------------------------------------
Please deploy a DNS TXT record under the name
_acme-challenge.iolo.kr with the following value:

d8jBCjPmomqUQVccpmtge_lcVsgTOZH8Id21X-f7OLs
Before continuing, verify the record is deployed.
-------------------------------------------------------------------------------
Press Enter to Continue
#
```

잠시 멈춰서, DNS에서 `_acme-challenge` 호스트에 `TXT` 레코드 추가하고...

```
# dig -t txt _acme-challenge.iolo.kr
...
;; ANSWER SECTION:
_acme-challenge.iolo.kr. 300	IN	TXT	"d8jBCjPmomqUQVccpmtge_lcVsgTOZH8Id21X-f7OLs"
...
```

...가던 길 계속가자.

```
-------------------------------------------------------------------------------
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/iolo.kr/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/iolo.kr/privkey.pem
   Your cert will expire on 2018-07-15. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot
   again. To non-interactively renew *all* of your certificates, run
   "certbot renew"
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le

#
```

### 2차 결과 확인 

* <https://blog.iolo.kr>
* <http://blog.iolo.kr> -> <https://blog.iolo.kr> 로 리디렉트(301)
* <http://iolo.github.io> -> <https://blog.iolo.kr> 로 리디렉트(301)
* <https://iolo.github.io> -> <https://blog.iolo.kr> 로 리디렉트(301)
* <https://www.ssllabs.com/ssltest/analyze.html?d=blog.iolo.kr>

### 참고자료

* [How To Secure Apache with Let's Encrypt on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04)
* [Secure and fast GitHub Pages with CloudFlare](https://blog.cloudflare.com/secure-and-fast-github-pages-with-cloudflare/)

That's All Folks!

