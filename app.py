from flask import Flask, request, jsonify
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse
import os
import requests

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

cookies = {
    'csrfToken': 'gCJ3QYY5xl4n1QdJg9ET7cVt',
    'browserid': 'xf7hSqn2ZlNm1RllRTeAgAuGk8_3SkSg7CPTY4XqNhJvGrIAAz185B8tmPc=',
    'lang': 'en',
    '_ga': 'GA1.1.845393145.1760981925',
    '_gcl_au': '1.1.1116555085.1760981925',
    '__stripe_mid': '7a25ddc6-2dd5-4c8e-aca8-b0e9e5f93244155de7',
    '__stripe_sid': 'bafdc81e-ed04-4a72-ab0c-d3dfb9753e60b1d31e',
    'ab_sr': '1.0.1_MGRjZTY0NmVjMDY0YjA1NjdlOTJhZjE0ZTc4YTliNzYxY2QzNjAxYWIxN2FkOTI5NWRjNjhhMzE3ODkxYjMwMmJjZDg0YWEyMGEwNTk5NDJmNGIyMjgyNTEyZDFmNDJiNDA0ZTAyZGIzNTk3NTU2YTNkOTA4ZDM2MDdlNzViN2M5YmEyZDJhZjlmMGNiZDdlMmI5NDE1NjAwNjZiOTRmYQ==',
    'ndus': 'Y-FPKK3teHui5DyD7Stn-GQBFkOEQXW-zUW5e9ua',
    '_ga_06ZNKL8C2E': 'GS2.1.s1760982251$o1$g1$t1760982277$j34$l0$h0',
    '__bid_n': '199e8eb7dfe48869674207',
    '_rdt_uuid': '1760981924685.eb66c3a6-8b48-4376-a5f5-0afe26f658b4',
    '_ga_HSVH9T016H': 'GS2.1.s1760981924$o1$g1$t1760983384$j40$l0$h0',
    'ndut_fmt': '3F9315EC006DC9562A3D9EACEF29B553861E48571A3D1FB7A975B582E9073792',
    'g_state': '{"i_l":0,"i_ll":1760983385514,"i_b":"3mb0eOuH2Bu9nN06qFTH69WnFZeop4lpEKQaPowsG4o"}',
    '_rdt_em': ':48e9f13f0b8f611092925eea7ca1a221f243d846f0a3b02be5c3319f3ccdef9a,a23c24a40de49c17f2d128d6d389387f589d57ccd8d970efc28007859f64bc1b,e5bfccebd4c329216bf5e2c68505357a5aaa24ca1479864e83ce78cc88cd99d9',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': '*/*',
    'Connection': 'keep-alive',
}

def find_between(string, start, end):
    start_index = string.find(start) + len(start)
    end_index = string.find(end, start_index)
    return string[start_index:end_index]

async def fetch_download_link_async(url):
    logging.info(f"Starting fetch_download_link_async for URL: {url}")
    try:
        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get(url) as response1:
                logging.info(f"Response 1 status: {response1.status}")
                response_data = await response1.text()
                if response1.status != 200:
                    logging.error(f"Response 1 failed with status {response1.status}: {response_data}")
                    return None
                
                js_token = find_between(response_data, 'fn%28%22', '%22%29')
                log_id = find_between(response_data, 'dp-logid=', '&')
                logging.info(f"Extracted js_token: {js_token}, log_id: {log_id}")

                if not js_token or not log_id:
                    logging.error("Failed to extract js_token or log_id")
                    return None

                request_url = str(response1.url)
                surl = request_url.split('surl=')[1]
                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': request_url,
                    'shorturl': surl,
                    'root': '1'
                }

                async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                    logging.info(f"Response 2 status: {response2.status}")
                    if response2.status != 200:
                        logging.error(f"Response 2 failed with status {response2.status}: {await response2.text()}")
                        return None
                    
                    response_data2 = await response2.json()
                    
                    if 'list' not in response_data2:
                        logging.error(f"Key 'list' not in response_data2: {response_data2}")
                        return None

                    if response_data2['list'][0]['isdir'] == "1":
                        params.update({
                            'dir': response_data2['list'][0]['path'],
                            'order': 'asc',
                            'by': 'name',
                            'dplogid': log_id
                        })
                        params.pop('desc')
                        params.pop('root')

                        async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                            logging.info(f"Response 3 status: {response3.status}")
                            if response3.status != 200:
                                logging.error(f"Response 3 failed with status {response3.status}: {await response3.text()}")
                                return None
                            
                            response_data3 = await response3.json()
                            if 'list' not in response_data3:
                                logging.error(f"Key 'list' not in response_data3: {response_data3}")
                                return None
                            return response_data3['list']
                    return response_data2['list']
    except aiohttp.ClientResponseError as e:
        logging.error(f"Aiohttp client error in fetch_download_link_async: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in fetch_download_link_async: {e}")
        return None

def extract_thumbnail_dimensions(url: str) -> str:
    """Extract dimensions from thumbnail URL's size parameter"""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        size_param = params.get('size', [''])[0]
        
        if size_param:
            parts = size_param.replace('c', '').split('_u')
            if len(parts) == 2:
                return f"{parts[0]}x{parts[1]}"
    except Exception as e:
        logging.warning(f"Could not extract thumbnail dimensions from {url}: {e}")
    return "original"

async def get_formatted_size_async(size_bytes):
    try:
        size_bytes = int(size_bytes)
        if size_bytes >= 1024 * 1024:
            size = size_bytes / (1024 * 1024)
            unit = "MB"
        elif size_bytes >= 1024:
            size = size_bytes / 1024
            unit = "KB"
        else:
            size = size_bytes
            unit = "bytes"
        return f"{size:.2f} {unit}"
    except (ValueError, TypeError) as e:
        logging.warning(f"Error formatting size: {e}")
        return "N/A"

async def format_message(link_data):
    thumbnails = {}
    if 'thumbs' in link_data:
        for key, url in link_data['thumbs'].items():
            if url:
                dimensions = extract_thumbnail_dimensions(url)
                thumbnails[dimensions] = url
    
    file_name = link_data.get("server_filename", "N/A")
    file_size = await get_formatted_size_async(link_data.get("size", 0))
    download_link = link_data.get("dlink", "N/A")
    
    sk = {
        'Title': file_name,
        'Size': file_size,
        'Direct Download Link': download_link,
        'Thumbnails': thumbnails
    }
    return sk

async def fetch_download_link_async2(url):
    logging.info(f"Starting fetch_download_link_async2 for URL: {url}")
    try:
        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get(url) as response1:
                logging.info(f"Response 1 status: {response1.status}")
                response_data = await response1.text()
                if response1.status != 200:
                    logging.error(f"Response 1 failed with status {response1.status}: {response_data}")
                    return None
                
                js_token = find_between(response_data, 'fn%28%22', '%22%29')
                log_id = find_between(response_data, 'dp-logid=', '&')
                logging.info(f"Extracted js_token: {js_token}, log_id: {log_id}")

                if not js_token or not log_id:
                    logging.error("Failed to extract js_token or log_id")
                    return None

                request_url = str(response1.url)
                surl = request_url.split('surl=')[1]

                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': request_url,
                    'shorturl': surl,
                    'root': '1'
                }

                async with session.get('https://www.1024tera.com/share/list', params=params) as response2:
                    logging.info(f"Response 2 status: {response2.status}")
                    if response2.status != 200:
                        logging.error(f"Response 2 failed with status {response2.status}: {await response2.text()}")
                        return None
                        
                    response_data2 = await response2.json()

                    if 'list' not in response_data2:
                        logging.error(f"Key 'list' not in response_data2: {response_data2}")
                        return None

                    files = response_data2['list']

                    if files and files[0]['isdir'] == "1":
                        params.update({
                            'dir': files[0]['path'],
                            'order': 'asc',
                            'by': 'name',
                            'dplogid': log_id
                        })
                        params.pop('desc')
                        params.pop('root')

                        async with session.get('https://www.1024tera.com/share/list', params=params) as response3:
                            logging.info(f"Response 3 status: {response3.status}")
                            if response3.status != 200:
                                logging.error(f"Response 3 failed with status {response3.status}: {await response3.text()}")
                                return None
                            
                            response_data3 = await response3.json()
                            if 'list' not in response_data3:
                                logging.error(f"Key 'list' not in response_data3: {response_data3}")
                                return None
                            files = response_data3['list']

                    file_data = []
                    for file in files:
                        file_info = {
                            "Title": file.get("server_filename"),
                            "Size": await get_formatted_size_async(file.get("size", 0)),
                            "Direct Download Link": file.get("dlink"),
                            "Thumbnails": {}
                        }
                        
                        if 'thumbs' in file:
                            for key, thumb_url in file['thumbs'].items():
                                if thumb_url:
                                    dimensions = extract_thumbnail_dimensions(thumb_url)
                                    file_info["Thumbnails"][dimensions] = thumb_url
                        
                        file_data.append(file_info)

                    return file_data

    except aiohttp.ClientResponseError as e:
        logging.error(f"Aiohttp client error in fetch_download_link_async2: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in fetch_download_link_async2: {e}")
        return None

@app.route('/')
def hello_world():
    response = {
        'status': 'success',
        'message': 'Welcome to the TeraBox Direct Downloader API!',
        'usage': 'To use the API, please use the /api/tera?url= or /api/tbox?url= or /api/proxy?url= endpoints.',
        'api 1 - advance': '/api/tbox?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 2 - standerd': '/api/tera?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 3 - proxy': '/api/proxy?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'help': '/help for more details',
        'contact': '@no_coder_pro'
    }
    return jsonify(response)

@app.route(rule='/api/tera', methods=['GET'])
async def Api():
    try:
        url = request.args.get('url', 'No URL Provided')
        logging.info(f"Received request for /api/tera with URL: {url}")
        link_data = await fetch_download_link_async(url)
        if link_data:
            tasks = [format_message(item) for item in link_data]
            formatted_message = await asyncio.gather(*tasks)
            response = {'ShortLink': url, 'Extracted Info': formatted_message, 'status': 'success'}
        else:
            response = {'status': 'error', 'message': 'Could not extract link info.', 'ShortLink': url}
        return jsonify(response)
    except Exception as e:
        logging.error(f"An error occurred in /api/tera: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'Link': url})

@app.route(rule='/api/tbox', methods=['GET'])
async def Api2():
    try:
        url = request.args.get('url', 'No URL Provided')
        logging.info(f"Received request for /api/tbox with URL: {url}")
        link_data = await fetch_download_link_async2(url)
        if link_data:
            response = {'ShortLink': url, 'Extracted Info': link_data, 'status': 'success'}
        else:
            response = {'status': 'error', 'message': 'No files found or error extracting data.', 'ShortLink': url}
        return jsonify(response)
    except Exception as e:
        logging.error(f"An error occurred in /api/tbox: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'Link': url})

@app.route(rule='/api/proxy', methods=['GET'])
def proxy_api():
    try:
        url = request.args.get('url', 'No URL Provided')
        logging.info(f"Received request for /api/proxy with URL: {url}")
        
        # Headers for the backend API
        proxy_headers = {
            'User-Agent': 'okhttp/5.0.0-alpha.10',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/json; application/json; charset=utf-8',
            'key': 'i094kjad090asd43094@asdj4390945',
        }
        
        # JSON data for the backend API
        json_data = {
            'url': url,
            'folder': '',
            'deviceId': '48eb081d1d5b0afd',
            'token': '1aMnclhhS8tSw0mlyYlEobft0m1BrMI6d8WyEfWfWiLW18T4e9MsyySr4VmUSVYMQ4L76kF8gt2jTZYwKeNC7bGjid6KiWlaEneDiAr7aE8=',
        }
        
        # Make request to backend API
        response = requests.post('https://tera.backend.live/android', headers=proxy_headers, json=json_data)
        
        # Return the response from backend API
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'ShortLink': url,
                'backend_response': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Backend API returned status code: {response.status_code}',
                'ShortLink': url,
                'backend_response': response.text
            })
            
    except Exception as e:
        logging.error(f"An error occurred in /api/proxy: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'ShortLink': url
        })

@app.route(rule='/help', methods=['GET'])
async def help():
    response = {
        'Info': "There are multiple ways to use this API as shown below",
        'usage': 'To use the API, please use the /api/tera?url= or /api/tbox?url= or /api/proxy?url= endpoints.',
        'api 1 - advance': '/api/tbox?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 2 - standerd': '/api/tera?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 3 - proxy': '/api/proxy?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'help': '/help for more details',
        'contact': '@no_coder_pro'
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
