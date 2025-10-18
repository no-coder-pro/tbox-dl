from flask import Flask, request, jsonify
import aiohttp
import asyncio
import logging
from urllib.parse import parse_qs, urlparse
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Main cookies - এই কুকি থেকে সব এন্ডপয়েন্ট ব্যবহার করবে
cookies = {
    'PANWEB': '1',
    'browserid': 'VYoG01yTo8XEnWfQsmH_3Flb4ljJ5LqlwtMquGl6ENACPgB2a_qT83Twm4Y=',
    'lang': 'en',
    'TSID': 'evoTWjUAz6HXsaWUbEM683YybAar0KTl',
    '__bid_n': '199e8eb7dfe48869674207',
    '_ga': 'GA1.1.739913387.1760549396',
    'ndus': 'Y4gNL3EteHuiltx5aeJ97I7g6uzMteYmPV6_woT1',
    '_gcl_au': '1.1.577111259.1760553404',
    'csrfToken': '16Ocjy8ahtuFQS46t-Jo9MYZ',
    'ab_sr': '1.0.1_M2RjMzk5NDE4ODg3NjJjOWEwMDA0ZGJiMTQwYjg5NDQ3YTFlYzNhMDNjNDgwMTk5NWU5MmU0YmI0OGY5MTE3MDNjYTlhNzgxNTdhNzM4OGI5MDQ0NjhiODZlZWI1YzY1MGEwMThjNGZhNjJhYTIzMWMyNWFiMmMxNWQ5MDJmODFlMmExYjczYTQwMTBkZTRiMjU5NjQ1ODAzN2I2ZDJlZA==',
    'ab_ymg_result': '{"data":"9d8c58e472ab1e2ecf868154994b91b153e218cc87ada4fb59bd3ddf893175064556389c6d7fd6230a1bf42fd60568c51718d2b223c7a6b05540a343d2d0eec882b72a055affef864046d6b735b37717d0506a27242c31e8df6fa777012d19e91232c7985e7cd9c85e399347f9b0dd6f2348c0c8e6c2a2c919329de84e922041","key_id":"66","sign":"5832272b"}',
    '_ga_06ZNKL8C2E': 'GS2.1.s1760752468$o6$g0$t1760752485$j43$l0$h0',
    '__stripe_mid': '171add92-3c03-42c9-8899-4eca77d7b00742e75c',
    '__stripe_sid': '7724941d-e578-4ccf-a309-2254c5b7360cc6e596',
    '_rdt_uuid': '1760553430382.98fd4e0c-c2e9-4d7f-81aa-9891310e62e1',
    '_rdt_em': ':6022ff9424d023ad1b5546c27c687bc02ad92f77fc51cc2bd057c298a4915c4b',
    'g_state': '{"i_l":0,"i_ll":1760753307664,"i_b":"rDzBRKpPLIajaTgnJObhPtzGCWnH4lqw1NTw4gBos4w"}',
    '_ga_HSVH9T016H': 'GS2.1.s1760753186$o5$g1$t1760753307$j58$l0$h0',
    'ndut_fmt': 'F780D97B55A21872100B5758F906AE249700ED6CF74EDA62ED1905C7F20C94DF',
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
        'usage': 'To use the API, please use the /api/tera?url= or /api/tbox?url= endpoints.',
        'api 1 - advance': '/api/tbox?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 2 - standerd': '/api/tera?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
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

@app.route(rule='/help', methods=['GET'])
async def help():
    response = {
        'Info': "There are multiple ways to use this API as shown below",
        'usage': 'To use the API, please use the /api/tera?url= or /api/tbox?url= endpoints.',
        'api 1 - advance': '/api/tbox?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'api 2 - standerd': '/api/tera?url=https://1024terabox.com/s/1JgR2kxkwLsM7kEpj2Gntvw',
        'help': '/help for more details',
        'contact': '@no_coder_pro'
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
