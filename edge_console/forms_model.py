#encoding: utf-8


from commons import get_obj_from_name, CheckForm
from django import forms
from django.contrib.auth.models import User
from django.db import transaction, router
from django.db.models import Q
from models import *
from modules.utils import *
from modules.utils_flow import pass_work_flow
from echelon.middleware import EchelonMiddleware

import socket


class Username_CheckForm(CheckForm):
    def __init__(self, id, data):
        CheckForm.__init__(self, id, data)
        self.model = User

    def clean_username(self):
        user = self.cleaned_data.get('username', "").strip()
        users = User.objects.filter(username=user)
        if users:
            raise forms.ValidationError("此用户名已存在，请确认是否已申请过")
        return users

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password', "").strip()
        confirm_password = self.cleaned_data.get('confirm_password', "").strip()

        if password != confirm_password:
            raise forms.ValidationError(u"两次填写密码不一致!")

        return confirm_password


class App_CheckForm(CheckForm):
    def __init__(self, id, data):
        CheckForm.__init__(self, id, data)
        self.model = App

    def clean_name(self):
        # check name, only (^[a-z][a-z0-9-]+$) is allowed.
        name = self.cleaned_data.get('name', "")
        if re.search(r'^[a-z][a-z0-9-]+$', name):
            return name
        raise forms.ValidationError("name %s is not allowed,no match (^[a-z][a-z0-9-]+$)" % name);

    def clean_product(self):
        product = self.cleaned_data.get('product', "").strip()
        product = get_obj_from_name(Product, product, match='is')
        if not product:
            raise forms.ValidationError("product can not be none")
        return product

    def clean_user(self):
        user = self.cleaned_data.get('user', "").strip()
        users = User.objects.filter(username=user)
        if not users:
            raise forms.ValidationError("user can not be none")
        current_user = EchelonMiddleware.get_user()
        if user != current_user.username and not current_user.is_superuser:
            raise forms.ValidationError("user can not be matched")
        return users[0]

    def clean_channels(self):
        # check duplicate channels, if exist, tell administrator to correct it
        name = self.cleaned_data.get('name', "")
        channels = self.cleaned_data.get('channels', "").rstrip()
        channels_split = channels.split(',')
        #apps = App.objects.filter(~Q(id=self.id))
        apps = Application.objects.all()
        channel_count = {}

        for app in apps:
            for ch in app.channels.split(','):
                if ch in channel_count:
                    raise forms.ValidationError(
                        "app '%s' and '%s' have the same channel '%s', "
                        "please remove one" % (app, channel_count[ch], ch))
                else:
                    channel_count[ch] = app.name

        for ch in channels_split:
            if ch in channel_count:
                if channel_count[ch] != name:
                    raise forms.ValidationError("channel '%s' already exist in '%s' app" % (ch, channel_count[ch]))
                else:
                    raise forms.ValidationError("duplicate channel '%s'" % ch);
            else:
                channel_count[ch] = name

        return channels

    def clean_origins(self):
        channels = self.cleaned_data.get('channels', "")
        channels_split = channels.split(',')
        origins = self.cleaned_data.get('origins', "").rstrip()
        origins_split = origins.split(',')


        for ch in channels_split:
            if ch in origins_split:
                raise forms.ValidationError("The origin can not be the same as channel !")

        for orig in origins_split: # jiedo modified
            if orig.find('$') >= 0:
                continue
            orig = orig.split(':')[0]
            try:
                socket.gethostbyname(orig)
            except:
                raise forms.ValidationError(
                    "The origin domain cann't be resolved(no A-record): %s" % orig)
        return origins


    def clean_check_url(self):
        check_url = self.cleaned_data.get('check_url','')
        if not check_url.startswith('/'):
            raise forms.ValidationError('check_url必须是以/开头的path路径')
        return check_url

    def clean_sinaedge_kid(self):
        is_sinaedge_anti_stealing_link = self.cleaned_data.get('is_sinaedge_anti_stealing_link', None)
        sinaedge_kid = self.cleaned_data.get('sinaedge_kid', '').strip()

        if is_sinaedge_anti_stealing_link and (not sinaedge_kid):
            raise forms.ValidationError("if is_sinaedge_anti_stealing_link is enabled, sinaedge_kid can not be empty")

        if is_sinaedge_anti_stealing_link and len(sinaedge_kid) != 20:
            raise forms.ValidationError("sinaedge_kid should be 20 chars")
        return sinaedge_kid

    def clean_sinaedge_key(self):
        is_sinaedge_anti_stealing_link = self.cleaned_data.get('is_sinaedge_anti_stealing_link', None)
        sinaedge_key = self.cleaned_data.get('sinaedge_key', '').strip()

        if is_sinaedge_anti_stealing_link and (not sinaedge_key):
            raise forms.ValidationError("if is_sinaedge_anti_stealing_link is enabled, sinaedge_key can not be empty")

        if is_sinaedge_anti_stealing_link and len(sinaedge_key) != 40:
            raise forms.ValidationError("sinaedge_key should be 40 chars")

        return sinaedge_key

    def clean_s3_kid(self):
        is_s3 = self.cleaned_data.get('is_s3', None)
        s3_kid = self.cleaned_data.get('s3_kid', "").strip()

        if is_s3 and (not s3_kid):
            raise forms.ValidationError("if is_s3 is enabled, s3_kid can not be empty !")
        else:
            return s3_kid

    def clean_s3_passwd(self):
        is_s3 = self.cleaned_data.get('is_s3', None)
        s3_passwd = self.cleaned_data.get('s3_passwd', "").strip()
        if is_s3 and (not s3_passwd):
            raise forms.ValidationError("if is_s3 enabled, s3_passwd can not be empty !")
        else:
            return s3_passwd

    def clean_convert_host(self):
        is_s3 = self.cleaned_data.get('is_s3', None)
        convert_host = self.cleaned_data.get('convert_host', None)

        if is_s3 and (convert_host == 1):
            raise forms.ValidationError("is_s3 and convert_host can not be enabled at same time !")

        return convert_host


    def clean_referer_redirect_url(self):
        url = self.cleaned_data.get('referer_redirect_url', "").strip()
        enable_referer = self.cleaned_data.get('referer_enable', None)

        if enable_referer and len(url) == 0:
            raise forms.ValidationError("referer redirect url is required!")
        else:
            return url

    def clean_referer_whitelist(self):
        whitelist = self.cleaned_data.get('referer_whitelist', "").strip()
        only_allow_whitelist = self.cleaned_data.get('referer_only_allow_whitelist', None)
        enable_referer = self.cleaned_data.get('referer_enable', None)

        if enable_referer and only_allow_whitelist and len(whitelist) == 0:
            raise forms.ValidationError("you select only allow whitelist, but didn't provide whitelist.")
        else:
            return whitelist

    def clean_header_to_add(self):
        header_to_add = self.cleaned_data.get('header_to_add', "").strip()
        enable_add_header = self.cleaned_data.get('enable_add_header', None)

        if enable_add_header:
            if not header_to_add:
                raise forms.ValidationError("please fill this field")

            colon_pos = header_to_add.find(':')

            if colon_pos < 1 or colon_pos == len(header_to_add) - 1:
                raise forms.ValidationError("wrong position for ':'")

            if header_to_add.find(' ') > -1:
                raise forms.ValidationError("should not contain whitespace")

        return header_to_add

    def clean_gzip_types(self):
        enable_gzip = self.cleaned_data.get('enable_gzip', None)
        gzip_types = self.cleaned_data.get('gzip_types', '').strip()

        if enable_gzip:
            if not gzip_types:
                raise forms.ValidationError("please fill gzip_types")

        return gzip_types

    def clean_secondary_schedule_visit_threshold(self):
        secondary_schedule_visit_threshold = self.cleaned_data.get("secondary_schedule_visit_threshold", "").strip()
        n_visit = 0
        try:
            if not secondary_schedule_visit_threshold:
                secondary_schedule_visit_threshold = '0'
                n_visit = int(secondary_schedule_visit_threshold)
        except Exception, e:
            raise forms.ValidationError(e + " must be an integer.")
        return n_visit

    def clean_secondary_schedule_host(self):
        secondary_schedule_host = self.cleaned_data.get("secondary_schedule_host", "").strip()
        print secondary_schedule_host
        secondary_schedule_host_split = secondary_schedule_host.split(",")
        print secondary_schedule_host_split
        if len(secondary_schedule_host_split) > 1:
            raise forms.ValidationError(u"只能填写一个二级调度地址")

        return secondary_schedule_host

    def clean_cluster(self):
        clusterids = self.cleaned_data.get('cluster', [])
        grids = [g.name for g in self.clean_grid()]
        if "dsa" in grids:
            if not clusterids:
                raise forms.ValidationError(u"DSA应用未关联cluster，请在DSA配置标签关联")
            else:
                if clusterids:
                    raise forms.ValidationError(u"非DSA应用关联cluster，请在DSA配置标签删除关联")

        clusters = [Cluster.objects.get(id=int(i)) for i in clusterids]
        return clusters

    def clean_grid(self):
        gridids = self.cleaned_data.get('grid', [])
        grids = [Grid.objects.get(id=int(i)) for i in gridids]
        return grids

    def before_save(self):
        self.cluster = self.cleaned_data.get('cluster', None)
        #print "add cluster", self.cluster, self.cleaned_data['cluster']
        if self.cluster is not None:
            del self.cleaned_data['cluster']
            self.grid = self.cleaned_data.get('grid', None)
            #print "add grid", self.grid, self.cleaned_data['grid']
            if self.grid is not None:
                del self.cleaned_data['grid']


    def save_model(self, obj, change):
        #===================================================================
        #@transaction.commit_on_success
        def save_func():
            obj.secondary_schedule_host = obj.secondary_schedule_host.strip()
            obj.wideip = "%s.gslb.sinaedge.com" % obj.name.strip()
            obj.interip = "%s.islb.sinaedge.com" % obj.name.strip()

            # 生成旧的grid的配置
            grid_names = []
            if change:
                origin_obj = App.objects.get(id=obj.id)
                grid_names = [g.name for g in origin_obj.grid.all()]

            obj.save()
            if self.cluster is not None:
                obj.cluster = self.cluster
                obj.save()

            if self.grid is not None:
                obj.grid = self.grid
                obj.save()

            if change:
                for grid_name in grid_names:
                    if grid_name not in [g.name for g in obj.grid.all()]:
                        write_grid_config(grid_name)

            #===================================================================
            # if this app has associated with grid in Acceleration, I'll regenereate
            # config for it when someone changed something of this app in Application
            # model
            grid_objs = obj.grid.all()
            for grid_obj in grid_objs:
                write_grid_config(grid_obj.name)
            #===================================================================
        try:
            #===================================================================
            # 如下这些验证的代码之所以不写在form的验证里，是因为form里没法判断是新加还是修改
            # 也不写在save_func里，是因为save_func里如果raise异常，将导致django db的rollback,
            # 并且跳回到了changelist界面
            #===================================================================
            if not change:
                exists_sinaedge_kid = App.objects.filter(sinaedge_kid=obj.sinaedge_kid)

                if obj.is_sinaedge_anti_stealing_link and exists_sinaedge_kid:
                    raise forms.ValidationError("this kid is already exists, you should change another one")
            save_func()

            # 添加gslb, islb域名
            gtmapi.domain_add_cname(obj.wideip, "you.should.change.this") # add default record to domain
            gtmapi.domain_enable(obj.wideip) # add default record to domain
            gtmapi.domain_add_cname(obj.interip, "you.should.change.this") # add default record to domain
            gtmapi.domain_enable(obj.interip) # add default record to domain

        except forms.ValidationError:
            raise
        except Exception,e:
            raise forms.ValidationError(e)

    def delete_model(self, obj):
        #===================================================================
        #@transaction.commit_on_success
        def delete_func():
            # if this app is not in any acceleration, just delete, otherwise
            # we should regenereate grid config
            grid_objs = obj.grid.all()
            obj.delete()
            for grid_obj in grid_objs:
                write_grid_config(grid_obj.name)
        #===================================================================
        try:
            delete_func()
        except Exception, e:
            raise forms.ValidationError(e)

