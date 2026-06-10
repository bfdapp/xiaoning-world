"""彤彤语音服务 - 微软 Edge TTS 代理（免费，不需要 API Key）"""
import asyncio, edge_tts, io, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys, os

PORT = 8081
VOICE = "zh-CN-XiaoxiaoNeural"  # 最好听的自然女声

class TTSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/tts':
            params = parse_qs(parsed.query)
            text = params.get('text', [''])[0]
            if not text:
                self.send_error(400, 'Missing text')
                return

            # 生成语音
            mp3_data = asyncio.run(self.generate(text))

            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(mp3_data)
        else:
            self.send_error(404)

    async def generate(self, text):
        communicate = edge_tts.Communicate(text, VOICE, rate='-10%', pitch='+5Hz')
        chunks = []
        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                chunks.append(chunk['data'])
        return b''.join(chunks)

    def log_message(self, format, *args):
        pass  # 静默

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), TTSHandler)
    print(f'🎤 彤彤语音服务已启动 → http://127.0.0.1:{PORT}/tts?text=你好')
    print(f'   声音：{VOICE}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()