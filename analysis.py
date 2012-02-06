#coding=utf-8
import os, sys
import datetime
import operator
import MySQLdb


"""
Nignx  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for" "$request_time"';
"""

html_template = """
<html>
   <head>
      <title>Wiyun Request-log-analyzer report</title><style type="text/css">
        body {
        	font: normal 11px auto "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
        	color: #4f6b72;
        	background: #E6EAE9;
        	padding-left:20px;
        	padding-top:20px;
        	padding-bottom:20px;
        }

        a {
        	color: #c75f3e;
        }

        .color_bar {
          border: 1px solid;
          height:10px;
        	background: #CAE8EA;
        }

        #mytable {
        	width: 760px;
        	padding: 0;
        	margin: 0;
        	padding-bottom:10px;
        }

        caption {
        	padding: 0 0 5px 0;
        	width: 700px;
        	font: italic 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
        	text-align: right;
        }

        th {
        	font: bold 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
        	color: #4f6b72;
        	border-right: 1px solid #C1DAD7;
        	border-bottom: 1px solid #C1DAD7;
        	border-top: 1px solid #C1DAD7;
        	letter-spacing: 2px;
        	text-transform: uppercase;
        	text-align: left;
        	padding: 2px 2px 2px 2px;
        	background: #CAE8EA url(images/bg_header.jpg) no-repeat;
        }

        td {
        	font: bold 11px "Trebuchet MS", Verdana, Arial, Helvetica, sans-serif;
        	border-right: 1px solid #C1DAD7;
        	border-bottom: 1px solid #C1DAD7;
        	background: #fff;
        	padding: 6px 6px 6px 12px;
        	color: #4f6b72;
        }

        td.alt {
        	background: #F5FAFA;
        	color: #797268;
        }
        </style>
   </head>

   <body>
            <h1>Wiyun Api Request-log-analyzer summary report</h1>
            %s
    </body>
</html>
"""

table_head_template = """<table id="mytable" cellspacing="0">
<tbody>
%s
</tbody>
</table>
"""

table_content_template = """
<tr>
    <td class="alt"><font><font>%s</font></font></td>
    <td class="alt"><font><font class="">%s</font></font></td>
    <td class="alt"><div class="color_bar" style="width:%s%%;"></div></td>
</tr>
"""

summery_sql = """insert into summery(`total_reqs`,`uniq_ips`,`flow_rate`,`date`) values(%s,%s,%s,'%s') """
info_sql = """insert into info(`type`,`key`,`value`,`date`) values(%s,'%s',%s,'%s') """
summery_select = """SELECT `total_reqs`,`uniq_ips`,`date` FROM summery order by date desc limit %s"""
max_summery = """SELECT max(`total_reqs`),max(`uniq_ips`) FROM summery"""
delete_no_use = "delete from %s where date='%s'"

_db = None
db_user = "root"
db_name = "apilog"
db_passwd = "bxjt@wiyun"

db_user = "root"
db_name = "apilog"
db_passwd = ""

def get_str_date():
    return datetime.datetime.now().strftime("%Y/%m/%d")


def connect():
    global _db
    _db = MySQLdb.connect(user=db_user, db=db_name, passwd=db_passwd)


def excute_sql(sql, args):
    global _db
    if not _db:
        connect()

    c = _db.cursor()
    try:
        esql = sql % args
        print "excute:", esql
        c.execute(esql)
        _db.commit()
    except Exception, e:
        print e


def delete_sql(sql, args):
    excute_sql(sql, args)


def insert_sql(sql, args):
    excute_sql(sql, args)


def select_sql(sql, args):
    global _db
    if not _db:
        connect()

    c = _db.cursor()
    esql = sql % args
    c.execute(esql)
    data = c.fetchall()
    return data


files = ["api.access.log100", "api.access.log101"]
files_len = len(files)
top_access_api = "cat %s |  awk '{print $7} ' |  awk -F'?' '{print $1}' |sort  |uniq -c | sort -r -n| head -n 10"
top_access_ip = "cat %s |  awk '{print $1} ' |  awk -F'?' '{print $1}' |sort  |uniq -c | sort -r -n| head -n 10"
top_access_time = "cat %s | awk '{print $4}'|awk -F'/' '{print $3}'|awk -F':' '{print $2}'|sort|uniq -c|head -n 24"

top_uniq_ips = "cat %s |  awk '{print $1} ' |  awk -F'?' '{print $1}' |sort  |uniq|  wc -l"
top_total_reqs = "cat %s | wc -l"
top_flow_rate = "cat %s| awk '{ SUM += $10} END { print SUM}'"

top_network = "cat %s|awk '{print $13}'|sort|uniq -c|sort -r -n |head -n 10"
top_status = "cat %s|awk '{print $9}'|sort|uniq -c|sort -r -n |head -n 10"

top_game = "cat %s|awk '{print $12}'|sort|uniq -c|sort -r -n |head -n 100 "
top_commands = [top_access_api, top_access_ip, top_access_time, top_status, top_network, top_game]

