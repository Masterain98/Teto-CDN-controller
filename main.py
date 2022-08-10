from PublicCloudAPI.HuaweiCloud import HuaweiCloudAccount
from PublicCloudAPI.QCloud import QCloudAccount
from PublicCloudAPI.GCore import GCoreAccount
from PaaSTask import PaaSTask
from TgMsg import TgMsg

import time
import schedule
import json
from schedule import every, repeat

switch_to_off_peak_cdn_list = []
switch_to_regular_cdn_list = []
switch_to_free_cdn_list = []


@repeat(every().day.at('00:00'))
def switch_to_off_peak_cdn():
    this_task_msg = TgMsg("=" * 20 + "\nStart switching to off-peak CDN")
    task_list = switch_to_off_peak_cdn_list.copy()
    # 默认假设只有华为云 CDN，或无指定平台的 CDN （仅设置了 cname 值的 CDN）
    # 遍历 switch_to_off_peak_cdn_list 中所有的 PaaSTask 对象
    for current_task in task_list:
        allow_switch = False

        # 针对 华为 CDN 进行切换
        if current_task.cdn_account_type == "huaweicloud":
            # 华为云/ Huawei Cloud
            # 检查 CDN 帐号流量包剩余量是否足高于最低限制
            remaining_traffic = current_task.cdn_account.get_remaining_traffic()
            this_task_msg.add_message("Current traffic package status: " + str(remaining_traffic))
            # 如果高于限制，则切换
            if remaining_traffic["china_off_peak_traffic_percent"] > current_task.traffic_package_floor_limit:
                allow_switch = True
            else:
                pass
        # 当没有指定的 CDN 服务商时，不做任何检测，直接更新 cname 解析值
        else:
            allow_switch = True

        if allow_switch:
            # 在 PaaSTask 对象和 Config.json 中 region 是一个列表，因此需要遍历
            # update_record_set_by_name_line 中 region 要求是一个字符串
            for region in current_task.region:
                current_task.dns_account.update_record_set_by_name_line(name=current_task.domain,
                                                                        target_line=region,
                                                                        record_type="CNAME",
                                                                        new_record_value=[current_task.cdn_cname])
            this_task_msg.add_message("Switch to off peak CDN: " + current_task.domain + "\nTarget CDN cname: "
                                      + current_task.cdn_cname)

            subdir_task = []
            file_task = []
            for refresh_task in current_task.refresh_task_list:
                if refresh_task.endswith("/"):
                    subdir_task.append(refresh_task)
                else:
                    file_task.append(refresh_task)
            if subdir_task:
                if current_task.cdn_account.create_refresh_directory_task(subdir_task) is not None:
                    this_task_msg.add_message("成功刷新目录缓存: " + str(subdir_task))
                else:
                    this_task_msg.add_message("刷新目录缓存失败: " + str(subdir_task))
            if file_task:
                if current_task.cdn_account.create_refresh_file_task(file_task) is not None:
                    this_task_msg.add_message("成功刷新文件缓存: " + str(file_task))
                else:
                    this_task_msg.add_message("刷新文件缓存失败: " + str(file_task))
    this_task_msg.add_message("Task Ended Successfully" + "\n" + "=" * 20)
    this_task_msg.push()


