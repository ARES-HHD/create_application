#!/usr/bin/env python
# encoding: utf-8
# vim:fileencoding=utf-8
#
# Copyright here
#
""" module summary comment here """



from admin_base import AdminNew
from commons import *
from django.db import transaction
from django.db.models import Q, Count, NOT_PROVIDED
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.log import getLogger
from edge_console.forms_model import *
from edge_console.models import *

from math import ceil


logger = getLogger('except')


class App_AdminNew(AdminNew):
    def __init__(self):
        AdminNew.__init__(self, 'app', App_CheckForm, 'apps')
        self.search_fields = ('name', 'user__username',
                              'product__name',
                              'product__productline__name',
                              'grid__name',
                              'origins',
                              'channels')
        self.manytomany_fields = ['cluster', 'grid']
        self.list_display = (
                             ('user', 7),
                             # ('productline', 7),
                             ('name', 13),
                             ('grid_str', 7),
                             ('jira_url', 7),
                             ('status', 7),
                             ('origins', 12),
                             ('channels', 15),
                             ('check_url', 10),
                             ('interip', 5),
                             ('wideip', 5),
                             ('desc', 10),
                             )
        self.actions = (
                        ('application_save', 'synchronous', 'eye-open'),
                        )

    def show_all(self, request):
        """  显示所有model
        Args:
            modelid: 数据库中记录的id
        """

        model_datas = []
        submit_type = 'create'
        page_n = 0

        cookie = request.COOKIES.get('list_display_show_items_%s' % self.model_name,
                                     "")
        cookie_list_display = cookie.split()

        # 搜索
        search_text = ''
        search_field = ''
        if request.method == 'POST':
            search_text = request.POST.get('search_text', '')  #.strip()
            search_field = request.POST.get('search_field', '').strip()

            cookie_list_display = [str(i) for i, e in enumerate(self.list_display)
                                   if request.POST.get('list_display_show_items_%s' % e[0], None)]

            page_n = request.POST.get('page', 0)
            try:
                page_n = int(page_n)
            except:
                page_n = 0

        edit_id = request.GET.get('id', 0)
        try:
            edit_id = int(edit_id)
        except:
            edit_id = 0
        page_show_edit = False
        if edit_id:
            models, total_in_page = self.model.objects.filter(id=edit_id), 1
            page_max = 0
            page_show_edit = True
            search_context = {
                'search_text': search_text,
                'search_fields': self.search_fields,
                'search_field': search_field,
                }
        else:
            # 获取要显示的结果数据, 总数
            models, total_in_page, search_context = self.search_model_datas(
                request, page_n, search_text, search_field)
            page_max = int(ceil(total_in_page/(self.N_PER_PAGE + 0.0)))

        page_choices = get_page_choices(page_n, page_max)

        for model_obj in models:
            model_datas += [self.get_data_from_obj(model_obj)]

        list_display_context = {}
        for i, e in enumerate(self.list_display):
            list_display_context["list_display_show_items_%s" % e[0]] = False
            if not cookie_list_display or str(i) in cookie_list_display:
                list_display_context["list_display_show_items_%s" % e[0]] = True


        fake_list_display = copy.deepcopy(self.list_display)
        if cookie_list_display:
            fake_list_display = [e for i, e in enumerate(self.list_display)
                                 if str(i) in cookie_list_display]

        render_context = {
                'model_actions': self.actions,
                'model_title_actions': self.title_actions,
                'model_all_list_display': self.list_display,
                'model_list_display': fake_list_display,
                'sub_action_children': self.sub_action_children,

                'page_show_edit': page_show_edit,
                'admin_tmpl_path': self.admin_tmpl_path,
                'group': self.group,

                'model': self.model_name,
                'model_url': self.admin_name, # model_url支持非model name做url路径
                'model_datas': model_datas,
                'model_new_data_for_head': self.get_group_create_data(request),

                'page_n': page_n,
                'page_pre': page_n == 0 and '-1' or page_n - 1,
                'page_next': page_n == page_max-1 and '-1' or page_n +1,
                'page_choices': page_choices,
                'total_in_page': total_in_page,
                'uniqid': '1',
                'title_action_is_hide': self.title_action_is_hide,
                'title_is_hide': self.title_is_hide,

                'tmpl_show_one' :self.tmpl_show_one,
                'tmpl_edit_show_one' :self.tmpl_edit_show_one,
                'tmpl_edit_after_delete_one' :self.tmpl_edit_after_delete_one,
                'tmpl_show_all' :self.tmpl_show_all,
                'tmpl_all_data' :self.tmpl_all_data,
                'tmpl_alert_msg' :self.tmpl_alert_msg,
                'list_display_context': list_display_context
                }

        edit_context = self.get_edit_context()
        show_all_context = self.get_show_all_context(models)
        render_context = dict(render_context.items() +
                              edit_context.items() +
                              show_all_context.items() +
                              search_context.items())


        response = render_to_response(self.tmpl_show_all, render_context,
                                  context_instance=RequestContext(request))

        if cookie_list_display:
            path = request.META.get('PATH_INFO', '/')
            path = path.replace('show/', '')
            response.set_cookie('list_display_show_items_%s' % self.model_name,
                                ' '.join(cookie_list_display),
                                path=path)

        # response.set_cookie(key, value,
        #                     path="/",
        #                     max_age=max_age,
        #                     expires=expires,
        #                     domain=settings.SESSION_COOKIE_DOMAIN,
        #                     secure=settings.SESSION_COOKIE_SECURE or None)
        return response

    def show_one(self, request, modelid):
        """  显示modelid一条数据,为table中的一行
        Args:
            modelid: 数据库中记录的id
        """

        modelid = int(modelid)
        models = self.model.objects.filter(id=modelid)
        if not models:
            return HttpResponse('')
        else:
            submit_type = 'edit_show'
            model_obj = models[0]
            one_data = self.get_data_from_obj(model_obj)

        cookie = request.COOKIES.get('list_display_show_items_%s' % self.model_name, "")
        cookie_list_display = cookie.split()
        fake_list_display = copy.deepcopy(self.list_display)
        if cookie_list_display:
            fake_list_display = [e for i, e in enumerate(self.list_display)
                                 if str(i) in cookie_list_display]

        show_one_context = self.get_show_one_context(model_obj)
        render_context = {
                'admin_tmpl_path': self.admin_tmpl_path,
                'group': self.group,
                'model': self.model_name,
                'model_url': self.admin_name,   # model_url支持非model name做url路径
                'model_all_list_display': self.list_display,
                'model_list_display': fake_list_display,
                'model_actions': self.actions,
                'sub_action_children': self.sub_action_children,
                'submit_type_button': submit_type,
                'one_model_data': one_data,

                'title_action_is_hide': self.title_action_is_hide,
                'title_is_hide': self.title_is_hide,
                }
        render_context = dict(show_one_context.items() + render_context.items())
        return render_to_response(self.tmpl_show_one, render_context,
                                  context_instance=RequestContext(request))

    @transaction.commit_manually
    def delete(self, request, modelid):
        """  删除model
        Args:
            modelid: 数据库中记录的id
        """

        modelid = int(modelid)
        cleaned_data = {}
        ccf = self.form(modelid, cleaned_data)
        try:
            ccf.delete()
        except Exception, e:
            transaction.rollback()
            return render_to_response(self.tmpl_edit_after_delete_one, {
                    'result': e
                    }, context_instance=RequestContext(request))
        transaction.commit()
        return HttpResponse('')     # ok

    @transaction.commit_manually
    def add_modify(self, request, modelid):
        """  处理添加/修改请求
        Args:
            modelid: 数据库中记录的id
        """

        modelid = int(modelid)
        if request.method == 'POST':
            model_error, modelid = self.do_save_form(request, modelid)

            if model_error:
                respons = self.edit_show(request, modelid, last_post=request.POST, error_msg=model_error)
                transaction.rollback()
                return respons

            transaction.commit()

        return HttpResponseRedirect('/%s/%s/show_one/%d/' % (self.group, self.admin_name, modelid))


    def edit_show(self, request, modelid, last_post=None, error_msg=None):
        """  显示form编辑框,包含modelid的数据
        Args:
            modelid: 数据库中记录的id
            model_obj: 出错时,缓存的之前的form
            error_msg: 出错信息
        """

        user_status = request.user.is_superuser
        #current_user = request.user.username
        modelid = int(modelid)
        model_obj = None
        if not model_obj:
            models = self.model.objects.filter(id=modelid)
            if models:
                model_obj = models[0]

        if not model_obj:
            submit_type = 'create'
            # 获取创建的初始值
            cdata = self.get_group_create_data(request)
            cdata['admin_new_inline_status'] = 'to-add'
            current_user = request.user.username
        else:
            submit_type = 'edit_show'
            cdata = self.get_data_from_obj(model_obj)
            cdata['admin_new_inline_status'] = 'to-modify'
            print cdata['user']['value']
            current_user = cdata['user']['value'] 

        if error_msg:
            model_error = error_msg
            for k, errormsg in model_error.items():
                if k not in cdata: continue
                #print 'error' , k, errormsg
                cdata[k]['class'] = 'error'
                cdata[k]['errormsg'] = errormsg
        if last_post:
            self.restore_last_post(cdata, last_post)

        render_context = {
                'admin_tmpl_path': self.admin_tmpl_path,
                'group': self.group,
                'model': self.model_name,
                'model_url': self.admin_name, # model_url支持非model name做url路径
                'model_list_display': self.list_display,

                'submit_type_button': submit_type,
                'one_model_data': cdata,
                'error_msg': error_msg,
                'user_status': user_status,
                'current_user': current_user,
                }
        edit_context = self.get_edit_context(model_obj, cdata)
        render_context = dict(render_context.items() + edit_context.items())

        return render_to_response(self.tmpl_edit_show_one, render_context, context_instance=RequestContext(request))

    # 获取要显示的结果数据, 总数
    def search_model_datas(self, request, page_n, search_text, search_field):
        """ edge_console.service.ApplicationService中有相同逻辑的查找方法 """
        Q_results = None
        current_user = request.user.username

        if search_text:
            for field in [f for f in self.search_fields if f.find(search_field) >= 0]:
                kargs = {}
                if search_text.startswith('~'):
                    kargs[field + "__iregex"] = search_text[1:]
                elif search_text.startswith('%'):
                    kargs[field + "__iendswith"] = search_text[1:]
                elif search_text.endswith('%'):
                    kargs[field + "__istartswith"] = search_text[:-1]
                else:
                    kargs[field + "__contains"] = search_text
                if not Q_results:
                    Q_results = Q(**kargs)
                else:
                    Q_results |= Q(**kargs)

        if not request.user.is_superuser:
            if Q_results:
                models = self.model.objects.filter(Q_results, Q(user__username=current_user)|Q(user__username='admin')).order_by('-id').distinct('id')[self.N_PER_PAGE * page_n: self.N_PER_PAGE * (page_n+1)]
                total_in_page = self.model.objects.filter(Q_results, Q(user__username=current_user)|Q(user__username='admin')).count()
            else:
                models = self.model.objects.filter(Q(user__username=current_user)|Q(user__username='admin')).order_by('-id')[self.N_PER_PAGE * page_n: self.N_PER_PAGE * (page_n+1)]  #
                total_in_page = self.model.objects.filter(Q(user__username=current_user)|Q(user__username='admin')).count()
        else:
            if Q_results:
                models = self.model.objects.filter(Q_results).order_by('-id').distinct('id')[self.N_PER_PAGE * page_n: self.N_PER_PAGE * (page_n+1)]
                total_in_page = self.model.objects.filter(Q_results).count()
            else:
                models = self.model.objects.all().order_by('-id')[self.N_PER_PAGE * page_n: self.N_PER_PAGE * (page_n+1)]  #
                total_in_page = self.model.objects.all().count()

        search_context = {
                'search_text': search_text,
                'search_fields': self.search_fields,
                'search_field': search_field,
                }

        return models, total_in_page, search_context

    # 获取model中的字段数据, 并以字典形式返回
    def get_value_from_model(self, obj=None):
        """参考了django ModelForm获取model fields的方法
        """
        data_from_obj = {}
        opts = self.model._meta
        for f in opts.fields + opts.many_to_many:
            default = getattr(f, 'default', '')
            if default == NOT_PROVIDED:
               default = ''
            name = getattr(f, 'name')
            try:
                value = getattr(obj, name)
            except Exception, e:
                value = default      # 如果取不到value, 则取''

            if name in ['id', 'secondary_schedule_visit_threshold', 'jira_url']:
                continue
            if name == 'grid':
                grid = value.all()
                continue
            if name == 'cluster':
                cluster = value.all()
                continue
            if name == 'name':
                app_name = value

            data_from_obj[name] = value

        return data_from_obj, grid, cluster, app_name

    def get_value_from_obj(self, s):
        cleaned_data, grid, cluster, app_name = self.get_value_from_model(s)
        result = Application.objects.filter(name=app_name)
        if not result:
            app = Application(**cleaned_data)
            app.save()
            app.grid = grid
            app.cluster = cluster
            app.save()
            return_message = ['Success!']
        else:
            raise Exception("the app name must unique,please change the app name!")
        return return_message


    def application_save(self, id):

        queryset = self.model.objects.filter(id=id)
        model_obj = queryset[0]
        return_message = self.get_value_from_obj(model_obj)
        return '<br>'.join(return_message), ""


    # 编辑时需要的context
    def get_edit_context(self, model_obj=None, dic_data=None):
        usernames = [c.username for c in User.objects.all()]
        usernames.sort()
        products = [c.name for c in Product.objects.all()]
        products.sort()

        # 已被选中的clusters
        exsist_clusters = []
        if model_obj:
            for c in model_obj.cluster.all():
                exsist_clusters += [(c.id, c.name)]

        # 未被选中的clusters
        clusters = []
        for c in get_all_dsa_clusters():
            if (c.id, c.name) not in exsist_clusters:
                clusters += [(c.id, c.name)]
        # 已被选中的grids
        exsist_grids = []
        if model_obj:
            for c in model_obj.grid.all():
                exsist_grids += [(c.id, c.name)]

        # 未被选中的grids
        grids = []
        for c in Grid.objects.all().order_by('is_vgrid', 'name'):
            if (c.id, c.name) not in exsist_grids:
                grids += [(c.id, c.name)]
        CONVERT_HOST_CHOICES = (
            (0, 'NONE'),
            (1, 'CONVERT_HOST'),
            (2, 'NEGATIVE_CACHE'),
        )
        DRAGGING_ON_MISS_CHOICES = (
            (0, 'NONE'),
            (1, 'mp4'),
            (2, 'flv'),
            (3, 'mp4+flv'),
        )

        return {
            'manytomany__fields': self.manytomany_fields,
            'manytomany_keys': { 'grid': grids,
                                 'cluster': clusters,
                                 },
            "convert_hostnames": CONVERT_HOST_CHOICES,
            "enable_dragging_on_missnames": DRAGGING_ON_MISS_CHOICES,
            'products': products,
            'usernames': usernames,
            }


    # 获取obj中的数据, 并以字典形式返回
    def get_data_from_obj(self, c):
        """生成application的数据,供template使用
        """
        cdata = self.get_data_from_model(c)

        clusters = [(int(i['id']), i['name']) for i in c.cluster.values('id', 'name')]
        cdata['cluster']['value'] = clusters
        cdata['cluster']['cluster'] = ','.join([name for id, name in clusters])
        grids = [(int(i['id']), i['name']) for i in c.grid.values('id', 'name')]
        cdata['grid']['value'] = grids
        cdata['grid']['grid'] = ','.join([name for id, name in grids])

        cdata['convert_host']['show_type'] = 'show_enum'
        cdata['enable_dragging_on_miss']['show_type'] = 'show_enum'
        cdata['grid_str'] = {'value': cdata['grid']['grid'], # for list_display
                             'class': cdata['grid']['class'],
                             'verbose_name': cdata['grid']['verbose_name'],
                             'help_text': cdata['grid']['help_text'],
                             'show_type': cdata['grid']['show_type'],
                             'errormsg': cdata['grid']['errormsg']
                             }


        cdata['productline'] = {'value': "%s-%s" % (c.product.productline.name, c.product.name),
                             'class': '',
                             'verbose_name': u'产品',
                             'help_text': '',
                             'show_type': cdata['grid']['show_type'],
                             'errormsg': '',
                             }

        return cdata

    # 决定创建时的预设值, 并以字典形式返回
    def get_group_create_data(self, request):
        cdata = self.get_data_from_model()
        cdata['id']      = 0
        cdata['grid_str'] = {'value': "",
                             'class': cdata['grid']['class'],
                             'verbose_name': cdata['grid']['verbose_name'],
                             'help_text': cdata['grid']['help_text'],
                             'show_type': cdata['grid']['show_type'],
                             'errormsg': cdata['grid']['errormsg']
                             }
        return cdata

    def model_action(self, request, action, modelid):
        """  执行actions
        Args:
            modelid: 数据库中记录的id
        """

        if not request.user.is_staff:
            return HttpResponse('Access Denied!')

        modelid = int(modelid)

        result = u"OK!"
        alert_type = "alert-success"
        result_js = ""
        try:
            action_fun = getattr(self, action)
            result_title, result_js = action_fun(modelid)
        except Exception, e:
            logger.exception(u"model_action fail: %s" % e)
            result = e
            alert_type = "alert-error"
            result_title = u" Run %s ERROR" % (action)
        return render_to_response(self.tmpl_alert_msg, {
                'result_title': result_title,
                'result': result,
                'result_js': result_js,
                'alert_type': alert_type,
                }, context_instance=RequestContext(request))

    # 出错时用上次POST值
    def restore_last_post(self, cdata, last_post, fake_str=''):
        for key, data in cdata.items():
            fake_key = key + fake_str
            if fake_key in last_post:

                if type(data) != type({}):
                    cdata[key] = last_post[fake_key]

                elif key == "cluster":
                    data['value'] = [(i.id, i.name) for i in
                                     Cluster.objects.filter(id__in=last_post.getlist(fake_key))]
                elif key == "grid":
                    data['value'] = [(i.id, i.name) for i in
                                     Grid.objects.filter(id__in=last_post.getlist(fake_key))]
                else:
                    data['value'] = last_post[fake_key]


