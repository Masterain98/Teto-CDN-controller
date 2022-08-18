# Teto-CDN-controller
Teto-CDN-Controller is a tool designed to reduce the cost of CDN in China by automatically switch between CDN providers.

Teto-CDN-Controller 是一个旨在通过自动化控制CDN解析，以降低用户在中国地区CDN成本的工具。

> 该项目尚未完成

## 前置要求

- 使用华为云 DNS 和 CDN 功能

## 功能

[CDN 优化：如何通过引入多个 CDN 服务商以降低 40% 的流量费用](https://blog.irain.in/archives/CDN-optimization-save-40-percentage-traffic-cost.html)

- DNS 解析
  - 支持海外、中国大陆线路分别解析
- CDN
  - 定时从当前的CDN服务商切换到华为云闲时 CDN，在闲时时段结束后切换为原始 CDN
  - 支持华为云、腾讯云、G-CoreLabs 流量包剩余量查询，并在低余量时自动切换至指定的 CDN
    - 定时监控流量包剩余量
- 其它
  - Docker 化支持
  - Telegram 推送日志



