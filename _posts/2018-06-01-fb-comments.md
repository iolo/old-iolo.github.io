---
title: GitHub Pages / Jekyll 에 페이스북 댓글 달기
date: 2018-06-01
---

### 1. [페이스북 개발자 페이지](https://developers.facebook.com/)에서 앱 등록 

GDPR 덕분에 꼭 입력해야하는 항목이 늘었다. 조금 귀찮지만 어쩌겠는가 찬찬히 채워넣자.

### 2. 사이트 설정에 페이스북 앱ID 추가

[`_config.yml`](https://github.com/iolo/iolo.github.io/blob/master/_config.yml#L57) 파일 수정


```yaml
...
facebook_app_id: 378872509298788
...
```

### 3. 페이스북 앱ID 설정 `meta` 태그 추가

[`_incldes/head.html`](https://github.com/iolo/iolo.github.io/blob/master/_includes/head.html#L20) 파일 수정

{% raw %}
```html
{% if site.facebook_app_id %}
<meta property="fb:app_id" content="{{ facebook_app_id }}" />
{% endif %}
```
{% endraw %}

### 4. 페이스북 JS SDK 추가 

[`_includes/facebook_js_sdk.html`](https://github.com/iolo/iolo.github.io/blob/master/_includes/facebook_js_sdk.html) 파일 추가

{% raw %}
```html
{% if site.facebook_app_id %}
<div id="fb-root"></div>
<script>(function(d, s, id) {
var js, fjs = d.getElementsByTagName(s)[0];
if (d.getElementById(id)) return;
js = d.createElement(s); js.id = id;
  js.src = 'https://connect.facebook.net/ko_KR/sdk.js#xfbml=1&version=v3.0&appId={{ facebook_app_id }}&autoLogAppEvents=1';
fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>
{% endif %}
```
{% endraw %}

[`_includes/footer.html`](https://github.com/iolo/iolo.github.io/blob/master/_includes/footer.html#L29) 파일 수정

{% raw %}
```html
{% include facebook_js_sdk.html %}
```
{% endraw %}

### 3. 페이스북 댓글 마크업 추가 

[`_includes/comments.html`](https://github.com/iolo/iolo.github.io/blob/master/_includes/comments.html) 파일 추가

{% raw %}
```html
{% if page.comments != 'no' %}
<div class="fb-comments" data-href="{{ site.url }}{{ page.url }}" data-width="100%"></div>
{% endif %}
```
{% endraw %}

[`_layouts/post.html`](https://github.com/iolo/iolo.github.io/blob/master/_layouts/post.html#L15) 파일 수정

{% raw %}
```html
...
{% include comments.html %}
...
```
{% endraw %}

### 4. 아래에 페북 댓글이 보이면... OK

날받아놓고 회사 나오니 딱히 할 짓도 없고...해서 테스트삼아 그냥 써 봄.

That's all Folks!

