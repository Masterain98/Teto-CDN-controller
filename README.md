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
  - 支持华为云、腾讯云、G-Core Labs 流量包剩余量查询，并在低余量时自动切换至指定的 CDN
    - 定时监控流量包剩余量
- 其它
  - Docker 化支持
  - Telegram 推送日志

## 使用方法

### 填写配置文件

- `config/telegram.json`

  - 用于 Telegram 机器人向用户推送系统消息
    - 其写法如下

  ```json
  {
    "TG_BOT_API": "https://api.telegram.org/bot",
    "TG_BOT_TOKEN": "你的 Telegram BOT Token",
    "TG_USER_ID": "接受通知的 Telegram 用户 ID"
  }
  ```

- `config/task.json`

  - 用于配置参与 CDN 调控的域名 DNS 和 CDN 信息
  - 主 `json` 中只有一个 `task`键，其值为一个列表，包含所有的任务
    - 其范例如下

  ```json
  {
    "task": [
      {
        "domain": "cdn.sample.com",   # 域名
        "enable_off_peak_switch": true,   # 是否启用在闲时自动切换 CDN 
        "enable_traffic_package_switch": true,  # 是否在流量包额度不足时切换至免费 CDN 
        "traffic_package_floor_limit": 5,   # 触发切换免费 CDN 时的流量包额度阈值
        "dns": {   # 域名的 DNS 云平台配置，仅支持华为云
          "huaweicloud": {   
            "ak": "",   # 华为云 API 帐号凭证 ak
            "sk": ""    # 华为云 API 帐号凭证 sk
          }
        },
        "cdn": {   # 域名的 CDN 云平台配置
          "huaweicloud": {   # 华为云 CDN
            "ak": "",  # 华为云 API 帐号凭证 ak
            "sk": "",   # 华为云 API 帐号凭证 sk
            "region": ["cn"],     # 该 CDN 所服务的区域
            "cname": "cdn.sample.com.805bjksdb.cdnhwc8.cn",  # 该 CDN 的 cname 解析值
            "off_peak_type": "off-peak",    # 该 CDN 的时段类型
            "priority": "active",     # 该 CDN 的付费类型
            "refresh_task_list": ["https://cdn.sample.com/"] # 切换该 CDN 时执行的刷新任务
          },
          "qcloud":{    # 腾讯云 CDN
            "SecretId": "",  # 腾讯 API 帐号凭证 SecretId
            "SecretKey": "",  # 腾讯 API 帐号凭证 SecretKey
            "cname": "cdn.sample.com.cdn.dnsv1.com.cn",  # 该 CDN 的 cname 解析值
            "region": ["cn"],     # 该 CDN 所服务的区域
            "off_peak_type": "regular",     # 该 CDN 的时段类型
            "priority": "active",      # 该 CDN 的付费类型
            "refresh_task_list": ["https://cdn.sample.com/"]# 切换该 CDN 时执行的刷新任务
          },
          "gcore": {   # G-Core Labs
            "api_key": "",  # G-Core Labs API 认证 Key
            "cname": "cl-f5610151.gcdn.co", # 该 CDN 的 cname 解析值
            "region": ["global"],     # 该 CDN 所服务的区域
            "off_peak_type": "all-time",     # 该 CDN 的时段类型
            "priority": "fail-over"      # 该 CDN 的付费类型
          }
        }
      },
        
      {
          ...  # 第二个 CDN 域名配置
      },
        
      {
          ...  # 第三个 CDN 域名配置  
      }
        ]
  }
  ```

  - 键值解释

    | 分类 |             键              |                             解释                             |
    | :--: | :-------------------------: | :----------------------------------------------------------: |
    | task | traffic_package_floor_limit | 一个 float 值，在检查流量包状态时，若剩余流量的百分比低于该值，则会执行切换至免费备用 CDN 的任务 |
    | cdn  |           region            | 一个列表，包含该 CDN 服务的区域；列表中允许的值包括 `cn`, `global`和`default` |
    | cdn  |        off_peak_type        | CDN 的时段类型，允许的值为`off-peak` 和 `regular`，分别对应闲时时间段和常规时间段 |
    | cdn  |          priority           | CDN 的付费类型，允许的值包括`active`和`fail-over`，分别对应常规CDN和免费备用 CDN |
    | cdn  |      refresh_task_list      | 一个列表，包含所有需要刷新缓存的目录或文件；若字串符以`/`结尾则执行目录刷新，否则执行文件刷新 |

    

