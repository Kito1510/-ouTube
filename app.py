from flask import Flask, jsonify, request
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/video_info', methods=['GET'])
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        command = ["yt-dlp", "-j", video_url]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        output = process.stdout
        video_info = json.loads(output)

        # サムネイルURLを生成
        if 'thumbnails' in video_info and video_info['thumbnails']:
            thumbnail_url = video_info['thumbnails'][-1].get('url', None)
            video_info['thumbnail'] = thumbnail_url

        # 必要な情報を抽出
        extracted_info = {
            'title': video_info.get('title'),
            'url': video_info.get('webpage_url'),
            'formats': video_info.get('formats', []),
            'thumbnail': video_info.get('thumbnail'),
            # 必要に応じて他の情報も追加
        }
        return jsonify(extracted_info)

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'yt-dlp error: {e.stderr}'}), 500
    except json.JSONDecodeError as e:
         return jsonify({'error': f'JSON error: {e}'}), 500
    except Exception as e:
         return jsonify({'error': f'Unexpected error: {e}'}), 500

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400
    try:
        command = ["yt-dlp", "-f", "bestvideo+bestaudio", "--no-playlist", "--no-progress", "--output", "video.%(ext)s", video_url]
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        #ダウンロードされた動画ファイルのパスを取得
        downloaded_file = process.stdout.split("Destination: ")[1].split(".")[0] + ".mp4"

        return jsonify({'downloaded_file': downloaded_file})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'yt-dlp error: {e.stderr}'}), 500
    except json.JSONDecodeError as e:
         return jsonify({'error': f'JSON error: {e}'}), 500
    except Exception as e:
         return jsonify({'error': f'Unexpected error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
