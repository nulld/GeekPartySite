from mod_python import apache
import modpythonhandler


def handler2(req):
	req.content_type = "text/plain"
	req.send_http_header()
	req.write("Hello World!")
	req.write(','.join(req.subprocess_env.keys()))
	req.write(req.subprocess_env["REQUEST_URI"])
	req.write(req.subprocess_env["SCRIPT_NAME"])
	req.write(req.subprocess_env["HTTP_X_FORWARDED_FOR"])
	req.write(req.uri)

	return apache.OK



def handler(req):
	req.subprocess_env['HTTP_X_FORWARDED_FOR'] = 'geekparty.su'
	req.subprocess_env['PATH_INFO'] = req.uri
	return modpythonhandler.handler(req)