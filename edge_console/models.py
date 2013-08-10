# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from account.models import UserProfile
from portal_console.dip.local_fetcher import LocalFetcher
from portal_console.dip.utils import minf_traffic_to_bps


class App(models.Model):
    name = models.CharField('名称', max_length=128, unique=True,
        help_text="域名的前一个或两个字段，例如down.apps.sina.cn，名称是downapps，确保名称唯一性即可")
    channels = models.TextField(help_text="加速域名，如果有多个域名请用逗号隔开")

    jira_url = models.CharField('提案链接或提案号', max_length=256, blank=True)
#    third_cdn_status = models.CharField('第三方CDN配置状态', max_length=256, blank=True)
#    channels_icp = models.CharField('channels对应备案号', max_length=256, blank=True)

    origins = models.TextField(
        help_text="源站，请提供能够解析的源站")
    check_url = models.CharField('健康检查URL', max_length=256, blank=True,
        help_text="根据业务内容上传图片或视频到源站，方便CDN进行监控加速域名，只需要path部分，如/null.jpg")
    is_s3 = models.BooleanField('是否是S3应用')
    s3_kid = models.CharField(max_length=128, blank=True)
    s3_passwd = models.CharField(max_length=128, blank=True)
    # convert_host = models.BooleanField(default=False,
    #                                    help_text="ATS 回源时将 interip 作为 host")

    CONVERT_HOST_CHOICES = (
        (0, 'NONE'),
        (1, 'CONVERT_HOST'),
        (2, 'NEGATIVE_CACHE'),
    )
    convert_host = models.SmallIntegerField(
        'ATS配置Conf', choices=CONVERT_HOST_CHOICES, default=0,
        help_text='选择ATS配置: ATS回源时将interip作为HOST / 缓存非200内容')

