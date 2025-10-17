from flask import Flask, request, jsonify
from TeraboxDL import TeraboxDL

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to the Terabox Downloader API!",
        "usage": "Send a GET request to /api/tbox with a 'url' query parameter containing the Terabox link.",
        "example": "/api/tbox?url=https://terabox.com/s/1kpYz6J8xalpQtoDk4DH8Aw",
        "author": "Mahir Labib",
        "contact": "https://t.me/no_coder_pro"
    })

@app.route('/api/tbox', methods=['GET'])
def get_file_info():
    terabox_url = request.args.get('url')
    if not terabox_url:
        return jsonify({"error": "url parameter is required"}), 400

    # The cookie can be made more dynamic, e.g., passed as a header
    cookie = "lang=en; ndus=YvVzggYteHuiMBvH0QNQzXPqMn2wEcdOv03qsEvU"
    
    try:
        terabox = TeraboxDL(cookie)
        file_info = terabox.get_file_info(terabox_url)

        if "error" in file_info:
            return jsonify({"error": file_info["error"]}), 400
        
        return jsonify(file_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
