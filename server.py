import os
import re
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

subjects = os.listdir('subjects')
subjects.sort()
subjects_option = ''.join(['<option value="%s">%s</option>' %
                           (subject, subject) for subject in subjects])
times = 0


def find_keyword(directory, pattern):
    result = ''
    global times
    times = times + 1
    with open('times.txt', 'w') as times_file:
        times_file.write(str(times))
    for dirpath, dirnames, filenames in os.walk(directory):
        filenames.sort()
        for filename in filenames:
            if filename[0] == '.':
                os.system('rm -f %s/%s' % (dirpath, filename))
            try:
                with open(dirpath + os.sep + filename) as file:
                    file_content = file.read().split('\n')
                    for file_line in file_content:
                        tmp = re.findall(pattern, file_line)
                        if len(tmp) > 0:
                            result = result + '<p>' + \
                                filename.split('.')[0][5:] + \
                                ':' + file_line + '<p>'
            except:
                pass
    return result


class LiniantiHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('linianti.html', subjects_option=subjects_option,
                    keyword='', result='')

    def post(self):
        subject_selected = self.get_argument('subject')
        subjects_option_selected = ''
        for subject in subjects:
            if subject == subject_selected:
                subjects_option_selected = subjects_option_selected + \
                    '<option value="%s" selected>%s</option>' % (
                        subject, subject)
            else:
                subjects_option_selected = subjects_option_selected + \
                    '<option value="%s">%s</option>' % (subject, subject)
        keyword = self.get_argument('keyword')
        result = find_keyword('subjects/%s' % (subject_selected), keyword)
        self.render('linianti.html', subjects_option=subjects_option_selected,
                    keyword=keyword, result=result)


class LibraryHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('library.html', userID='', passWord='', devID='', response='')

    def post(self):
        userID = self.get_argument('userID')
        devID = self.get_argument('devID')
        passWord = self.get_argument('passWord')
        self.render('library.html', userID=userID, passWord=passWord, devID=devID, response=self.response(userID, passWord, devID))

    def response(self, userID, passWord, devID):
        info = json.load(open('json/activate.json'))
        seat = json.load(open('json/seat.json'))
        if devID == "":
            try:
                info.pop(userID)
                json.dump(info, open('json/activate.json', 'w'))
            except:
                pass
            return 'alert("停止预定！")'
        else:
            try:
                int(userID)
                int(devID)
                info[userID] = {}
                info[userID]['devID'] = seat["%03d" % (int(devID))]
                info[userID]['passWord'] = passWord
                json.dump(info, open('json/activate.json', 'w'))
                return 'alert("提交成功！")'
            except:
                return 'alert("输入错误！")'


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    #app.add_handlers(r'^lib.*?$', [(r'/', LibraryHandler), ])
    app.add_handlers(r'^lin.*?$', [(r'/', LiniantiHandler), ])
    #app.add_handlers(r'^.*?$', [(r'/', LibraryHandler), ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()