top_total_delay = """cat %s|grep %s| awk '{print $NF}'| awk -F'"' 'BEGIN{total=0}{total+=$2}END{print total}'"""

TypeRequest = 1
TypeIp = 2
TypeHour = 3
TypeGame = 4
TypeStatus = 5
TypeNetwork = 6
TypeDelay = 7
TYPES = [TypeRequest, TypeIp, TypeHour, TypeStatus, TypeNetwork, TypeGame, TypeDelay]

HEADERS = ["<h2><font><font class="">Top API Daily Total Reqs</font></font></h2> ",
           "<h2><font><font class="">Top API Daily Total IPs</font></font></h2> ",
           "<h2><font><font class="">Top API Daily Hours</font></font></h2> ",
           "<h2><font><font class="">Top API Daily Status</font></font></h2> ",
           "<h2><font><font class="">Top API Daily Network</font></font></h2> ",
           "<h2><font><font class="">Top API Daily Game</font></font></h2> ", ]

def merge(data):
    if not data:
        return 0, {}

    total = 0
    data_max = 0
    dic = {}
    keys = []
    #print type(data),len(data)
    for d in data:
        if d:
            datas = d.strip().split()
            if len(datas) == 2:
                count = int(datas[0])
                key = datas[1]
                if key == '"-"':
                    continue
                key = str(key).strip()

                dic.setdefault(key, 0)
                dic[key] += count
                total += count

                if count > data_max:
                    data_max = count

                if key not in keys:
                    keys.append(key)

    return data_max * files_len, total, dic, keys


def run(path, out_path, date=None):
    data_dic = {}
    total_reqs = 0
    uniq_ips = 0
    flow_rate = 1
    rate = 100.0
    if not date:
        date = get_str_date()

    for f in files:
        try:
            for command, _type in zip(top_commands, TYPES):
                data_dic.setdefault(_type, [])
                for t in os.popen(command % (path + "/" + f)).read().strip().split("\n"):
                    data_dic[_type].append(t)

            total_reqs += int(os.popen(top_total_reqs % (path + "/" + f)).read().strip())
            uniq_ips += int(os.popen(top_uniq_ips % (path + "/" + f)).read().strip())
            flow_rate += int(os.popen(top_flow_rate % (path + "/" + f)).read().strip())
        except Exception, e:
            print "error:", e


    #clear data
    delete_sql(delete_no_use, ('summery', date))
    delete_sql(delete_no_use, ('info', date))

    tables = "<h2>Request summary %s</h2> " % (date)
    tables += "<h2><font><font class="">Total Requst: %s </font></font></h2>" % (total_reqs)
    tables += "<h2><font><font class="">Uniq IPs: %s </font></font></h2>" % (uniq_ips)
    tables += "<h2><font><font class="">Flow Rate: +%.2fM </font></font></h2>" % (float(flow_rate) / 1024 / 1024)

    print "total_reqs,uniq_ips", total_reqs, uniq_ips, flow_rate
    insert_sql(summery_sql, (total_reqs, uniq_ips, flow_rate, date))

    #generate max daily
    data = select_sql(summery_select, (10))
    max_data = select_sql(max_summery, ())
    if max_data:
        tables += ""
        day_conent = ""
        for d in data:
            day_conent += table_content_template % (d[2], d[0], float(d[0]) / int(max_data[0][0]) * rate)
        tables += table_head_template % day_conent

        tables += "<h2><font><font class="">API Daily Uniq IPs</font></font></h2> "
        day_conent = ""
        for d in data:
            day_conent += table_content_template % (d[2], d[1], float(d[1]) / int(max_data[0][1]) * rate)
        tables += table_head_template % day_conent

    #generate html
    for _type, h in zip(TYPES, HEADERS):
        content = ""
        data_max, total, api_dic, keys = merge(data_dic[_type])
        tables += h
        for key in keys:
            value = api_dic[key]
            insert_sql(info_sql, (_type, key, value, date))

            if _type == TypeRequest:
                delay = 0
                for f in files:
                    try:
                        delay += float(os.popen(top_total_delay % (path + "/" + f, key)).read().strip())
                    except Exception, e:
                        print "!", e
                        
                insert_sql(info_sql, (TypeDelay, key, delay, date))
                content += table_content_template % (
                    key, "ResCount:%s ,TotalSec:%s, AverageSec:%.3fs" % (value, delay, float(delay) / float(value)),\
                    float(value) / data_max * rate)
            else:
                content += table_content_template % (key,  value,float(value) / data_max * rate)
                

        tables += table_head_template % content

    r = html_template % tables
    write_path = os.path.join(out_path, "index.html")
    print "write_path", write_path

    fs = open(write_path, 'w')
    fs.write(r)

    fs.close()


if __name__ == "__main__":
    #run(sys.argv[1], sys.argv[2], sys.argv[3])
    run("/Users/liuzheng/Desktop/log", "/Users/liuzheng/Desktop/log")