@repeat(every().day.at('18:00'))
def switch_to_regular_cdn():
    task_list = switch_to_regular_cdn_list.copy()
    this_task_msg = TgMsg("=" * 20 + "\nStart switching to regular CDN")
    for current_task in task_list:
        allow_switch = False
        if current_task.cdn_account is None:
            this_task_msg.add_message("未知 CDN 服务商，根据规则默认允许切换")
            allow_switch = True
        else:
            remaining_traffic = current_task.cdn_account.get_remaining_traffic_percentage()
            if remaining_traffic > current_task.traffic_package_floor_limit:
                this_task_msg.add_message("高于限制，切换")
                allow_switch = True
            else:
                this_task_msg.add_message("剩余流量：" + str(remaining_traffic) +
                                          " | 低于限制：" + str(current_task.traffic_package_floor_limit) + " | 不切换")
            if current_task.cdn_account_type == "huaweicloud":
                this_task_msg.add_message("切换至华为云 CDN")
                # 华为云/ Huawei Cloud
            elif current_task.cdn_account_type == "qcloud":
                this_task_msg.add_message("切换至腾讯云 CDN")
                # 腾讯云/ Qcloud/ Tencent Cloud
            elif current_task.cdn_account_type == "gcore":
                this_task_msg.add_message("切换至 G-Core CDN")
                # G-Core CDN
            else:
                # Others
                this_task_msg.add_message("未知 CDN 服务商，根据规则默认允许切换")
                allow_switch = True

        if allow_switch:
            this_task_msg.add_message(
                "Switch to regular CDN: " + current_task.domain + "\nTarget CDN cname: " + current_task.cdn_cname)
            # 在 PaaSTask 对象和 Config.json 中 region 是一个列表，因此需要遍历
            # update_record_set_by_name_line 中 region 要求是一个字符串
            for region in current_task.region:
                this_task_msg.add_message("目标域名: " + current_task.domain + "\n目标解析记录: " +
                                          current_task.cdn_cname + "\n目标区域: " + region)
                current_task.dns_account.update_record_set_by_name_line(name=current_task.domain,
                                                                        target_line=region,
                                                                        record_type="CNAME",
                                                                        new_record_value=[current_task.cdn_cname])

            subdir_task = []
            file_task = []
            if current_task.refresh_task_list is not None:
                for refresh_task in current_task.refresh_task_list:
                    if refresh_task.endswith("/"):
                        subdir_task.append(refresh_task)
                    else:
                        file_task.append(refresh_task)
                if subdir_task:
                    if current_task.cdn_account.create_refresh_directory_task(subdir_task) is not None:
                        this_task_msg.add_message("成功刷新目录缓存：" + str(subdir_task))
                    else:
                        this_task_msg.add_message("刷新目录缓存失败：" + str(subdir_task))
                if file_task:
                    if current_task.cdn_account.create_refresh_file_task(file_task) is not None:
                        this_task_msg.add_message("成功刷新文件缓存：" + str(file_task))
                    else:
                        this_task_msg.add_message("刷新文件缓存失败：" + str(file_task))
    this_task_msg.add_message("Task Ended Successfully" + "\n" + "=" * 20)
    this_task_msg.push()