#    use_origin_as_interip = models.BooleanField(
#        default=False,
#        help_text="ats 将源站地址作为回源地址，不使用 islb 域名")
    acl_source_ip = models.TextField(blank=True, help_text="not work now")
    user = models.ForeignKey(User)
    wideip = models.CharField(max_length=256)
    interip = models.CharField(max_length=256)
    desc = models.TextField('描述', blank=True)

    """ sinaedge kid, key option """
    is_sinaedge_anti_stealing_link = models.BooleanField(
        '启用SinaEdge防盗链',
        default=False,
        help_text="此项选中的情况下，kid and key才能生效, 此项不可和 is_s3 同时选中")
    sinaedge_kid = models.CharField(max_length=128, blank=True)
    sinaedge_key = models.CharField(max_length=128, blank=True)


    """ referer filter related """
    referer_enable = models.BooleanField("是否启用Referer过滤", default=False,
            help_text="此项选中的情况下，下面的选项才能生效")
    referer_optional = models.BooleanField('是否允许请求头中不带Referer', default=True)

    referer_only_allow_whitelist = models.BooleanField(
        "是否仅启用白名单", default=False,
        help_text="此项选中的情况下, 仅请求的referer在白名单中可访问; 此项不选中, 黑名单以外的请求可访问")

    referer_redirect_url = models.CharField('Referer重定向url', max_length=256, blank=True,
            default="http://www.sinaedge.com/", help_text="required field")
    referer_whitelist = models.TextField('Referer白名单', blank=True,
            help_text="如: \"canvisit\.qq\.com\" 请用','分隔")
    referer_blacklist = models.TextField("Referer黑名单", blank=True,
            help_text="如: qq\.com/,taobao\.com/\" 请用','分隔, 注意开头不要加'\.'")

    """ plugin related """
    escape_filename = models.BooleanField('启用文件名转义', default=True,
            help_text="if User-Agent is MSIE, encode filename in Content-Disposition based on fn or x-sina-attachement")

    """ trafficserver 特殊选项 """
    is_regex_map = models.BooleanField('启用正则匹配Channel', default=False, help_text="正则匹配 channel")
    remap_extra_rule = models.CharField('附加remap规则', max_length=1000, blank=True, help_text="附加到map规则后的额外规则,请注意测试,否则会导致崩溃")
    enable_add_header = models.BooleanField(default=False, help_text="回源添加 header")
    header_to_add = models.CharField("需要添加的 header", max_length=1000, blank=True, help_text="启用添加Http头，头信息：key:value")
    remove_duplicate = models.BooleanField("移除已有 header", default=False, help_text="添加时移除已有的头")
    cache_ignore_querystring = models.BooleanField("缓存时忽略 querystring", default=False)
    enable_combo = models.BooleanField("启用 combo", default=False, help_text="插件稳定前慎用")
    enable_gzip = models.BooleanField("启用 gzip", default=False, help_text="ATS 压缩 response 并缓存")
    gzip_types = models.CharField('gzip 文件类型', max_length=256, blank=True,
            default="text/*, application/x-javascript", help_text="Content-Type, 用逗号 ',' 分隔")


    """ 限速和限连接数相关 """
    is_limit = models.BooleanField("是否启用限速", default=False,
                                   help_text=("此项选中的情况下，下面的选项才能生效"))

    limit_conn = models.IntegerField("并发数限制", default=0, help_text="限并发数")
    limit_rate = models.IntegerField("速度限制", default=0, help_text="限速，单位为k")

    """ 二级调度高级选项 """
    enable_secondary_schedule = models.BooleanField("启用 BK二级调度", default=False,
                                                    help_text=("此项选中的情况下，并且是Bigfile下面的选项才能生效"))
    secondary_schedule_visit_threshold = models.IntegerField("访问次数阈值", default=0, help_text="访问次数不超过这个阈值时,回源")
    secondary_schedule_host = models.CharField("BK集群二级调度地址", max_length=128,
                                               blank=True,
                                               help_text="BK集群内二级调度的目标地址, 目前用于冷文件调度的回源地址域名")

    enable_proxy_cache  = models.BooleanField("是否启用proxy_cache", default=False, help_text=
                                               "生成Bigfile配置时对channel使用proxy_cache;")
    enable_backend_cache = models.BooleanField("是否启用backend_cache", default=False, help_text=
                                               "生成Bigfile配置时添加 backend_cache on;")
    DRAGGING_ON_MISS_CHOICES = (
        (0, 'NONE'),
        (1, 'mp4'),
        (2, 'flv'),
        (3, 'mp4+flv'),
    )
    enable_dragging_on_miss = models.SmallIntegerField(
        '支持拖动文件', choices=DRAGGING_ON_MISS_CHOICES, default=0,
        help_text='选择Nginx支持拖动文件配置: 不支持拖动 / mp4 / flv / mp4+flv')

    # grid = models.ForeignKey('Grid', limit_choices_to={'is_vgrid': False})
    status = models.BooleanField('是否启用加速', default=True,
                                 help_text="是否启用到Grid上加速?")

    product = models.ForeignKey('Product', help_text="所属产品")
    grid = models.ManyToManyField('Grid', db_table='grid_app', blank=True,
                                  help_text="右边窗口是待选择的Grid")

    cluster = models.ManyToManyField('Cluster', db_table='cluster_app', blank=True,
                                     help_text="右边窗口是待选择的出口节点，双击或者多 \
                                     选后双击将节点添加到左边窗口作为跟源站绑定的出口节点。\
                                     当选择多个节点时，入口节点会选择和自身ISP最匹配的 “出口节点” \
                                     作为跟源站绑定的出口节点。<b><font color='red'>注意：如果源站只有一个，那么在选择出口的\
                                     时候请只选择一个跟源站在同isp的出口节点，这样可以提高回源效率。如果\
                                     源站有2个的话，那么选择2个和其isp一致的出口节点。当源站只有一个的情况下，\
                                     选择多个isp的出口，那么其中多个出口回源的时候是跨isp的，效率较低。</font></b>\
                                     ")

    class Meta:
        verbose_name = "App"
        verbose_name_plural = "App"
        db_table = 'app'

    def __unicode__(self):
        return u"%s" % self.name.strip()

    def channel_list(self):
        return [c.strip() for c in self.channels.split(',')]

    def dip_channel(self, channel):
        if self.is_regex_map:
            raise Exception("不支持正则域名")

        if self.convert_host == 1:
            return self.origins.strip()

        if self.enable_add_header and self.header_to_add.lower().find('host:') >= 0:
            return self.header_to_add[5:].strip()

        return channel

    def current_bandwidth(self):
        try:
            data = LocalFetcher().fetch_current_bandwidth(self.dip_channel(self.channel_list()))
            return minf_traffic_to_bps(data[0])
        except Exception, e:
            return "n/a"

    def current_bandwidth_int(self):
        try:
            data = LocalFetcher().fetch_current_bandwidth(self.dip_channel(self.channel_list()))
            return int(data[0])
        except Exception, e:
            return -1

    def get_grids(self):
        return self.grid.all()

