//model_add_one.js
function load_{{model}}_0(id)
{
    var xmlhttp;
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.getElementById("{{model}}data_create_" + id).outerHTML += xmlhttp.responseText;

            var newdiv = document.createElement('div');
            newdiv.innerHTML = xmlhttp.responseText;

            var scripts = newdiv.getElementsByTagName('script');
            for (var i=scripts.length-1; i >= 0; i--) {
                eval(scripts[i].innerHTML);
                //console.log(scripts[i].innerHTML);
            }
        }
    }
    xmlhttp.open("GET","/{{group}}/{{model_url}}/edit_show/0/?id=" + id, false);
    xmlhttp.setRequestHeader("Cache-Control", "no-cache");
    xmlhttp.send();
}


//{{model}}_show_one.js
function load_{{model}}(id, fakeid)
{
    var xmlhttp;
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.getElementById("{{model}}data_" + id + "_" + fakeid).outerHTML=xmlhttp.responseText;
            var newdiv = document.createElement('div');
            newdiv.innerHTML = xmlhttp.responseText;

            var scripts = newdiv.getElementsByTagName('script');
            for (var i=scripts.length-1; i >= 0; i--) {
                eval(scripts[i].innerHTML);
                //console.log(scripts[i].innerHTML);
            }

        }
    }
    xmlhttp.open("GET","/{{group}}/{{model_url}}/edit_show/" + id + "/",true);
    xmlhttp.send();
}


function load_{{model}}_show(id, fakeid)
{
    var xmlhttp;
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.getElementById("{{model}}data_" + id + "_" + fakeid).outerHTML=xmlhttp.responseText;
        }
    }
    xmlhttp.open("GET","/{{group}}/{{model_url}}/show_one/" + id + "/",true);
    xmlhttp.send();
}

function load_{{model}}_delete(id, fakeid)
{

    bootbox.dialog(
        "确定删除?",
        [{
            "label" : "Cancel",
            "class" : "btn",
        },{
            "label" : "Delete",
            "class" : "btn-danger",
            "callback": function() {

                var xmlhttp;
                if (window.XMLHttpRequest)
                {// code for IE7+, Firefox, Chrome, Opera, Safari
                    xmlhttp=new XMLHttpRequest();
                }
                else
                {// code for IE6, IE5
                    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
                }
                xmlhttp.onreadystatechange=function()
                {
                    if (xmlhttp.readyState==4 && xmlhttp.status==200)
                    {
                        if (xmlhttp.responseText == ""){
                            document.getElementById("{{model}}data_" + id + "_" + fakeid).outerHTML = "";
                        }
                        else{
                            document.getElementById("global_alert_slot").innerHTML = xmlhttp.responseText;
                        }
                    }
                }
                xmlhttp.open("GET","/{{group}}/{{model_url}}/delete/" + id + "/",true);
                xmlhttp.send();
            }
        }],
        {
            "animate": false
        });

}



function load_{{model}}_action(action, id)
{
    var xmlhttp;
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            bootbox.dialog(
                xmlhttp.responseText,
                [{
                    "label" : "Cancel",
                    "class" : "btn",
                },{
                    "label" : "Ok",
                    "class" : "btn-danger",
                    "callback": function() {
                        document.getElementById("global_alert_slot").innerHTML = xmlhttp.responseText;
                        eval("__ok_callback();");
                    }
                }],
                {
                    "animate": false
                });
        }
    }
    xmlhttp.open("GET","/{{group}}/{{model_url}}/action_" + action + "/" + id + "/",true);
    xmlhttp.send();
}