@repeat(every(90).minutes)
def switch_to_free_cdn():
    """
    切换到免费 CDN
    相比闲时CDN切换，switch_to_free_cdn 有一个更复杂的逻辑
    其参数中的列表包含的并不是目标 CDN 而是 fail-over CDN
    该方法会检查目标域名当前的 CDN 服务商，并获得其剩余流量包量
    当流量低于阈值时，则切换到 fail-over CDN
    该列表结构为 [ fail-over CDN 的 PaaSTask 对象, [Activate CDN 帐号对象, CDN 服务商名(str)], [Activate CDN 帐号对象, CDN 服务商名(str)]]
    :return:
    """
    task_list = switch_to_free_cdn_list.copy()
    this_task_message = TgMsg("\nStart timely traffic check\n" + "=" * 20)
    for current_task in task_list:
        current_PaaSTask = current_task[0]
        # 每一个 current_task 代表一个 CDN 域名
        current_cdn_status = current_PaaSTask.dns_account.describe_cdn_provider(name=current_PaaSTask.domain)
        this_task_message.add_message_no_time("\nStart checking " + current_PaaSTask.domain + " CDN\n")
        this_task_message.add_message(current_cdn_status)
        # current_cdn_status 的结构为         {
        #             "name": "www.example.com",
        #             "default": default_line_cdn_provider,
        #             "CN": china_line_cdn_provider,
        #             "Abroad": abroad_line_cdn_provider
        #         }

        for i in range(len(current_task)):
            # i == 0 位置为 fail-over CDN 帐号对象
            if i > 0:
                this_cdn_type = current_task[i][1]
                this_task_message.add_message("Checking: " + str(this_cdn_type))
                if this_cdn_type in current_cdn_status["default"]:
                    # 如果该 CDN 帐号是默认 CDN 帐号，则不需要检查流量包剩余量
                    current_remaining_traffic_percent = current_task[i][0].get_remaining_traffic_percentage()
                    this_task_message.add_message("Remaining traffic percentage: " + str(current_remaining_traffic_percent))
                    if current_remaining_traffic_percent < current_task[i][2]:
                        this_task_message.add_message(
                            "CDN Traffic Package is low at [Default] line, switch to fail-over CDN: " + current_PaaSTask.domain)
                        current_PaaSTask.dns_account.update_record_set_by_name_line(name=current_PaaSTask.domain,
                                                                                    target_line="default-view",
                                                                                    record_type="CNAME",
                                                                                    new_record_value=[
                                                                                        current_PaaSTask.cdn_cname])
                    else:
                        this_task_message.add_message(
                            "CDN Traffic Package is high, keep current record at [Default] line: "
                            + current_PaaSTask.domain)
                        pass
                elif this_cdn_type in current_cdn_status["CN"]:
                    current_remaining_traffic_percent = current_task[i][0].get_remaining_traffic_percentage()
                    this_task_message.add_message(
                        "Remaining traffic percentage: " + str(current_remaining_traffic_percent))
                    if current_remaining_traffic_percent < current_task[i][2]:
                        this_task_message.add_message(
                            "CDN Traffic Package is low at [CN] line, switch to fail-over CDN: " + current_PaaSTask.domain)
                        current_PaaSTask.dns_account.update_record_set_by_name_line(name=current_PaaSTask.domain,
                                                                                    target_line="CN",
                                                                                    record_type="CNAME",
                                                                                    new_record_value=[
                                                                                        current_PaaSTask.cdn_cname])
                    else:
                        this_task_message.add_message(
                            "CDN Traffic Package is high, keep current record at [CN] line: " + current_PaaSTask.domain)
                        pass
                elif this_cdn_type in current_cdn_status["Abroad"]:
                    current_remaining_traffic_percent = current_task[i][0].get_remaining_traffic_percentage()
                    this_task_message.add_message(
                        "Remaining traffic percentage: " + str(current_remaining_traffic_percent))
                    if current_remaining_traffic_percent < current_task[i][2]:
                        this_task_message.add_message(
                            "CDN Traffic Package is low at [Abroad] line, switch to fail-over CDN: " + current_PaaSTask.domain)
                        current_PaaSTask.dns_account.update_record_set_by_name_line(name=current_PaaSTask.domain,
                                                                                    target_line="Abroad",
                                                                                    record_type="CNAME",
                                                                                    new_record_value=[
                                                                                        current_PaaSTask.cdn_cname])
                    else:
                        this_task_message.add_message(
                            "CDN Traffic Package is high, keep current record at [Aboard] line: " + current_PaaSTask.domain)
                        pass
                else:
                    this_task_message.add_message("this CDN is currently not in used")
                    this_task_message.add_message(
                        "Remaining traffic percentage: " + str(current_task[i][0].get_remaining_traffic_percentage()))

            else:
                continue
            this_task_message.add_message_no_time("#" * 20)
        this_task_message.add_message_no_time("-" * 20)
    this_task_message.add_message("Task Ended Successfully" + "\n" + "=" * 20)
    this_task_message.push()


if __name__ == '__main__':
    welcome_msg = TgMsg("\n" + "Teto CDN Control System Started" + "\n" + "=" * 20)
    with open("config.json", "r") as f:
        config = json.load(f)
    for task in config["task"]:
        domain = task["domain"]
        welcome_msg.add_message_no_time("\nStart checking domain config: " + domain)
        enable_off_peak_switch = task["enable_off_peak_switch"]
        enable_traffic_package_switch = task["enable_traffic_package_switch"]
        traffic_package_floor_limit = task["traffic_package_floor_limit"]
        dns_provider = list(task["dns"].keys())[0]
        if dns_provider.lower() == "huaweicloud":
            dns_account = HuaweiCloudAccount(ak=task["dns"][dns_provider]["ak"], sk=task["dns"][dns_provider]["sk"])
        else:
            welcome_msg.add_message("Unsupported DNS provider: " + dns_provider)
            break

        for cdn_provider in list(task["cdn"].keys()):
            if cdn_provider.lower() == "huaweicloud":
                welcome_msg.add_message("Generating Huawei Cloud CDN account")
                cdn_account = HuaweiCloudAccount(ak=task["cdn"][cdn_provider]["ak"], sk=task["cdn"][cdn_provider]["sk"])
                this_task = PaaSTask(domain=domain, dns_account=dns_account,
                                     cdn_cname=task["cdn"][cdn_provider]["cname"], cdn_account=cdn_account,
                                     cdn_account_type=cdn_provider, region=task["cdn"][cdn_provider]["region"],
                                     traffic_package_floor_limit=traffic_package_floor_limit,
                                     refresh_task_list=task["cdn"][cdn_provider]["refresh_task_list"])
            elif cdn_provider.lower() == "qcloud":
                welcome_msg.add_message("Generating QCloud CDN account")
                cdn_account = QCloudAccount(SecretId=task["cdn"][cdn_provider]["SecretId"],
                                            SecretKey=task["cdn"][cdn_provider]["SecretKey"])
                this_task = PaaSTask(domain=domain, dns_account=dns_account,
                                     cdn_cname=task["cdn"][cdn_provider]["cname"], cdn_account=cdn_account,
                                     cdn_account_type=cdn_provider, region=task["cdn"][cdn_provider]["region"],
                                     traffic_package_floor_limit=traffic_package_floor_limit,
                                     refresh_task_list=task["cdn"][cdn_provider]["refresh_task_list"])
            elif cdn_provider.lower() == "gcore":
                welcome_msg.add_message("Generating GCore CDN account")
                cdn_account = GCoreAccount(api_key=task["cdn"][cdn_provider]["api_key"])
                this_task = PaaSTask(domain=domain, dns_account=dns_account,
                                     cdn_cname=task["cdn"][cdn_provider]["cname"], cdn_account=cdn_account,
                                     cdn_account_type=cdn_provider, region=task["cdn"][cdn_provider]["region"],
                                     traffic_package_floor_limit=traffic_package_floor_limit)
            else:
                welcome_msg.add_message("\nUnsupported CDN provider: " + cdn_provider)
                if task["cdn"][cdn_provider]["cname"] != "":
                    this_task = PaaSTask(domain=domain, dns_account=dns_account,
                                         region=task["cdn"][cdn_provider]["region"],
                                         cdn_cname=task["cdn"][cdn_provider]["cname"])
                else:
                    break

            if enable_off_peak_switch:
                if task["cdn"][cdn_provider]["off_peak_type"] == "off-peak":
                    switch_to_off_peak_cdn_list.append(this_task)
                    welcome_msg.add_message("Find off-peak CDN: " + cdn_provider)
                elif task["cdn"][cdn_provider]["off_peak_type"] == "regular":
                    switch_to_regular_cdn_list.append(this_task)
                    welcome_msg.add_message("Find regular CDN: " + cdn_provider)
                elif task["cdn"][cdn_provider]["off_peak_type"] == "all-time":
                    welcome_msg.add_message("All time CDN provider: " + cdn_provider)
                else:
                    welcome_msg.add_message("Error reading off peak CDN config")
                    break

            # 当检测到有 fail-over CDN 时，将该域名加入定时检测任务列表中
            if task["cdn"][cdn_provider]["priority"] == "fail-over":
                # 将 fail-over CDN 设置为每个任务列表中的第一个位置
                fail_over_task_list = [this_task]
                # 进行另一次 loop
                for this_cdn in list(task["cdn"].keys()):
                    if task["cdn"][this_cdn]["priority"] == "active":
                        this_active_cdn_provider = this_cdn
                        # 只有 CDN 服务商提供了查询流量的接口也可以加入以下的条件
                        if this_active_cdn_provider.lower() == "huaweicloud":
                            this_active_cdn_account = HuaweiCloudAccount(ak=task["cdn"][this_active_cdn_provider]["ak"],
                                                                         sk=task["cdn"][this_active_cdn_provider]["sk"])
                            fail_over_task_list.append(
                                [this_active_cdn_account, "huaweicloud", traffic_package_floor_limit])
                        elif this_active_cdn_provider.lower() == "qcloud":
                            this_active_cdn_account = QCloudAccount(
                                SecretId=task["cdn"][this_active_cdn_provider]["SecretId"],
                                SecretKey=task["cdn"][this_active_cdn_provider]["SecretKey"])
                            fail_over_task_list.append([this_active_cdn_account, "qcloud", traffic_package_floor_limit])
                        elif this_active_cdn_provider.lower() == "gcore":
                            this_active_cdn_account = GCoreAccount(
                                api_key=task["cdn"][this_active_cdn_provider]["api_key"])
                            fail_over_task_list.append([this_active_cdn_account, "gcore", traffic_package_floor_limit])
                        else:
                            print("Unsupported CDN provider for fail-over check: " + this_active_cdn_provider)
                switch_to_free_cdn_list.append(fail_over_task_list)
        welcome_msg.add_message_no_time("#" * 20)
    welcome_msg.add_message("Read config file successfully" + "\n" + "=" * 20)
    welcome_msg.push()

    switch_to_free_cdn()
